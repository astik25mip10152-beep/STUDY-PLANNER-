
from storage import StorageManager
from planner import StudyPlanner, SubjectManager
from config import DEFAULT_USER_ID

class CLI:
    """
    Main CLI interface - handles all user interactions
    TODO: Add color support for better UX (maybe use colorama?)
    """
    def __init__(self):

        self.user = StorageManager.load_user(DEFAULT_USER_ID)
        
    def save_and_exit(self):
        """Save and exit - pretty straightforward"""
        StorageManager.save_user(self.user)
        print("\nThank you for using the Study Planner. Goodbye!")
        exit()
        
    def run(self):
        """Main loop - keeps app running until user exits"""
        print("-----------------------------------------------------")
        print("    PERSONALIZED STUDY PLANNER & RECOMMENDATION SYSTEM   ")
        print("-----------------------------------------------------")
        
      
        while True:
            self._display_menu()
            choice = input("Enter your choice: ").strip()
            
            try:
              
                if choice == '1':
                    self._add_subject()
                elif choice == '2':
                    self._remove_subject()
                elif choice == '3':
                    SubjectManager.view_subjects(self.user)
                elif choice == '4':
                    self._input_study_slots()
                elif choice == '5':
                    self._generate_and_view_plan()
                elif choice == '6':
                    self.save_and_exit()
                else:
                    print("Invalid choice. Please try again.")
            except ValueError as e:
                print(f"Invalid input format: {e}. Please enter numerical values where expected.")
            except KeyboardInterrupt:
            
                print("\n\nInterrupted by user. Saving data...")
                self.save_and_exit()
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                # TODO: Add proper logging here

    def _display_menu(self):
        """Display main menu options"""
        print("\n--- Main Menu ---")
        print("1. Add a Subject")
        print("2. Remove a Subject")
        print("3. View All Subjects")
        print("4. Input Available Study Slots")
        print("5. Generate Study Plan")
        print("6. Save & Exit")
        
    def _add_subject(self):
        """
        Add new subject with validation
        FIXME: Need to add better weight explanation for users
        """
        print("\n--- Add New Subject ---")
        name = input("Enter Subject Name: ").strip()
        
        if not name:
            print("Subject name cannot be empty.")
            return
        
       
        while True:
            try:
                weight = int(input("Enter Weight/Difficulty (1=Easy to 5=Hard): ").strip())
                if 1 <= weight <= 5:
                    break
                else:
                    print("Weight must be between 1 and 5.")
            except ValueError:
                print("Invalid input. Please enter a number for weight.")
        
     
        while True:
            try:
                target_hours = float(input("Enter Target Total Study Hours (e.g., 50.0): ").strip())
                if target_hours >= 0:
                    break
                else:
                    print("Target hours must be non-negative.")
            except ValueError:
                print("Invalid input. Please enter a number for target hours.")
            
        SubjectManager.add_subject(self.user, name, weight, target_hours)

    def _remove_subject(self):
        """Remove subject by name"""
        name = input("Enter Subject Name to Remove: ").strip()
        SubjectManager.remove_subject(self.user, name)
        
    def _input_study_slots(self):
        """
        Get weekly study availability
        Note: This could be optimized to save partial input if user exits
        """
        print("\n--- Input Weekly Study Slots (Available Hours) ---")
        self.user.study_slots = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            while True:
                try:
                    hours = float(input(f"Available hours for {day}: ").strip())
                    if hours >= 0 and hours <= 24:  # basic validation
                        self.user.study_slots.append(hours)
                        break
                    else:
                        print("Hours must be between 0 and 24.")
                except ValueError:
                    print("Invalid input. Please enter a number for hours.")
                    
        total_hours = sum(self.user.study_slots)
        print(f"\nTotal available study hours for the week: {total_hours:.1f} hours.")

    def _generate_and_view_plan(self):
        """Generate and display the weekly study plan"""
        print("\n-----------------------------------------------------")
        print("              GENERATING WEEKLY STUDY PLAN             ")
        print("-----------------------------------------------------")
        
        plan = StudyPlanner.generate_plan(self.user)
        
        if not plan:
            print("Plan cannot be generated. Ensure you have added subjects and study slots.")
            return
            
      
        daily_plan, allocated_hours_map = self._structure_plan_by_day(plan)
        
        total_allocated_hours = sum(allocated_hours_map.values())
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
      
        print("\n--- Weekly Schedule Details ---")
        for i, day in enumerate(days):
            available_hours = self.user.study_slots[i] if i < len(self.user.study_slots) else 0
            tasks = daily_plan.get(day, [])
            
            print(f"\n--- {day} (Available: {available_hours:.1f} hrs) ---")
            if not tasks:
                print("   No tasks allocated.")
                continue

            current_day_hours = 0.0
            for task in tasks:
                print(f"   - {task}")
                current_day_hours += task.hours_allocated
                
            print(f"   (Total allocated for {day}: {current_day_hours:.2f} hrs)")

        print("\n-----------------------------------------------------")
        print(f"TOTAL ALLOCATED HOURS THIS WEEK: {total_allocated_hours:.2f} hrs")
        print("-----------------------------------------------------")
        
 
        self._display_analytics_report(allocated_hours_map)

    def _structure_plan_by_day(self, plan: list) -> tuple[dict, dict]:
        """
        Distribute tasks across the week
        This was tricky to get right - had to fix the consecutive hours bug
        """
        daily_plan = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        allocated_hours_map = {s.name: 0.0 for s in self.user.subjects}
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
       
        task_queue = []
        for task in plan:
            task_queue.append({
                'subject': task.subject_name,
                'topic': task.topic,
                'remaining_hours': task.hours_allocated
            })
        
      
        for day_index, day in enumerate(days):
            if day_index >= len(self.user.study_slots):
                break
            
            available_hours = self.user.study_slots[day_index]
            if available_hours <= 0:
                continue
            
            hours_used = 0.0
            last_subject = None
            consecutive_hours = 0.0
            day_tasks = []
            
            task_index = 0
            while hours_used < available_hours and task_index < len(task_queue):
                current_task_data = task_queue[task_index]
                
                
                if current_task_data['remaining_hours'] <= 0.001:
                    task_index += 1
                    continue
                
             
                if current_task_data['subject'] == last_subject:
                    if consecutive_hours >= StudyPlanner.MAX_CONSECUTIVE_HOURS:
                       
                        found_different = False
                        for alt_index in range(task_index + 1, len(task_queue)):
                            if (task_queue[alt_index]['remaining_hours'] > 0.001 and 
                                task_queue[alt_index]['subject'] != last_subject):
                                task_index = alt_index
                                current_task_data = task_queue[task_index]
                                found_different = True
                                break
                        
                        if not found_different:
                            break
                else:
                    consecutive_hours = 0.0
                
         
                max_by_task = current_task_data['remaining_hours']
                max_by_day = available_hours - hours_used
                max_by_consecutive = StudyPlanner.MAX_CONSECUTIVE_HOURS - consecutive_hours
                
                time_to_allocate = min(max_by_task, max_by_day, max_by_consecutive)
                
                if time_to_allocate < 0.001:
                    task_index += 1
                    continue
                
              
                from models import Task
                new_task = Task(
                    current_task_data['subject'],
                    current_task_data['topic'],
                    time_to_allocate
                )
                
                day_tasks.append(new_task)
                hours_used += time_to_allocate
                consecutive_hours += time_to_allocate
                allocated_hours_map[current_task_data['subject']] += time_to_allocate
                
                current_task_data['remaining_hours'] -= time_to_allocate
                
                last_subject = current_task_data['subject']
                
                if current_task_data['remaining_hours'] < 0.001:
                    task_index += 1
            
            daily_plan[day] = day_tasks
        
        return daily_plan, allocated_hours_map
    
    def _display_analytics_report(self, allocated_hours_map: dict):
        """Display target vs allocated analysis"""
        print("\n=====================================================")
        print("          ANALYTICAL REPORT: TARGET VS. ALLOCATED      ")
        print("=====================================================")
        
        if not self.user.subjects:
            print("No subjects to analyze.")
            return
        
        print(f"{'Subject':<20}{'Target Hrs':<12}{'Allocated Hrs':<15}{'Status':<20}")
        print("-" * 67)

        for subject in self.user.subjects:
            name = subject.name
            target = subject.target_hours
            allocated = allocated_hours_map.get(name, 0.0)
            
            status = ""
            if target > 0:
                if allocated >= target:
                    surplus = allocated - target
                    status = f"✓ MET (+{surplus:.1f}h)"
                else:
                    deficit = target - allocated
                    status = f"✗ DEFICIT (-{deficit:.1f}h)"
            else:
                if allocated > 0:
                    status = "Allocated"
                else:
                    status = "Not Scheduled"

            print(f"{name:<20}{target:<12.1f}{allocated:<15.2f}{status:<20}")
        
  
        total_target = sum(s.target_hours for s in self.user.subjects)
        total_allocated = sum(allocated_hours_map.values())
        
        print("-" * 67)
        print(f"{'TOTAL':<20}{total_target:<12.1f}{total_allocated:<15.2f}")
        
        if total_target > 0:
            completion_rate = (total_allocated / total_target) * 100
            print(f"\nOverall Progress: {completion_rate:.1f}% of target hours")
        
        print("=====================================================\n")


if __name__ == "__main__":
    app = CLI()
    app.run()
    