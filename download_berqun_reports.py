"""
BERQUN EXCEL İNDİRME — Domain Bazlı Paketleme & Mail Gönderme
Her domain için:
  1. Kişilerin Berqun raporlarını Excel olarak indir
  2. Domain/Ay klasörleme yapısına kaydet
  3. ZIP olarak paketleyip mail at
"""
import os, time, zipfile
from berqun_client import get_berqun_client, PERIOD_MONTH
from berqun_report_generator import group_staff_by_gmy
from mail_sender import send_report_mail

# ─── Ayarlar ────────────────────────────────────────────
REPORT_MONTH = "Ocak 2026"
REPORT_DATE = "2026-01-01"
START_DATE = "2026-01-01"
END_DATE = "2026-01-31"
SEND_TO = "ahmetmesutercikan18@gmail.com"
BASE_DIR = "generated_reports/berqun_exports"


def main():
    print("=" * 70)
    print(f"  BERQUN EXCEL İNDİRME — {REPORT_MONTH}")
    print("=" * 70)

    client = get_berqun_client()
    staff_list = client.get_staff_list()
    groups = group_staff_by_gmy(staff_list)

    total = sum(g["total_staff"] for g in groups.values())
    print(f"\n📊 {total} personel, {len(groups)} domain\n")

    results = []
    counter = 0

    for domain_idx, (domain_name, domain_data) in enumerate(
        sorted(groups.items(), key=lambda x: -x[1]["total_staff"]), 1
    ):
        staff_count = domain_data["total_staff"]
        safe_domain = domain_name.replace(" ", "_").replace("/", "-").replace("&", "ve")
        safe_month = REPORT_MONTH.replace(" ", "_")
        domain_dir = os.path.join(BASE_DIR, safe_domain, safe_month)
        os.makedirs(domain_dir, exist_ok=True)

        print(f"\n{'='*70}")
        print(f"  [{domain_idx}/{len(groups)}] {domain_name} ({staff_count} kişi)")
        print(f"  📂 {domain_dir}")
        print(f"{'='*70}")

        downloaded = 0
        failed = 0

        for team_name, team_staff in domain_data["teams"].items():
            for staff in team_staff:
                guid = staff.get("guid")
                name = staff.get("full_name", "?")
                counter += 1

                if not guid:
                    print(f"  [{counter}/{total}] {name} — GUID yok, atlanıyor")
                    failed += 1
                    continue

                try:
                    print(f"  [{counter}/{total}] {name}...", end=" ", flush=True)

                    result = client.download_user_excel(
                        person_guid=guid,
                        person_name=name,
                        date=REPORT_DATE,
                        start_date=START_DATE,
                        end_date=END_DATE,
                        month_label=REPORT_MONTH,
                        include_nonwork_bq=True
                    )

                    if result["success"]:
                        filepath = os.path.join(domain_dir, result["filename"])
                        with open(filepath, "wb") as f:
                            f.write(result["content"])
                        print(f"✅ {result['size']//1024}KB")
                        downloaded += 1
                    else:
                        print(f"❌ {result.get('error', '?')}")
                        failed += 1

                except Exception as e:
                    print(f"❌ {e}")
                    failed += 1

                time.sleep(0.1)

        # ZIP oluştur
        zip_filename = f"{safe_domain}_{safe_month}.zip"
        zip_path = os.path.join(BASE_DIR, zip_filename)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(domain_dir):
                for file in files:
                    abs_path = os.path.join(root, file)
                    arc_name = os.path.join(safe_domain, safe_month, file)
                    zf.write(abs_path, arc_name)
        zip_size = os.path.getsize(zip_path) // 1024
        print(f"\n  📦 ZIP: {zip_filename} ({zip_size}KB, {downloaded} dosya)")

        # Mail gönder
        subject = f"Berqun Verimlilik Raporları — {domain_name} — {REPORT_MONTH}"
        html_body = f"""
        <div style="font-family:Segoe UI,sans-serif;max-width:600px;margin:auto;">
            <h2 style="color:#1e293b;">📊 {domain_name}</h2>
            <p style="color:#64748b;">Dönem: <b>{REPORT_MONTH}</b></p>
            <table style="border-collapse:collapse;width:100%;margin:16px 0;">
                <tr><td style="padding:8px;border:1px solid #e2e8f0;">Personel Sayısı</td>
                    <td style="padding:8px;border:1px solid #e2e8f0;font-weight:600;">{staff_count}</td></tr>
                <tr><td style="padding:8px;border:1px solid #e2e8f0;">İndirilen Rapor</td>
                    <td style="padding:8px;border:1px solid #e2e8f0;font-weight:600;color:#16a34a;">{downloaded}</td></tr>
                <tr><td style="padding:8px;border:1px solid #e2e8f0;">Başarısız</td>
                    <td style="padding:8px;border:1px solid #e2e8f0;font-weight:600;color:#dc2626;">{failed}</td></tr>
            </table>
            <p style="color:#94a3b8;font-size:12px;">
                NOT: Ekte {downloaded} adet kişisel verimlilik raporu bulunmaktadır.<br>
                Çalışma günü olmayan zamanlardaki verimli süre BQ puanına dahil edilmiştir.
            </p>
        </div>"""

        print(f"  📧 Mail gönderiliyor: {subject}")
        mail_result = send_report_mail(
            to_emails=[SEND_TO],
            subject=subject,
            html_body=html_body,
            attachments=[zip_path]
        )
        status = "✅" if mail_result.get("success") else "❌"
        print(f"  {status} {mail_result.get('message', '?')}")

        results.append({
            "domain": domain_name,
            "staff": staff_count,
            "downloaded": downloaded,
            "failed": failed,
            "zip_kb": zip_size,
            "mail": mail_result.get("success", False)
        })

    # Özet
    print("\n" + "=" * 70)
    print("  ÖZET")
    print("=" * 70)
    total_dl = 0
    total_fail = 0
    for r in results:
        s = "✅" if r["mail"] else "❌"
        print(f"  {s} {r['domain']}: {r['downloaded']}/{r['staff']} indirildi, "
              f"ZIP={r['zip_kb']}KB")
        total_dl += r["downloaded"]
        total_fail += r["failed"]

    sent = sum(1 for r in results if r["mail"])
    print(f"\n  📥 {total_dl} rapor indirildi, {total_fail} başarısız")
    print(f"  📨 {sent}/{len(results)} mail gönderildi")
    print("=" * 70)


if __name__ == "__main__":
    main()
