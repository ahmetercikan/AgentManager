"""
Berqun API Client — Verimlilik Analizi uygulaması API entegrasyonu.
Berqun'dan personel listesi, BQ puanları, aktivite verileri ve
dashboard bilgilerini çeker.
"""

import os
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

BERQUN_SERVER = os.getenv("BERQUN_SERVER", "http://berqun.dgpays.local")
BERQUN_USER = os.getenv("BERQUN_USER", "ahmet.ercikan@dgpaysit.com")
BERQUN_PASS = os.getenv("BERQUN_PASS", "")

# Period type ID'leri
PERIOD_DAY = 13001
PERIOD_WEEK = 13002
PERIOD_MONTH = 13003
PERIOD_YEAR = 13004


class BerqunClient:
    """Berqun API istemcisi — otomatik token yönetimi ile"""

    def __init__(self, server=None, username=None, password=None):
        self.server = server or BERQUN_SERVER
        self.username = username or BERQUN_USER
        self.password = password or BERQUN_PASS
        self.base_url = f"{self.server}/api/v1"
        self.auth_token = None
        self.token_expire = 0  # epoch ms
        self.staff_cache = None

    # ─── Authentication ───────────────────────────────────────

    def login(self) -> bool:
        """Berqun'a giriş yap ve auth token al (GET request, 1 saat geçerli)"""
        try:
            url = f"{self.base_url}/login"
            resp = requests.get(url, params={
                "user_name": self.username,
                "password": self.password
            }, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            # Berqun response yapısı: { meta: { return_code: 0 }, data: { auth_token: "..." } }
            meta = data.get("meta", {})
            if meta.get("return_code") == 0:
                self.auth_token = data.get("data", {}).get("auth_token")
                # Berqun API expiry döndürmez, 1 saat olarak ayarla
                self.token_expire = time.time() * 1000 + (60 * 60 * 1000)
                print(f"✅ Berqun giriş başarılı: {self.username}")
                return True
            else:
                msg = meta.get("message", "Bilinmeyen hata")
                print(f"❌ Berqun login hatası: {msg}")
                return False
        except Exception as e:
            print(f"❌ Berqun giriş hatası: {e}")
            return False

    def _headers(self) -> dict:
        """Authorization header"""
        return {"Authorization": f"Bearer {self.auth_token}"}

    def _ensure_auth(self):
        """Token yoksa veya süresi dolduysa login yap (1 dk margin)"""
        now = time.time() * 1000
        if self.auth_token and now < (self.token_expire - 60000):
            return  # Token hâlâ geçerli
        if not self.login():
            raise Exception("Berqun kimlik doğrulama başarısız!")

    def _parse_response(self, resp) -> any:
        """Berqun response'u parse et (meta + data yapısı)"""
        data = resp.json()
        meta = data.get("meta", {})
        if meta.get("return_code") != 0:
            raise Exception(f"Berqun API hatası: {meta.get('message', 'Bilinmeyen hata')}")
        return data.get("data", data)

    # ─── Staff (Personel) ────────────────────────────────────

    def get_staff_list(self, page: int = 1, limit: int = 1000) -> list:
        """Tüm personel listesini al (POST + pagination)"""
        self._ensure_auth()
        resp = requests.post(
            f"{self.base_url}/staff_list",
            json={"page": page, "limit": limit},
            headers=self._headers(),
            timeout=30
        )
        resp.raise_for_status()
        result = self._parse_response(resp)
        # Berqun yapısı: data: { total: N, data: [...staff...] }
        if isinstance(result, dict) and "data" in result:
            self.staff_cache = result["data"]
        elif isinstance(result, list):
            self.staff_cache = result
        else:
            self.staff_cache = []
        return self.staff_cache

    def get_staff_by_guid(self, staff_guid: str) -> Optional[dict]:
        """GUID ile personel bilgisi al"""
        if not self.staff_cache:
            self.get_staff_list()
        for staff in (self.staff_cache or []):
            if staff.get("guid") == staff_guid or staff.get("staff_guid") == staff_guid:
                return staff
        return None

    # ─── Dashboard / BQ Puanları ─────────────────────────────

    def get_user_dashboard(self, person_guid: str, date: str, period: int = PERIOD_MONTH) -> dict:
        """
        Kullanıcı dashboard verisi — BQ puanı, verimli/verimsiz süre vs.

        Args:
            person_guid: Personelin GUID'i (staff_list'den alınır)
            date: Tarih (yyyy-mm-dd formatında)
            period: Period tipi (13001=Gün, 13002=Hafta, 13003=Ay, 13004=Yıl)
        """
        self._ensure_auth()
        resp = requests.post(
            f"{self.base_url}/user_dashboard",
            params={
                "date": date,
                "person_guid": person_guid,
                "period_type_id": period
            },
            headers=self._headers(),
            timeout=30
        )
        resp.raise_for_status()
        return self._parse_response(resp)

    def get_all_staff_monthly_bq(self, date: str) -> list:
        """
        Tüm personelin aylık BQ puanlarını al.

        Args:
            date: Ayın herhangi bir günü (yyyy-mm-dd)

        Returns:
            [{"staff_guid", "name", "surname", "bq_score", "dashboard": {...}}]
        """
        staff_list = self.get_staff_list()
        results = []

        for staff in staff_list:
            guid = staff.get("guid") or staff.get("staff_guid")
            if not guid:
                continue
            try:
                dashboard = self.get_user_dashboard(guid, date, PERIOD_MONTH)
                bq_score = self._extract_bq_score(dashboard)
                results.append({
                    "staff_guid": guid,
                    "name": staff.get("name", ""),
                    "surname": staff.get("surname", ""),
                    "email": staff.get("email", ""),
                    "domain_login": staff.get("domain_login", ""),
                    "bq_score": bq_score,
                    "dashboard": dashboard
                })
            except Exception as e:
                print(f"⚠️ Dashboard alınamadı: {staff.get('name', guid)} — {e}")

        return results

    # ─── Aktivite Verileri ───────────────────────────────────

    def get_all_staff_activity(self, date: str) -> list:
        """Tüm personelin belirli bir güne ait aktivite verisi"""
        self._ensure_auth()
        resp = requests.post(
            f"{self.base_url}/staff_activity_list",
            params={"date": date, "all_staff_flag": 1},
            headers=self._headers(),
            timeout=120  # Büyük veri seti için uzun timeout
        )
        resp.raise_for_status()
        return self._parse_response(resp)

    def get_staff_activity(self, staff_guid: str, date: str) -> list:
        """Belirli bir personelin günlük aktivitesi"""
        self._ensure_auth()
        resp = requests.post(
            f"{self.base_url}/staff_activity_list",
            params={"date": date, "staff_guid": staff_guid},
            headers=self._headers(),
            timeout=30
        )
        resp.raise_for_status()
        return self._parse_response(resp)

    def get_user_app_usage(self, staff_guid: str, date: str,
                           period: int = PERIOD_MONTH, top_n: int = 10) -> dict:
        """
        Kullanıcının uygulama kullanım özeti — Top N verimli ve verimsiz uygulamalar.

        Returns:
            {
                "productive": [{"app": str, "duration": int, "duration_fmt": str}],
                "distractive": [{"app": str, "duration": int, "duration_fmt": str}],
                "total_productive_sec": int,
                "total_distractive_sec": int
            }
        """
        self._ensure_auth()
        resp = requests.post(
            f"{self.base_url}/staff_activity_list",
            params={
                "date": date,
                "staff_guid": staff_guid,
                "period_type_id": period
            },
            headers=self._headers(),
            timeout=30
        )
        resp.raise_for_status()
        items = self._parse_response(resp)
        if not isinstance(items, list):
            items = []

        productive_apps = {}
        distractive_apps = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            app = item.get("activity_type_name", "Unknown")
            level = item.get("level", 0)
            dur = item.get("duration", 0) or 0
            if level == 1:
                productive_apps[app] = productive_apps.get(app, 0) + dur
            elif level == -1:
                distractive_apps[app] = distractive_apps.get(app, 0) + dur

        def _fmt_dur(sec):
            h, m = int(sec // 3600), int((sec % 3600) // 60)
            return f"{h}sa {m}dk" if h > 0 else f"{m}dk"

        def _top(app_dict):
            return [
                {"app": app, "duration": dur, "duration_fmt": _fmt_dur(dur)}
                for app, dur in sorted(app_dict.items(), key=lambda x: -x[1])[:top_n]
            ]

        return {
            "productive": _top(productive_apps),
            "distractive": _top(distractive_apps),
            "total_productive_sec": sum(productive_apps.values()),
            "total_distractive_sec": sum(distractive_apps.values()),
        }

    def download_user_excel(self, person_guid: str, person_name: str,
                            date: str, start_date: str, end_date: str,
                            month_label: str = "",
                            include_nonwork_bq: bool = True) -> dict:
        """
        Berqun'dan kişisel verimlilik raporu Excel'i indir.

        /export/user_dashboard.aspx endpoint'ini kullanır.

        Args:
            person_guid: Kişinin GUID'i
            person_name: Dosya adı için kişinin adı
            date: Ayın ilk günü (yyyy-mm-dd)
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            month_label: Dosya adı için ay etiketi (ör. "Ocak 2026")
            include_nonwork_bq: Çalışma günü dışı verimli süreyi BQ'ya dahil et

        Returns:
            {"success": bool, "content": bytes, "filename": str, "size": int}
        """
        self._ensure_auth()
        server_url = self.base_url.rsplit("/api/v1", 1)[0]
        url = f"{server_url}/export/user_dashboard.aspx"

        params = {
            "ExportToExcel": 1,
            "person_guid": person_guid,
            "calculation_policy": "all",
            "period_type_id": PERIOD_MONTH,
            "date": date,
            "start_date": start_date,
            "end_date": end_date,
            "export_to_excel_flag": 1,
            "UserSelectedFileName": f"Personel Verimliliği {person_name} {month_label}",
            "include_out_productive_hours_in_bqpoint": 1 if include_nonwork_bq else 0,
            "AuthToken": self.auth_token,
        }

        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()

            ct = resp.headers.get("content-type", "")
            if "excel" in ct or "spreadsheet" in ct or len(resp.content) > 500:
                safe_name = person_name.replace(" ", "_").replace("/", "-")
                filename = f"{safe_name}_{month_label.replace(' ', '_')}.xlsx"
                return {
                    "success": True,
                    "content": resp.content,
                    "filename": filename,
                    "size": len(resp.content)
                }
            else:
                return {"success": False, "content": b"", "filename": "",
                        "size": 0, "error": f"Unexpected content-type: {ct}"}
        except Exception as e:
            return {"success": False, "content": b"", "filename": "",
                    "size": 0, "error": str(e)}

    def get_monthly_calendar(self, date: str) -> dict:
        """Tüm personelin aylık çalışma takvimi"""
        self._ensure_auth()
        resp = requests.post(
            f"{self.base_url}/calendar_staff_monthly_list",
            data={"date": date},
            headers=self._headers(),
            timeout=30
        )
        resp.raise_for_status()
        return self._parse_response(resp)

    # ─── Ekran Görüntüleri ───────────────────────────────────

    def get_staff_screenshots(self, person_guid: str, date: str, interval: int = 60) -> list:
        """Personelin ekran görüntüleri"""
        self._ensure_auth()
        resp = requests.post(
            f"{self.base_url}/staff_screenshot_list",
            params={
                "date": date,
                "person_guid": person_guid,
                "interval_min": interval,
                "sort": "asc",
                "start": 0,
                "limit": 200
            },
            headers=self._headers(),
            timeout=30
        )
        resp.raise_for_status()
        return self._parse_response(resp)

    # ─── Rapor Oluşturma (Yüksek Seviye Fonksiyonlar) ────────

    def generate_monthly_report(self, date: str) -> dict:
        """
        Aylık GMY raporu için gerekli tüm veriyi topla.

        Returns:
            {
                "date": "2025-02-01",
                "total_staff": 150,
                "bq_below_100": [{"name", "bq_score", ...}],
                "bq_below_100_count": 8,
                "vpn_missing_3days": [{"name", "last_vpn", ...}],
                "vpn_missing_count": 8,
                "risk_assessment": "Riskli durum izlenmemiştir.",
                "staff_details": [...]
            }
        """
        report = {
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "total_staff": 0,
            "bq_below_100": [],
            "bq_below_100_count": 0,
            "vpn_missing_3days": [],
            "vpn_missing_count": 0,
            "risk_assessment": "Riskli durum izlenmemiştir.",
            "staff_details": []
        }

        try:
            # 1. Tüm personel BQ puanlarını al
            all_bq = self.get_all_staff_monthly_bq(date)
            report["total_staff"] = len(all_bq)
            report["staff_details"] = all_bq

            # 2. BQ < 100 olanları filtrele
            for staff in all_bq:
                bq_score = staff.get("bq_score")
                if bq_score is not None and bq_score < 100:
                    report["bq_below_100"].append({
                        "name": f"{staff['name']} {staff['surname']}",
                        "email": staff["email"],
                        "bq_score": bq_score,
                        "staff_guid": staff["staff_guid"]
                    })

            report["bq_below_100_count"] = len(report["bq_below_100"])

            # 3. VPN kontrol — son 3 gün aktivite olmayan personel
            report["vpn_missing_3days"] = self._check_vpn_compliance(date)
            report["vpn_missing_count"] = len(report["vpn_missing_3days"])

        except Exception as e:
            report["error"] = str(e)
            print(f"❌ Rapor oluşturma hatası: {e}")

        return report

    def _extract_bq_score(self, dashboard: any) -> Optional[float]:
        """Dashboard verisinden BQ puanını çıkar"""
        if isinstance(dashboard, dict):
            # Berqun'un olası alan isimleri
            for key in ["bq_score", "score", "business_quality", "bq",
                         "total_score", "productivity_score", "bq_point"]:
                if key in dashboard:
                    try:
                        return float(dashboard[key])
                    except (ValueError, TypeError):
                        pass
            # İç içe yapıda arama
            for nested_key in ["summary", "data", "result", "dashboard"]:
                if nested_key in dashboard and isinstance(dashboard[nested_key], dict):
                    result = self._extract_bq_score(dashboard[nested_key])
                    if result is not None:
                        return result
        return None

    def _check_vpn_compliance(self, date: str, staff_list: list = None) -> list:
        """
        Son 3 gün VPN bağlantısı olmayan personeli tespit et.
        
        staff_list parametresi verilirse yeniden API çağrısı yapmaz.
        Filtreleme: last_seen_date < (şu an - 3 gün) veya last_seen_date yok.
        """
        missing = []
        try:
            if staff_list is None:
                staff_list = self.get_staff_list()

            now = datetime.now()
            three_days_ago = now - timedelta(days=3)

            for staff in staff_list:
                last_seen = staff.get("last_seen_date")
                guid = staff.get("guid") or staff.get("staff_guid")

                if not guid:
                    continue

                is_inactive = False
                if not last_seen:
                    is_inactive = True
                else:
                    try:
                        # last_seen_date formatı: "2026-02-23T14:30:00" veya benzeri
                        last_seen_dt = datetime.fromisoformat(
                            last_seen.replace("Z", "+00:00").split("+")[0]
                        )
                        if last_seen_dt < three_days_ago:
                            is_inactive = True
                    except (ValueError, TypeError):
                        is_inactive = True

                if is_inactive:
                    full_name = staff.get("full_name",
                                         f"{staff.get('name', '')} {staff.get('surname', '')}").strip()

                    # Son sinyal metnini hesapla
                    son_sinyal = "Veri yok"
                    if last_seen:
                        try:
                            last_dt = datetime.fromisoformat(
                                last_seen.replace("Z", "+00:00").split("+")[0]
                            )
                            days_ago = (now - last_dt).days
                            son_sinyal = f"{days_ago} gün önce" if days_ago > 0 else "Bugün"
                        except (ValueError, TypeError):
                            son_sinyal = "Bilinmiyor"

                    # İzleme durumu
                    tracking_disabled = staff.get("tracking_disabled", False)
                    izleme = "Devre Dışı" if tracking_disabled else "Etkin"

                    missing.append({
                        "name": full_name,
                        "email": staff.get("email", ""),
                        "staff_guid": guid,
                        "team_name": staff.get("team_name", "-"),
                        "computer_name": staff.get("computer_name", "-"),
                        "son_sinyal": son_sinyal,
                        "izleme": izleme,
                        "last_seen_date": last_seen or "Veri yok",
                    })
        except Exception as e:
            print(f"⚠️ VPN kontrol hatası: {e}")

        return missing


# Singleton instance
berqun_client = BerqunClient()


def get_berqun_client() -> BerqunClient:
    """Berqun client instance döndür"""
    return berqun_client
