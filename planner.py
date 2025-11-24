

from models import User, Task, Subject

class StudyPlanner:
    """
    Module 3: Contains the core logic for generating study plans 
    (Data Input & Processing / Prediction & Analytics).
    """
    

    MAX_CONSECUTIVE_HOURS = 2.0 
    @staticmethod
    def generate_plan(user: User) -> list[Task]:
        """
        Generates a study plan by allocating available time slots to subjects 
        based on their weight (difficulty/importance).
        """
        if not user.subjects or not user.study_slots:
            return [] 

        total_available_hours = sum(user.study_slots)
        if total_available_hours == 0:
            return []

       
        total_weight = sum(s.weight for s in user.subjects)
        if total_weight == 0:
           
            equal_weight = 1
            total_weight = len(user.subjects) * equal_weight
            weighted_allocations = {s.name: total_available_hours / len(user.subjects) for s in user.subjects}
        else:
            
            weighted_allocations = {}
            for subject in user.subjects:
                
                proportion = subject.weight / total_weight
                hours_to_allocate = total_available_hours * proportion
                weighted_allocations[subject.name] = hours_to_allocate

        plan: list[Task] = []

      
        for subject in user.subjects:
            allocated = weighted_allocations.get(subject.name, 0)
            if allocated >= 1.0:
               
                num_tasks = int(allocated)
                remainder = allocated - num_tasks
                
               
                for i in range(num_tasks):
                    task_desc = "High-priority concept review" if i == 0 else "Practice problems and exercises"
                    plan.append(Task(subject.name, task_desc, 1.0))
                
                
                if remainder > 0.01: 
                     plan.append(Task(subject.name, "Quick review/Problem set", remainder))
            elif allocated > 0.01:
                
                plan.append(Task(subject.name, "Quick review/Problem set", allocated))


        plan.sort(key=lambda t: t.subject_name)
        
        
        StudyPlanner._add_recommendations(plan)

        return plan

    @staticmethod
    def _add_recommendations(plan: list[Task]):
        """A simple, hardcoded recommendation based on the subject."""
       
        recommendations = {
            "Algorithms": "Suggested Resource: Watch a video on Dynamic Programming on YouTube.",
            "Data Structures": "Suggested Resource: Read an article on Hash Table collision resolution techniques.",
            "C Programming": "Suggested Resource: Practice pointer arithmetic problems online.",
            "Calculus": "Suggested Resource: Review related theorems and proof methods.",
            "Physics": "Suggested Resource: Practice derivations and problem-solving techniques.",
            "Mathematics": "Suggested Resource: Work through practice problems from your textbook.",
            "Chemistry": "Suggested Resource: Review reaction mechanisms and balancing equations.",
            "Default": "Suggested Resource: Find a recent tech blog post related to your field."
        }
        
       
        seen_subjects = set()
        for task in plan:
            if task.subject_name not in seen_subjects:
                recommendation = recommendations.get(task.subject_name, recommendations["Default"])
                task.topic = f"{task.topic} ({recommendation})"
                seen_subjects.add(task.subject_name)

class SubjectManager:
    """
    Module 1: Manages the subjects for the user (CRUD Operations).
    """
    @staticmethod
    def add_subject(user: User, name: str, weight: int, target_hours: float):
        """Adds a new subject."""
      
        if not name or not name.strip():
            print("Subject name cannot be empty.")
            return False
        
        name = name.strip()  
        
        if not (1 <= weight <= 5):
            print("Weight must be between 1 and 5.")
            return False
        
        if target_hours < 0:
            print("Target hours must be non-negative.")
            return False

      
        if any(s.name.lower() == name.lower() for s in user.subjects):
            print(f"Subject '{name}' already exists.")
            return False

        new_subject = Subject(name, weight, target_hours)
        user.subjects.append(new_subject)
        print(f"Subject '{name}' added successfully (Weight: {weight}, Target: {target_hours:.1f} hrs).")
        return True

    @staticmethod
    def remove_subject(user: User, name: str):
        """Removes a subject by name."""
        if not name or not name.strip():
            print("Subject name cannot be empty.")
            return False
            
        name = name.strip()
        initial_count = len(user.subjects)
        user.subjects = [s for s in user.subjects if s.name.lower() != name.lower()]
        if len(user.subjects) < initial_count:
            print(f"Subject '{name}' removed successfully.")
            return True
        else:
            print(f"Subject '{name}' not found.")
            return False
            
    @staticmethod
    def view_subjects(user: User):
        """Displays all subjects."""
        if not user.subjects:
            print("No subjects added yet.")
            return
        print("\n--- Current Subjects ---")
        print(f"{'Name':<20}{'Weight (1-5)':<15}{'Target Hrs':<15}")
        print("-" * 50)
        for s in user.subjects:
            print(f"{s.name:<20}{s.weight:<15}{s.target_hours:<15.1f}")
        print("------------------------\n")
        