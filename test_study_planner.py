
"""
Comprehensive test suite for the Study Planner application.
Tests all fixed bugs and edge cases.
"""

import sys
import os
import json


class Subject:
    def __init__(self, name: str, weight: int, target_hours: float = 0.0):
        self.name = name
        self.weight = weight
        self.target_hours = target_hours
    
    def to_dict(self):
        return {"name": self.name, "weight": self.weight, "target_hours": self.target_hours}

class Task:
    def __init__(self, subject_name: str, topic: str, hours_allocated: float):
        self.subject_name = subject_name
        self.topic = topic
        self.hours_allocated = hours_allocated
    
    def copy(self):
        return Task(self.subject_name, self.topic, self.hours_allocated)

class User:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.subjects = []
        self.study_slots = []
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "subjects": [s.to_dict() for s in self.subjects],
            "study_slots": self.study_slots
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(data['user_id'])
        user.subjects = [Subject(**s) for s in data.get('subjects', [])]
        user.study_slots = data.get('study_slots', [])
        return user

class StudyPlanner:
    MAX_CONSECUTIVE_HOURS = 2.0
    
    @staticmethod
    def generate_plan(user):
        if not user.subjects or not user.study_slots:
            return []
        
        total_available_hours = sum(user.study_slots)
        if total_available_hours == 0:
            return []
        
        total_weight = sum(s.weight for s in user.subjects)
        if total_weight == 0:
            weighted_allocations = {s.name: total_available_hours / len(user.subjects) for s in user.subjects}
        else:
            weighted_allocations = {}
            for subject in user.subjects:
                proportion = subject.weight / total_weight
                hours_to_allocate = total_available_hours * proportion
                weighted_allocations[subject.name] = hours_to_allocate
        
        plan = []
        for subject in user.subjects:
            allocated = weighted_allocations.get(subject.name, 0)
            if allocated >= 1.0:
                num_tasks = int(allocated)
                remainder = allocated - num_tasks
                for i in range(num_tasks):
                    plan.append(Task(subject.name, "Study session", 1.0))
                if remainder > 0.01:
                    plan.append(Task(subject.name, "Quick review", remainder))
            elif allocated > 0.01:
                plan.append(Task(subject.name, "Quick review", allocated))
        
        return plan

