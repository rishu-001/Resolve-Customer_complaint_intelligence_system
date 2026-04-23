"""
data_manager.py — Manages complaint storage (JSON-based local DB)
"""

import json
import os
from datetime import datetime, date
import pandas as pd

DATA_FILE = "complaints_db.json"


class DataManager:
    def __init__(self):
        self.data_path = DATA_FILE
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.data_path):
            with open(self.data_path, "w") as f:
                json.dump([], f)

    def _load(self) -> list:
        with open(self.data_path, "r") as f:
            return json.load(f)

    def _save(self, data: list):
        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def save_complaint(self, text: str, result: dict, customer_id: str = "", channel: str = ""):
        data = self._load()
        record = {
            "id": len(data) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "complaint_text": text,
            "customer_id": customer_id,
            "channel": channel,
            **result
        }
        data.append(record)
        self._save(data)

    def get_all(self) -> list:
        return self._load()

    def get_dataframe(self) -> pd.DataFrame:
        data = self._load()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if "labels" in df.columns:
            df["labels"] = df["labels"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        if "key_issues" in df.columns:
            df["key_issues"] = df["key_issues"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        return df

    def get_stats(self) -> dict:
        data = self._load()
        if not data:
            return {"total": 0, "critical_today": 0, "top_category": "N/A"}

        today = date.today().strftime("%Y-%m-%d")
        critical_today = sum(
            1 for r in data
            if r.get("urgency") == "Critical" and r.get("timestamp", "").startswith(today)
        )

        categories = [r.get("category", "") for r in data]
        top_category = max(set(categories), key=categories.count) if categories else "N/A"

        return {
            "total": len(data),
            "critical_today": critical_today,
            "top_category": top_category
        }

    def clear_all(self):
        self._save([])
