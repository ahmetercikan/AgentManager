# whatsapp_approval_agent.py
"""
WhatsApp Approval Agent - Trello taskları için onay mekanizması

Bu agent:
1. Backlog'dan yeni task geldiğinde analiz yapar
2. Task detaylarını WhatsApp'tan gönderir
3. Kullanıcıdan onay bekler (✅ Onayla / ❌ Reddet / 📝 Düzenle)
4. Onay alındıktan sonra Orchestrator'a devredilir

Desteklenen WhatsApp Entegrasyonları:
- Twilio API (Ücretli, en güvenilir)
- WhatsApp Business API (Resmi, kurulum karmaşık)
- pywhatkit (Ücretsiz, WhatsApp Web bazlı)
"""

import os
import sys
import signal
import json
import time
from typing import Dict, Optional, List
from datetime import datetime

# Windows signal duzeltmesi (CrewAI icin gerekli)
if sys.platform.startswith('win'):
    def handler(signum, frame):
        pass

    missing_signals = [
        'SIGHUP', 'SIGQUIT', 'SIGTSTP', 'SIGCONT',
        'SIGUSR1', 'SIGUSR2', 'SIGALRM'
    ]

    for sig_name in missing_signals:
        if not hasattr(signal, sig_name):
            setattr(signal, sig_name, signal.SIGTERM if hasattr(signal, 'SIGTERM') else 1)

from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

# WhatsApp entegrasyonu için Twilio kullanıyoruz
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio kurulu degil. 'pip install twilio' calistirin")

load_dotenv()

# Konfigürasyon
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "")  # Format: whatsapp:+14155238886
USER_WHATSAPP_NUMBER = os.getenv("USER_WHATSAPP_NUMBER", "")  # Format: whatsapp:+905551234567

# LLM ayarları
my_llm = LLM(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY
)

# ============================================================================
# WHATSAPP SERVICE
# ============================================================================

