"""
Agent Manager - Merkezi Yönetim API
Takım oluşturma, iş akışı yönetimi, maliyet takibi ve monitoring.
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
import json
import os
import uuid

from domains import get_all_domains, get_domain, get_domain_agents, get_agent, BUSINESS_DOMAINS
from cost_tracker import cost_tracker
from mail_listener import MailListenerAgent

app = Flask(__name__, static_folder='monitor/static', template_folder='monitor/templates')
CORS(app)

# ============================================================
# IN-MEMORY DATA STORES
# ============================================================

# Takımlar
TEAMS_FILE = os.path.join(os.path.dirname(__file__), "teams_data.json")

teams = {}

def load_teams():
    global teams
    if os.path.exists(TEAMS_FILE):
        try:
            with open(TEAMS_FILE, "r", encoding="utf-8") as f:
                teams = json.load(f)
        except:
            teams = {}

def save_teams():
    with open(TEAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)

load_teams()

# Canlı durum
current_status = {
    "agent": "Idle",
    "task": "Waiting for tasks...",
    "project": "None",
    "step": "0/0",
    "logs": [],
    "last_updated": datetime.now().isoformat()
}

# ============================================================
# PAGES
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')

# ============================================================
# DOMAIN API
# ============================================================

@app.route('/api/domains', methods=['GET'])
def api_get_domains():
    """Tüm iş alanlarını listele"""
    return jsonify(get_all_domains())

@app.route('/api/domains/<domain_id>', methods=['GET'])
def api_get_domain(domain_id):
    """Belirli bir iş alanını getir"""
    domain = get_domain(domain_id)
    if not domain:
        return jsonify({"error": "Domain not found"}), 404
    return jsonify(domain)

@app.route('/api/domains/<domain_id>/agents', methods=['GET'])
def api_get_domain_agents(domain_id):
    """Bir iş alanındaki ajanları getir"""
    agents = get_domain_agents(domain_id)
    if not agents:
        return jsonify({"error": "Domain not found"}), 404
    return jsonify(agents)

# ============================================================
# TEAM API
# ============================================================

@app.route('/api/teams', methods=['GET'])
def api_get_teams():
    """Tüm takımları listele"""
    return jsonify(list(teams.values()))

@app.route('/api/teams', methods=['POST'])
def api_create_team():
    """Yeni takım oluştur"""
    data = request.json
    team_id = str(uuid.uuid4())[:8]

    team = {
        "id": team_id,
        "name": data.get("name", f"Takım-{team_id}"),
        "domain_id": data.get("domain_id"),
        "domain_name": "",
        "agents": data.get("agents", []),  # Agent ID listesi
        "agent_order": data.get("agent_order", []),  # Sıralama
        "status": "idle",
        "created_at": datetime.now().isoformat(),
        "total_runs": 0,
        "total_cost_usd": 0
    }

    # Domain adını ekle
    domain = get_domain(data.get("domain_id", ""))
    if domain:
        team["domain_name"] = domain["name"]
        # Agent detaylarını ekle
        team["agent_details"] = []
        for agent_id in team["agents"]:
            agent = get_agent(team["domain_id"], agent_id)
            if agent:
                team["agent_details"].append(agent)

    teams[team_id] = team
    save_teams()

    return jsonify(team), 201

@app.route('/api/teams/<team_id>', methods=['GET'])
def api_get_team(team_id):
    """Takım detaylarını getir"""
    team = teams.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404
    return jsonify(team)

@app.route('/api/teams/<team_id>', methods=['PUT'])
def api_update_team(team_id):
    """Takımı güncelle (agent ekle/çıkar/sırala)"""
    team = teams.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    data = request.json
    if "name" in data:
        team["name"] = data["name"]
    if "agents" in data:
        team["agents"] = data["agents"]
        # Agent detaylarını güncelle
        team["agent_details"] = []
        for agent_id in team["agents"]:
            agent = get_agent(team["domain_id"], agent_id)
            if agent:
                team["agent_details"].append(agent)
    if "agent_order" in data:
        team["agent_order"] = data["agent_order"]

    save_teams()
    return jsonify(team)

@app.route('/api/teams/<team_id>', methods=['DELETE'])
def api_delete_team(team_id):
    """Takımı sil"""
    if team_id in teams:
        del teams[team_id]
        save_teams()
        return jsonify({"success": True})
    return jsonify({"error": "Team not found"}), 404

# ============================================================
# TASK EXECUTION API
# ============================================================

@app.route('/api/teams/<team_id>/run', methods=['POST'])
def api_run_team(team_id):
    """Takımı bir görev üzerinde çalıştır"""
    team = teams.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    # Agent kontrolü - takımda agent yoksa çalıştırma
    agent_ids = team.get("agent_order") or team.get("agents", [])
    if not agent_ids:
        return jsonify({
            "error": "Bu takımda hiç agent yok! Lütfen önce takıma agent ekleyin.",
            "team_id": team_id,
            "team_name": team.get("name", "")
        }), 400

    data = request.json
    task_description = data.get("task", "")
    if not task_description:
        return jsonify({"error": "Task description is required"}), 400

    task_id = str(uuid.uuid4())[:8]

    # Takım durumunu güncelle
    team["status"] = "running"
    team["total_runs"] = team.get("total_runs", 0) + 1
    save_teams()

    # Arka planda çalıştır
    from team_executor import run_team_task_async
    run_team_task_async(team, task_description, task_id)

    return jsonify({
        "task_id": task_id,
        "team_id": team_id,
        "status": "started",
        "message": f"Görev başlatıldı! Task ID: {task_id}"
    }), 202

@app.route('/api/tasks/<task_id>', methods=['GET'])
def api_get_task_result(task_id):
    """Görev sonuçlarını getir"""
    results_dir = os.path.join(os.path.dirname(__file__), "task_results")
    filepath = os.path.join(results_dir, f"{task_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Eğer eski format ise (generated_files yok), retroactively işle
            if "generated_files" not in data and "outputs" in data:
                from team_executor import save_project_files
                generated_files = save_project_files(task_id, data["outputs"])
                data["generated_files"] = generated_files
                data["project_dir"] = f"generated_projects/{task_id}"
                with open(filepath, "w", encoding="utf-8") as fw:
                    json.dump(data, fw, indent=2, ensure_ascii=False)
            return jsonify(data)
    return jsonify({"status": "running", "task_id": task_id})

@app.route('/api/tasks', methods=['GET'])
def api_list_tasks():
    """Tüm tamamlanmış görevleri listele"""
    results_dir = os.path.join(os.path.dirname(__file__), "task_results")
    if not os.path.exists(results_dir):
        return jsonify([])
    tasks = []
    for fname in sorted(os.listdir(results_dir), reverse=True):
        if fname.endswith(".json"):
            filepath = os.path.join(results_dir, fname)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                tasks.append({
                    "task_id": data.get("task_id"),
                    "team_name": data.get("team_name"),
                    "task_description": data.get("task_description"),
                    "timestamp": data.get("timestamp"),
                    "agent_count": len(data.get("outputs", [])),
                    "file_count": len(data.get("generated_files", []))
                })
    return jsonify(tasks)

@app.route('/api/tasks/<task_id>/files/<path:filename>', methods=['GET'])
def api_get_file_content(task_id, filename):
    """Oluşturulan dosyanın içeriğini getir"""
    project_dir = os.path.join(os.path.dirname(__file__), "generated_projects", task_id)
    filepath = os.path.join(project_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({
            "filename": filename,
            "content": content,
            "lines": len(content.split('\n'))
        })
    return jsonify({"error": "File not found"}), 404

# ============================================================
# COST API
# ============================================================

@app.route('/api/costs', methods=['GET'])
def api_get_costs():
    """Genel maliyet özeti"""
    return jsonify(cost_tracker.get_all_summary())

@app.route('/api/costs/team/<team_id>', methods=['GET'])
def api_get_team_costs(team_id):
    """Takım bazında maliyet"""
    return jsonify(cost_tracker.get_team_summary(team_id))

@app.route('/api/costs/log', methods=['POST'])
def api_log_cost():
    """Maliyet kaydı ekle (orchestrator'dan çağrılır)"""
    data = request.json
    record = cost_tracker.log_usage(
        team_id=data.get("team_id", "default"),
        agent_id=data.get("agent_id", "unknown"),
        agent_name=data.get("agent_name", "Unknown"),
        input_tokens=data.get("input_tokens", 0),
        output_tokens=data.get("output_tokens", 0),
        model=data.get("model", "gpt-4o-mini"),
        task_description=data.get("task_description", "")
    )
    return jsonify(record)

# ============================================================
# MONITORING API (Mevcut dashboard ile uyumlu)
# ============================================================

@app.route('/api/status', methods=['GET'])
def api_get_status():
    """Canlı durum"""
    return jsonify(current_status)

@app.route('/api/update_status', methods=['POST'])
def api_update_status():
    """Durum güncelle (orchestrator'dan çağrılır)"""
    global current_status
    data = request.json

    new_log = data.get("log")
    if new_log:
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {new_log}"
        current_status["logs"].append(log_entry)
        if len(current_status["logs"]) > 50:
            current_status["logs"] = current_status["logs"][-50:]

    if "agent" in data: current_status["agent"] = data["agent"]
    if "task" in data: current_status["task"] = data["task"]
    if "project" in data: current_status["project"] = data["project"]
    if "step" in data: current_status["step"] = data["step"]

    current_status["last_updated"] = datetime.now().isoformat()
    return jsonify({"success": True})

# ============================================================
# KNOWLEDGE API (Agent Eğitim Bilgi Bankası)
# ============================================================

from knowledge_base import (
    list_domains_with_knowledge, list_knowledge_files,
    get_knowledge_content, save_knowledge_file,
    delete_knowledge_file, get_knowledge_stats
)

@app.route('/api/knowledge', methods=['GET'])
def api_list_knowledge():
    """Tüm domain bilgi dosyalarını listele"""
    return jsonify(list_domains_with_knowledge())

@app.route('/api/knowledge/stats', methods=['GET'])
def api_knowledge_stats():
    """Bilgi bankası istatistikleri"""
    return jsonify(get_knowledge_stats())

@app.route('/api/knowledge/<domain_id>', methods=['GET'])
def api_list_domain_knowledge(domain_id):
    """Belirli bir domainin bilgi dosyalarını listele"""
    return jsonify(list_knowledge_files(domain_id))

@app.route('/api/knowledge/<domain_id>/<filename>', methods=['GET'])
def api_get_knowledge_file(domain_id, filename):
    """Bilgi dosyasının içeriğini oku"""
    content = get_knowledge_content(domain_id, filename)
    if content is None:
        return jsonify({"error": "Dosya bulunamadı"}), 404
    return jsonify({"filename": filename, "domain": domain_id, "content": content})

@app.route('/api/knowledge/<domain_id>', methods=['POST'])
def api_save_knowledge(domain_id):
    """Yeni bilgi dosyası ekle veya güncelle"""
    data = request.json
    filename = data.get("filename", "")
    content = data.get("content", "")
    if not filename or not content:
        return jsonify({"error": "filename ve content gerekli"}), 400
    result = save_knowledge_file(domain_id, filename, content)
    return jsonify(result)

@app.route('/api/knowledge/<domain_id>/<filename>', methods=['DELETE'])
def api_delete_knowledge(domain_id, filename):
    """Bilgi dosyasını sil"""
    if delete_knowledge_file(domain_id, filename):
        return jsonify({"success": True, "deleted": filename})
    return jsonify({"error": "Dosya bulunamadı"}), 404

# ============================================================
# BERQUN API (Verimlilik Analizi Entegrasyonu)
# ============================================================

from berqun_client import get_berqun_client

@app.route('/api/berqun/test', methods=['GET'])
def api_berqun_test():
    """Berqun bağlantı testi"""
    client = get_berqun_client()
    success = client.login()
    return jsonify({
        "connected": success,
        "server": client.server,
        "username": client.username
    })

@app.route('/api/berqun/staff', methods=['GET'])
def api_berqun_staff():
    """Berqun personel listesi"""
    try:
        client = get_berqun_client()
        staff = client.get_staff_list()
        return jsonify({"total": len(staff), "staff": staff})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/berqun/dashboard/<person_guid>', methods=['GET'])
def api_berqun_dashboard(person_guid):
    """Personel BQ dashboard verisi"""
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    period = int(request.args.get('period', 13003))  # default: aylık
    try:
        client = get_berqun_client()
        data = client.get_user_dashboard(person_guid, date, period)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/berqun/report/monthly', methods=['POST'])
def api_berqun_monthly_report():
    """Aylık verimlilik raporu oluştur"""
    data = request.json or {}
    date = data.get("date", datetime.now().strftime("%Y-%m-01"))
    try:
        client = get_berqun_client()
        report = client.generate_monthly_report(date)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# RAPOR & MAİL API
# ============================================================

from berqun_report_generator import (
    generate_full_gmy_report, group_staff_by_gmy,
    classify_team_to_gmy, group_staff_by_team
)
from mail_sender import send_report_mail, send_gmy_reports

@app.route('/api/berqun/report/generate', methods=['POST'])
def api_generate_report():
    """Tam GMY raporu oluştur (HTML + Excel)"""
    data = request.json or {}
    date = data.get("date", datetime.now().strftime("%Y-%m-01"))
    output_dir = data.get("output_dir", "generated_reports")
    try:
        import threading
        task_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        def run():
            result = generate_full_gmy_report(date, output_dir)
            # Sonucu dosyaya kaydet
            import json
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, f"{task_id}.json"), "w", encoding="utf-8") as f:
                # HTML'i çıkar (çok büyük)
                save_data = {k: v for k, v in result.items()}
                for gmy in save_data.get("gmy_reports", {}):
                    save_data["gmy_reports"][gmy] = {
                        k: v for k, v in save_data["gmy_reports"][gmy].items()
                        if k != "html"
                    }
                json.dump(save_data, f, ensure_ascii=False, indent=2, default=str)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return jsonify({"task_id": task_id, "status": "generating", "date": date})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/berqun/teams', methods=['GET'])
