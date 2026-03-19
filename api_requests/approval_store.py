"""Approval store for external API requests that require human input.
"""
from typing import List, Dict


class ApprovalStore:
    def __init__(self):
        self.approvals: List[Dict] = []

    def add_approval(self, item: Dict):
        self.approvals.append(item)

    def get_all(self) -> List[Dict]:
        return self.approvals

    def remove_approval(self, item_id: str):
        self.approvals = [a for a in self.approvals if a.get("id") != item_id]