class WhatsAppService:
    """WhatsApp mesajlaşma servisi (Twilio API)"""

    def __init__(self):
        if not TWILIO_AVAILABLE:
            raise ImportError("Twilio kurulu degil!")

        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, USER_WHATSAPP_NUMBER]):
            raise ValueError("Twilio credentials eksik! .env dosyasini kontrol edin.")

        self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        self.from_number = TWILIO_WHATSAPP_FROM
        self.to_number = USER_WHATSAPP_NUMBER
        self.pending_approvals: Dict[str, Dict] = {}  # card_id -> approval data

    def send_approval_request(self, card_id: str, task_summary: Dict) -> bool:
        """Task onay isteğini WhatsApp'tan gönder"""
        message = self._format_approval_message(task_summary)

        try:
            msg = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=self.to_number
            )

            # Onay bekleyen taskları kaydet
            self.pending_approvals[card_id] = {
                "task_summary": task_summary,
                "message_sid": msg.sid,
                "sent_at": datetime.now().isoformat(),
                "status": "pending"
            }

            print(f"✅ WhatsApp mesaji gonderildi! (SID: {msg.sid})")
            return True

        except Exception as e:
            print(f"❌ WhatsApp mesaji gonderilemedi: {e}")
            return False

    def _format_approval_message(self, task_summary: Dict) -> str:
        """Onay mesajını formatlama"""
        msg = f"""
🤖 *YENİ TASK ONAYI GEREKİYOR*
━━━━━━━━━━━━━━━━━━━━━━

📋 *Task:* {task_summary.get('task_name', 'N/A')}

📊 *Proje Tipi:* {task_summary.get('project_type', 'N/A')}

💡 *Özet:*
{task_summary.get('summary', 'N/A')}

🔧 *Teknik Detaylar:*
• Dil: {task_summary.get('programming_language', 'N/A')}
• Framework: {task_summary.get('framework', 'N/A')}
• Dosya: {task_summary.get('file_name', 'N/A')}

⚙️ *Gereksinimler:*
{self._format_requirements(task_summary.get('requirements', []))}

⏱️ *Tahmini Süre:* {task_summary.get('estimated_time', 'Bilinmiyor')}

💰 *Maliyet:* ~{task_summary.get('estimated_cost', '0.10')} USD

━━━━━━━━━━━━━━━━━━━━━━

*CEVAP SEÇENEKLERİ:*
✅ ONAYLA - Task'ı başlat
❌ REDDET - Task'ı iptal et
📝 DÜZENLE - Değişiklik iste

Lütfen yanıt olarak şunlardan birini gönderin:
• "ONAYLA" veya "OK" veya "✅"
• "REDDET" veya "HAYIR" veya "❌"
• "DÜZENLE: [açıklama]" veya "📝 [açıklama]"

Task ID: {task_summary.get('card_id', 'N/A')}
"""
        return msg.strip()

    def _format_requirements(self, requirements: List[str]) -> str:
        """Gereksinimleri listele"""
        if not requirements:
            return "  • Belirtilmemiş"
        return "\n".join([f"  • {req}" for req in requirements[:5]])

    def check_approval_status(self, card_id: str, timeout: int = 300) -> Optional[str]:
        """
        Kullanıcının onayını bekle (polling yöntemi)

        Returns:
            "approved" | "rejected" | "edit" | None (timeout)
        """
        print(f"\n⏳ WhatsApp onayı bekleniyor... (Timeout: {timeout}s)")
        print(f"📱 Lütfen WhatsApp'tan yanıt verin!")

        start_time = time.time()

        while (time.time() - start_time) < timeout:
            # Gelen mesajları kontrol et
            response = self._check_incoming_messages()

            if response:
                decision = self._parse_user_decision(response)
                if decision:
                    self.pending_approvals[card_id]["status"] = decision
                    self.pending_approvals[card_id]["response"] = response
                    self.pending_approvals[card_id]["responded_at"] = datetime.now().isoformat()
                    return decision

            # Her 5 saniyede bir kontrol et
            time.sleep(5)
            print(".", end="", flush=True)

        print("\n⏰ Timeout! Onay alınamadı.")
        return None

    def _check_incoming_messages(self) -> Optional[str]:
        """Son gelen mesajları kontrol et"""
        try:
            # Son 1 dakikada gelen mesajları al
            messages = self.client.messages.list(
                to=self.from_number,
                from_=self.to_number,
                limit=5
            )

            if messages:
                # En son mesajı al
                latest = messages[0]

                # Mesaj yeni mi? (son 1 dakika içinde)
                msg_time = latest.date_created
                if (datetime.now(msg_time.tzinfo) - msg_time).seconds < 60:
                    return latest.body.strip()

            return None

        except Exception as e:
            print(f"⚠️  Mesaj kontrolu hatasi: {e}")
            return None

    def _parse_user_decision(self, message: str) -> Optional[str]:
        """Kullanıcı kararını parse et (Regex ile tam kelime eşleşmesi)"""
        import re
        msg_lower = message.lower().strip()

        # Regex ile tam kelime kontrolü yapan yardımcı fonksiyon
        def check_keywords(text, keywords):
            for keyword in keywords:
                # \bkelime\b şeklinde regex oluştur (emoji değilse)
                if any(char in keyword for char in ["✅", "❌", "❓", "📝"]):
                    if keyword in text:
                        return True
                else: 
                    # Kelime sınırlarını kontrol et
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, text):
                        return True
            return False

        # Onay
        approve_keywords = ["onayla", "ok", "evet", "yes", "✅", "tamam", "y"]
        if check_keywords(msg_lower, approve_keywords):
            return "approved"

        # Ret
        reject_keywords = ["reddet", "hayir", "no", "❌", "iptal", "n"]
        if check_keywords(msg_lower, reject_keywords):
            return "rejected"

        # Düzenleme
        edit_keywords = ["düzenle", "edit", "📝", "değiştir"]
        if check_keywords(msg_lower, edit_keywords):
            return "edit"

        # Bilgi İsteği (Soru)
        info_keywords = ["soru", "question", "❓", "nedir", "nasıl", "hangi", "kaç", "ne", "kim"]
        if check_keywords(msg_lower, info_keywords):
            return "info"
            
        # Eğer soru işareti varsa direk info kabul et
        if "?" in msg_lower:
            return "info"

        return None

    def send_status_update(self, message: str) -> bool:
        """Durum güncellemesi gönder"""
        try:
            self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=self.to_number
            )
            return True
        except Exception as e:
            print(f"⚠️  Durum mesaji gonderilemedi: {e}")
            return False


