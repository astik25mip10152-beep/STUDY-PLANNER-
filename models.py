

import json

class Subject:
    """Represents a course or subject a user is studying."""
    def __init__(self, name: str, weight: int, target_hours: float = 0.0):
       
        self.name = name
        self.weight = weight
        self.target_hours = target_hours

    def to_dict(self):
        return {
            "name": self.name,
            "weight": self.weight,
            "target_hours": self.target_hours
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            weight=data['weight'],
            target_hours=data.get('target_hours', 0.0)
        )

class Task:
    """Represents a planned study activity or recommendation."""
    def __init__(self, subject_name: str, topic: str, hours_allocated: float):
        self.subject_name = subject_name
        self.topic = topic
        self.hours_allocated = hours_allocated

    def __str__(self):
        return f"[{self.subject_name}] Study {self.topic} for {self.hours_allocated:.2f} hours."
    
    def copy(self):
        """Creates a deep copy of the task to avoid mutation issues."""
        return Task(self.subject_name, self.topic, self.hours_allocated)

class User:
    """The main entity holding the user's data."""
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.subjects: list[Subject] = []
        self.study_slots: list[float] = [] 

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "subjects": [s.to_dict() for s in self.subjects],
            "study_slots": self.study_slots
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(data['user_id'])
        user.subjects = [Subject.from_dict(s) for s in data.get('subjects', [])]
        user.study_slots = data.get('study_slots', [])
        return user 
      