class ShortTermMemory:
    def __init__(self, max_messages=12):
        self.max_messages = max_messages
        self.session = {}

    def add_message(self, session_id, role, content):
        message = self.session.setdefault(session_id, [])
        message.append({
            "role": role,
            "content": content
        })

        self.session[session_id]=message[-self.max_messages:]

    def get_messages(self, session_id):
        return self.session.get(session_id, [])

    def clear(self, session_id):
        if session_id in self.session:
            del self.session[session_id]
