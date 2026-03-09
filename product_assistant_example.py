"""
Product Assistant - Örnek Kullanım Senaryoları

Bu dosya Product Assistant'ın nasıl kullanılacağını gösterir.
"""

from product_assistant import analyze_idea, continue_discussion, finalize_tasks

# ============================================================
# ÖRNEK 1: BASİT FİKİR ANALİZİ
# ============================================================

def example_1_simple_idea():
    """
    Örnek 1: Basit bir fikir analizi
    """
    print("\n" + "=" * 80)
    print("ÖRNEK 1: BASİT FİKİR ANALİZİ")
    print("=" * 80)

    idea = """
    Öğrencilerin aylık harcamalarını takip edebileceği bir mobil uygulama.
    Kategorilere göre harcamaları gruplamak ve aylık bütçe hedefi belirlemek istiyorum.
    """

    result = analyze_idea(idea)
    print(f"\n📊 ANALİZ SONUCU:\n{result}")


# ============================================================
# ÖRNEK 2: KAPSAMLI SOHBET SİMÜLASYONU
# ============================================================

def example_2_full_conversation():
    """
    Örnek 2: Tam bir sohbet simülasyonu (programatik)
    """
    print("\n" + "=" * 80)
    print("ÖRNEK 2: KAPSAMLI SOHBET SİMÜLASYONU")
    print("=" * 80)

    # 1. İlk fikir analizi
    idea = """
    Şirket içi çalışanlar için bir AI chatbot.
    HR politikaları, izin süreçleri ve şirket bilgilerini yanıtlayabilsin.
    """

    print("\n📝 İLK FİKİR:")
    print(idea)

    analysis = analyze_idea(idea)

    conversation_history = [
        {'role': 'user', 'content': f"Fikir: {idea}"},
        {'role': 'assistant', 'content': analysis}
    ]

    print(f"\n🤖 İLK ANALİZ:\n{analysis[:500]}...\n")

    # 2. Kullanıcı yanıtı (simüle edilmiş)
    user_response_1 = """
    Hedef kitle tüm çalışanlar (500+ kişi).
    AI olarak GPT-4 kullanmayı düşünüyorum.
    Web tabanlı olsun, mobil uygulamaya gerek yok.
    """

    print("\n📝 KULLANICI YANITI 1:")
    print(user_response_1)

    previous_context = "\n\n".join([
        f"{item['role'].upper()}: {item['content']}"
        for item in conversation_history
    ])

    response_1 = continue_discussion(previous_context, user_response_1)

    conversation_history.append({'role': 'user', 'content': user_response_1})
    conversation_history.append({'role': 'assistant', 'content': response_1})

    print(f"\n🤖 ASİSTAN YANITI 1:\n{response_1[:500]}...\n")

    # 3. Kullanıcı yanıtı 2 (simüle edilmiş)
    user_response_2 = """
    Haklısın, ilk aşamada basit bir FAQ botu ile başlayalım.
    Sonra ihtiyaca göre AI ekleriz.
    Hangi teknolojileri önerirsin?
    """

    print("\n📝 KULLANICI YANITI 2:")
    print(user_response_2)

    previous_context = "\n\n".join([
        f"{item['role'].upper()}: {item['content']}"
        for item in conversation_history
    ])

    response_2 = continue_discussion(previous_context, user_response_2)

    conversation_history.append({'role': 'user', 'content': user_response_2})
    conversation_history.append({'role': 'assistant', 'content': response_2})

    print(f"\n🤖 ASİSTAN YANITI 2:\n{response_2[:500]}...\n")

    # 4. Final task oluşturma
    print("\n📝 KULLANICI: Tamam, taskları oluşturalım")

    full_context = "\n\n".join([
        f"{item['role'].upper()}: {item['content']}"
        for item in conversation_history
    ])

    tasks = finalize_tasks(full_context)

    print(f"\n🎯 OLUŞTURULAN TASKLAR:\n{tasks}")

    # Dosyaya kaydet
    with open("product_assistant_example_tasks.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PRODUCT ASSISTANT - ÖRNEK SOHBET TASKLARI\n")
        f.write("=" * 80 + "\n\n")
        f.write(tasks)

    print("\n💾 Tasklar kaydedildi: product_assistant_example_tasks.txt")


