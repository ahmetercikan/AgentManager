"""
Trello Webhook Handler

Trello'dan gelen webhook event'lerini işler ve uygun aksiyonları tetikler.
Polling yerine push-based mimari sağlar.

Desteklenen Event'ler:
- createCard: Backlog'a yeni kart eklendi
- updateCard: Kart başka listeye taşındı (Backlog'a taşınma dahil)

Kullanım:
    from trello_webhook_handler import WebhookHandler

    handler = WebhookHandler(trello_helper, board_id, list_ids)
    handler.process_event(webhook_payload)
"""

import os
import sys
import json
import signal
import threading
import hashlib
import hmac
import base64
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Callable

# Logging yapılandırması
logger = logging.getLogger("webhook_handler")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    )
    logger.addHandler(console_handler)


class WebhookEvent:
    """Trello webhook event'ini temsil eder"""

    def __init__(self, payload: Dict):
        self.raw = payload
        self.action = payload.get("action", {})
        self.model = payload.get("model", {})

        # Action detayları
        self.action_type = self.action.get("type", "")
        self.action_data = self.action.get("data", {})
        self.action_date = self.action.get("date", "")

        # Kart bilgileri
        self.card = self.action_data.get("card", {})
        self.card_id = self.card.get("id", "")
        self.card_name = self.card.get("name", "")

        # Liste bilgileri
        self.list_before = self.action_data.get("listBefore", {})
        self.list_after = self.action_data.get("listAfter", {})
        self.current_list = self.action_data.get("list", {})

        # Board bilgileri
        self.board = self.action_data.get("board", {})
        self.board_id = self.board.get("id", "")

        # Kullanıcı
        member = self.action.get("memberCreator", {})
        self.member_name = member.get("fullName", "Unknown")

    @property
    def is_card_created(self) -> bool:
        return self.action_type == "createCard"

    @property
    def is_card_moved(self) -> bool:
        return self.action_type == "updateCard" and bool(self.list_after)

    @property
    def is_card_updated(self) -> bool:
        return self.action_type == "updateCard" and not self.list_after

    @property
    def target_list_name(self) -> str:
        """Kartın taşındığı liste adı"""
        if self.is_card_moved:
            return self.list_after.get("name", "")
        if self.is_card_created:
            return self.current_list.get("name", "")
        return ""

    @property
    def source_list_name(self) -> str:
        """Kartın geldiği liste adı"""
        if self.is_card_moved:
            return self.list_before.get("name", "")
        return ""

    def __repr__(self) -> str:
        if self.is_card_created:
            return f"<WebhookEvent CREATE '{self.card_name}' → {self.target_list_name}>"
        if self.is_card_moved:
            return f"<WebhookEvent MOVE '{self.card_name}' {self.source_list_name} → {self.target_list_name}>"
        return f"<WebhookEvent {self.action_type} '{self.card_name}'>"


