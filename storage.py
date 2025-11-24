

import json
import os
from models import User
from config import DATA_FILE

class StorageManager:
    """Handles loading and saving the User object to a JSON file (data persistence)."""
    
    @staticmethod
    def load_user(user_id: str) -> User:
        """Loads user data from the JSON file. Creates a new user if file not found."""
        
        if not user_id or not user_id.strip():
            print("Invalid user ID. Creating default user.")
            return User("default_user")
        
        try:
           
            if not os.path.exists(DATA_FILE):
                print(f"--- Data file '{DATA_FILE}' not found. Creating new user. ---")
                return User(user_id)
            
           
            if os.path.getsize(DATA_FILE) == 0:
                print(f"--- Data file '{DATA_FILE}' is empty. Creating new user. ---")
                return User(user_id)
            
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                
              
                if not isinstance(data, dict):
                    print("--- Invalid data format. Creating new user. ---")
                    return User(user_id)
                
                # We assume only one user for this simple CLI project, but structure for multi-user
                if user_id in data:
                    print(f"--- Data loaded successfully for User: {user_id} ---")
                    return User.from_dict(data[user_id])
                else:
                    print(f"--- No data found for User: {user_id}. Creating new user. ---")
                    return User(user_id)
                    
        except FileNotFoundError:
            print(f"--- Data file '{DATA_FILE}' not found. Creating new user and file. ---")
            return User(user_id)
        except json.JSONDecodeError as e:
            print(f"--- Error decoding data file: {e}. Starting with a fresh user. ---")
            # FIX: Backup corrupted file
            try:
                backup_file = DATA_FILE + ".backup"
                if os.path.exists(DATA_FILE):
                    os.rename(DATA_FILE, backup_file)
                    print(f"--- Corrupted file backed up to {backup_file} ---")
            except Exception:
                pass
            return User(user_id)
        except Exception as e:
            print(f"An unexpected error occurred during loading: {e}. Starting fresh.")
            return User(user_id)

    @staticmethod
    def save_user(user: User):
        """Saves the current User object data to the JSON file."""
        try:
            # FIX: Validate user object before saving
            if not user or not hasattr(user, 'user_id'):
                print("Error: Invalid user object. Cannot save.")
                return False
            
            # Load existing data first to prevent overwriting other users (if structure expands)
            existing_data = {}
            try:
                if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
                    with open(DATA_FILE, 'r') as f:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, dict):
                            existing_data = {}
            except (FileNotFoundError, json.JSONDecodeError):
                pass # If file doesn't exist or is empty, start fresh.
            
            # Update with current user data
            existing_data[user.user_id] = user.to_dict()
            
            # FIX: Write to temporary file first, then rename (atomic operation)
            temp_file = DATA_FILE + ".tmp"
            try:
                with open(temp_file, 'w') as f:
                    json.dump(existing_data, f, indent=4)
                
                # Replace original file with temp file
                if os.path.exists(DATA_FILE):
                    os.replace(temp_file, DATA_FILE)
                else:
                    os.rename(temp_file, DATA_FILE)
                    
                print("--- Data saved successfully. ---")
                return True
            except Exception as e:
                # Clean up temp file if it exists
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                raise e
                
        except PermissionError:
            print(f"Error: Permission denied when saving to {DATA_FILE}")
            return False
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
          