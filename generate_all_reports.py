"""
TÜM DOMAIN'LER İÇİN AYRI AYRI RAPOR OLUŞTUR VE MAİL AT
Ocak 2026 — 11 Domain → 11 ayrı mail
"""
import json, time, os, sys
from berqun_client import get_berqun_client, PERIOD_MONTH
from berqun_report_generator import (
    group_staff_by_gmy, generate_team_summary_html, generate_mail_html,
    generate_team_excel, _safe_get, _to_float
)
from mail_sender import send_report_mail

REPORT_DATE = "2026-01-15"
REPORT_MONTH = "Ocak 2026"
SEND_TO = "ahmetmesutercikan18@gmail.com"
OUTPUT_DIR = "generated_reports"

def main():
    print("=" * 70)
    print(f"  TÜM DOMAIN'LER İÇİN RAPOR OLUŞTURMA — {REPORT_MONTH}")
    print("=" * 70)

    client = get_berqun_client()
    staff_list = client.get_staff_list()
    groups = group_staff_by_gmy(staff_list)

    total_domains = len(groups)
    total_staff = sum(g["total_staff"] for g in groups.values())
    print(f"\n📊 {total_staff} personel, {total_domains} domain\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results = []

    for domain_idx, (domain_name, domain_data) in enumerate(
        sorted(groups.items(), key=lambda x: -x[1]["total_staff"]), 1
    ):
        staff_count = domain_data["total_staff"]
        team_count = len(domain_data["teams"])
        print(f"\n{'='*70}")
        print(f"  [{domain_idx}/{total_domains}] {domain_name}")
        print(f"  {staff_count} personel, {team_count} takım")
        print(f"{'='*70}")

        # Her takım için dashboard verilerini çek
        enriched_teams = {}
        bq_below_100 = []
        staff_done = 0

        for team_name, team_staff in domain_data["teams"].items():
            enriched = []
            for staff in team_staff:
                guid = staff.get("guid")
                name = staff.get("full_name", "?")
                staff_done += 1

                if guid:
                    try:
                        print(f"  [{staff_done}/{staff_count}] {name}...", end=" ", flush=True)
                        dashboard = client.get_user_dashboard(guid, REPORT_DATE, PERIOD_MONTH)
                        staff_copy = dict(staff)
                        staff_copy["dashboard"] = dashboard
                        bq = _to_float(_safe_get(dashboard, "user_bq_point_avg"))
                        staff_copy["bq_score"] = bq
                        print(f"BQ={bq}")

                        if bq is not None and bq < 100:
                            bq_below_100.append({
                                "name": name,
                                "team_name": team_name,
                                "bq_score": bq,
                                "email": staff.get("email", "")
                            })
                        enriched.append(staff_copy)
                    except Exception as e:
                        print(f"HATA: {e}")
                        enriched.append(staff)
                else:
                    enriched.append(staff)
                time.sleep(0.2)

            enriched_teams[team_name] = enriched

        # HTML rapor
        html = generate_mail_html(
            gmy_name=domain_name,
            report_date=REPORT_MONTH,
            teams_data=enriched_teams,
            bq_below_100=bq_below_100,
            vpn_missing=[]
        )

        # Excel raporlar
        excel_files = []
        for team_name, team_staff in enriched_teams.items():
            if team_staff:
                excel = generate_team_excel(team_name, team_staff, REPORT_MONTH, OUTPUT_DIR)
                if excel:
                    excel_files.append(excel)

        # Mail gönder
        subject = f"Verimlilik Analizi — {domain_name} — {REPORT_MONTH}"
        print(f"\n  📧 Mail gönderiliyor: {subject}")
        result = send_report_mail(
            to_emails=[SEND_TO],
            subject=subject,
            html_body=html,
            attachments=excel_files
        )

        status = "✅" if result.get("success") else "❌"
        print(f"  {status} {result.get('message', 'Bilinmeyen hata')}")
        results.append({
            "domain": domain_name,
            "staff": staff_count,
            "bq_below_100": len(bq_below_100),
            "excel_count": len(excel_files),
            "mail_sent": result.get("success", False)
        })

        # HTML dosya kaydet
        safe_name = domain_name.replace(" ", "_").replace("/", "-").replace("&", "ve")
        html_path = os.path.join(OUTPUT_DIR, f"{safe_name}_{REPORT_MONTH.replace(' ','_')}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

    # Özet
    print("\n" + "=" * 70)
    print("  ÖZET")
    print("=" * 70)
    for r in results:
        status = "✅" if r["mail_sent"] else "❌"
        print(f"  {status} {r['domain']}: {r['staff']} kişi, "
              f"BQ<100: {r['bq_below_100']}, {r['excel_count']} Excel")
    
    sent = sum(1 for r in results if r["mail_sent"])
    print(f"\n  📨 {sent}/{len(results)} mail gönderildi")
    print("=" * 70)

if __name__ == "__main__":
    main()