# ============================================================================
# APPROVAL AGENT
# ============================================================================

def create_approval_agent():
    """Onay agent'i oluştur - Task'ları detaylı analiz eder"""
    return Agent(
        role='Task Approval Specialist',
        goal='Gelen tasklari detayli analiz edip onay icin hazirlamak',
        backstory="""
        Sen bir Task Approval Specialist'sin. Gorevlerin:

        1. TASK ANALİZİ:
           - Task'in ne istedigini net bir sekilde acikla
           - Teknik gereksinimleri listele
           - Proje tipini belirle (fullstack, backend, frontend, cli)

        2. TAHMİN:
           - Tahmini tamamlanma suresini hesapla
           - Tahmini kod satir sayisini ver
           - Tahmini maliyeti hesapla (API kullanimi)

        3. RİSK ANALİZİ:
           - Potansiyel zorlukları belirt
           - Eksik bilgileri tespit et
           - Oneriler sun

        4. ÖZET ÇIKARIM:
           - Kullaniciya gonderilecek ozet mesaji haziirla
           - Teknik detaylari acik ve anlasilir sekilde yaz

        ÇIKTI FORMATI (JSON):
        {
            "task_name": "Gorev adi",
            "card_id": "Trello card ID",
            "project_type": "fullstack|backend|frontend|cli",
            "summary": "Gorev ozeti (2-3 cumle)",
            "programming_language": "Python|JavaScript|Go|...",
            "framework": "Django|React|FastAPI|...",
            "file_name": "dosya_adi.py",
            "requirements": ["Gereksinim 1", "Gereksinim 2", ...],
            "estimated_time": "15-30 dakika",
            "estimated_lines": "~200 satir",
            "estimated_cost": "0.15 USD",
            "risks": ["Risk 1", "Risk 2"],
            "recommendations": ["Oneri 1", "Oneri 2"],
            "missing_info": ["Eksik bilgi 1", ...]
        }

        DİKKAT: Her zaman JSON formatinda cikti ver!
        """,
        verbose=False,
        llm=my_llm,
        allow_delegation=False
    )


