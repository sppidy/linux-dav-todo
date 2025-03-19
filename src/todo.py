class Todo:
    def __init__(self, uid=None, title="", description="", status="NEEDS-ACTION", href=None):
        self.uid = uid
        self.title = title
        self.description = description
        self.status = status
        self.href = href
        
    @classmethod
    def from_dav_task(cls, task_data):
        return cls(
            uid=task_data.get('uid'),
            title=task_data.get('title', ''),
            description=task_data.get('description', ''),
            status=task_data.get('status', 'NEEDS-ACTION').upper(),
            href=task_data.get('href')
        )

    def update(self, title=None, description=None, status=None):
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if status is not None:
            self.status = status
        return self

    def to_dict(self):
        return {
            'uid': self.uid,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'href': self.href
        }
        
    @property
    def is_completed(self):
        return self.status.upper() == 'COMPLETED'
        
    @is_completed.setter
    def is_completed(self, value):
        self.status = 'COMPLETED' if value else 'NEEDS-ACTION'

    def __str__(self):
        return f'Todo(title="{self.title}", status={self.status})'