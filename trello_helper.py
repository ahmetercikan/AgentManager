"""
Trello REST API Helper

Trello API kullanarak kart oluşturma, taşıma, yorum ekleme işlemlerini yapar.
"""
import requests
from typing import Dict, List, Optional
import json


class TrelloHelper:
    """
    Trello REST API ile çalışmak için helper sınıfı

    Attributes:
        api_key: Trello API Key
        token: Trello Token
        board_id: Board ID (opsiyonel)
    """

    def __init__(self, api_key: str, token: str, board_id: Optional[str] = None):
        """
        TrelloHelper başlatıcı

        Args:
            api_key: Trello API Key
            token: Trello Token
            board_id: Board ID (opsiyonel)
        """
        self.api_key = api_key
        self.token = token
        self.board_id = board_id
        self.base_url = "https://api.trello.com/1"

    def _get_auth_params(self) -> Dict:
        """Auth parametrelerini döndürür"""
        return {
            "key": self.api_key,
            "token": self.token
        }

    # ============================================================
    # BOARD İŞLEMLERİ
    # ============================================================

    def get_boards(self, member: str = "me") -> Optional[List[Dict]]:
        """
        Kullanıcının board'larını getirir

        Args:
            member: Member ID veya "me"

        Returns:
            Board listesi veya None
        """
        url = f"{self.base_url}/members/{member}/boards"
        params = self._get_auth_params()

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Board'lar getirilemedi: {e}")
            return None

    def get_board(self, board_id: Optional[str] = None) -> Optional[Dict]:
        """
        Board bilgilerini getirir

        Args:
            board_id: Board ID (verilmezse self.board_id kullanılır)

        Returns:
            Board bilgileri veya None
        """
        board_id = board_id or self.board_id
        if not board_id:
            print("❌ Board ID belirtilmedi!")
            return None

        url = f"{self.base_url}/boards/{board_id}"
        params = self._get_auth_params()

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Board bilgileri alınamadı: {e}")
            return None

    def create_board(self, name: str) -> Optional[Dict]:
        """
        Yeni board oluşturur

        Args:
            name: Board adı

        Returns:
            Board bilgileri veya None
        """
        url = f"{self.base_url}/boards"
        params = self._get_auth_params()
        params["name"] = name

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            board = response.json()
            self.board_id = board['id']
            print(f"✅ Board oluşturuldu: {board['name']} ({board['id']})")
            return board
        except Exception as e:
            print(f"❌ Board oluşturulamadı: {e}")
            return None

    # ============================================================
    # LIST İŞLEMLERİ
    # ============================================================

    def get_lists(self, board_id: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Board'daki listeleri getirir

        Args:
            board_id: Board ID

        Returns:
            Liste listesi veya None
        """
        board_id = board_id or self.board_id
        if not board_id:
            print("❌ Board ID belirtilmedi!")
            return None

        url = f"{self.base_url}/boards/{board_id}/lists"
        params = self._get_auth_params()

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Listeler getirilemedi: {e}")
            return None

    def create_list(self, name: str, board_id: Optional[str] = None) -> Optional[Dict]:
        """
        Board'da yeni liste oluşturur

        Args:
            name: Liste adı
            board_id: Board ID

        Returns:
            Liste bilgileri veya None
        """
        board_id = board_id or self.board_id
        if not board_id:
            print("❌ Board ID belirtilmedi!")
            return None

        url = f"{self.base_url}/lists"
        params = self._get_auth_params()
        params["name"] = name
        params["idBoard"] = board_id

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            list_data = response.json()
            print(f"✅ Liste oluşturuldu: {list_data['name']} ({list_data['id']})")
            return list_data
        except Exception as e:
            print(f"❌ Liste oluşturulamadı: {e}")
            return None

    def get_list_by_name(self, list_name: str, board_id: Optional[str] = None) -> Optional[Dict]:
        """
        İsme göre liste bulur

        Args:
            list_name: Liste adı
            board_id: Board ID

        Returns:
            Liste bilgileri veya None
        """
        lists = self.get_lists(board_id)
        if not lists:
            return None

        for lst in lists:
            if lst['name'] == list_name:
                return lst

        return None

    # ============================================================
    # CARD İŞLEMLERİ
    # ============================================================

    def create_card(self,
                    name: str,
                    description: str = "",
                    list_id: Optional[str] = None,
                    list_name: Optional[str] = None,
                    labels: Optional[List[str]] = None,
                    due_date: Optional[str] = None) -> Optional[Dict]:
        """
        Yeni kart oluşturur

        Args:
            name: Kart başlığı
            description: Kart açıklaması
            list_id: Liste ID (veya list_name kullan)
            list_name: Liste adı (veya list_id kullan)
            labels: Label renkleri (örn: ["red", "blue"])
            due_date: Bitiş tarihi (ISO 8601 format)

        Returns:
            Kart bilgileri veya None
        """
        # Liste ID'yi bul
        if not list_id and list_name:
            lst = self.get_list_by_name(list_name)
            if lst:
                list_id = lst['id']
            else:
                print(f"❌ '{list_name}' listesi bulunamadı!")
                return None

        if not list_id:
            print("❌ Liste ID veya adı belirtilmedi!")
            return None

        url = f"{self.base_url}/cards"
        params = self._get_auth_params()
        params["name"] = name
        params["desc"] = description
        params["idList"] = list_id

        if due_date:
            params["due"] = due_date

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            card = response.json()

            # Label ekle
            if labels:
                for color in labels:
                    self.add_label_to_card(card['id'], color)

            print(f"✅ Kart oluşturuldu: {card['name']} ({card['shortUrl']})")
            return card
        except Exception as e:
            print(f"❌ Kart oluşturulamadı: {e}")
            return None

    def get_card(self, card_id: str) -> Optional[Dict]:
        """
        Kart bilgilerini getirir

        Args:
            card_id: Kart ID

        Returns:
            Kart bilgileri veya None
        """
        url = f"{self.base_url}/cards/{card_id}"
        params = self._get_auth_params()

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Kart bilgileri alınamadı: {e}")
            return None

    def update_card(self, card_id: str, **kwargs) -> Optional[Dict]:
        """
        Kartı günceller

        Args:
            card_id: Kart ID
            **kwargs: Güncellenecek alanlar (name, desc, idList, due, vb.)

        Returns:
            Güncellenmiş kart bilgileri veya None
        """
        url = f"{self.base_url}/cards/{card_id}"
        params = self._get_auth_params()
        params.update(kwargs)

        try:
            response = requests.put(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Kart güncellenemedi: {e}")
            return None

    def move_card(self, card_id: str, list_id: Optional[str] = None, list_name: Optional[str] = None) -> Optional[Dict]:
        """
        Kartı başka bir listeye taşır

        Args:
            card_id: Kart ID
            list_id: Hedef liste ID (veya list_name kullan)
            list_name: Hedef liste adı

        Returns:
            Güncellenmiş kart bilgileri veya None
        """
        # Liste ID'yi bul
        if not list_id and list_name:
            lst = self.get_list_by_name(list_name)
            if lst:
                list_id = lst['id']
            else:
                print(f"❌ '{list_name}' listesi bulunamadı!")
                return None

        if not list_id:
            print("❌ Liste ID veya adı belirtilmedi!")
            return None

        return self.update_card(card_id, idList=list_id)

    def add_comment(self, card_id: str, comment: str) -> Optional[Dict]:
        """
        Karta yorum ekler

        Args:
            card_id: Kart ID
            comment: Yorum metni

        Returns:
            Yorum bilgileri veya None
        """
        url = f"{self.base_url}/cards/{card_id}/actions/comments"
        params = self._get_auth_params()
        params["text"] = comment

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            print(f"✅ Yorum eklendi: {card_id}")
            return response.json()
        except Exception as e:
            print(f"❌ Yorum eklenemedi: {e}")
            return None

    def add_label_to_card(self, card_id: str, color: str) -> bool:
        """
        Karta label ekler

        Args:
            card_id: Kart ID
            color: Label rengi (red, yellow, green, blue, purple, orange, black, sky, pink, lime)

        Returns:
            Başarılı ise True
        """
        url = f"{self.base_url}/cards/{card_id}/labels"
        params = self._get_auth_params()
        params["color"] = color

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            print(f"✅ Label eklendi: {color}")
            return True
        except Exception as e:
            print(f"❌ Label eklenemedi: {e}")
            return False

    # ============================================================
    # WEBHOOK İŞLEMLERİ
    # ============================================================

    def create_webhook(self, callback_url: str, id_model: str, description: str = "Orchestrator V3 Webhook") -> Optional[Dict]:
        """
        Trello Webhook oluşturur.

        Trello, belirtilen model (board/list) üzerinde değişiklik olduğunda
        callback_url'e POST isteği gönderir.

        Args:
            callback_url: Webhook bildirimlerinin gönderileceği URL
            id_model: İzlenecek model ID (board_id veya list_id)
            description: Webhook açıklaması

        Returns:
            Webhook bilgileri veya None
        """
        url = f"{self.base_url}/webhooks"
        params = self._get_auth_params()
        params["callbackURL"] = callback_url
        params["idModel"] = id_model
        params["description"] = description
        params["active"] = "true"

        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            webhook = response.json()
            print(f"✅ Webhook oluşturuldu: {webhook['id']} → {callback_url}")
            return webhook
        except Exception as e:
            print(f"❌ Webhook oluşturulamadı: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Detay: {e.response.text}")
            return None

    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Webhook'u siler.

        Args:
            webhook_id: Silinecek webhook ID

        Returns:
            Başarılı ise True
        """
        url = f"{self.base_url}/webhooks/{webhook_id}"
        params = self._get_auth_params()

        try:
            response = requests.delete(url, params=params)
            response.raise_for_status()
            print(f"✅ Webhook silindi: {webhook_id}")
            return True
        except Exception as e:
            print(f"❌ Webhook silinemedi: {e}")
            return False

    def list_webhooks(self) -> Optional[List[Dict]]:
        """
        Aktif webhook'ları listeler.

        Returns:
            Webhook listesi veya None
        """
        url = f"{self.base_url}/tokens/{self.token}/webhooks"
        params = self._get_auth_params()

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Webhook'lar listelenemedi: {e}")
            return None

    def delete_all_webhooks(self) -> int:
        """
        Tüm aktif webhook'ları siler.

        Returns:
            Silinen webhook sayısı
        """
        webhooks = self.list_webhooks()
        if not webhooks:
            return 0

        deleted = 0
        for wh in webhooks:
            if self.delete_webhook(wh['id']):
                deleted += 1

        print(f"🗑️ {deleted}/{len(webhooks)} webhook silindi")
        return deleted

    # ============================================================
    # YARDIMCI FONKSİYONLAR
    # ============================================================

    def setup_board_structure(self, board_name: str) -> Optional[Dict]:
        """
        Standart board yapısını oluşturur:
        - Backlog
        - To Do
        - In Progress
        - Code Review
        - Testing
        - Done
        - Bugs

        Args:
            board_name: Board adı

        Returns:
            Board ve liste bilgileri
        """
        # Board oluştur
        board = self.create_board(board_name)
        if not board:
            return None

        # Mevcut listeleri sil (Welcome to Trello vb.)
        existing_lists = self.get_lists()
        if existing_lists:
            for lst in existing_lists:
                try:
                    url = f"{self.base_url}/lists/{lst['id']}/closed"
                    params = self._get_auth_params()
                    params["value"] = "true"
                    requests.put(url, params=params)
                except:
                    pass

        # Yeni listeleri oluştur
        list_names = ["Backlog", "To Do", "In Progress", "Code Review", "Testing", "Done", "Bugs"]
        lists = {}

        for name in list_names:
            lst = self.create_list(name)
            if lst:
                lists[name] = lst['id']

        return {
            "board": board,
            "lists": lists
        }

    def print_board_info(self, board_id: Optional[str] = None):
        """Board bilgilerini yazdırır"""
        board = self.get_board(board_id)
        if not board:
            return

        print("\n" + "=" * 60)
        print(f"📋 BOARD: {board['name']}")
        print(f"🔗 URL: {board['url']}")
        print("=" * 60)

        lists = self.get_lists(board_id)
        if lists:
            print("\n📝 LISTELER:")
            for lst in lists:
                print(f"   - {lst['name']} ({lst['id']})")

        print("=" * 60)
