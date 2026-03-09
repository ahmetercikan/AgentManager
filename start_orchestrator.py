"""
Trello Orchestrator V2 - Board Seçimi ile Başlatma
Input sorununu çözen wrapper
"""
import sys
import os

# Ortam değişkenleri
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

# ============================================================
# YAPILANDIRMA
# ============================================================

TRELLO_API_KEY = "27cf0f02c65de97bf9f699cd79b5fc18"
TRELLO_TOKEN = "YOUR_TRELLO_TOKEN"

# Önce Trello Helper'ı import et (diğer import'lardan önce)
from trello_helper import TrelloHelper
trello = TrelloHelper(TRELLO_API_KEY, TRELLO_TOKEN)

# ============================================================
# BOARD SEÇİMİ - Import'lardan ÖNCE
# ============================================================

print("\n" + "=" * 80)
print("🎯 TRELLO ORCHESTRATOR V2")
print("🆕 Backend & Frontend Developer Destekli")
print("=" * 80)

boards = trello.get_boards()

if not boards:
    print("❌ Board bulunamadi!")
    sys.exit(1)

print("\n📋 Mevcut Board'lariniz:")
for i, board in enumerate(boards, 1):
    print(f"{i}. {board['name']} ({board['id']})")

print(f"\n0. Yeni board olustur")

# Input'u al
try:
    # stdin'i flush et
    sys.stdin.flush()

    secim_str = input("\nHangi board'u izlemek istersiniz? (numara girin): ").strip()

    if not secim_str:
        print("❌ Bos giris!")
        sys.exit(1)

    secim = int(secim_str)

    if secim == 0:
        board_name = input("Yeni board adi: ").strip()
        if not board_name:
            print("❌ Board adi bos olamaz!")
            sys.exit(1)

        board_structure = trello.setup_board_structure(board_name)
        if board_structure:
            board_id = board_structure['board']['id']
            print(f"\n✅ Yeni board olusturuldu: {board_structure['board']['url']}")
        else:
            print("❌ Board olusturulamadi!")
            sys.exit(1)
    elif 1 <= secim <= len(boards):
        board_id = boards[secim - 1]['id']
        print(f"\n✅ Secilen board: {boards[secim - 1]['name']}")
    else:
        print("❌ Gecersiz secim!")
        sys.exit(1)

except ValueError as e:
    print(f"❌ Gecersiz giris! Sayi giriniz. Hata: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\n👋 Program sonlandirildi.")
    sys.exit(0)
except Exception as e:
    print(f"❌ Beklenmeyen hata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================
# ORCHESTRATOR'U BAŞLAT - Board ID alındıktan SONRA import et
# ============================================================

print(f"\n⏳ Orchestrator başlatılıyor...")
print("💡 Backlog listesine kart ekleyin, otomatik işlenecek!")
print("🛑 Durdurmak için Ctrl+C yapın")
print("=" * 80)

# Şimdi orchestrator'u import et ve çalıştır
from trello_orchestrator_v2 import run_orchestrator_v2

# Orchestrator'u başlat
run_orchestrator_v2(board_id)
