"""
Product Assistant - Decision & Product Brain

Yazilim ve yapay zeka odakli urun fikirleri uzerinde dusunen,
karar ureten ve isi dogru sekilde tasklara bolen bir asistan.

AMAC:
- Fikirleri sorgulamak
- Alternatifleri tartismak
- Riskleri erken gostermek
- Net karar opsiyonlari sunmak
- Seçilen karar dogrultusunda execution agent'larina verilebilecek net tasklar onermek

ONEMLI: Kod yazmaz. Test yazmaz. Jira'ya issue acmaz.
Sadece dusunur, yapilandirir ve onerir.
"""
import os
import signal
import sys
import io

# Windows encoding fix
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Windows signal duzeltmesi - crewai kutuphanesi icin gerekli
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

import warnings
warnings.filterwarnings('ignore')

from crewai import Agent, Task, Crew, Process, LLM

# ============================================================
# YAPILANDIRMA
# ============================================================

# OpenAI API Key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# LLM Modeli - Dusunme ve analiz icin daha guclu model
my_llm = LLM(
    model="gpt-4o",  # Daha guclu model, daha iyi analiz icin
    api_key=OPENAI_API_KEY
)

# ============================================================
# PRODUCT ASSISTANT AGENT DEFINITIONI
# ============================================================

def create_product_assistant():
    """
    Decision & Product Brain - Hiçbir kod yazmayan, sadece düşünen asistan
    """
    return Agent(
        role='Product & Decision Brain',
        goal='Yazilim ve AI projelerini analiz edip dogru kararlarin alinmasini saglamak',
        backstory="""
        Sen bir yazilim ve yapay zeka urun yoneticisisin. Kod yazmaz, test yazmazsin.
        Tek gorevun dogru kararlarin alinmasini saglamak ve isi dogru tasklara bolmektir.

        # CALISMA PRENSIPLERI (ZORUNLU)

        1. HEMEN COZUM URETME:
           - Once problemi netlestir
           - Belirsizlik varsa acikca belirt
           - Kullaniciya soru sor

        2. ALTERNATIFSIZ ILERLEME YOK:
           - En az 2 cozum yolu uret
           - Tercih edilen yolu gerekcelendir
           - Reddedilenleri neden reddettigini acikla

        3. AI ELESTIRISI ZORUNLU:
           - "AI sart mi?" sorusunu her zaman sor
           - Gereksiz AI kullanimini ozellikle belirt
           - Basit cozumler varsa onlari oner

        4. MVP DISIPLINI:
           - Mutlaka out-of-scope tanimi yap
           - "Sonra bakariz" dedigin her seyi listele
           - Minimum gereksinimi belirle

        5. EXECUTION'A GECME:
           - Task onerir, ama hicbir agent'i otomatik tetiklemezsin
           - Kod yazmaz, test yazmaz, Jira'ya issue acmazsin
           - Sadece dusunur ve onerir, karar kullaniciya aittir

        # ICSEL ROL DAGILIMI

        Her fikirde su rolleri zihinsel olarak calistir (kullaniciya soyleme):

        1. Product Thinker:
           - Problem nedir?
           - Kim icin?
           - Neden onemli?
           - Basari metrigi ne?

        2. Solution Architect:
           - Cozum yollari neler?
           - Teknik yaklasim farklari
           - Basitlik vs guc dengesi

        3. Risk & Reality Checker:
           - Nerede patlar?
           - Hangi varsayimlar kritik?
           - Zaman / veri / bakim riskleri

        4. Task Decomposer:
           - Epic / Feature / Task ayrimi
           - Acceptance criteria
           - Test edilebilirlik

        5. Vision Agent:
           - 6-12 ay sonrasi
           - Genisleme ihtimalleri
           - Bugunden verilmesi gereken kararlar

        # CIKTI FORMATI

        Her analiz asagidaki yapiyi takip etmelidir:

        ## 1. PROBLEM NETLESTIRME
        - Problem tam olarak nedir?
        - Belirsizlikler hangileri?
        - Kullaniciya sorulacak sorular

        ## 2. ALTERNATIF COZUMLER (En az 2)
        - Cozum A: [Aciklama, Artilari, Eksileri]
        - Cozum B: [Aciklama, Artilari, Eksileri]
        - ONERI: [Hangi cozum ve neden?]

        ## 3. AI GEREKLILIGI
        - AI gerekli mi? Neden?
        - Basit cozum var mi?
        - AI'siz yapilabilir mi?

        ## 4. MVP TANIMI
        - Minimum gereksinimler
        - OUT-OF-SCOPE: [Simdilik yapilmayacaklar]
        - SONRA: [Gelecekte eklenebilecekler]

        ## 5. RISKLER
        - Teknik riskler
        - Zaman riskleri
        - Veri/Bakim riskleri

        ## 6. TASK ONERILERI (Execution'a hazir)
        - Epic: [Buyuk resim]
        - Feature 1: [Task detayi, Acceptance Criteria]
        - Feature 2: [Task detayi, Acceptance Criteria]

        ## 7. VIZYON (6-12 Ay)
        - Olasi genislemeler
        - Simdi verilmesi gereken kararlar
        """,
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )


# ============================================================
# INTERAKTIF SOHBET FONKSIYONLARI
# ============================================================

def analyze_idea(idea: str) -> str:
    """
    Bir urun fikri veya ozellik talebini analiz eder

    Args:
        idea: Kullanicinin fikri/talebi

    Returns:
        Detayli analiz raporu
    """
    print("\n" + "=" * 80)
    print("🧠 PRODUCT ASSISTANT - Fikir Analiz Ediliyor...")
    print("=" * 80)

    assistant = create_product_assistant()

    analysis_task = Task(
        description=f"""
        Asagidaki urun fikri/ozellik talebini analiz et:

        FIKIR/TALEP:
        {idea}

        CIKTI FORMATINI TAKIP ET (backstory'de belirtilen):
        1. Problem Netlestirme
        2. Alternatif Cozumler (en az 2)
        3. AI Gerekliligi
        4. MVP Tanimi
        5. Riskler
        6. Task Onerileri
        7. Vizyon (6-12 ay)

        ONEMLI:
        - Kod yazma, sadece analiz et
        - En az 2 alternatif sun
        - AI'nin gerekli olup olmadigini sorgula
        - MVP'yi net tanimla
        - Out-of-scope'u acikca belirt
        """,
        agent=assistant,
        expected_output="Yapilandirilmis analiz raporu (7 bolum)"
    )

    crew = Crew(
        agents=[assistant],
        tasks=[analysis_task],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()

    print("\n" + "=" * 80)
    print("✅ ANALİZ TAMAMLANDI")
    print("=" * 80)

    return str(result)


def continue_discussion(previous_context: str, user_response: str) -> str:
    """
    Kullanici yaniti ile sohbeti devam ettirir

    Args:
        previous_context: Onceki sohbet baglami
        user_response: Kullanicinin yaniti

    Returns:
        Asistanin yaniti
    """
    print("\n" + "=" * 80)
    print("🧠 PRODUCT ASSISTANT - Sohbet Devam Ediyor...")
    print("=" * 80)

    assistant = create_product_assistant()

    discussion_task = Task(
        description=f"""
        ONCEKI BAGLAM:
        {previous_context}

        KULLANICI YANITI:
        {user_response}

        Kullanicinin yanitini degerlendir ve:
        - Belirsizlikleri netlestir
        - Yeni sorular sor (gerekirse)
        - Guncel oneriyi guncelle
        - Karar alinabiliyorsa, net task onerileri sun

        ONEMLI:
        - Kod yazma
        - Kullanicinin karari netlesene kadar ilerleme
        - Her zaman en az 2 alternatif sun (yeni karar gerekiyorsa)
        """,
        agent=assistant,
        expected_output="Kullanicinin yanitina gore guncel analiz/oneri"
    )

    crew = Crew(
        agents=[assistant],
        tasks=[discussion_task],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()

    print("\n" + "=" * 80)
    print("✅ YANIT HAZIRLANDI")
    print("=" * 80)

    return str(result)


def finalize_tasks(full_context: str) -> str:
    """
    Son karari alip execution-ready tasklar uretir

    Args:
        full_context: Tum sohbet baglami

    Returns:
        Execution-ready task listesi
    """
    print("\n" + "=" * 80)
    print("🧠 PRODUCT ASSISTANT - Task Listesi Hazirlaniyor...")
    print("=" * 80)

    assistant = create_product_assistant()

    task_creation = Task(
        description=f"""
        TUM SOHBET BAGLAMI:
        {full_context}

        Alinan kararlar dogrultusunda, execution agent'lari icin HAZIR TASKLARI olustur.

        FORMAT:

        # PROJE BILGILERI
        - Proje Adi: [...]
        - Programlama Dili: [...]
        - Aciklama: [...]

        # EPIC
        [Epic tanimi]

        # FEATURES & TASKS

        ## Feature 1: [Adi]
        - Task 1.1: [Detay]
          - Acceptance Criteria:
            - [ ] Kriter 1
            - [ ] Kriter 2

        ## Feature 2: [Adi]
        - Task 2.1: [Detay]
          - Acceptance Criteria:
            - [ ] Kriter 1

        # OUT-OF-SCOPE
        - [Simdilik yapilmayacak sey 1]
        - [Simdilik yapilmayacak sey 2]

        # TEKNIK GEREKSINIMLER
        - [Gereksinim 1]
        - [Gereksinim 2]

        ONEMLI:
        - Her task execution-ready olmali
        - Acceptance criteria test edilebilir olmali
        - Kod yazma, sadece task tanimi yap
        """,
        agent=assistant,
        expected_output="Execution-ready task listesi"
    )

    crew = Crew(
        agents=[assistant],
        tasks=[task_creation],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()

    print("\n" + "=" * 80)
    print("✅ TASKLAR HAZIRLANDI")
    print("=" * 80)

    return str(result)


# ============================================================
# INTERAKTIF CLI
# ============================================================

def interactive_session():
    """
    Kullanici ile interaktif sohbet oturumu
    """
    print("\n" + "=" * 80)
    print("🧠 PRODUCT ASSISTANT - Decision & Product Brain")
    print("=" * 80)
    print("Yapay zeka ve yazilim projeleri icin karar destek asistani")
    print("Kod yazmaz, sadece dusunur ve onerir!")
    print("-" * 80)
    print("Komutlar:")
    print("  - 'yeni': Yeni fikir analizi baslatir")
    print("  - 'tasklar': Mevcut sohbetten execution-ready tasklar uretir")
    print("  - 'cikis': Programi kapatir")
    print("=" * 80)

    conversation_history = []

    while True:
        print("\n" + "-" * 80)
        user_input = input("\n📝 Sen: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['cikis', 'exit', 'quit', 'q']:
            print("\n👋 Gule gule!")
            break

        if user_input.lower() in ['yeni', 'new']:
            # Yeni analiz baslat
            conversation_history = []
            print("\n💡 Yeni fikir/ozellik talebini yaz:")
            idea = input("📝 Fikir: ").strip()

            if idea:
                result = analyze_idea(idea)
                conversation_history.append({
                    'role': 'user',
                    'content': f"Fikir: {idea}"
                })
                conversation_history.append({
                    'role': 'assistant',
                    'content': result
                })

                print(f"\n🤖 Asistan:\n{result}")
            continue

        if user_input.lower() in ['tasklar', 'tasks']:
            # Task listesi uret
            if not conversation_history:
                print("\n❌ Once bir fikir analizi yapmaniz gerekiyor! 'yeni' yazin.")
                continue

            full_context = "\n\n".join([
                f"{item['role'].upper()}: {item['content']}"
                for item in conversation_history
            ])

            tasks = finalize_tasks(full_context)

            print(f"\n🎯 EXECUTION-READY TASKLAR:\n{tasks}")

            # Tasklari dosyaya kaydet
            filename = "product_assistant_tasks.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("PRODUCT ASSISTANT - EXECUTION-READY TASKS\n")
                f.write("=" * 80 + "\n\n")
                f.write(tasks)

            print(f"\n💾 Tasklar kaydedildi: {filename}")
            continue

        # Normal sohbet devam
        if not conversation_history:
            print("\n❌ Once bir fikir analizi yapmaniz gerekiyor! 'yeni' yazin.")
            continue

        # Onceki baglami hazirla
        previous_context = "\n\n".join([
            f"{item['role'].upper()}: {item['content']}"
            for item in conversation_history
        ])

        # Sohbeti devam ettir
        result = continue_discussion(previous_context, user_input)

        conversation_history.append({
            'role': 'user',
            'content': user_input
        })
        conversation_history.append({
            'role': 'assistant',
            'content': result
        })

        print(f"\n🤖 Asistan:\n{result}")


# ============================================================
# ANA FONKSIYON
# ============================================================

def main():
    """
    Product Assistant'i baslat
    """
    interactive_session()


if __name__ == "__main__":
    main()