def analyze_task_for_approval(card_data: Dict) -> Dict:
    """
    Trello card'ini analiz edip onay için hazırla

    Args:
        card_data: Trello card bilgileri (name, desc, id)

    Returns:
        Task analiz özeti
    """
    print("\n🔍 Task analizi yapiliyor...")

    approval_agent = create_approval_agent()

    analysis_task = Task(
        description=f"""
        Asagidaki Trello task'ini detayli analiz et ve onay icin hazirla:

        **Task Adi:** {card_data.get('name', 'Belirsiz')}
        **Aciklama:** {card_data.get('desc', 'Aciklama yok')}
        **Card ID:** {card_data.get('id', 'N/A')}

        Gorev: Bu task'i detayli analiz et, teknik gereksinimleri cikart,
        tahmini sure ve maliyet hesapla, riskleri belirle.

        MUTLAKA JSON formatinda cikti ver (yukardaki CIKTI FORMATI'na uygun).
        """,
        agent=approval_agent,
        expected_output="JSON formatinda detayli task analizi"
    )

    crew = Crew(
        agents=[approval_agent],
        tasks=[analysis_task],
        verbose=False
    )

    result = crew.kickoff()

    # JSON parse et
    try:
        # Agent'in ciktisini JSON'a cevirmeye calis
        result_str = str(result)

        # JSON kismini bul (```json ... ``` formatinda olabilir)
        if "```json" in result_str:
            json_start = result_str.find("```json") + 7
            json_end = result_str.find("```", json_start)
            json_str = result_str[json_start:json_end].strip()
        elif "{" in result_str and "}" in result_str:
            json_start = result_str.find("{")
            json_end = result_str.rfind("}") + 1
            json_str = result_str[json_start:json_end]
        else:
            raise ValueError("JSON bulunamadi")

        task_summary = json.loads(json_str)

        # Card ID'yi ekle (eksikse)
        task_summary["card_id"] = card_data.get("id", "N/A")
        task_summary["task_name"] = task_summary.get("task_name", card_data.get("name", "Belirsiz"))

        return task_summary

    except Exception as e:
        print(f"⚠️  JSON parse hatasi: {e}")

        # Fallback: Basit bir ozet dondur
        return {
            "task_name": card_data.get("name", "Belirsiz"),
            "card_id": card_data.get("id", "N/A"),
            "project_type": "cli",
            "summary": card_data.get("desc", "Aciklama yok")[:200],
            "programming_language": "Python",
            "framework": "N/A",
            "file_name": "output.py",
            "requirements": ["Belirsiz"],
            "estimated_time": "Bilinmiyor",
            "estimated_lines": "~100 satir",
            "estimated_cost": "0.10 USD",
            "risks": ["Detayli analiz yapilamadi"],
            "recommendations": ["Manuel kontrol gerekli"],
            "missing_info": []
        }


# ============================================================================
# APPROVAL WORKFLOW
# ============================================================================

def request_approval_via_whatsapp(card_data: Dict, timeout: int = 300) -> tuple[bool, Optional[Dict]]:
    """
    WhatsApp üzerinden onay iste

    Args:
        card_data: Trello card bilgileri
        timeout: Onay bekleme süresi (saniye)

    Returns:
        (approved: bool, task_summary: Dict)
    """
    print("\n" + "="*60)
    print("📱 WHATSAPP ONAY SÜRECİ BAŞLIYOR")
    print("="*60)

    # 1. Task'i analiz et
    task_summary = analyze_task_for_approval(card_data)
    print(f"\n✅ Task analizi tamamlandi: {task_summary['task_name']}")

    # 2. WhatsApp servisi baslat
    try:
        whatsapp = WhatsAppService()
    except Exception as e:
        print(f"\n❌ WhatsApp servisi baslatılamadi: {e}")
        print("⚠️  UYARI: WhatsApp onay olmadan devam edilecek (auto-approve)")
        return True, task_summary  # Auto-approve (geliştirme ortamı için)

    # 3. Onay isteği gönder
    card_id = card_data.get("id", "unknown")
    sent = whatsapp.send_approval_request(card_id, task_summary)

    if not sent:
        print("❌ WhatsApp mesaji gonderilemedi!")
        return False, task_summary

    # 4. Onay bekle
    decision = whatsapp.check_approval_status(card_id, timeout)

    # 5. Karari isle
    if decision == "approved":
        print("\n✅ TASK ONAYLANDI! Orchestrator'a gonderiliyor...")
        whatsapp.send_status_update(f"✅ Task onaylandi: {task_summary['task_name']}\n\n🤖 Agentlar calismaya basladi!")
        return True, task_summary

    elif decision == "rejected":
        print("\n❌ TASK REDDEDİLDİ!")
        whatsapp.send_status_update(f"❌ Task reddedildi: {task_summary['task_name']}")
        return False, task_summary

    elif decision == "edit":
        print("\n📝 DEĞİŞİKLİK İSTENDİ!")
        whatsapp.send_status_update(f"📝 Task düzenleme modu aktif: {task_summary['task_name']}\n\nLütfen Trello card'ini güncelleyin.")
        return False, task_summary

    elif decision == "info":
        print("\n❓ KULLANICI SORU SORDU!")
        user_question = whatsapp.pending_approvals[card_id].get("response", "").replace("SORU:", "").replace("soru:", "").strip()
        
        # LLM ile soruyu cevapla
        info_agent = Agent(
            role='Technical Consultant',
            goal='Kullanıcının teknik sorularını yanıtlamak',
            backstory="Sen teknik bir danışmansın. Kullanıcının task hakkındaki sorularını net bir şekilde yanıtlarsın.",
            verbose=False,
            llm=my_llm
        )
        
        answer_task = Task(
            description=f"""
            Kullanıcı şu task ile ilgili bir soru sordu:
            
            TASK ÖZETİ: {json.dumps(task_summary)}
            
            SORU: {user_question}
            
            GÖREV: Soruyu kısa ve net bir şekilde yanıtla (Türkçe).
            """,
            agent=info_agent,
            expected_output="Kısa ve net cevap"
        )
        
        crew = Crew(agents=[info_agent], tasks=[answer_task], verbose=False)
        answer = crew.kickoff()
        
        # Cevabı gönder ve tekrar onay iste
        whatsapp.send_status_update(f"🤖 **CEVAP:**\n{answer}\n\nLütfen tekrar ONAYLA veya REDDET yazın.")
        
        # Recursive call (tekrar onay bekle)
        return request_approval_via_whatsapp(card_data, timeout)

    else:
        print("\n⏰ TIMEOUT! Onay alınamadı.")
        whatsapp.send_status_update(f"⏰ Timeout: {task_summary['task_name']}\n\nTask otomatik olarak iptal edildi.")
        return False, task_summary


