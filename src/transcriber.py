import os
import sys
import json
import torch
import whisper
import numpy as np
from datetime import timedelta
from tqdm import tqdm

# Add the project root to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class AudioTranscriber:
    """Class to handle audio transcription with timestamps using Whisper"""
    
    def __init__(self, model_name=config.DEFAULT_TRANSCRIPT_MODEL, language=config.DEFAULT_LANGUAGE):
        """
        Initialize the transcriber with the specified model.
        
        Args:
            model_name (str): Name of the Whisper model to use
                              (tiny, base, small, medium, large)
            language (str): Language code for transcription
        """
        self.model_name = model_name
        self.language = language
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Transcriber will use device: {self.device}")
    
    def load_model(self):
        """Load the Whisper model into memory"""
        if self.model is None:
            print(f"Loading Whisper {self.model_name} model...")
            try:
                self.model = whisper.load_model(self.model_name, device=self.device)
                print(f"Model loaded successfully")
            except Exception as e:
                print(f"Error loading model: {str(e)}")
                raise
    
    def transcribe_audio(self, audio_path, output_path=None, metadata=None):
        """
        Transcribe an audio file and save the result with timestamps.
        
        Args:
            audio_path (str): Path to the audio file
            output_path (str, optional): Path to save the transcript
            metadata (dict, optional): Additional metadata to include
            
        Returns:
            str: Path to the saved transcript file
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load the model if not already loaded
        self.load_model()
        
        print(f"Transcribing audio file: {audio_path}")
        
        try:
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_path,
                language=self.language,
                verbose=True,
                word_timestamps=True  # Enable word-level timestamps
            )
            
            # Process the transcription result
            transcript_data = self._process_transcript(result, metadata)
            
            # Save the transcript
            if output_path is None:
                # Create output path based on input filename
                base_name = os.path.splitext(os.path.basename(audio_path))[0]
                output_path = os.path.join(config.TRANSCRIPT_DIR, f"{base_name}_transcript.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)
            
            print(f"Transcript saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            raise
    
    def _process_transcript(self, result, metadata=None):
        """
        Process the Whisper transcription result into a structured format with timestamps.
        
        Args:
            result: Whisper transcription result
            metadata (dict, optional): Additional metadata to include
            
        Returns:
            dict: Structured transcript data with segments and timestamps
        """
        # Initialize transcript data structure
        transcript_data = {
            "metadata": metadata or {},
            "transcript": result.get("text", ""),
            "segments": [],
            "words": []
        }
        
        # Add model information to metadata
        transcript_data["metadata"]["transcription"] = {
            "model": self.model_name,
            "language": self.language,
            "device": self.device
        }
        
        # Process segments (sentence/paragraph level)
        for segment in result.get("segments", []):
            formatted_segment = {
                "id": segment.get("id"),
                "start": segment.get("start"),
                "end": segment.get("end"),
                "text": segment.get("text"),
                "start_formatted": self._format_timestamp(segment.get("start")),
                "end_formatted": self._format_timestamp(segment.get("end"))
            }
            transcript_data["segments"].append(formatted_segment)
        
        # Process words if available (word level timestamps)
        if "words" in result:
            for word_data in result["words"]:
                formatted_word = {
                    "word": word_data.get("word"),
                    "start": word_data.get("start"),
                    "end": word_data.get("end"),
                    "start_formatted": self._format_timestamp(word_data.get("start")),
                    "end_formatted": self._format_timestamp(word_data.get("end"))
                }
                transcript_data["words"].append(formatted_word)
        
        return transcript_data
    
    def _format_timestamp(self, seconds):
        """
        Format seconds into HH:MM:SS format.
        
        Args:
            seconds (float): Time in seconds
            
        Returns:
            str: Formatted time string
        """
        if seconds is None:
            return "00:00:00"
        
        # Convert to timedelta and format
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Include milliseconds
        milliseconds = int(td.microseconds / 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
