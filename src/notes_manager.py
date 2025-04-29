"""
Notes manager for the Video QnA
Saves and retrieves user notes for each transcript
"""

import os
import sys
import json
import datetime

# Add the project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils.timestamp_utils import format_seconds_to_timestamp

class NotesManager:
    """Manages user notes for transcripts"""
    
    def __init__(self, notes_dir=None):
        """
        Initialize the notes manager.
        
        Args:
            notes_dir (str, optional): Directory to store notes files
        """
        self.notes_dir = notes_dir or os.path.join(config.DATA_DIR, "notes")
        os.makedirs(self.notes_dir, exist_ok=True)
    
    def add_note(self, transcript_path, note_text, timestamp_seconds=None, tags=None):
        """
        Add a note to a transcript.
        
        Args:
            transcript_path (str): Path to the transcript file
            note_text (str): The note content
            timestamp_seconds (float, optional): Timestamp in seconds
            tags (list, optional): List of tags for the note
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get transcript ID (filename without extension)
            transcript_id = os.path.splitext(os.path.basename(transcript_path))[0]
            
            # Create notes file path
            notes_path = os.path.join(self.notes_dir, f"{transcript_id}_notes.json")
            
            # Load existing notes or create new
            if os.path.exists(notes_path):
                with open(notes_path, 'r', encoding='utf-8') as f:
                    notes_data = json.load(f)
            else:
                notes_data = {
                    "transcript_id": transcript_id,
                    "transcript_path": transcript_path,
                    "notes": []
                }
            
            # Format timestamp if provided
            timestamp_str = None
            if timestamp_seconds is not None:
                timestamp_str = format_seconds_to_timestamp(timestamp_seconds)
            
            # Add new note
            note = {
                "id": len(notes_data["notes"]) + 1,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "text": note_text,
                "timestamp_seconds": timestamp_seconds,
                "timestamp_str": timestamp_str,
                "tags": tags or []
            }
            
            notes_data["notes"].append(note)
            
            # Save updated notes
            with open(notes_path, 'w', encoding='utf-8') as f:
                json.dump(notes_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error adding note: {str(e)}")
            return False
    
    def get_notes(self, transcript_path):
        """
        Get all notes for a transcript.
        
        Args:
            transcript_path (str): Path to the transcript file
            
        Returns:
            list: List of notes (or empty list if none found)
        """
        try:
            # Get transcript ID (filename without extension)
            transcript_id = os.path.splitext(os.path.basename(transcript_path))[0]
            
            # Create notes file path
            notes_path = os.path.join(self.notes_dir, f"{transcript_id}_notes.json")
            
            # Load notes if they exist
            if os.path.exists(notes_path):
                with open(notes_path, 'r', encoding='utf-8') as f:
                    notes_data = json.load(f)
                return notes_data.get("notes", [])
            else:
                return []
                
        except Exception as e:
            print(f"Error getting notes: {str(e)}")
            return []
    
    def search_notes(self, transcript_path, search_term=None, tag=None):
        """
        Search notes by text content or tag.
        
        Args:
            transcript_path (str): Path to the transcript file
            search_term (str, optional): Term to search for in note text
            tag (str, optional): Tag to search for
            
        Returns:
            list: List of matching notes
        """
        notes = self.get_notes(transcript_path)
        
        # Filter notes
        if search_term and tag:
            # Match both search term and tag
            search_term = search_term.lower()
            tag = tag.lower()
            return [
                note for note in notes
                if search_term in note.get("text", "").lower() and
                tag in [t.lower() for t in note.get("tags", [])]
            ]
        elif search_term:
            # Match search term only
            search_term = search_term.lower()
            return [
                note for note in notes
                if search_term in note.get("text", "").lower()
            ]
        elif tag:
            # Match tag only
            tag = tag.lower()
            return [
                note for note in notes
                if tag in [t.lower() for t in note.get("tags", [])]
            ]
        else:
            # No filters, return all notes
            return notes
    
    def update_note(self, transcript_path, note_id, note_text=None, tags=None):
        """
        Update an existing note.
        
        Args:
            transcript_path (str): Path to the transcript file
            note_id (int): ID of the note to update
            note_text (str, optional): New note text
            tags (list, optional): New tags
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get transcript ID (filename without extension)
            transcript_id = os.path.splitext(os.path.basename(transcript_path))[0]
            
            # Create notes file path
            notes_path = os.path.join(self.notes_dir, f"{transcript_id}_notes.json")
            
            # Check if notes file exists
            if not os.path.exists(notes_path):
                return False
            
            # Load notes
            with open(notes_path, 'r', encoding='utf-8') as f:
                notes_data = json.load(f)
            
            # Find the note to update
            for note in notes_data["notes"]:
                if note["id"] == note_id:
                    # Update note text if provided
                    if note_text is not None:
                        note["text"] = note_text
                    
                    # Update tags if provided
                    if tags is not None:
                        note["tags"] = tags
                    
                    # Update timestamp
                    note["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Save updated notes
                    with open(notes_path, 'w', encoding='utf-8') as f:
                        json.dump(notes_data, f, indent=2)
                    
                    return True
            
            # Note not found
            return False
                
        except Exception as e:
            print(f"Error updating note: {str(e)}")
            return False
    
    def delete_note(self, transcript_path, note_id):
        """
        Delete a note.
        
        Args:
            transcript_path (str): Path to the transcript file
            note_id (int): ID of the note to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get transcript ID (filename without extension)
            transcript_id = os.path.splitext(os.path.basename(transcript_path))[0]
            
            # Create notes file path
            notes_path = os.path.join(self.notes_dir, f"{transcript_id}_notes.json")
            
            # Check if notes file exists
            if not os.path.exists(notes_path):
                return False
            
            # Load notes
            with open(notes_path, 'r', encoding='utf-8') as f:
                notes_data = json.load(f)
            
            # Find the note to delete
            for i, note in enumerate(notes_data["notes"]):
                if note["id"] == note_id:
                    # Remove the note
                    notes_data["notes"].pop(i)
                    
                    # Save updated notes
                    with open(notes_path, 'w', encoding='utf-8') as f:
                        json.dump(notes_data, f, indent=2)
                    
                    return True
            
            # Note not found
            return False
                
        except Exception as e:
            print(f"Error deleting note: {str(e)}")
            return False