# ============================================================
# ÖRNEK 3: FİKİRLER LİSTESİ (TOPLU ANALİZ)
# ============================================================

def example_3_batch_analysis():
    """
    Örnek 3: Birden fazla fikri toplu analiz et
    """
    print("\n" + "=" * 80)
    print("ÖRNEK 3: TOPLU FİKİR ANALİZİ")
    print("=" * 80)

    ideas = [
        {
            'name': 'E-ticaret Platformu',
            'description': 'Küçük işletmeler için basit e-ticaret sitesi'
        },
        {
            'name': 'Inventory Takip Sistemi',
            'description': 'Restoran mutfağı için malzeme takip sistemi'
        },
        {
            'name': 'Toplantı Asistanı',
            'description': 'Zoom/Teams toplantılarını kaydedip özetleyen AI'
        }
    ]

    results = []

    for idx, idea in enumerate(ideas, 1):
        print(f"\n{'=' * 80}")
        print(f"FİKİR {idx}/{len(ideas)}: {idea['name']}")
        print(f"{'=' * 80}")

        idea_text = f"{idea['name']}\n\n{idea['description']}"

        result = analyze_idea(idea_text)
        results.append({
            'idea': idea['name'],
            'analysis': result
        })

        print(f"\n✅ {idea['name']} analizi tamamlandı!")

    # Tüm sonuçları kaydet
    with open("product_assistant_batch_analysis.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PRODUCT ASSISTANT - TOPLU FİKİR ANALİZİ\n")
        f.write("=" * 80 + "\n\n")

        for idx, result in enumerate(results, 1):
            f.write(f"\n{'#' * 80}\n")
            f.write(f"FİKİR {idx}: {result['idea']}\n")
            f.write(f"{'#' * 80}\n\n")
            f.write(result['analysis'])
            f.write("\n\n")

    print(f"\n💾 Tüm analizler kaydedildi: product_assistant_batch_analysis.txt")


# ============================================================
# ÖRNEK 4: AI GEREKLİLİĞİ SORGULAMA
# ============================================================

def example_4_ai_critique():
    """
    Örnek 4: AI'nin gereksiz kullanıldığı bir senaryo
    """
    print("\n" + "=" * 80)
    print("ÖRNEK 4: AI GEREKLİLİĞİ SORGULAMA")
    print("=" * 80)

    idea = """
    Çalışanların doğum günlerini hatırlatan ve e-posta gönderen bir sistem.
    AI kullanarak her çalışan için özel doğum günü mesajları oluşturmak istiyorum.
    GPT-4 ile her mesajı kişiselleştireceğim.
    """

    print("\n📝 FİKİR (AI over-engineering örneği):")
    print(idea)

    result = analyze_idea(idea)

    print(f"\n🤖 ASİSTAN ANALİZİ:")
    print(result)

    # Asistan muhtemelen şöyle bir şey söyleyecek:
    # "AI gerekli mi? Hayır! Basit bir template sistemi yeterli."


# ============================================================
# ANA PROGRAM
# ============================================================

def main():
    """
    Örnek seçim menüsü
    """
    print("\n" + "=" * 80)
    print("🧠 PRODUCT ASSISTANT - ÖRNEK KULLANIM SENARYOLARI")
    print("=" * 80)
    print("1. Basit fikir analizi")
    print("2. Kapsamlı sohbet simülasyonu (programatik)")
    print("3. Toplu fikir analizi (batch)")
    print("4. AI gerekliliği sorgulama (AI over-engineering)")
    print("0. Tümünü çalıştır")
    print("=" * 80)

    try:
        choice = input("\n📝 Seçim (0-4): ").strip()

        if choice == "1":
            example_1_simple_idea()
        elif choice == "2":
            example_2_full_conversation()
        elif choice == "3":
            example_3_batch_analysis()
        elif choice == "4":
            example_4_ai_critique()
        elif choice == "0":
            print("\n🚀 Tüm örnekler çalıştırılıyor...\n")
            example_1_simple_idea()
            example_2_full_conversation()
            example_3_batch_analysis()
            example_4_ai_critique()
            print("\n✅ Tüm örnekler tamamlandı!")
        else:
            print("❌ Geçersiz seçim!")

    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı.")


if __name__ == "__main__":
    main()
