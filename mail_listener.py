import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
import time
import os
import threading
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import reporting logic
try:
    from generate_combined_reports import run_batch_reports
    # from domains import BUSINESS_DOMAINS # OLD
    from berqun_report_generator import TEAM_DOMAIN_MAP # NEW
    from mail_sender import send_report_mail
except ImportError:
    # Fallback for testing isolation
    TEAM_DOMAIN_MAP = {}
    pass

# Load environment variables
load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
IMAP_SERVER = "imap.gmail.com"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MailListener")

class MailListenerAgent:
    def __init__(self, check_interval=60):
        self.check_interval = check_interval
        self.is_running = False
        self.thread = None
        self.imap = None

    def connect(self):
        try:
            self.imap = imaplib.IMAP4_SSL(IMAP_SERVER)
            self.imap.login(SMTP_USER, SMTP_PASS)
            logger.info(f"✅ Mail Listener bağlı: {SMTP_USER}")
            return True
        except Exception as e:
            logger.error(f"❌ Bağlantı hatası: {e}")
            return False

    def parse_date_request(self, text: str):
        """
        Metin içindeki tarih ifadelerini (Ocak, Şubat 2026 vb.) analiz eder.
        Varsayılan: Bir önceki ay.
        Returns: (month_label, month_en, start_date, end_date, report_date)
        """
        import calendar
        from datetime import datetime, timedelta

        # Ay İsimleri (Lower case mapping)
        TR_MONTHS = {
            "ocak": 1, "şubat": 2, "subat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "mayis": 5,
            "haziran": 6, "temmuz": 7, "ağustos": 8, "agustos": 8, "eylül": 9, "eylul": 9,
            "ekim": 10, "kasım": 11, "kasim": 11, "aralık": 12, "aralik": 12
        }

        text = text.lower()
        now = datetime.now()
        target_year = now.year
        target_month = None

        # 1. Yıl Tespiti (2024, 2025, 2026...)
        import re
        year_match = re.search(r'202[4-9]', text)
        if year_match:
            target_year = int(year_match.group(0))

        # 2. Ay Tespiti
        for m_name, m_num in TR_MONTHS.items():
            if m_name in text:
                target_month = m_num
                break
        
        # 3. "Geçen Ay" / "Bu Ay" kontrolü
        if target_month is None:
            if "geçen ay" in text or "gecen ay" in text:
                # Bir önceki ay
                if now.month == 1:
                    target_month = 12
                    target_year = now.year - 1
                else:
                    target_month = now.month - 1
            elif "bu ay" in text:
                target_month = now.month
            else:
                # Hiçbir şey bulunamazsa varsayılan: Bir önceki ay (Raporlar genelde biten ay için alınır)
                if now.month == 1:
                    target_month = 12
                    target_year = now.year - 1
                else:
                    target_month = now.month - 1

        # Tarih Hesaplamaları
        # Start Date: YYYY-MM-01
        start_date = datetime(target_year, target_month, 1)
        
        # End Date: Ayın son günü
        _, last_day = calendar.monthrange(target_year, target_month)
        end_date = datetime(target_year, target_month, last_day)

        # Label'lar
        # Ay ismini bul (Ters map veya listeden)
        # TR_MONTHS keys are lower, lets make a proper list
        TR_MONTHS_LIST = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                          "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        
        month_name = TR_MONTHS_LIST[target_month]
        month_label = f"{month_name} {target_year}"
        month_en = f"{month_name}_{target_year}" # Dosya adı için
        
        # Report Date (Genelde ayın 1'i verilir API için)
        report_date_str = start_date.strftime("%Y-%m-%d")
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        logger.info(f"📅 Tarih Algılandı: {month_label} ({start_date_str} - {end_date_str})")
        return month_label, month_en, start_date_str, end_date_str, report_date_str

    def analyze_with_llm(self, subject: str, body: str):
        """
        Cloudflare Workers AI kullanarak e-posta analizi yapar.
        Skill dosyasını (skills/email_analyst.md) prompt olarak kullanır.
        """
        try:
            import requests
            import json
            from datetime import datetime

            account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
            api_token = os.getenv("CLOUDFLARE_API_TOKEN")
            model_id = os.getenv("CLOUDFLARE_MODEL_ID", "@cf/openai/gpt-oss-120b")

            if not account_id or not api_token:
                logger.warning("⚠️ Cloudflare credentials bulunamadı. Regex kullanılıyor.")
                return None

            # Input text hazırlama
            input_text = f"Subject: {subject}\n\nBody: {body}"

            # Skill Prompt'u Oku ve Hazırla
            skill_path = os.path.join(os.path.dirname(__file__), "skills", "email_analyst.md")
            if not os.path.exists(skill_path):
                logger.warning(f"⚠️ Skill dosyası bulunamadı: {skill_path}")
                return None
                
            with open(skill_path, "r", encoding="utf-8") as f:
                system_prompt_template = f.read()

            # Context Variables
            current_date = datetime.now().strftime("%Y-%m-%d")
            domain_list = "\n".join([f"- {d}" for d in set(TEAM_DOMAIN_MAP.values())])
            
            system_prompt = system_prompt_template.replace("{CURRENT_DATE}", current_date) \
                                                  .replace("{DOMAIN_LIST}", domain_list)

            # Cloudflare API Call
            url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model_id}"
            
            body_payload = {
                "input": f"System: {system_prompt}\n\nUser: {input_text}\n\nAssistant:",
                "max_tokens": 4096,
            }

            logger.info(f"🤖 Cloudflare LLM Analizi Yapılıyor ({model_id})...")
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=body_payload,
                timeout=30
            )

            if response.status_code != 200:
                logger.error(f"❌ Cloudflare API Hatası ({response.status_code}): {response.text}")
                return None

            api_response = response.json()
            
            # Extract result using robust logic from user snippet
            result = api_response.get("result", api_response)
            response_text = ""
            
            if isinstance(result, dict):
                if "output" in result and isinstance(result["output"], list):
                    # Handle complex structure: output: [{ type: "message", content: [{ text: "..." }] }]
                    for item in result["output"]:
                        if item.get("type") == "message":
                            content_list = item.get("content", [])
                            if content_list and len(content_list) > 0:
                                response_text = content_list[0].get("text", "")
                                break
                
                if not response_text:
                    response_text = result.get("response", "")
            
            if not response_text and isinstance(result, str):
                response_text = result

            if not response_text:
                logger.warning(f"⚠️ AI'dan geçersiz cevap formatı geldi: {api_response}")
                return None

            # JSON temizleme (Markdown bloklarını temizle)
            clean_json = response_text.strip()
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
            data = json.loads(clean_json)
            
            logger.info(f"🤖 LLM Sonuç: {json.dumps(data, ensure_ascii=False)}")
            
            # Veri Formatlama
            intent = data.get("intent", "OTHER")
            if intent != "REPORT":
                return None
            
            domains = data.get("domains")
            if domains and (isinstance(domains, str) or "ALL" in domains):
                domains = None # All
                
            date_info = data.get("date_range", {})
            month_label = date_info.get("month_label", "")
            month_en = date_info.get("month_en", "")
            start_date = date_info.get("start_date", "")
            end_date = date_info.get("end_date", "")
            report_date = start_date
            
            return domains, month_label, month_en, start_date, end_date, report_date

        except Exception as e:
            logger.error(f"❌ LLM Analiz Hatası (Cloudflare): {e}")
            return None

    def parse_domain_request(self, subject: str, body: str) -> list:
        """
        Konu ve içerikten hangi domainlerin istendiğini analiz eder.
        TEAM_DOMAIN_MAP kullanarak doğru eşleştirmeyi yapar.
        """
        text = (subject + " " + body).lower()
        selected_domains = set()

        # 1. Target Domain Isimlerini Kontrol Et (Values)
        target_domains = set(TEAM_DOMAIN_MAP.values())
        for domain in target_domains:
            # "Temel Bankacılık" -> "temel bankacılık"
            if domain.lower() in text:
                selected_domains.add(domain)
                logger.info(f"🔍 Domain (Target) tespit edildi: {domain}")

        # 2. Kaynak Team Isimlerini Kontrol Et (Keys)
        # Örn: "Android POS" -> "Payment Facilitator..."
        for team_key, target_domain in TEAM_DOMAIN_MAP.items():
            if team_key.lower() in text:
                selected_domains.add(target_domain)
                logger.info(f"🔍 Domain (Key: {team_key}) tespit edildi: {target_domain}")

        return list(selected_domains)

    def send_receipt_email(self, to_email: str, domains: list, month_label: str = ""):
        """Kullanıcıya 'Talebiniz alındı' maili atar."""
        try:
            domain_list_str = ", ".join(domains) if domains else "TÜM DOMAINLER"
            subject = "✅ Rapor Talebiniz Alındı"
            body = f"""
            <h3>Merhaba,</h3>
            <p>Berqun verimlilik raporu talebiniz işleme alınmıştır.</p>
            <p><strong>Kapsam:</strong> {domain_list_str}</p>
            <p><strong>Dönem:</strong> {month_label}</p>
            <p>Raporlar hazırlandığında bu adrese e-posta ile gönderilecektir.</p>
            <p><i>Bu mesaj otomatiktir.</i></p>
            """
            
            result = send_report_mail(
                to_emails=[to_email],
                subject=subject,
                html_body=body
            )
            
            if result.get("success"):
                logger.info(f"📤 Alındı maili gönderildi: {to_email}")
            else:
                logger.error(f"❌ Alındı maili gönderilemedi: {to_email} | Sebep: {result.get('message')}")
        except Exception as e:
            logger.error(f"❌ Alındı maili hatası: {e}")

    def process_email(self, msg_id):
        try:
            _, msg_data = self.imap.fetch(msg_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject_raw = msg["Subject"]
                    if subject_raw:
                        subject, encoding = decode_header(subject_raw)[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding or "utf-8")
                    else:
                        subject = "(No Subject)"
                    
                    sender = msg.get("From")
                    name, sender_email = parseaddr(sender)
                    logger.info(f"📨 Gönderici: {name} <{sender_email}>")

                    # --- Robust Body Extraction ---
                    body = ""
                    if msg.is_multipart():
                        parts = []
                        # 1. Önce text/plain parçalarını topla
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                try:
                                    payload = part.get_payload(decode=True)
                                    charset = part.get_content_charset() or "utf-8"
                                    parts.append(payload.decode(charset, errors="ignore"))
                                except Exception as e:
                                    logger.warning(f"⚠️ Body decode (plain) hatası: {e}")
                        
                        # 2. Eğer text/plain yoksa text/html'e bak
                        if not parts:
                            for part in msg.walk():
                                if part.get_content_type() == "text/html":
                                    try:
                                        import re
                                        html_payload = part.get_payload(decode=True)
                                        charset = part.get_content_charset() or "utf-8"
                                        html_text = html_payload.decode(charset, errors="ignore")
                                        # Basit tag temizleme
                                        cleaned = re.sub(r'<[^>]+>', ' ', html_text)
                                        parts.append(cleaned)
                                    except Exception as e:
                                        logger.warning(f"⚠️ Body decode (html) hatası: {e}")
                                        
                        body = "\n".join(parts).strip()
                    else:
                        try:
                            payload = msg.get_payload(decode=True)
                            charset = msg.get_content_charset() or "utf-8"
                            body = payload.decode(charset, errors="ignore").strip()
                        except Exception as e:
                            logger.warning(f"⚠️ Body decode (non-multipart) hatası: {e}")

                    logger.info(f"📨 Yeni E-posta Konu: {subject}")
                    logger.info(f"📝 E-posta İçeriği (İlk 150 Karakter): {body[:150].replace('\n', ' ')}...")

                    # 1. Kendi kendimize attığımız mailleri yoksay (Loop Koruması)
                    if SMTP_USER in sender_email:
                        logger.info("🛑 Kendi gönderdiğimiz mail, işlem yapılmıyor.")
                        return

                    # Filtreleme
                    if "rapor" in subject.lower() or "berqun" in subject.lower() or "verimlilik" in subject.lower():
                        logger.info("✅ Talep algılandı. Analiz ediliyor...")
                        
                        # 0. Analiz (LLM Öncelikli)
                        llm_result = self.analyze_with_llm(subject, body)
                        
                        domains_to_run = None
                        month_label = ""
                        month_en = ""
                        start_date = ""
                        end_date = ""
                        report_date = ""

                        if llm_result:
                            domains_to_run, month_label, month_en, start_date, end_date, report_date = llm_result
                            logger.info("✨ LLM Analizi Başarılı!")
                        else:
                            # 1. Regex Fallback
                            logger.info("⚠️ LLM Analizi Atlandı -> Regex Fallback Kullanılıyor.")
                            
                            # Domain Analizi
                            domains_to_run = self.parse_domain_request(subject, body)
                            
                            if not domains_to_run:
                                if "tüm" in (subject + body).lower() or "hepsi" in (subject + body).lower():
                                    domains_to_run = None # All
                                    logger.info("🌐 'Tüm' anahtar kelimesi -> Bütün domainler.")
                                else:
                                    logger.warning("⚠️ Spesifik domain bulunamadı. Güvenlik için işlem yapılmıyor veya varsayılan atanıyor.")
                                    domains_to_run = None 
                            
                            # Tarih Analizi
                            month_label, month_en, start_date, end_date, report_date = self.parse_date_request(subject + " " + body)

                        # Yanıt Gönder
                        self.send_receipt_email(sender_email, domains_to_run, month_label)
                        
                        # Raporu Başlat
                        logger.info(f"🚀 Raporlama başlatılıyor... Hedefler: {domains_to_run if domains_to_run else 'TÜMÜ'} | Dönem: {month_label}")
                        
                        def trigger_job():
                            try:
                                run_batch_reports(
                                    selected_domains=domains_to_run, 
                                    log_callback=logger.info,
                                    recipient_email=sender_email,
                                    report_month=month_label,
                                    month_en=month_en,
                                    start_date=start_date,
                                    end_date=end_date,
                                    report_date=report_date
                                )
                            except Exception as e:
                                logger.error(f"❌ Raporlama hatası: {e}")

                        threading.Thread(target=trigger_job).start()

                    else:
                        logger.info("ℹ️ İlgisiz e-posta.")

        except Exception as e:
            logger.error(f"❌ Mail işleme hatası: {e}")

    def loop(self):
        logger.info("👀 Mail Dinleyici Başladı (Her 20sn)...")
        while self.is_running:
            try:
                if self.imap is None:
                    if not self.connect():
                        time.sleep(20)
                        continue
                
                # Sadece OKUNMAMIŞ (UNSEEN) mailleri al
                self.imap.select("INBOX")
                status, messages = self.imap.search(None, "UNSEEN")
                
                if status == "OK":
                    msg_ids = messages[0].split()
                    # Optimize: Sadece son 5 maili kontrol et (Kullanıcı talebi)
                    if len(msg_ids) > 5:
                        msg_ids = msg_ids[-5:]
                        
                    for msg_id in msg_ids:
                        self.process_email(msg_id)
                
            except Exception as e:
                logger.error(f"⚠️ Döngü hatası (Yeniden bağlanılıyor): {e}")
                self.imap = None # Reconnect next loop

            time.sleep(self.check_interval)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.is_running = False
        if self.imap:
            try:
                self.imap.logout()
            except:
                pass


# Test için doğrudan çalıştırma
if __name__ == "__main__":
    agent = MailListenerAgent(check_interval=10)
    agent.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()
