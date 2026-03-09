"""
Jira Helper - Jira API işlemlerini kolaylaştıran yardımcı sınıf
"""
import requests
from requests.auth import HTTPBasicAuth
import json
from typing import List, Dict, Optional
import sys
import io

# Windows konsol encoding sorunu için
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class JiraHelper:
    """Jira API işlemleri için helper sınıfı"""

    def __init__(self, url: str, email: str, token: str, project_key: str):
        """
        Jira Helper başlatıcı

        Args:
            url: Jira URL (örn: https://dgpaysit.atlassian.net)
            email: Jira kullanıcı email
            token: Jira API token
            project_key: Proje anahtarı (örn: TES)
        """
        self.url = url.rstrip('/')
        self.email = email
        self.token = token
        self.project_key = project_key
        self.auth = HTTPBasicAuth(email, token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_issue(self,
                     summary: str,
                     description: str,
                     issue_type: str = "Task",
                     assignee_email: Optional[str] = None,
                     priority: str = "Medium",
                     story_points: float = 1.0) -> Optional[Dict]:
        """
        Yeni bir issue oluşturur

        Args:
            summary: Issue başlığı
            description: Issue açıklaması
            issue_type: Issue tipi (Task, Bug, Story, vb.)
            assignee_email: Atanacak kişinin email'i (None ise atama yapılmaz)
            priority: Öncelik (Highest, High, Medium, Low, Lowest)
            story_points: Story Points (TES projesi için zorunlu, default: 1.0)

        Returns:
            Oluşturulan issue bilgileri veya None
        """
        # Assignee account ID'sini al
        assignee_id = None
        if assignee_email:
            assignee_id = self.get_user_account_id(assignee_email)

        issue_data = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": issue_type
                },
                "customfield_10037": story_points  # Story Points (TES projesi için zorunlu)
            }
        }

        # Assignee ekle
        if assignee_id:
            issue_data["fields"]["assignee"] = {"accountId": assignee_id}

        try:
            response = requests.post(
                f"{self.url}/rest/api/3/issue",
                headers=self.headers,
                auth=self.auth,
                data=json.dumps(issue_data)
            )

            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Issue oluşturuldu: [{result['key']}] {summary}")
                return result
            else:
                print(f"❌ Issue oluşturulamadı: {response.status_code}")
                print(f"   Hata: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Hata: {e}")
            return None

    def get_user_account_id(self, email: str) -> Optional[str]:
        """
        Email adresinden kullanıcı account ID'sini bulur

        Args:
            email: Kullanıcı email

        Returns:
            Account ID veya None
        """
        try:
            # Kullanıcıyı email ile ara
            response = requests.get(
                f"{self.url}/rest/api/3/user/search",
                headers=self.headers,
                auth=self.auth,
                params={"query": email}
            )

            if response.status_code == 200:
                users = response.json()
                if users:
                    return users[0]['accountId']
            return None
        except Exception as e:
            print(f"⚠️  Kullanıcı bulunamadı: {e}")
            return None

    def get_issues(self, jql: str = None, max_results: int = 50) -> List[Dict]:
        """
        JQL sorgusu ile issue'ları getirir

        Args:
            jql: JQL sorgusu (None ise proje bazlı tüm issue'ları getirir)
            max_results: Maksimum sonuç sayısı

        Returns:
            Issue listesi
        """
        if jql is None:
            jql = f"project={self.project_key} ORDER BY created DESC"

        try:
            response = requests.post(
                f"{self.url}/rest/api/3/search/jql",
                headers=self.headers,
                auth=self.auth,
                data=json.dumps({
                    "jql": jql,
                    "maxResults": max_results
                })
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('issues', [])
            else:
                print(f"❌ Issue'lar alınamadı: {response.status_code}")
                print(f"   Hata: {response.text}")
                return []
        except Exception as e:
            print(f"❌ Hata: {e}")
            return []

    def get_issue(self, issue_key: str) -> Optional[Dict]:
        """
        Belirli bir issue'yu getirir

        Args:
            issue_key: Issue anahtarı (örn: TES-123)

        Returns:
            Issue bilgileri veya None
        """
        try:
            response = requests.get(
                f"{self.url}/rest/api/3/issue/{issue_key}",
                headers=self.headers,
                auth=self.auth
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Issue bulunamadı: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Hata: {e}")
            return None

    def update_issue_status(self, issue_key: str, status: str) -> bool:
        """
        Issue durumunu günceller (transition yapar)

        Args:
            issue_key: Issue anahtarı
            status: Hedef durum (örn: "In Progress", "Done")

        Returns:
            Başarılı ise True
        """
        try:
            # Önce mevcut transition'ları al
            transitions_response = requests.get(
                f"{self.url}/rest/api/3/issue/{issue_key}/transitions",
                headers=self.headers,
                auth=self.auth
            )

            if transitions_response.status_code != 200:
                print(f"❌ Transition'lar alınamadı: {transitions_response.status_code}")
                return False

            transitions = transitions_response.json().get('transitions', [])

            # İstenen duruma geçiş yapacak transition'ı bul
            target_transition = None
            for transition in transitions:
                if transition['to']['name'].lower() == status.lower():
                    target_transition = transition
                    break

            if not target_transition:
                print(f"⚠️  '{status}' durumuna geçiş bulunamadı. Mevcut geçişler:")
                for t in transitions:
                    print(f"   - {t['to']['name']}")
                return False

            # Transition yap
            transition_response = requests.post(
                f"{self.url}/rest/api/3/issue/{issue_key}/transitions",
                headers=self.headers,
                auth=self.auth,
                data=json.dumps({
                    "transition": {
                        "id": target_transition['id']
                    }
                })
            )

            if transition_response.status_code == 204:
                print(f"✅ [{issue_key}] durumu '{status}' olarak güncellendi")
                return True
            else:
                print(f"❌ Durum güncellenemedi: {transition_response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Hata: {e}")
            return False

    def add_comment(self, issue_key: str, comment: str) -> bool:
        """
        Issue'ya yorum ekler

        Args:
            issue_key: Issue anahtarı
            comment: Yorum metni

        Returns:
            Başarılı ise True
        """
        try:
            comment_data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment
                                }
                            ]
                        }
                    ]
                }
            }

            response = requests.post(
                f"{self.url}/rest/api/3/issue/{issue_key}/comment",
                headers=self.headers,
                auth=self.auth,
                data=json.dumps(comment_data)
            )

            if response.status_code == 201:
                print(f"✅ [{issue_key}] yorumu eklendi")
                return True
            else:
                print(f"❌ Yorum eklenemedi: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Hata: {e}")
            return False

    def get_issues_by_status(self, status: str) -> List[Dict]:
        """
        Belirli bir durumdaki issue'ları getirir

        Args:
            status: Durum adı

        Returns:
            Issue listesi
        """
        jql = f'project={self.project_key} AND status="{status}" ORDER BY created DESC'
        return self.get_issues(jql)

    def get_my_issues(self) -> List[Dict]:
        """
        Mevcut kullanıcıya atanmış issue'ları getirir

        Returns:
            Issue listesi
        """
        jql = f'project={self.project_key} AND assignee=currentUser() ORDER BY created DESC'
        return self.get_issues(jql)
