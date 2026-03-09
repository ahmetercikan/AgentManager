"""
Knowledge Base — Şirket bilgi bankası yönetim modülü.
Agent'lara şirket bilgisi, prosedürler, standartlar ve domain-spesifik
bilgileri yüklemek için kullanılır.
"""

import os
import json
from datetime import datetime
from typing import Optional

BASE_DIR = os.path.dirname(__file__)
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "company_knowledge")


def ensure_knowledge_dir():
    """Bilgi bankası dizinini oluştur"""
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    os.makedirs(os.path.join(KNOWLEDGE_DIR, "global"), exist_ok=True)


def list_domains_with_knowledge():
    """Knowledge dosyası olan domainleri listele"""
    ensure_knowledge_dir()
    domains = []
    for item in os.listdir(KNOWLEDGE_DIR):
        full_path = os.path.join(KNOWLEDGE_DIR, item)
        if os.path.isdir(full_path):
            files = [f for f in os.listdir(full_path) if f.endswith('.md')]
            domains.append({
                "domain": item,
                "file_count": len(files),
                "files": files
            })
    return domains


def list_knowledge_files(domain_id: str):
    """Belirli bir domainin bilgi dosyalarını listele"""
    ensure_knowledge_dir()
    domain_dir = os.path.join(KNOWLEDGE_DIR, domain_id)
    if not os.path.exists(domain_dir):
        return []

    files = []
    for fname in sorted(os.listdir(domain_dir)):
        if fname.endswith('.md'):
            filepath = os.path.join(domain_dir, fname)
            stat = os.stat(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            files.append({
                "filename": fname,
                "title": fname.replace('.md', '').replace('_', ' ').title(),
                "size": stat.st_size,
                "lines": len(content.split('\n')),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "preview": content[:150] + ("..." if len(content) > 150 else "")
            })
    return files


def get_knowledge_content(domain_id: str, filename: str) -> Optional[str]:
    """Bilgi dosyasının içeriğini oku"""
    filepath = os.path.join(KNOWLEDGE_DIR, domain_id, filename)
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def save_knowledge_file(domain_id: str, filename: str, content: str) -> dict:
    """Bilgi dosyası kaydet veya güncelle"""
    ensure_knowledge_dir()
    domain_dir = os.path.join(KNOWLEDGE_DIR, domain_id)
    os.makedirs(domain_dir, exist_ok=True)

    if not filename.endswith('.md'):
        filename += '.md'

    filepath = os.path.join(domain_dir, filename)
    is_new = not os.path.exists(filepath)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "filename": filename,
        "domain": domain_id,
        "action": "created" if is_new else "updated",
        "size": len(content),
        "lines": len(content.split('\n'))
    }


def delete_knowledge_file(domain_id: str, filename: str) -> bool:
    """Bilgi dosyasını sil"""
    filepath = os.path.join(KNOWLEDGE_DIR, domain_id, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def load_knowledge_for_agent(domain_id: str) -> str:
    """
    Agent çalıştırılmadan önce ilgili domain + global bilgiyi birleştir.
    Bu fonksiyon team_executor tarafından çağrılır.
    """
    ensure_knowledge_dir()
    knowledge_parts = []

    # 1. Global bilgiyi yükle (tüm agentlar için)
    global_dir = os.path.join(KNOWLEDGE_DIR, "global")
    if os.path.exists(global_dir):
        for fname in sorted(os.listdir(global_dir)):
            if fname.endswith('.md'):
                filepath = os.path.join(global_dir, fname)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    title = fname.replace('.md', '').replace('_', ' ').upper()
                    knowledge_parts.append(f"## {title}\n{content}")

    # 2. Domain-spesifik bilgiyi yükle
    domain_dir = os.path.join(KNOWLEDGE_DIR, domain_id)
    if os.path.exists(domain_dir):
        for fname in sorted(os.listdir(domain_dir)):
            if fname.endswith('.md'):
                filepath = os.path.join(domain_dir, fname)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    title = fname.replace('.md', '').replace('_', ' ').upper()
                    knowledge_parts.append(f"## {title}\n{content}")

    if not knowledge_parts:
        return ""

    return "# ŞİRKET BİLGİ BANKASI\n\n" + "\n\n---\n\n".join(knowledge_parts)


def get_knowledge_stats() -> dict:
    """Bilgi bankası istatistikleri"""
    ensure_knowledge_dir()
    stats = {
        "total_files": 0,
        "total_size": 0,
        "domains": {}
    }

    for item in os.listdir(KNOWLEDGE_DIR):
        full_path = os.path.join(KNOWLEDGE_DIR, item)
        if os.path.isdir(full_path):
            files = [f for f in os.listdir(full_path) if f.endswith('.md')]
            total_size = sum(
                os.path.getsize(os.path.join(full_path, f))
                for f in files
            )
            stats["domains"][item] = {
                "file_count": len(files),
                "total_size": total_size
            }
            stats["total_files"] += len(files)
            stats["total_size"] += total_size

    return stats