class WebhookHandler:
    """
    Trello Webhook event'lerini işler ve orchestrator'a yönlendirir.

    İşleyiş:
    1. Trello bir event gönderir (POST /api/trello/webhook)
    2. WebhookHandler event'i parse eder
    3. Event filtrelenir (sadece Backlog'a eklenen/taşınan kartlar)
    4. Uygun callback fonksiyonu çağrılır (process_backlog_card_v3)
    5. İşlem arka planda thread ile yürütülür
    """

    def __init__(self, trello_helper, board_id: str, list_ids: Dict[str, str]):
        """
        Args:
            trello_helper: TrelloHelper instance
            board_id: İzlenen board ID
            list_ids: Liste adı → ID eşlemesi
        """
        self.trello = trello_helper
        self.board_id = board_id
        self.list_ids = list_ids

        # İşlenen kart ID'leri (tekrar işlemeyi engelle)
        self._processed_cards: set = set()
        self._processing_lock = threading.Lock()

        # Şu an işlenmekte olan kartlar
        self._active_tasks: Dict[str, threading.Thread] = {}

        # Event callback'leri
        self._on_backlog_card: Optional[Callable] = None

        # İstatistikler
        self.stats = {
            "total_events": 0,
            "backlog_events": 0,
            "ignored_events": 0,
            "processed_cards": 0,
            "errors": 0,
            "started_at": datetime.now().isoformat()
        }

        logger.info(f"WebhookHandler başlatıldı — Board: {board_id}")

    def set_backlog_callback(self, callback: Callable):
        """
        Backlog'a kart geldiğinde çağrılacak fonksiyonu ayarlar.

        Args:
            callback: fn(card: Dict, board_id: str, list_ids: Dict) -> bool
        """
        self._on_backlog_card = callback
        logger.info("Backlog callback ayarlandı")

    def process_event(self, payload: Dict) -> Dict:
        """
        Gelen webhook event'ini işler.

        Args:
            payload: Trello webhook payload (JSON)

        Returns:
            İşlem sonucu dict
        """
        self.stats["total_events"] += 1
        event = WebhookEvent(payload)

        logger.info(f"📨 Event alındı: {event}")

        # Sadece kart oluşturma ve taşıma event'lerini işle
        if not (event.is_card_created or event.is_card_moved):
            self.stats["ignored_events"] += 1
            logger.debug(f"   ⏭️ İlgisiz event tipi: {event.action_type}")
            return {"status": "ignored", "reason": f"event_type:{event.action_type}"}

        # Backlog'a mı eklendi/taşındı?
        target_list = event.target_list_name
        if target_list != "Backlog":
            self.stats["ignored_events"] += 1
            logger.debug(f"   ⏭️ Hedef liste Backlog değil: {target_list}")
            return {"status": "ignored", "reason": f"target_list:{target_list}"}

        # Daha önce işlendi mi?
        with self._processing_lock:
            if event.card_id in self._processed_cards:
                logger.info(f"   ⏭️ Kart zaten işlendi: {event.card_name}")
                return {"status": "already_processed", "card_id": event.card_id}

            # Şu an işleniyor mu?
            if event.card_id in self._active_tasks:
                logger.info(f"   ⏭️ Kart hâlâ işleniyor: {event.card_name}")
                return {"status": "in_progress", "card_id": event.card_id}

        self.stats["backlog_events"] += 1

        # Callback ayarlı mı?
        if not self._on_backlog_card:
            logger.warning("⚠️ Backlog callback ayarlanmamış!")
            return {"status": "error", "reason": "no_callback"}

        # Kart bilgilerini Trello'dan tam olarak çek
        full_card = self.trello.get_card(event.card_id)
        if not full_card:
            logger.error(f"❌ Kart bilgileri alınamadı: {event.card_id}")
            self.stats["errors"] += 1
            return {"status": "error", "reason": "card_fetch_failed"}

        # Arka planda işle
        logger.info(f"🚀 Kart işleniyor (arka plan): {event.card_name}")
        thread = threading.Thread(
            target=self._process_card_async,
            args=(full_card,),
            name=f"webhook-card-{event.card_id[:8]}",
            daemon=True
        )

        with self._processing_lock:
            self._active_tasks[event.card_id] = thread

        thread.start()

        return {
            "status": "processing",
            "card_id": event.card_id,
            "card_name": event.card_name,
            "thread": thread.name
        }

    def _process_card_async(self, card: Dict):
        """Kart işlemeyi arka planda yürütür"""
        card_id = card["id"]
        card_name = card.get("name", "Unknown")

        try:
            logger.info(f"🔄 İşlem başladı: {card_name}")

            # CrewAI, arka plan thread'inde signal handler kaydetmeye çalışır.
            # Bu sadece main thread'de çalışır ve ValueError fırlatır.
            # Bunu engellemek için signal.signal'ı geçici olarak susturuyoruz.
            with _suppress_signal_in_thread():
                success = self._on_backlog_card(card, self.board_id, self.list_ids)

            if success:
                with self._processing_lock:
                    self._processed_cards.add(card_id)
                self.stats["processed_cards"] += 1
                logger.info(f"✅ İşlem tamamlandı: {card_name}")
            else:
                logger.warning(f"⚠️ İşlem başarısız: {card_name}")
                self.stats["errors"] += 1

        except Exception as e:
            logger.error(f"❌ İşlem hatası ({card_name}): {e}")
            self.stats["errors"] += 1

        finally:
            with self._processing_lock:
                self._active_tasks.pop(card_id, None)

    def get_stats(self) -> Dict:
        """Webhook istatistiklerini döndürür"""
        with self._processing_lock:
            active = list(self._active_tasks.keys())

        return {
            **self.stats,
            "active_tasks": len(active),
            "active_card_ids": active,
            "total_processed_unique": len(self._processed_cards)
        }

    def is_card_processed(self, card_id: str) -> bool:
        """Kartın daha önce işlenip işlenmediğini kontrol eder"""
        return card_id in self._processed_cards

    def reset_card(self, card_id: str) -> bool:
        """İşlenmiş bir kartı sıfırlar (tekrar işlenmesine izin verir)"""
        with self._processing_lock:
            if card_id in self._processed_cards:
                self._processed_cards.discard(card_id)
                logger.info(f"🔄 Kart sıfırlandı: {card_id}")
                return True
        return False


@contextmanager
def _suppress_signal_in_thread():
    """
    CrewAI'ın arka plan thread'lerinde signal handler kaydetme
    girişimini susturur.

    CrewAI telemetry modülü SIGTERM/SIGINT handler'ları kaydetmeye çalışır,
    ancak bu Python'da sadece main thread'de çalışır. Non-main thread'lerde
    ValueError fırlatılır ve log'ları kirletir.

    Bu context manager, signal.signal'ı geçici olarak no-op yaparak
    bu uyarıları engeller.
    """
    if threading.current_thread() is threading.main_thread():
        # Main thread'deyiz, müdahale etme
        yield
        return

    original_signal = signal.signal

    def _noop_signal(signum, handler):
        """Non-main thread'de signal kaydını sessizce atla"""
        return None

    try:
        signal.signal = _noop_signal
        yield
    finally:
        signal.signal = original_signal


def verify_trello_signature(payload_body: bytes, signature: str, callback_url: str, secret: str = "") -> bool:
    """
    Trello webhook imzasını doğrular.

    Trello, her webhook isteğinde X-Trello-Webhook header'ında
    HMAC-SHA1 imzası gönderir.

    Args:
        payload_body: Ham request body (bytes)
        signature: X-Trello-Webhook header değeri
        callback_url: Webhook callback URL
        secret: Trello API secret (genelde token'ın kendisi)

    Returns:
        İmza geçerli ise True
    """
    if not secret or not signature:
        # Secret yoksa doğrulama atla (geliştirme ortamı)
        return True

    content = payload_body + callback_url.encode("utf-8")
    computed = base64.b64encode(
        hmac.new(secret.encode("utf-8"), content, hashlib.sha1).digest()
    ).decode("utf-8")

    return hmac.compare_digest(computed, signature)