def api_berqun_teams():
    """Berqun takımlarını GMY bazında grupla"""
    try:
        client = get_berqun_client()
        staff_list = client.get_staff_list()
        teams = group_staff_by_team(staff_list)
        gmy_groups = group_staff_by_gmy(staff_list)

        result = {}
        for gmy_name, gmy_data in gmy_groups.items():
            team_summary = {}
            for team_name, team_staff in gmy_data["teams"].items():
                team_summary[team_name] = {
                    "count": len(team_staff),
                    "members": [
                        {"name": f"{s.get('name','')} {s.get('surname','')}",
                         "email": s.get("email", "")}
                        for s in team_staff
                    ]
                }
            result[gmy_name] = {
                "total_staff": gmy_data["total_staff"],
                "team_count": len(gmy_data["teams"]),
                "teams": team_summary
            }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/berqun/report/preview/<gmy_name>', methods=['GET'])
def api_report_preview(gmy_name):
    """Belirli bir GMY'nin rapor HTML önizlemesi"""
    report_dir = "generated_reports"
    # En son oluşturulan raporu bul
    try:
        files = [f for f in os.listdir(report_dir)
                 if f.endswith("_mail.html") and gmy_name.replace(" ", "_") in f]
        if files:
            latest = sorted(files)[-1]
            with open(os.path.join(report_dir, latest), "r", encoding="utf-8") as f:
                return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
        return jsonify({"error": "Rapor bulunamadı"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/berqun/report/send', methods=['POST'])
def api_send_report():
    """GMY raporlarını mail olarak gönder"""
    data = request.json or {}
    gmy_emails = data.get("gmy_emails", {})
    report_dir = data.get("report_dir", "generated_reports")

    try:
        # En son raporu yükle
        json_files = [f for f in os.listdir(report_dir) if f.startswith("report_") and f.endswith(".json")]
        if not json_files:
            return jsonify({"error": "Önce rapor oluşturun"}), 400

        latest = sorted(json_files)[-1]
        with open(os.path.join(report_dir, latest), "r", encoding="utf-8") as f:
            report_data = json.load(f)

        results = send_gmy_reports(report_data, gmy_emails)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from generate_combined_reports import run_batch_reports

@app.route('/api/berqun/domains', methods=['GET'])
def api_berqun_domains():
    """Rapor için kullanılabilir domainleri listele"""
    try:
        client = get_berqun_client()
        staff_list = client.get_staff_list()
        groups = group_staff_by_gmy(staff_list)
        # Personel sayısına göre sıralı
        domains = sorted(groups.keys(), key=lambda k: -groups[k]["total_staff"])
        return jsonify({"domains": domains})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/berqun/run_batch', methods=['POST'])
def api_run_batch():
    """Seçili domainler için rapor sürecini başlat"""
    data = request.json or {}
    domains = data.get("domains") # List or None
    month_label = data.get("month_label", "Ocak 2026")
    month_en = data.get("month_en", "Ocak_2026")
    
    # Custom log callback that updates global status
    def log_to_dashboard(msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [BERQUN] {msg}"
        print(entry) # Console
        current_status["logs"].append(entry)
        if len(current_status["logs"]) > 100:
            current_status["logs"] = current_status["logs"][-100:]
        current_status["task"] = f"Berqun Rapor: {msg[:50]}..."
        current_status["last_updated"] = datetime.now().isoformat()

    import threading
    def run():
        try:
            current_status["agent"] = "Working"
            kwargs = {
                "selected_domains": domains,
                "report_month": month_label,
                "month_en": month_en,
                "log_callback": log_to_dashboard
            }
            if data.get("start_date"): kwargs["start_date"] = data["start_date"]
            if data.get("end_date"): kwargs["end_date"] = data["end_date"]
            if data.get("report_date"): kwargs["report_date"] = data["report_date"]

            total_count = run_batch_reports(**kwargs)
            
            # Log Cost
            if total_count and total_count > 0:
                from cost_tracker import cost_tracker
                cost_tracker.log_usage(
                    team_id="berqun_reporting",
                    agent_id="berqun-reporter",
                    agent_name="Berqun Verimlilik Ajanı",
                    input_tokens=total_count,
                    output_tokens=total_count,
                    model="berqun-api",
                    task_description=f"Rapor Paketi: {month_label}"
                )

            current_status["agent"] = "Idle"
            current_status["task"] = "Berqun Raporları Tamamlandı"
        except Exception as e:
            current_status["agent"] = "Error"
            log_to_dashboard(f"Hata: {str(e)}")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    
    return jsonify({"status": "started", "domains": domains})


# ============================================================
# HAFTALIK RAPOR API
# ============================================================

@app.route('/api/berqun/weekly_pos', methods=['POST'])
def api_weekly_report():
    """Haftalik ekip raporu tetikle (tum ekipler veya belirli bir ekip)"""
    data = request.json or {}
    week_start = data.get("week_start")
    week_end = data.get("week_end")
    no_mail = data.get("no_mail", False)
    team_filter = data.get("team")

    def log_to_dashboard_wp(msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [BERQUN-WEEKLY] {msg}"
        print(entry)
        current_status["logs"].append(entry)
        if len(current_status["logs"]) > 100:
            current_status["logs"] = current_status["logs"][-100:]
        current_status["task"] = f"Haftalik Rapor: {msg[:50]}..."
        current_status["last_updated"] = datetime.now().isoformat()

    import threading as _threading_wp
    def run_wp():
        try:
            current_status["agent"] = "Working"
            log_to_dashboard_wp("Haftalik rapor baslatiliyor...")

            import subprocess, sys
            cmd = [sys.executable, "generate_weekly_reports.py"]
            if week_start:
                cmd += ["--week-start", week_start]
            if week_end:
                cmd += ["--week-end", week_end]
            if no_mail:
                cmd.append("--no-mail")
            if team_filter:
                cmd += ["--team", team_filter]

            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace"
            )
            for line in iter(proc.stdout.readline, ''):
                line = line.strip()
                if line:
                    log_to_dashboard_wp(line)
            proc.wait()

            if proc.returncode == 0:
                current_status["agent"] = "Idle"
                current_status["task"] = "Haftalik Rapor Tamamlandi"
                log_to_dashboard_wp("Haftalik rapor basariyla tamamlandi!")
            else:
                current_status["agent"] = "Error"
                log_to_dashboard_wp(f"❌ Rapor hatası (exit code: {proc.returncode})")
        except Exception as e:
            current_status["agent"] = "Error"
            log_to_dashboard_wp(f"❌ Hata: {str(e)}")

    _t = _threading_wp.Thread(target=run_wp, daemon=True)
    _t.start()
    return jsonify({"status": "started", "week_start": week_start, "week_end": week_end})


@app.route('/api/berqun/bq_trends', methods=['GET'])
def api_bq_trends():
    """Hafta-hafta BQ puan karşılaştırması — son 4 hafta"""
    try:
        from datetime import timedelta
        from berqun_client import PERIOD_WEEK
        client = get_berqun_client()
        staff_list = client.get_staff_list()
        groups = group_staff_by_gmy(staff_list)

        DOMAIN_NAME = "Payment Facilitator & Android POS & Soft POS"
        if DOMAIN_NAME not in groups:
            return jsonify({"error": "POS domain bulunamadı"}), 404

        pos_domain = groups[DOMAIN_NAME]
        today = datetime.now()

        # Son 4 haftanın Pazartesi'leri
        weeks = []
        for i in range(4):
            monday = today - timedelta(days=today.weekday() + 7 * (i + 1))
            weeks.append(monday.strftime("%Y-%m-%d"))
        weeks.reverse()

        trends = []
        for team_name, team_staff in pos_domain["teams"].items():
            for staff in team_staff[:5]:
                guid = staff.get("guid")
                name = staff.get("full_name",
                    f"{staff.get('name', '')} {staff.get('surname', '')}")
                if not guid:
                    continue
                weekly_bq = []
                for w in weeks:
                    try:
                        dash = client.get_user_dashboard(guid, w, PERIOD_WEEK)
                        bq = dash.get("user_bq_point_avg")
                        weekly_bq.append(float(bq) if bq else None)
                    except Exception:
                        weekly_bq.append(None)

                valid = [b for b in weekly_bq if b is not None]
                change = (valid[-1] - valid[0]) if len(valid) >= 2 else 0

                trends.append({
                    "name": name.strip(),
                    "team": team_name,
                    "weeks": weekly_bq,
                    "change": round(change, 1),
                    "latest_bq": valid[-1] if valid else None,
                })

        improving = sorted(
            [t for t in trends if t["change"] > 0], key=lambda x: -x["change"]
        )[:5]
        declining = sorted(
            [t for t in trends if t["change"] < 0], key=lambda x: x["change"]
        )[:5]

        return jsonify({
            "week_labels": weeks,
            "trends": trends,
            "improving": improving,
            "declining": declining,
            "total_staff": pos_domain["total_staff"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/berqun/ai_summary', methods=['POST'])
def api_ai_summary():
    """Haftalık yönetici özeti oluştur (rule-based + isteğe bağlı GPT)"""
    data = request.json or {}
    week_label = data.get("week_label", "Bu Hafta")

    try:
        from berqun_client import PERIOD_WEEK
        client = get_berqun_client()
        staff_list = client.get_staff_list()
        groups = group_staff_by_gmy(staff_list)

        DOMAIN_NAME = "Payment Facilitator & Android POS & Soft POS"
        if DOMAIN_NAME not in groups:
            return jsonify({"error": "POS domain bulunamadı"}), 404

        pos_domain = groups[DOMAIN_NAME]
        total = pos_domain["total_staff"]

        bq_scores = []
        low_bq_count = 0
        for team_name, team_staff in pos_domain["teams"].items():
            for staff in team_staff:
                guid = staff.get("guid")
                if guid:
                    try:
                        dash = client.get_user_dashboard(
                            guid,
                            datetime.now().strftime("%Y-%m-%d"),
                            PERIOD_WEEK
                        )
                        bq = dash.get("user_bq_point_avg")
                        if bq:
                            bq_val = float(bq)
                            bq_scores.append(bq_val)
                            if bq_val < 100:
                                low_bq_count += 1
                    except Exception:
                        pass

        avg_bq = sum(bq_scores) / len(bq_scores) if bq_scores else 0
        max_bq = max(bq_scores) if bq_scores else 0
        min_bq = min(bq_scores) if bq_scores else 0

        parts = [
            f"📊 **{week_label} — POS Ekibi Haftalık Özet**\n",
            f"• Toplam personel: **{total}** kişi",
            f"• Ortalama BQ puanı: **{avg_bq:.1f}**",
            f"• En yüksek BQ: **{max_bq:.0f}** | En düşük: **{min_bq:.0f}**",
            f"• BQ < 100 olan: **{low_bq_count}** kişi",
        ]

        if avg_bq >= 120:
            parts.append(
                "\n🟢 **Değerlendirme:** Ekip yüksek verimlilikle çalışıyor."
            )
        elif avg_bq >= 100:
            parts.append(
                "\n🟡 **Değerlendirme:** Verimlilik kabul edilebilir. İyileştirme alanları mevcut."
            )
        else:
            parts.append(
                "\n🔴 **Değerlendirme:** Verimlilik kritik. Acil aksiyon gerekli."
            )

        if low_bq_count > 0:
            ratio = (low_bq_count / total * 100) if total > 0 else 0
            parts.append(
                f"\n⚠️ Personelin **%{ratio:.0f}**'i hedef BQ altında. Bireysel takip önerilir."
            )

        parts.append(
            f"\n_Rapor otomatik oluşturulmuştur — {datetime.now().strftime('%d.%m.%Y %H:%M')}_"
        )

        return jsonify({
            "summary": "\n".join(parts),
            "metrics": {
                "total_staff": total,
                "avg_bq": round(avg_bq, 1),
                "max_bq": round(max_bq, 1),
                "min_bq": round(min_bq, 1),
                "low_bq_count": low_bq_count,
                "measured_count": len(bq_scores),
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================
# SKILL MANAGEMENT API
# Tek kaynak: .agent/skills/{skill-name}/SKILL.md
# ============================================================

import glob as glob_module

SKILLS_DIR = os.path.join(os.path.dirname(__file__), ".agent", "skills")


def resolve_skill_path(skill_name):
    """
    domains.py'deki skill_name (alt çizgili) -> .agent/skills/{tire-format}/SKILL.md
    Döndürür: (filepath, exists)
    """
    dash_name = skill_name.replace("_", "-")
    filepath = os.path.join(SKILLS_DIR, dash_name, "SKILL.md")
    return filepath, os.path.exists(filepath)


@app.route('/api/skills', methods=['GET'])
def api_list_skills():
    """Tüm skill dosyalarını listele (.agent/skills/ altından)"""
    skills = []
    if not os.path.exists(SKILLS_DIR):
        return jsonify(skills)

    for dirname in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, dirname)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isdir(skill_dir) or not os.path.exists(skill_file):
            continue

        # Tire -> alt çizgi (domains.py formatı)
        skill_name = dirname.replace("-", "_")
        size = os.path.getsize(skill_file)

        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
            first_line = content.split("\n")[0].replace("#", "").strip()

        # YAML frontmatter varsa asıl başlığı al
        if first_line.startswith("---"):
            lines = content.split("\n")
            for line in lines[1:]:
                if line.startswith("name:"):
                    first_line = line.replace("name:", "").strip().strip('"').strip("'")
                    break
                if line.startswith("---"):
                    break

        # Bu skill'i kullanan agent'ları bul
        assigned_agents = []
        for domain_id, domain in BUSINESS_DOMAINS.items():
            for agent_id, agent in domain["agents"].items():
                if agent.get("skill") == skill_name:
                    assigned_agents.append({
                        "agent_id": agent_id,
                        "agent_name": agent["name"],
                        "agent_icon": agent["icon"],
                        "domain_id": domain_id,
                        "domain_name": domain["name"]
                    })
        skills.append({
            "name": skill_name,
            "title": first_line,
            "filename": "SKILL.md",
            "dir": dirname,
            "size": size,
            "lines": len(content.split("\n")),
            "assigned_agents": assigned_agents,
            "agent_count": len(assigned_agents)
        })
    return jsonify(skills)

@app.route('/api/skills/<skill_name>', methods=['GET'])
def api_get_skill(skill_name):
    """Skill içeriğini oku"""
    filepath, exists = resolve_skill_path(skill_name)
    if not exists:
        return jsonify({"error": "Skill bulunamadı"}), 404
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Atanan agent'ları bul
    assigned_agents = []
    for domain_id, domain in BUSINESS_DOMAINS.items():
        for agent_id, agent in domain["agents"].items():
            if agent.get("skill") == skill_name:
                assigned_agents.append({
                    "agent_id": agent_id,
                    "agent_name": agent["name"],
                    "agent_icon": agent["icon"],
                    "domain_id": domain_id
                })
    return jsonify({
        "name": skill_name,
        "content": content,
        "lines": len(content.split("\n")),
        "size": len(content),
        "assigned_agents": assigned_agents
    })

@app.route('/api/skills/<skill_name>', methods=['PUT'])
def api_update_skill(skill_name):

    """Skill içeriğini güncelle"""
    data = request.json
    content = data.get("content", "")
    if not content:
        return jsonify({"error": "content gerekli"}), 400

    filepath, exists = resolve_skill_path(skill_name)
    if exists:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        dash_name = skill_name.replace("_", "-")
        skill_dir = os.path.join(SKILLS_DIR, dash_name)
        os.makedirs(skill_dir, exist_ok=True)
        filepath = os.path.join(skill_dir, "SKILL.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return jsonify({"success": True, "name": skill_name, "size": len(content)})

@app.route('/api/skills', methods=['POST'])
def api_create_skill():
    """Yeni skill oluştur"""
    data = request.json
    name = data.get("name", "").strip().lower().replace(" ", "_")
    content = data.get("content", "")
    if not name or not content:
        return jsonify({"error": "name ve content gerekli"}), 400

    _, exists = resolve_skill_path(name)
    if exists:
        return jsonify({"error": "Bu isimde skill zaten var"}), 409

    dash_name = name.replace("_", "-")
    skill_dir = os.path.join(SKILLS_DIR, dash_name)
    os.makedirs(skill_dir, exist_ok=True)
    filepath = os.path.join(skill_dir, "SKILL.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return jsonify({"success": True, "name": name, "size": len(content)}), 201

@app.route('/api/skills/<skill_name>', methods=['DELETE'])
def api_delete_skill(skill_name):
    """Skill sil"""
    filepath, exists = resolve_skill_path(skill_name)
    if not exists:
        return jsonify({"error": "Skill bulunamadı"}), 404
    os.remove(filepath)
    return jsonify({"success": True, "deleted": skill_name})

@app.route('/api/agents/skills-overview', methods=['GET'])
def api_agents_skills_overview():
    """Tüm agent'ların skill durumunu özet olarak döndür"""
    overview = []
    for domain_id, domain in BUSINESS_DOMAINS.items():
        for agent_id, agent in domain["agents"].items():
            skill_name = agent.get("skill", "")
            skill_loaded = False
            skill_size = 0
            if skill_name:
                filepath, exists = resolve_skill_path(skill_name)
                if exists:
                    skill_loaded = True
                    skill_size = os.path.getsize(filepath)
            overview.append({
                "agent_id": agent_id,
                "agent_name": agent["name"],
                "agent_icon": agent["icon"],
                "domain_id": domain_id,
                "domain_name": domain["name"],
                "skill": skill_name or None,
                "skill_loaded": skill_loaded,
                "skill_size": skill_size,
                "cost_per_hour": agent.get("cost_per_hour", 0)
            })
    return jsonify(overview)


# ============================================================
# AGENT PERFORMANCE API
# ============================================================

@app.route('/api/performance/agents', methods=['GET'])
def api_agent_performance():
    """Agent bazında performans metrikleri"""
    summary = cost_tracker.get_all_summary()
    agents_perf = {}

    # Cost tracker'dan agent bazında veri topla
    for record in summary.get("records", []):
        agent_id = record.get("agent_id", "unknown")
        if agent_id not in agents_perf:
            agents_perf[agent_id] = {
                "agent_id": agent_id,
                "agent_name": record.get("agent_name", "Unknown"),
                "total_runs": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost_usd": 0,
                "tasks": []
            }
        perf = agents_perf[agent_id]
        perf["total_runs"] += 1
        perf["total_input_tokens"] += record.get("input_tokens", 0)
        perf["total_output_tokens"] += record.get("output_tokens", 0)
        perf["total_cost_usd"] += record.get("cost_usd", 0)
        perf["tasks"].append({
            "task": record.get("task_description", "")[:60],
            "cost": record.get("cost_usd", 0),
            "tokens": record.get("input_tokens", 0) + record.get("output_tokens", 0),
            "timestamp": record.get("timestamp", "")
        })

    # Skill bilgisini ekle
    for agent_id, perf in agents_perf.items():
        for _, domain in BUSINESS_DOMAINS.items():
            agent_config = domain["agents"].get(agent_id)
            if agent_config:
                perf["skill"] = agent_config.get("skill", "")
                perf["agent_icon"] = agent_config.get("icon", "")
                perf["domain"] = domain["name"]
                break

    return jsonify(list(agents_perf.values()))

# ============================================================
# PROJECTS API (Oluşturulan Projeleri Görüntüleme & Test)
# ============================================================

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "Projects")
GENERATED_PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "generated_projects")

@app.route('/api/projects')
def api_list_projects():
    """Projects ve generated_projects klasörlerindeki tüm projeleri listele"""
    projects = []

    # Her iki klasörü de tara
    dirs_to_scan = [
        (PROJECTS_DIR, "manual"),
        (GENERATED_PROJECTS_DIR, "generated")
    ]

    for base_dir, source in dirs_to_scan:
        if not os.path.exists(base_dir):
            continue

        for name in sorted(os.listdir(base_dir), reverse=True):
            proj_path = os.path.join(base_dir, name)
            if os.path.isdir(proj_path):
                files = []
                total_size = 0
                for fname in sorted(os.listdir(proj_path)):
                    fpath = os.path.join(proj_path, fname)
                    if os.path.isfile(fpath):
                        size = os.path.getsize(fpath)
                        total_size += size
                        ext = os.path.splitext(fname)[1].lower()
                        lang_map = {
                            '.py': 'python', '.js': 'javascript', '.jsx': 'jsx',
                            '.ts': 'typescript', '.tsx': 'tsx', '.html': 'html',
                            '.css': 'css', '.json': 'json', '.md': 'markdown',
                            '.sql': 'python'
                        }
                        files.append({
                            "name": fname,
                            "size": size,
                            "language": lang_map.get(ext, "text"),
                            "extension": ext
                        })

                if not files:
                    continue

                has_jsx = any(f['extension'] in ['.jsx', '.tsx'] for f in files)
                has_js = any(f['extension'] in ['.js'] for f in files)
                has_py = any(f['extension'] == '.py' for f in files)
                has_html = any(f['extension'] == '.html' for f in files)
                has_css = any(f['extension'] == '.css' for f in files)

                if (has_jsx or has_js) and has_py:
                    proj_type = "fullstack"
                elif has_jsx or (has_js and has_css):
                    proj_type = "frontend"
                elif has_html:
                    proj_type = "static"
                elif has_py:
                    proj_type = "backend"
                else:
                    proj_type = "other"

                # Generated projeler için task sonucundan isim al
                display_name = name.replace("_", " ")
                if source == "generated":
                    task_result_path = os.path.join(os.path.dirname(__file__), "task_results", f"{name}.json")
                    if os.path.exists(task_result_path):
                        try:
                            with open(task_result_path, "r", encoding="utf-8") as f:
                                task_data = json.load(f)
                                desc = task_data.get("task_description", "")
                                if desc:
                                    display_name = desc[:50] + ("..." if len(desc) > 50 else "")
                        except:
                            pass

                projects.append({
                    "name": name,
                    "display_name": display_name,
                    "type": proj_type,
                    "files": files,
                    "file_count": len(files),
                    "total_size": total_size,
                    "source": source
                })

    return jsonify(projects)


@app.route('/api/projects/<project_name>/files/<filename>')
def api_get_project_file(project_name, filename):
    """Proje dosyasinin icerigini dondur"""
    # Her iki klasörde de ara
    file_path = os.path.join(PROJECTS_DIR, project_name, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(GENERATED_PROJECTS_DIR, project_name, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "Dosya bulunamadi"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({
            "filename": filename,
            "project": project_name,
            "content": content,
            "size": os.path.getsize(file_path),
            "lines": len(content.split('\n'))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/projects/<project_name>/preview')
def api_project_preview(project_name):
    """Proje onizleme - JSX/React projeleri icin sandbox HTML"""
    import re as regex
    # Her iki klasörde de ara
    proj_path = os.path.join(PROJECTS_DIR, project_name)
    if not os.path.exists(proj_path):
        proj_path = os.path.join(GENERATED_PROJECTS_DIR, project_name)
    if not os.path.exists(proj_path):
        return "Proje bulunamadi", 404

    files = os.listdir(proj_path)
    jsx_files = [f for f in files if f.endswith('.jsx') or f.endswith('.tsx')]
    html_files = [f for f in files if f.endswith('.html')]

    if jsx_files:
        jsx_path = os.path.join(proj_path, jsx_files[0])
        with open(jsx_path, "r", encoding="utf-8") as f:
            jsx_code = f.read()

        clean_code = regex.sub(r"^import\s+.*?;\s*$", "", jsx_code, flags=regex.MULTILINE)
        clean_code = regex.sub(r"^export\s+default\s+\w+;\s*$", "", clean_code, flags=regex.MULTILINE)
        clean_code = clean_code.replace("{", "{{").replace("}", "}}")
        # Undo double-braces for JSX/JS code blocks
        # Actually, since f-string uses {{ }}, we need to be careful
        # Let's use .format() instead

        sandbox = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROJ_NAME - Preview</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: 'Inter', sans-serif; background: #f8fafc; }
        .preview-banner {
            background: linear-gradient(135deg, #0d6efd, #6610f2);
            color: white; padding: 8px 16px; font-size: 12px;
            display: flex; align-items: center; justify-content: space-between;
        }
        .preview-banner span { font-weight: 600; }
        #root { padding: 20px; }
        .error-box {
            background: #fee2e2; border: 1px solid #fca5a5;
            border-radius: 8px; padding: 20px; margin: 20px;
            color: #991b1b; font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="preview-banner">
        <span>PROJ_DISPLAY - Live Preview</span>
        <span>React Sandbox</span>
    </div>
    <div id="root"></div>
    <script type="text/babel">
        const axios = {
            get: async (url) => ({ data: [
                { id: 1, name: 'Ornek Kategori 1', description: 'Bu bir demo kategorisidir' },
                { id: 2, name: 'Ornek Kategori 2', description: 'Test verisi' },
                { id: 3, name: 'Ornek Kategori 3', description: 'Sandbox onizleme' }
            ] }),
            post: async (url, data) => ({ data: { success: true, ...data } }),
            put: async (url, data) => ({ data: { success: true, ...data } }),
            delete: async (url) => ({ data: { success: true } })
        };

        try {
            JSX_CODE_HERE

            const root = ReactDOM.createRoot(document.getElementById('root'));
            if (typeof App !== 'undefined') {
                root.render(React.createElement(App));
            } else if (typeof MenuList !== 'undefined') {
                root.render(React.createElement(MenuList));
            } else {
                document.getElementById('root').innerHTML = '<div class="error-box">App bileseni bulunamadi.</div>';
            }
        } catch(e) {
            document.getElementById('root').innerHTML =
                '<div class="error-box"><strong>Render Hatasi:</strong><br/>' + e.message + '</div>';
            console.error(e);
        }
    </script>
</body>
</html>"""
        sandbox = sandbox.replace("PROJ_NAME", project_name)
        sandbox = sandbox.replace("PROJ_DISPLAY", project_name.replace('_', ' '))
        sandbox = sandbox.replace("JSX_CODE_HERE", clean_code)
        return sandbox, 200, {'Content-Type': 'text/html; charset=utf-8'}

    elif html_files:
        html_path = os.path.join(proj_path, html_files[0])
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}

    else:
        py_files = [f for f in files if f.endswith('.py')]
        if py_files:
            py_path = os.path.join(proj_path, py_files[0])
            with open(py_path, "r", encoding="utf-8") as f:
                code = f.read()

            lines_html = ""
            for i, line in enumerate(code.split('\n')):
                safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                lines_html += '<span style="color:#858585;margin-right:16px;user-select:none;">{:4d}</span>{}\n'.format(i+1, safe_line)

            page = """<!DOCTYPE html>
<html><head>
<style>
    body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; margin: 0; }
    .banner { background: linear-gradient(135deg, #198754, #0d6efd); color: white; padding: 8px 16px; font-size: 12px; margin: -20px -20px 20px; display:flex; justify-content:space-between; }
    pre { white-space: pre-wrap; line-height: 1.6; font-size: 14px; }
</style>
</head><body>
<div class="banner"><span>FILE_NAME - Backend Code</span><span>Python</span></div>
<pre>CODE_LINES</pre>
</body></html>"""
            page = page.replace("FILE_NAME", py_files[0])
            page = page.replace("CODE_LINES", lines_html)
            return page, 200, {'Content-Type': 'text/html; charset=utf-8'}

        return "Onizleme bulunamadi", 404


# ============================================================
# TRELLO WEBHOOK API
# ============================================================

from trello_webhook_handler import WebhookHandler, verify_trello_signature

# Webhook handler instance (board ayarlandığında oluşturulur)
_webhook_handler: WebhookHandler = None
_webhook_config = {
    "board_id": None,
    "webhook_id": None,
    "callback_url": None,
    "active": False
}

@app.route('/api/trello/webhook', methods=['HEAD'])
def api_trello_webhook_verify():
    """
    Trello webhook doğrulama endpoint'i.

    Trello, webhook oluştururken bu URL'e HEAD isteği gönderir.
    200 döndürmemiz yeterli.
    """
    return '', 200


@app.route('/api/trello/webhook', methods=['POST'])
def api_trello_webhook_receive():
    """
    Trello webhook event'lerini alan ana endpoint.

    Trello, board üzerinde değişiklik olduğunda bu endpoint'e
    JSON payload ile POST isteği gönderir.
    """
    global _webhook_handler

    if not _webhook_handler:
        return jsonify({"status": "not_configured"}), 200

    # İmza doğrulama (opsiyonel, güvenlik için)
    signature = request.headers.get("X-Trello-Webhook", "")
    if signature:
        callback_url = _webhook_config.get("callback_url", "")
        if not verify_trello_signature(request.data, signature, callback_url):
            return jsonify({"error": "Invalid signature"}), 403

    # Event'i işle
    payload = request.json
    if not payload:
        return jsonify({"status": "empty"}), 200

    result = _webhook_handler.process_event(payload)
    return jsonify(result), 200


@app.route('/api/trello/webhook/setup', methods=['POST'])
def api_trello_webhook_setup():
    """
    Webhook'u yapılandırır ve Trello'ya kaydeder.

    Body:
    {
        "board_id": "abc123",
        "callback_url": "https://your-domain.com/api/trello/webhook"  (opsiyonel)
    }

    Not: Lokal geliştirmede ngrok veya benzer bir tunnel gerekir.
    """
    global _webhook_handler, _webhook_config

    data = request.json or {}
    board_id = data.get("board_id")

    if not board_id:
        return jsonify({"error": "board_id gerekli"}), 400

    # Callback URL: Sağlanmazsa otomatik oluştur
    callback_url = data.get("callback_url")
    is_local = False
    if not callback_url:
        # Lokal geliştirme — Trello bu URL'e erişemez
        host = request.host
        scheme = request.scheme
        callback_url = f"{scheme}://{host}/api/trello/webhook"
        is_local = True
    elif "localhost" in callback_url or "127.0.0.1" in callback_url:
        is_local = True

    # TrelloHelper'ı oluştur
    from trello_helper import TrelloHelper
    trello_api_key = os.environ.get("TRELLO_API_KEY", "")
    trello_token = os.environ.get("TRELLO_TOKEN", "")

    if not trello_api_key or not trello_token:
        return jsonify({"error": "TRELLO_API_KEY ve TRELLO_TOKEN environment variable'ları gerekli"}), 500

    trello = TrelloHelper(trello_api_key, trello_token, board_id)

    # Board listelerini al
    lists = trello.get_lists(board_id)
    if not lists:
        return jsonify({"error": "Board listeleri alınamadı"}), 500

    list_ids = {lst['name']: lst['id'] for lst in lists}

    if "Backlog" not in list_ids:
        return jsonify({"error": "'Backlog' listesi bulunamadı"}), 400

    # Eski webhook varsa sil
    if _webhook_config.get("webhook_id"):
        trello.delete_webhook(_webhook_config["webhook_id"])

    # Webhook oluştur (sadece public URL varsa)
    webhook = None
    if is_local:
        print("ℹ️ Lokal ortam tespit edildi — Trello webhook kaydı atlanıyor")
        print("   Handler kuruldu → /api/trello/webhook/push ile manuel test edilebilir")
        print("   💡 Gerçek webhook için: ngrok http 5000 → callback_url olarak gönderin")
    else:
        webhook = trello.create_webhook(
            callback_url=callback_url,
            id_model=board_id,
            description=f"Orchestrator V3 Webhook - Board {board_id}"
        )
        if not webhook:
            print("⚠️ Trello webhook oluşturulamadı — callback URL erişilebilir olmalı")

    # WebhookHandler'ı kur
    _webhook_handler = WebhookHandler(trello, board_id, list_ids)

    # Orchestrator callback'ini bağla
    try:
        from trello_orchestrator_v3 import process_backlog_card_v3
        _webhook_handler.set_backlog_callback(process_backlog_card_v3)
    except ImportError:
        print("⚠️ trello_orchestrator_v3 import edilemedi, callback ayarlanmadı")

    # Config güncelle
    _webhook_config.update({
        "board_id": board_id,
        "webhook_id": webhook["id"] if webhook else None,
        "callback_url": callback_url,
        "active": True,
        "list_ids": list_ids,
        "mode": "local_push" if is_local else ("webhook" if webhook else "fallback")
    })

    # Yanıt mesajı
    if webhook:
        note = "✅ Trello Webhook aktif! Backlog'a kart eklediğinizde otomatik işlenecek."
    elif is_local:
        note = (
            "ℹ️ Lokal mod: Handler kuruldu. "
            "POST /api/trello/webhook/push ile test edin. "
            "Gerçek webhook için ngrok ile public URL sağlayın."
        )
    else:
        note = "⚠️ Handler kuruldu ama Trello webhook oluşturulamadı. Callback URL'i kontrol edin."

    return jsonify({
        "success": True,
        "webhook_id": webhook["id"] if webhook else None,
        "board_id": board_id,
        "callback_url": callback_url,
        "mode": _webhook_config["mode"],
        "lists": list_ids,
        "note": note
    }), 201


@app.route('/api/trello/webhook/remove', methods=['DELETE'])
def api_trello_webhook_remove():
    """Aktif webhook'u kaldırır"""
    global _webhook_handler, _webhook_config

    if not _webhook_config.get("active"):
        return jsonify({"error": "Aktif webhook yok"}), 404

    # Trello'dan sil
    webhook_id = _webhook_config.get("webhook_id")
    if webhook_id:
        from trello_helper import TrelloHelper
        trello = TrelloHelper(
            os.environ.get("TRELLO_API_KEY", ""),
            os.environ.get("TRELLO_TOKEN", "")
        )
        trello.delete_webhook(webhook_id)

    _webhook_handler = None
    _webhook_config.update({
        "board_id": None,
        "webhook_id": None,
        "callback_url": None,
        "active": False
    })

    return jsonify({"success": True, "message": "Webhook kaldırıldı"})


@app.route('/api/trello/webhook/stats', methods=['GET'])
def api_trello_webhook_stats():
    """Webhook istatistiklerini döndürür"""
    if not _webhook_handler:
        return jsonify({
            "active": False,
            "config": _webhook_config
        })

    return jsonify({
        "active": True,
        "config": _webhook_config,
        "stats": _webhook_handler.get_stats()
    })


@app.route('/api/trello/webhook/push', methods=['POST'])
def api_trello_webhook_push():
    """
    Manuel test endpoint'i — Trello webhook payload'ını simüle eder.

    Lokal geliştirmede ngrok kurmadan webhook akışını test etmek için.

    Body:
    {
        "card_id": "abc123"
    }

    Bu endpoint, verilen card_id'yi Backlog'a eklenmiş gibi işler.
    """
    global _webhook_handler

    if not _webhook_handler:
        return jsonify({"error": "Webhook handler kurulmamış. Önce /api/trello/webhook/setup çağırın."}), 400

    data = request.json or {}
    card_id = data.get("card_id")

    if not card_id:
        return jsonify({"error": "card_id gerekli"}), 400

    # Simüle edilmiş Trello webhook payload'ı
    simulated_payload = {
        "action": {
            "type": "createCard",
            "date": datetime.now().isoformat(),
            "data": {
                "card": {"id": card_id, "name": f"Manual Push - {card_id}"},
                "list": {"id": _webhook_config.get("list_ids", {}).get("Backlog", ""), "name": "Backlog"},
                "board": {"id": _webhook_config.get("board_id", "")}
            },
            "memberCreator": {"fullName": "Manual Test"}
        },
        "model": {"id": _webhook_config.get("board_id", "")}
    }

    result = _webhook_handler.process_event(simulated_payload)
    return jsonify(result)


@app.route('/api/trello/webhook/reset/<card_id>', methods=['POST'])
def api_trello_webhook_reset_card(card_id):
    """Bir kartı sıfırlar (tekrar işlenmesine izin verir)"""
    if not _webhook_handler:
        return jsonify({"error": "Webhook handler kurulmamış"}), 400

    reset = _webhook_handler.reset_card(card_id)
    return jsonify({"success": reset, "card_id": card_id})


@app.route('/api/trello/webhooks/list', methods=['GET'])
def api_trello_list_all_webhooks():
    """Trello hesabındaki TÜM aktif webhook'ları listeler"""
    from trello_helper import TrelloHelper
    trello_token = os.environ.get("TRELLO_TOKEN", "")
    trello_api_key = os.environ.get("TRELLO_API_KEY", "")

    if not trello_token or not trello_api_key:
        return jsonify({"error": "Trello credentials eksik"}), 500

    trello = TrelloHelper(trello_api_key, trello_token)
    webhooks = trello.list_webhooks()

    return jsonify({
        "count": len(webhooks) if webhooks else 0,
        "webhooks": webhooks or []
    })

# ============================================================
# AGENTIC AGILE (TRELLO ORCHESTRATOR) API
# ============================================================

import threading
import trello_orchestrator_v3

_agile_thread = None

@app.route('/api/agile/start', methods=['POST'])
def api_agile_start():
    global _agile_thread
    
    if _agile_thread and _agile_thread.is_alive():
        return jsonify({"success": False, "message": "Orchestrator şu anda çalışıyor."})
    
    from trello_helper import TrelloHelper
    trello_api_key = os.environ.get("TRELLO_API_KEY", "27cf0f02c65de97bf9f699cd79b5fc18")
    trello_token = os.environ.get("TRELLO_TOKEN", "YOUR_TRELLO_TOKEN")
    trello = TrelloHelper(trello_api_key, trello_token)
    
    boards = trello.get_boards() or []
    target_board_id = None
    
    for b in boards:
        if "Agentic Agile" in b['name']:
            target_board_id = b['id']
            break
            
    if not target_board_id:
        board_structure = trello.setup_board_structure("Agentic Agile")
        if board_structure:
            target_board_id = board_structure['board']['id']
    
    if not target_board_id:
        return jsonify({"success": False, "message": "Agentic Agile panosu bulunamadı ve oluşturulamadı."}), 500

    trello_orchestrator_v3.STOP_ORCHESTRATOR = False
    trello_orchestrator_v3.ORCHESTRATOR_LOGS.clear()
    
    def run_agile():
        try:
            trello_orchestrator_v3.run_orchestrator_v3(target_board_id, check_interval=10)
        except Exception as e:
            trello_orchestrator_v3.print(f"❌ Orchestrator Thread Hatası: {e}")

    _agile_thread = threading.Thread(target=run_agile, daemon=True)
    _agile_thread.start()
    
    return jsonify({"success": True, "message": "Agentic Agile başlatıldı.", "board_id": target_board_id})

@app.route('/api/agile/stop', methods=['POST'])
def api_agile_stop():
    global _agile_thread
    
    if not _agile_thread or not _agile_thread.is_alive():
        return jsonify({"success": False, "message": "Zaten durdurulmuş durumda."})
        
    trello_orchestrator_v3.STOP_ORCHESTRATOR = True
    return jsonify({"success": True, "message": "Durdurma sinyali gönderildi."})

@app.route('/api/agile/status', methods=['GET'])
def api_agile_status():
    is_running = _agile_thread is not None and _agile_thread.is_alive()
    return jsonify({
        "status": "running" if is_running else "stopped",
        "logs": trello_orchestrator_v3.ORCHESTRATOR_LOGS,
        "pending_approval": trello_orchestrator_v3.PENDING_APPROVAL
    })

@app.route('/api/agile/approval/approve', methods=['POST'])
def api_agile_approve():
    if not trello_orchestrator_v3.PENDING_APPROVAL:
        return jsonify({"success": False, "message": "Onay bekleyen bir işlem yok."})
    trello_orchestrator_v3.APPROVAL_RESULT = "approved"
    return jsonify({"success": True, "message": "Düzeltme onaylandı."})

@app.route('/api/agile/approval/reject', methods=['POST'])
def api_agile_reject():
    if not trello_orchestrator_v3.PENDING_APPROVAL:
        return jsonify({"success": False, "message": "Onay bekleyen bir işlem yok."})
    trello_orchestrator_v3.APPROVAL_RESULT = "rejected"
    return jsonify({"success": True, "message": "Düzeltme reddedildi."})

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Ahmet Mesut Erçıkan - AGENT MANAGER PLATFORM")
    print("=" * 60)
    print(f"📊 Dashboard: http://localhost:5000")
    print(f"📋 API Docs:  http://localhost:5000/api/domains")
    print(f"👥 Teams:     http://localhost:5000/api/teams")
    print(f"💰 Costs:     http://localhost:5000/api/costs")
    print(f"🔗 Webhook:   POST http://localhost:5000/api/trello/webhook/setup")
    print(f"📈 WH Stats:  http://localhost:5000/api/trello/webhook/stats")
    print("=" * 60)

    # Start Mail Listener
    print("📧 Starting Mail Listener Agent...", end=" ")
    try:
        mail_agent = MailListenerAgent()
        mail_agent.start()
        print("OK")
    except Exception as e:
        print(f"FAILED: {e}")

    app.run(debug=True, port=5000, use_reloader=False)

