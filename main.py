import os
import sys
import json
from datetime import datetime

# Add the project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
import config
from src.youtube_downloader import download_audio, get_video_info, is_valid_youtube_url
from src.transcriber import AudioTranscriber
from src.transcript_manager import TranscriptManager
from src.ai_handler import AIHandler
from src.history_manager import HistoryManager
from src.notes_manager import NotesManager
from utils.timestamp_utils import extract_time_range, parse_timestamp
from utils.response_formatter import format_response

class VideoQnA:
    """Main application class for VideoQnA"""
    
    def __init__(self):
        """Initialize the application"""
        self.transcript_manager = TranscriptManager()
        self.transcriber = AudioTranscriber()
        self.ai_handler = AIHandler()
        self.history_manager = HistoryManager()
        self.notes_manager = NotesManager()
        
        # Create necessary directories
        os.makedirs(config.AUDIO_DIR, exist_ok=True)
        os.makedirs(config.TRANSCRIPT_DIR, exist_ok=True)
        
        # Track current transcript
        self.current_transcript = None
        self.current_transcript_path = None
    
    def display_welcome(self):
        """Display welcome message and application info"""
        print("\n" + "="*60)
        print("WELCOME TO VIDEOQNA | MAIN MENU")
        print("="*60)

    
    def display_main_menu(self):
        """Display the main menu options"""
        print("1. Add new YouTube video")
        print("2. Select previously uploaded video")
        print("3. View question history")
        print("4. Exit")
        print("\nType 'q' at any time to return to this menu")
        
        choice = input("\nEnter your choice (1-4): ")
        return choice
    
    def add_youtube_video(self):
        """Add a new YouTube video to the system"""
        print("\n" + "="*60)
        print("ADD NEW YOUTUBE VIDEO")
        print("="*60)
        print("Type 'q' to return to main menu")
        
        url = input("\nEnter YouTube URL: ")
        
        if url.lower() == 'q':
            return
        
        if not is_valid_youtube_url(url):
            print("Invalid YouTube URL. Please try again.")
            return
        
        # Get video info
        print("\nRetrieving video information...")
        video_info = get_video_info(url)
        
        if not video_info:
            print("Failed to retrieve video information. Please try again.")
            return
        
        # Only display the title to the user
        print(f"\nVideo Title: {video_info['title']}")
        
        confirm = input("\nDownload and transcribe this video? (y/n): ")
        
        if confirm.lower() == 'q':
            return
            
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
        
        # Download audio
        print("\nDownloading audio (this may take a while)...")
        try:
            audio_path = download_audio(url, config.AUDIO_DIR)
            print(f"Audio downloaded successfully!")
            
            # Transcribe audio
            print("\nTranscribing audio (this may take a while)...")
            transcript_path = self.transcriber.transcribe_audio(audio_path, metadata=video_info)
            
            print(f"\nTranscription complete!")
            print(f"Transcript saved to: {transcript_path}")
            
            # Set as current transcript
            self.load_transcript(transcript_path)
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    def select_transcript(self):
        """Select a transcript to work with"""
        print("\n" + "="*60)
        print("SELECT TRANSCRIPT")
        print("="*60)
        print("Type 'q' to return to main menu")
        
        # Get all transcripts
        transcripts = self.transcript_manager.list_transcripts()
        
        if not transcripts:
            print("\nNo transcripts found. Add a YouTube video first.")
            return
            
        # Display all transcripts
        print(f"\nFound {len(transcripts)} transcripts:\n")
        
        for i, (path, info) in enumerate(transcripts, 1):
            title = info.get("title", "Unknown")
            print(f"{i}. {title}")
        
        # Get selection
        while True:
            selection = input("\nSelect transcript number or press Enter for most recent: ")
            
            if selection.lower() == 'q':
                return
                
            if selection.strip() == "":
                # Use most recent transcript (first in the list)
                selected_path = transcripts[0][0]
                break
            
            try:
                choice = int(selection)
                if 1 <= choice <= len(transcripts):
                    selected_path = transcripts[choice-1][0]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(transcripts)}")
            except ValueError:
                print("Please enter a valid number")
        
        # Load the selected transcript
        self.load_transcript(selected_path)
        
        # Show interface for the loaded transcript
        self.study_transcript()
    
    def study_transcript(self):
        """Interface for studying the loaded transcript"""
        if not self.current_transcript:
            print("No transcript is currently loaded.")
            return
            
        title = self.current_transcript.get("metadata", {}).get("title", "Unknown")
        
        while True:
            print("\n" + "="*60)
            print(f"VIDEO: {title}")
            print("="*60)
            print("Type 'q' to return to main menu")
            print("Type 'back' to select a different video")
            print("\nOptions:")
            print("1. Ask a question")
            print("2. Add a note")
            print("3. View notes")
            print("4. View question history")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice.lower() == 'q':
                return
                
            if choice.lower() == 'back':
                return self.select_transcript()
                
            if choice == '1':
                # Ask a question
                print("\n" + "="*60)
                print("ASK A QUESTION")
                print("="*60)
                
                user_request = input("\nAsk anything about this video? ")
                
                if user_request.lower() == 'q':
                    continue
                    
                if user_request.lower() == 'back':
                    continue
                    
                if not user_request.strip():
                    print("Please enter a valid question or request.")
                    continue
                
                # Process the request using the flexible AI handler
                print("\nThinking about your request (this may take a moment)...")
                response = self.ai_handler.process_any_request(
                    user_request,
                    self.current_transcript
                )
                
                # Save to history
                self.history_manager.add_to_history(
                    self.current_transcript_path,
                    user_request,
                    response
                )
                
                # Display the formatted response
                print("\nResponse:")
                print("-" * 60)
                print(format_response(response))
                print("-" * 60)
                
                input("\nPress Enter to continue...")
                
            elif choice == '2':
                # Add a note
                print("\n" + "="*60)
                print("ADD A NOTE")
                print("="*60)
                
                # Get timestamp
                timestamp_str = input("Enter timestamp (e.g., 5:30) or press Enter for no timestamp: ")
                timestamp_seconds = None
                
                if timestamp_str.strip():
                    try:
                        timestamp_seconds = parse_timestamp(timestamp_str)
                    except:
                        print("Invalid timestamp format. Using no timestamp.")
                
                # Get note text
                note_text = input("\nEnter your note: ")
                
                if not note_text.strip():
                    print("Note cannot be empty.")
                    continue
                
                # Get tags
                tags_str = input("\nEnter tags (comma-separated) or press Enter for no tags: ")
                tags = [tag.strip() for tag in tags_str.split(',')] if tags_str.strip() else []
                
                # Add the note
                success = self.notes_manager.add_note(
                    self.current_transcript_path,
                    note_text,
                    timestamp_seconds,
                    tags
                )
                
                if success:
                    print("\nNote added successfully!")
                else:
                    print("\nFailed to add note.")
                
                input("\nPress Enter to continue...")
                
            elif choice == '3':
                # View notes
                print("\n" + "="*60)
                print("VIEW NOTES")
                print("="*60)
                
                notes = self.notes_manager.get_notes(self.current_transcript_path)
                
                if not notes:
                    print("\nNo notes found for this video.")
                    input("\nPress Enter to continue...")
                    continue
                
                print(f"\nFound {len(notes)} notes:\n")
                
                for note in notes:
                    timestamp = note.get("timestamp_str", "No timestamp")
                    tags = ", ".join(note.get("tags", []))
                    
                    print(f"Note {note['id']} ({timestamp}):")
                    print(f"  {note['text']}")
                    if tags:
                        print(f"  Tags: {tags}")
                    print()
                
                # Options for notes - only search is available
                print("\nOptions:")
                print("1. Search notes")
                print("2. Return to video menu")
                
                note_choice = input("\nEnter your choice (1-2): ")
                
                if note_choice == '1':
                    # Search notes
                    search_type = input("Search by text or tag? (text/tag): ")
                    
                    if search_type.lower() == 'text':
                        search_term = input("Enter search term: ")
                        results = self.notes_manager.search_notes(
                            self.current_transcript_path,
                            search_term=search_term
                        )
                    elif search_type.lower() == 'tag':
                        tag = input("Enter tag to search for: ")
                        results = self.notes_manager.search_notes(
                            self.current_transcript_path,
                            tag=tag
                        )
                    else:
                        print("Invalid search type.")
                        continue
                    
                    if not results:
                        print("\nNo matching notes found.")
                    else:
                        print(f"\nFound {len(results)} matching notes:\n")
                        
                        for note in results:
                            timestamp = note.get("timestamp_str", "No timestamp")
                            tags = ", ".join(note.get("tags", []))
                            
                            print(f"Note {note['id']} ({timestamp}):")
                            print(f"  {note['text']}")
                            if tags:
                                print(f"  Tags: {tags}")
                            print()
                    
                input("\nPress Enter to continue...")
                
            elif choice == '4':
                # View question history
                print("\n" + "="*60)
                print("QUESTION HISTORY")
                print("="*60)
                
                history = self.history_manager.get_history(self.current_transcript_path)
                
                if not history:
                    print("\nNo question history found for this video.")
                    input("\nPress Enter to continue...")
                    continue
                
                print(f"\nFound {len(history)} questions:\n")
                
                for i, entry in enumerate(history, 1):
                    print(f"{i}. {entry['question']}")
                
                # Option to view a specific answer
                entry_num = input("\nEnter question number to view answer (or press Enter to continue): ")
                
                if entry_num.strip():
                    try:
                        entry_num = int(entry_num)
                        if 1 <= entry_num <= len(history):
                            entry = history[entry_num-1]
                            print("\n" + "="*60)
                            print(f"ANSWER TO: {entry['question']}")
                            print("="*60)
                            print(entry['answer'])
                        else:
                            print(f"Please enter a number between 1 and {len(history)}")
                    except ValueError:
                        print("Please enter a valid number")
                
                input("\nPress Enter to continue...")
            
            else:
                print("\nInvalid choice. Please try again.")
    
    def view_history(self):
        """View question history"""
        print("\n" + "="*60)
        print("QUESTION HISTORY")
        print("="*60)
        print("Type 'q' to return to main menu")
        
        # Get all transcripts
        transcripts = self.transcript_manager.list_transcripts()
        
        if not transcripts:
            print("\nNo transcripts found. Add a YouTube video first.")
            input("\nPress Enter to continue...")
            return
            
        # Display all transcripts
        print(f"\nSelect a video to view history:\n")
        
        for i, (path, info) in enumerate(transcripts, 1):
            title = info.get("title", "Unknown")
            print(f"{i}. {title}")
        
        # Get selection
        while True:
            selection = input("\nSelect video number or press Enter for most recent: ")
            
            if selection.lower() == 'q':
                return
                
            if selection.strip() == "":
                # Use most recent transcript (first in the list)
                selected_path = transcripts[0][0]
                break
            
            try:
                choice = int(selection)
                if 1 <= choice <= len(transcripts):
                    selected_path = transcripts[choice-1][0]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(transcripts)}")
            except ValueError:
                print("Please enter a valid number")
        
        # Get history for selected transcript
        history = self.history_manager.get_history(selected_path)
        
        if not history:
            print("\nNo history found for this video.")
            input("\nPress Enter to continue...")
            return
        
        # Display history
        print("\n" + "="*60)
        title = next((info.get("title", "Unknown") for path, info in transcripts if path == selected_path), "Unknown")
        print(f"HISTORY FOR: {title}")
        print("="*60)
        
        for i, entry in enumerate(history, 1):
            print(f"\n--- Question {i} ({entry['timestamp']}) ---")
            print(f"Q: {entry['question']}")
            print(f"A: {entry['answer'][:100]}..." if len(entry['answer']) > 100 else f"A: {entry['answer']}")
        
        # Options for history
        while True:
            print("\nOptions:")
            print("1. View full answer")
            print("2. Search history")
            print("3. Clear history")
            print("4. Return to main menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                entry_num = input("Enter question number to view: ")
                try:
                    entry_num = int(entry_num)
                    if 1 <= entry_num <= len(history):
                        entry = history[entry_num-1]
                        print("\n" + "="*60)
                        print(f"FULL ANSWER TO: {entry['question']}")
                        print("="*60)
                        print(entry['answer'])
                        input("\nPress Enter to continue...")
                    else:
                        print(f"Please enter a number between 1 and {len(history)}")
                except ValueError:
                    print("Please enter a valid number")
            elif choice == '2':
                search_term = input("Enter search term: ")
                results = self.history_manager.search_history(selected_path, search_term)
                
                if not results:
                    print(f"\nNo results found for '{search_term}'")
                else:
                    print(f"\nFound {len(results)} results:")
                    for i, entry in enumerate(results, 1):
                        print(f"{i}. Q: {entry['question']}")
                    
                    # Option to view a result
                    result_num = input("\nEnter result number to view or press Enter to continue: ")
                    if result_num.strip():
                        try:
                            result_num = int(result_num)
                            if 1 <= result_num <= len(results):
                                entry = results[result_num-1]
                                print("\n" + "="*60)
                                print(f"FULL ANSWER TO: {entry['question']}")
                                print("="*60)
                                print(entry['answer'])
                                input("\nPress Enter to continue...")
                            else:
                                print(f"Please enter a number between 1 and {len(results)}")
                        except ValueError:
                            print("Please enter a valid number")
            elif choice == '3':
                confirm = input("Are you sure you want to clear history? (y/n): ")
                if confirm.lower() == 'y':
                    self.history_manager.clear_history(selected_path)
                    print("\nHistory cleared.")
                    break
            elif choice == '4' or choice.lower() == 'q':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def load_transcript(self, transcript_path):
        """Load a transcript file"""
        try:
            self.current_transcript = self.transcript_manager.load_transcript(transcript_path)
            self.current_transcript_path = transcript_path
            
            # Display basic info about the loaded transcript
            title = self.current_transcript.get("metadata", {}).get("title", "Unknown")
            segments = len(self.current_transcript.get("segments", []))
            
            print(f"\nLoaded video: {title}")
            print(f"Contains {segments} segments")
            print(f"Ready for your questions!")
            
        except Exception as e:
            print(f"Error loading transcript: {str(e)}")
            self.current_transcript = None
            self.current_transcript_path = None
    
    def run(self):
        """Run the main application loop"""
        # Display welcome message only once
        self.display_welcome()
        
        while True:
            choice = self.display_main_menu()
            
            if choice.lower() == 'q':
                continue
                
            if choice == '1':
                self.add_youtube_video()
            elif choice == '2':
                self.select_transcript()
            elif choice == '3':
                self.view_history()
            elif choice == '4':
                print("\nGoodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")

def main():
    """Main entry point for the application"""
    app = VideoQnA()
    app.run()

if __name__ == "__main__":
    main()