# ============================================================================
# TEST
# ============================================================================

def test_approval_agent():
    """Test: Approval agent'i test et"""
    print("\n" + "="*60)
    print("🧪 APPROVAL AGENT TEST")
    print("="*60)

    # Örnek Trello card
    test_card = {
        "id": "test123",
        "name": "E-ticaret sitesi için ürün filtreleme sistemi",
        "desc": """
        Bir e-ticaret sitesi için gelişmiş ürün filtreleme sistemi geliştir.

        Gereksinimler:
        - Kategoriye göre filtreleme
        - Fiyat aralığı filtreleme
        - Marka filtreleme
        - Stok durumu filtreleme
        - API endpoint'leri (REST)
        - Frontend için React komponenti

        Veritabanı: PostgreSQL
        """
    }

    # Analiz yap
    task_summary = analyze_task_for_approval(test_card)

    print("\n📊 TASK ANALİZ SONUCU:")
    print("-" * 60)
    print(json.dumps(task_summary, indent=2, ensure_ascii=False))

    print("\n" + "="*60)
    print("✅ Test tamamlandi!")
    print("="*60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_approval_agent()
    else:
        print("""
╔════════════════════════════════════════════════════════════╗
║         WHATSAPP APPROVAL AGENT - KULLANIM                 ║
╚════════════════════════════════════════════════════════════╝

Bu modul trello_orchestrator.py icinde kullanilir.

MANUEL TEST:
  python whatsapp_approval_agent.py --test

KURULUM:
  1. Twilio hesabı aç: https://www.twilio.com
  2. WhatsApp Sandbox aktif et
  3. .env dosyasına credentials ekle:
     TWILIO_ACCOUNT_SID=ACxxxxxxx
     TWILIO_AUTH_TOKEN=xxxxxxx
     TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
     USER_WHATSAPP_NUMBER=whatsapp:+905551234567

ALTERNATIF (Ucretsiz):
  - pywhatkit (WhatsApp Web bazli, kullanici onayı gerekli)
  - selenium + WhatsApp Web (otomasyon)

NOT: Production'da webhook kullanmak daha iyi (polling yerine)
        """)
