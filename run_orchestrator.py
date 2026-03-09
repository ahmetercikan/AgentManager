"""
Trello Orchestrator V2 - Direkt Board ID ile Çalıştırma
Input almak yerine direkt board ID kullanır.
"""
import sys
import os

# Ortam değişkenleri
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

# trello_orchestrator_v2'den fonksiyonu import et
from trello_orchestrator_v2 import run_orchestrator_v2
from trello_helper import TrelloHelper

# ============================================================
# YAPILANDIRMA
# ============================================================

TRELLO_API_KEY = "27cf0f02c65de97bf9f699cd79b5fc18"
TRELLO_TOKEN = "YOUR_TRELLO_TOKEN"

# ============================================================
# BOARD SEÇİMİ - BURAYI DEĞİŞTİR
# ============================================================

# Kullanmak istediğin board'un ID'sini buraya yaz:
# 1. AhmetBoard: 69425606a7aa11bfd53b8c78
# 2. AI Agents - Hello World App: 693fddc09f086c4c0d49d959
# 3. Test Architecture: 663c9b8b1deb3c2b4c83ce35
# 4. TestApp: 69400eb0ff1739190f050124
# 5. TestAppManagement: 693fe6c9ed41c5b364a3e155
# 6. Tümleşik Veri Analizi: 6791fa4779998fed7f093b97
# 7. Whatsap: 69401ad6c992defcba74028d

BOARD_ID = "69400eb0ff1739190f050124"  # TestApp board'u

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🎯 TRELLO ORCHESTRATOR V2 - Direkt Başlatma")
    print("🆕 Backend & Frontend Developer Destekli")
    print("=" * 80)

    # Board bilgisini göster
    trello = TrelloHelper(TRELLO_API_KEY, TRELLO_TOKEN)
    boards = trello.get_boards()

    selected_board = None
    for board in boards:
        if board['id'] == BOARD_ID:
            selected_board = board
            break

    if selected_board:
        print(f"\n📋 Board: {selected_board['name']}")
        print(f"🔗 URL: {selected_board['url']}")
        print(f"\n⏳ Orchestrator başlatılıyor...")
        print("💡 Backlog listesine kart ekleyin, otomatik işlenecek!")
        print("🛑 Durdurmak için Ctrl+C yapın")
        print("=" * 80)

        # Orchestrator'u başlat
        run_orchestrator_v2(BOARD_ID)
    else:
        print(f"\n❌ Board bulunamadı! ID: {BOARD_ID}")
        print("\n📋 Mevcut Board'lar:")
        for board in boards:
            print(f"  - {board['name']}: {board['id']}")
