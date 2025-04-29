"""
History manager for the Video QnA
Saves and retrieves question history for each transcript
"""

import os
import sys
import json
import datetime

# Add the project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class HistoryManager:
    """Manages the history of questions and answers for transcripts"""
    
    def __init__(self, history_dir=None):
        """
        Initialize the history manager.
        
        Args:
            history_dir (str, optional): Directory to store history files
        """
        self.history_dir = history_dir or os.path.join(config.DATA_DIR, "history")
        os.makedirs(self.history_dir, exist_ok=True)
    
    def add_to_history(self, transcript_path, question, answer):
        """
        Add a question and answer to the history.
        
        Args:
            transcript_path (str): Path to the transcript file
            question (str): The question asked
            answer (str): The answer received
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get transcript ID (filename without extension)
            transcript_id = os.path.splitext(os.path.basename(transcript_path))[0]
            
            # Create history file path
            history_path = os.path.join(self.history_dir, f"{transcript_id}_history.json")
            
            # Load existing history or create new
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = {
                    "transcript_id": transcript_id,
                    "transcript_path": transcript_path,
                    "entries": []
                }
            
            # Add new entry
            entry = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "question": question,
                "answer": answer
            }
            
            history["entries"].append(entry)
            
            # Save updated history
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error adding to history: {str(e)}")
            return False
    
    def get_history(self, transcript_path):
        """
        Get the history for a transcript.
        
        Args:
            transcript_path (str): Path to the transcript file
            
        Returns:
            list: List of history entries (or empty list if none found)
        """
        try:
            # Get transcript ID (filename without extension)
            transcript_id = os.path.splitext(os.path.basename(transcript_path))[0]
            
            # Create history file path
            history_path = os.path.join(self.history_dir, f"{transcript_id}_history.json")
            
            # Load history if it exists
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return history.get("entries", [])
            else:
                return []
                
        except Exception as e:
            print(f"Error getting history: {str(e)}")
            return []
    
    def search_history(self, transcript_path, search_term):
        """
        Search history for entries containing the search term.
        
        Args:
            transcript_path (str): Path to the transcript file
            search_term (str): Term to search for
            
        Returns:
            list: List of matching history entries
        """
        entries = self.get_history(transcript_path)
        search_term = search_term.lower()
        
        # Filter entries containing the search term
        matching_entries = [
            entry for entry in entries
            if search_term in entry.get("question", "").lower() or 
               search_term in entry.get("answer", "").lower()
        ]
        
        return matching_entries
    
    def clear_history(self, transcript_path):
        """
        Clear the history for a transcript.
        
        Args:
            transcript_path (str): Path to the transcript file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get transcript ID (filename without extension)
            transcript_id = os.path.splitext(os.path.basename(transcript_path))[0]
            
            # Create history file path
            history_path = os.path.join(self.history_dir, f"{transcript_id}_history.json")
            
            # Remove history file if it exists
            if os.path.exists(history_path):
                os.remove(history_path)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error clearing history: {str(e)}")
            return False

