"""
Cost Tracker - Agent bazında maliyet takibi
OpenAI API token kullanımını izler ve agent bazında maliyet hesaplar.
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional


# Token fiyatları (GPT-4o mini varsayılan)
TOKEN_PRICES = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},      # per 1K tokens
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "berqun-api": {"input": 1.0, "output": 1.0},            # 1000 items = $1 (Simulation)
}

# Maliyet veritabanı dosyası
COST_DB_FILE = os.path.join(os.path.dirname(__file__), "cost_data.json")


class CostTracker:
    def __init__(self):
        self.records = []
        self.load()

    def load(self):
        """Kayıtlı maliyet verilerini yükle"""
        if os.path.exists(COST_DB_FILE):
            try:
                with open(COST_DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = data.get("records", [])
            except:
                self.records = []

    def save(self):
        """Maliyet verilerini kaydet"""
        with open(COST_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"records": self.records}, f, indent=2, ensure_ascii=False)

    def log_usage(self, team_id: str, agent_id: str, agent_name: str,
                  input_tokens: int = 0, output_tokens: int = 0,
                  model: str = "gpt-4o-mini", task_description: str = ""):
        """Agent'ın token kullanımını logla"""
        prices = TOKEN_PRICES.get(model, TOKEN_PRICES["gpt-4o-mini"])
        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]
        total_cost = input_cost + output_cost

        record = {
            "timestamp": datetime.now().isoformat(),
            "team_id": team_id,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost_usd": round(input_cost, 6),
            "output_cost_usd": round(output_cost, 6),
            "total_cost_usd": round(total_cost, 6),
            "task_description": task_description
        }

        self.records.append(record)
        self.save()
        return record

    def get_agent_costs(self, agent_id: str = None, team_id: str = None) -> Dict:
        """Agent veya takım bazında maliyet özeti"""
        filtered = self.records
        if agent_id:
            filtered = [r for r in filtered if r["agent_id"] == agent_id]
        if team_id:
            filtered = [r for r in filtered if r["team_id"] == team_id]

        total_input = sum(r["input_tokens"] for r in filtered)
        total_output = sum(r["output_tokens"] for r in filtered)
        total_cost = sum(r["total_cost_usd"] for r in filtered)

        return {
            "total_calls": len(filtered),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_cost_usd": round(total_cost, 6),
            "records": filtered[-20:]  # Son 20 kayıt
        }

    def get_team_summary(self, team_id: str) -> Dict:
        """Takım bazında agent maliyet dağılımı"""
        team_records = [r for r in self.records if r["team_id"] == team_id]

        agent_costs = {}
        for r in team_records:
            aid = r["agent_id"]
            if aid not in agent_costs:
                agent_costs[aid] = {
                    "agent_id": aid,
                    "agent_name": r["agent_name"],
                    "total_calls": 0,
                    "total_tokens": 0,
                    "total_cost_usd": 0
                }
            agent_costs[aid]["total_calls"] += 1
            agent_costs[aid]["total_tokens"] += r["total_tokens"]
            agent_costs[aid]["total_cost_usd"] = round(
                agent_costs[aid]["total_cost_usd"] + r["total_cost_usd"], 6
            )

        total_cost = sum(a["total_cost_usd"] for a in agent_costs.values())

        return {
            "team_id": team_id,
            "total_cost_usd": round(total_cost, 6),
            "agent_breakdown": list(agent_costs.values())
        }

    def get_all_summary(self) -> Dict:
        """Genel maliyet özeti"""
        total_cost = sum(r["total_cost_usd"] for r in self.records)
        total_tokens = sum(r["total_tokens"] for r in self.records)

        # Agent bazında
        agent_map = {}
        for r in self.records:
            aid = r["agent_id"]
            if aid not in agent_map:
                agent_map[aid] = {"name": r["agent_name"], "cost": 0, "calls": 0}
            agent_map[aid]["cost"] += r["total_cost_usd"]
            agent_map[aid]["calls"] += 1

        return {
            "total_cost_usd": round(total_cost, 6),
            "total_tokens": total_tokens,
            "total_records": len(self.records),
            "agents": [
                {
                    "agent_id": k,
                    "agent_name": v["name"],
                    "total_cost_usd": round(v["cost"], 6),
                    "total_calls": v["calls"]
                }
                for k, v in sorted(agent_map.items(), key=lambda x: x[1]["cost"], reverse=True)
            ]
        }


# Singleton
cost_tracker = CostTracker()
