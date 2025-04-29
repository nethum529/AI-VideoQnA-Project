"""
Transcript manager for the Video QnA
Manages transcript files and provides access to transcript data
"""

import os
import sys
import json
import uuid

# Add the project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class TranscriptManager:
    """Manages transcript files and provides access to transcript data"""
    
    def __init__(self, transcript_dir=None):
        """
        Initialize the transcript manager.
        
        Args:
            transcript_dir (str, optional): Directory to store transcript files
        """
        self.transcript_dir = transcript_dir or config.TRANSCRIPT_DIR
        os.makedirs(self.transcript_dir, exist_ok=True)
    
    def save_transcript(self, transcript_data, audio_path=None):
        """
        Save transcript data to a file.
        
        Args:
            transcript_data (dict): Transcript data
            audio_path (str, optional): Path to the audio file
            
        Returns:
            str: Path to the saved transcript file
        """
        # Extract metadata
        metadata = transcript_data.get("metadata", {})
        title = metadata.get("title", "Unknown")
        
        # Create a filename based on the title
        safe_title = "".join([c if c.isalnum() or c in " _-" else "_" for c in title])
        filename = f"{safe_title}_{uuid.uuid4().hex[:8]}.json"
        path = os.path.join(self.transcript_dir, filename)
        
        # Save the transcript
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2)
        
        return path
    
    def load_transcript(self, path):
        """
        Load a transcript from a file.
        
        Args:
            path (str): Path to the transcript file
            
        Returns:
            dict: Transcript data
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)
            
            # Make sure metadata exists
            if "metadata" not in transcript_data:
                transcript_data["metadata"] = {}
            
            # If title is missing, use filename
            if "title" not in transcript_data["metadata"]:
                filename = os.path.basename(path)
                transcript_data["metadata"]["title"] = os.path.splitext(filename)[0]
            
            return transcript_data
        except Exception as e:
            print(f"Error loading transcript: {str(e)}")
            return None
    
    def list_transcripts(self):
        """
        List all available transcripts.
        
        Returns:
            list: List of (path, info) tuples
        """
        transcripts = []
        
        for filename in os.listdir(self.transcript_dir):
            if filename.endswith(".json"):
                path = os.path.join(self.transcript_dir, filename)
                
                try:
                    # Load basic info without loading entire transcript
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract metadata
                    metadata = data.get("metadata", {})
                    title = metadata.get("title", os.path.splitext(filename)[0])
                    
                    # Create info dictionary with just the title
                    info = {
                        "title": title
                    }
                    
                    transcripts.append((path, info))
                except:
                    # If there's an error loading, just use the filename
                    info = {
                        "title": os.path.splitext(filename)[0]
                    }
                    transcripts.append((path, info))
        
        # Sort by modification time (newest first)
        transcripts.sort(key=lambda x: os.path.getmtime(x[0]), reverse=True)
        
        return transcripts
    
    def get_transcript_text(self, transcript_data):
        """
        Get the full text of a transcript.
        
        Args:
            transcript_data (dict): Transcript data
            
        Returns:
            str: Full transcript text
        """
        if "transcript" in transcript_data:
            return transcript_data["transcript"]
        
        # If pre-computed transcript is not available, build it from segments
        segments = transcript_data.get("segments", [])
        if not segments:
            return ""
        
        transcript_text = ""
        for segment in segments:
            text = segment.get("text", "").strip()
            if text:
                transcript_text += text + " "
        
        return transcript_text.strip()
    
    def display_transcript_info(self, transcript_data):
        """
        Display information about a transcript.
        
        Args:
            transcript_data (dict): Transcript data
        """
        metadata = transcript_data.get("metadata", {})
        title = metadata.get("title", "Unknown")
        segments = len(transcript_data.get("segments", []))
        
        print(f"Title: {title}")
        print(f"Segments: {segments}")

