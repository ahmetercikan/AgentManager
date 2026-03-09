"""
Mail Gönderici — Verimlilik Analizi raporlarını SMTP ile gönderir.
HTML mail + Excel ek dosyaları destekler.
"""

import os
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "ahmetmesutercikan18@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "").replace(" ", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
MAIL_FROM = os.getenv("MAIL_FROM", "ahmetmesutercikan18@gmail.com")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Verimlilik Analizi")


def send_report_mail(
    to_emails: list,
    subject: str,
    html_body: str,
    attachments: list = None,
    cc_emails: list = None,
    bcc_emails: list = None
) -> dict:
    """
    HTML mail gönder, opsiyonel Excel ekleri ile.

    Args:
        to_emails: Alıcı mail adresleri
        subject: Mail konusu
        html_body: HTML mail içeriği
        attachments: Ek dosya yolları listesi
        cc_emails: CC adresleri
        bcc_emails: BCC adresleri

    Returns:
        {"success": True/False, "message": "...", "recipients": [...]}
    """
    try:
        # Mail oluştur
        msg = MIMEMultipart("mixed")
        msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM}>"
        msg["To"] = ", ".join(to_emails)
        msg["Subject"] = subject

        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)

        # HTML body
        html_part = MIMEText(html_body, "html", "utf-8")
        msg.attach(html_part)

        # Ek dosyalar
        if attachments:
            for filepath in attachments:
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        filename = os.path.basename(filepath)
                        part.add_header(
                            "Content-Disposition",
                            "attachment",
                            filename=filename
                        )
                        msg.attach(part)
                    print(f"  📎 Ek dosya: {filename}")
                else:
                    print(f"  ⚠️ Dosya bulunamadı: {filepath}")

        # Tüm alıcılar
        all_recipients = list(to_emails)
        if cc_emails:
            all_recipients.extend(cc_emails)
        if bcc_emails:
            all_recipients.extend(bcc_emails)

        # SMTP gönder (Gmail STARTTLS)
        if SMTP_PASS:
            # SSL context — sertifika sorunlarını atla (rejectUnauthorized: false)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                server.ehlo()
                if SMTP_USE_TLS:
                    server.starttls(context=context)
                    server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg, to_addrs=all_recipients)

            print(f"✅ Mail gönderildi: {subject} → {', '.join(to_emails)}")
            return {
                "success": True,
                "message": f"Mail başarıyla gönderildi",
                "recipients": to_emails,
                "subject": subject,
                "attachment_count": len(attachments or [])
            }
        else:
            # SMTP şifresi yoksa sadece HTML dosyasını kaydet (test modu)
            print(f"⚠️ SMTP şifresi ayarlanmamış — test modunda")
            return {
                "success": False,
                "message": "SMTP şifresi ayarlanmamış. .env dosyasına SMTP_PASS ekleyin.",
                "test_mode": True,
                "recipients": to_emails,
                "subject": subject
            }

    except Exception as e:
        print(f"❌ Mail gönderme hatası: {e}")
        return {
            "success": False,
            "message": str(e),
            "recipients": to_emails
        }


def send_gmy_reports(gmy_reports: dict, gmy_emails: dict = None) -> list:
    """
    Tüm GMY raporlarını ilgili kişilere gönder.

    Args:
        gmy_reports: generate_full_gmy_report()'un döndürdüğü rapor
        gmy_emails: {"Teknoloji GMY": ["gmy@dgpaysit.com", ...]}

    Returns:
        [{"gmy": "...", "result": {...}}]
    """
    results = []
    report_date = gmy_reports.get("date", "")

    for gmy_name, report_data in gmy_reports.get("gmy_reports", {}).items():
        to_emails = (gmy_emails or {}).get(gmy_name, [])
        if not to_emails:
            print(f"⚠️ {gmy_name}: Mail adresi tanımlanmamış, atlanıyor.")
            results.append({
                "gmy": gmy_name,
                "result": {"success": False, "message": "Mail adresi tanımlanmamış"}
            })
            continue

        subject = f"Verimlilik Analizi Raporları - {gmy_name} - {report_date}"

        result = send_report_mail(
            to_emails=to_emails,
            subject=subject,
            html_body=report_data.get("html", ""),
            attachments=report_data.get("excel_files", [])
        )
        results.append({"gmy": gmy_name, "result": result})

    return results