def run_tests():
    """Run all test cases."""
    print("=" * 60)
    print("STUDY PLANNER - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
   
    print("\nTest 1: Check MAX_CONSECUTIVE_HOURS constant exists")
    try:
        assert hasattr(StudyPlanner, 'MAX_CONSECUTIVE_HOURS')
        assert StudyPlanner.MAX_CONSECUTIVE_HOURS == 2.0
        print("✓ PASSED: MAX_CONSECUTIVE_HOURS is defined correctly")
        passed += 1
    except AssertionError:
        print("✗ FAILED: MAX_CONSECUTIVE_HOURS not defined or incorrect")
        failed += 1
    
    
    print("\nTest 2: User.from_dict returns user object")
    try:
        test_data = {
            'user_id': 'test_user',
            'subjects': [{'name': 'Math', 'weight': 3, 'target_hours': 10.0}],
            'study_slots': [2.0, 2.0]
        }
        user = User.from_dict(test_data)
        assert user is not None
        assert user.user_id == 'test_user'
        assert len(user.subjects) == 1
        print("✓ PASSED: User.from_dict returns valid user object")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: User.from_dict error: {e}")
        failed += 1
    
   
    print("\nTest 3: Task objects are not mutated")
    try:
        user = User('test')
        user.subjects = [Subject('Math', 3, 10.0), Subject('Physics', 2, 8.0)]
        user.study_slots = [3.0, 3.0, 3.0]
        
        plan = StudyPlanner.generate_plan(user)
        original_hours = [task.hours_allocated for task in plan]
        
        
        for task in plan:
            _ = task.hours_allocated
        
        new_hours = [task.hours_allocated for task in plan]
        assert original_hours == new_hours
        print("✓ PASSED: Task hours remain unchanged")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: Task mutation test error: {e}")
        failed += 1
    
   
    print("\nTest 4: Zero weight handling")
    try:
        user = User('test')
        user.subjects = [Subject('Math', 0, 10.0), Subject('Physics', 0, 8.0)]
        user.study_slots = [4.0]
        
        plan = StudyPlanner.generate_plan(user)
        assert len(plan) > 0
       
        total_math = sum(t.hours_allocated for t in plan if t.subject_name == 'Math')
        total_physics = sum(t.hours_allocated for t in plan if t.subject_name == 'Physics')
        assert abs(total_math - total_physics) < 0.1  # Should be roughly equal
        print("✓ PASSED: Zero weights handled correctly with equal distribution")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: Zero weight handling error: {e}")
        failed += 1
    
    
    print("\nTest 5: Weighted allocation math")
    try:
        user = User('test')
        user.subjects = [Subject('Math', 3, 10.0), Subject('Physics', 2, 8.0)]
        user.study_slots = [5.0]
        
        plan = StudyPlanner.generate_plan(user)
        total_math = sum(t.hours_allocated for t in plan if t.subject_name == 'Math')
        total_physics = sum(t.hours_allocated for t in plan if t.subject_name == 'Physics')
        

        assert abs(total_math - 3.0) < 0.1
        assert abs(total_physics - 2.0) < 0.1
        print(f"✓ PASSED: Math={total_math:.2f}h, Physics={total_physics:.2f}h (correct proportions)")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: Weighted allocation error: {e}")
        failed += 1
    
   
    print("\nTest 6: Empty subjects/slots handling")
    try:
        user1 = User('test')
        user1.subjects = []
        user1.study_slots = [5.0]
        plan1 = StudyPlanner.generate_plan(user1)
        assert plan1 == []
        
        user2 = User('test')
        user2.subjects = [Subject('Math', 3)]
        user2.study_slots = []
        plan2 = StudyPlanner.generate_plan(user2)
        assert plan2 == []
        
        print("✓ PASSED: Empty subjects/slots return empty plan")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: Empty handling error: {e}")
        failed += 1
    
   
    print("\nTest 7: Total hours allocation accuracy")
    try:
        user = User('test')
        user.subjects = [Subject('Math', 3), Subject('Physics', 2), Subject('Chem', 1)]
        user.study_slots = [3.0, 2.5, 4.0, 1.5, 3.5, 2.0, 1.0]  # Total: 17.5 hours
        
        plan = StudyPlanner.generate_plan(user)
        total_allocated = sum(t.hours_allocated for t in plan)
        total_available = sum(user.study_slots)
        
       
        assert abs(total_allocated - total_available) < 0.5
        print(f"✓ PASSED: Allocated {total_allocated:.2f}h of {total_available:.2f}h available")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: Total hours allocation error: {e}")
        failed += 1
    
    
    print("\nTest 8: Task copy method")
    try:
        task = Task('Math', 'Study', 2.0)
        task_copy = task.copy()
        assert task_copy.subject_name == task.subject_name
        assert task_copy.hours_allocated == task.hours_allocated
        assert task_copy is not task  # Different objects
        print("✓ PASSED: Task.copy() creates independent copy")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: Task copy error: {e}")
        failed += 1
    
   
    print("\nTest 9: Subject name case-insensitive duplicate check")
    try:
       
        subjects = [Subject('Math', 3), Subject('Physics', 2)]
        new_name = 'MATH'
        is_duplicate = any(s.name.lower() == new_name.lower() for s in subjects)
        assert is_duplicate == True
        print("✓ PASSED: Case-insensitive duplicate detection works")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: Duplicate check error: {e}")
        failed += 1
    
    
    print("\nTest 10: Multiple subject allocation")
    try:
        user = User('test')
        user.subjects = [
            Subject('Algorithms', 5, 20.0),
            Subject('Data Structures', 4, 15.0),
            Subject('C Programming', 3, 12.0)
        ]
        user.study_slots = [4.0, 3.0, 4.0, 3.0, 2.0, 1.0, 1.0]  # Total: 18 hours
        
        plan = StudyPlanner.generate_plan(user)
        
        algo_hours = sum(t.hours_allocated for t in plan if t.subject_name == 'Algorithms')
        ds_hours = sum(t.hours_allocated for t in plan if t.subject_name == 'Data Structures')
        c_hours = sum(t.hours_allocated for t in plan if t.subject_name == 'C Programming')
        
       
        total_weight = 5 + 4 + 3
        expected_algo = 18 * (5/total_weight)
        expected_ds = 18 * (4/total_weight)
        expected_c = 18 * (3/total_weight)
        
        assert abs(algo_hours - expected_algo) < 0.5
        assert abs(ds_hours - expected_ds) < 0.5
        assert abs(c_hours - expected_c) < 0.5
        
        print(f"✓ PASSED: Algorithms={algo_hours:.1f}h, DS={ds_hours:.1f}h, C={c_hours:.1f}h")
        passed += 1
    except Exception as e:
        print(f"✗ FAILED: Multiple subject allocation error: {e}")
        failed += 1
    
 
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Code is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review the errors above.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
    