class MemoryStore:
    def __init__(self):
        self.tasks = {}
        self.decisions = {}
        self.logs = []

    def add_task(self, task_id: str, task: dict):
        self.tasks[task_id] = task

    def get_task(self, task_id: str) -> dict:
        return self.tasks.get(task_id)

    def add_decision(self, decision_id: str, decision: dict):
        self.decisions[decision_id] = decision

    def log_event(self, event: str):
        self.logs.append(event)