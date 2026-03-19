class ApprovalSystem:
    def __init__(self):
        self.pending_requests = {}

    def request_approval(self, task_id: str, api_call: dict):
        self.pending_requests[task_id] = api_call

    def approve(self, task_id: str):
        if task_id in self.pending_requests:
            del self.pending_requests[task_id]
            return True
        return False

    def get_pending(self) -> dict:
        return self.pending_requests