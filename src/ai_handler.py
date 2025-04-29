"""
AI handler for VideoQnA
Manages interactions with the Ollama API for answering questions about video transcripts
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime

# Add the project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils.timestamp_utils import extract_time_range, find_segments_in_time_range, extract_text_from_segments

class AIHandler:
    """Handles AI interactions for answering questions about video transcripts"""
    
    def __init__(self, model_name=None):
        """
        Initialize the AI handler.
        
        Args:
            model_name (str, optional): Name of the Ollama model to use
        """
        # Use mistral:7b as the default model
        self.model_name = model_name or "mistral:7b"
        self.api_base = "http://localhost:11434/api"
        self.using_gpu = False
        
        # Check GPU availability
        try:
            nvidia_output = subprocess.check_output(['nvidia-smi']).decode('utf-8')
            print("NVIDIA GPU detected. Using GPU acceleration.")
            self.using_gpu = True
        except:
            print("No NVIDIA GPU detected or drivers not installed. Using CPU.")
        
        # Check if Ollama is running
        try:
            response = requests.get(f"{self.api_base}/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                
                if self.model_name not in available_models:
                    print(f"Model {self.model_name} not found. Available models: {', '.join(available_models)}")
                    print(f"Please run: ollama pull {self.model_name}")
                else:
                    print(f"Connected to Ollama. Using model: {self.model_name}")
                    if self.using_gpu:
                        print("GPU acceleration is enabled.")
            else:
                print("Could not connect to Ollama API")
        except requests.exceptions.ConnectionError:
            print("Ollama API not running. Please start Ollama.")
    
    def process_any_request(self, user_request, transcript_data):
        """
        Process any type of request about the video transcript.
        
        Args:
            user_request (str): The user's request in natural language
            transcript_data (dict): The transcript data
            
        Returns:
            str: The AI's response
        """
        # Extract time range if present
        start_time, end_time = extract_time_range(user_request)
        
        # Prepare context from transcript
        context = self._prepare_context(transcript_data, start_time, end_time)
        
        # Create a flexible system prompt
        system_prompt = self._create_flexible_system_prompt(transcript_data)
        
        # Prepare the message for the AI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context from video transcript:\n\n{context}\n\nUser request: {user_request}"}
        ]
        
        # Prepare options based on GPU availability
        options = {}
        if self.using_gpu:
            options = {
                "num_gpu": 1,  # Use 1 GPU
                "num_thread": 4  # Use 4 CPU threads for additional processing
            }
        
        # Make API request to Ollama
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False
            }
            
            # Add options if we have any
            if options:
                payload["options"] = options
                
            response = requests.post(
                f"{self.api_base}/chat",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "No response from AI")
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama API. Please make sure Ollama is running."
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _prepare_context(self, transcript_data, start_time=None, end_time=None):
        """
        Prepare context from the video transcript based on time range.
        
        Args:
            transcript_data (dict): The transcript data
            start_time (float, optional): Start time in seconds
            end_time (float, optional): End time in seconds
            
        Returns:
            str: The context text
        """
        # If no time range specified, use the full transcript
        if start_time is None or end_time is None:
            context = transcript_data.get("transcript", "")
            
            # Limit context size for performance if needed
            if len(context) > 12000:  # 12k character limit for better performance
                context = context[:12000] + "...[truncated for performance]"
            
            return context
        
        # Find segments in the specified time range
        segments = find_segments_in_time_range(transcript_data, start_time, end_time)
        
        # Extract text from segments
        context = extract_text_from_segments(segments)
        
        return context
    
    def _create_flexible_system_prompt(self, transcript_data):
        """
        Create a flexible system prompt that can handle any request.
        
        Args:
            transcript_data (dict): The transcript data
            
        Returns:
            str: The system prompt
        """
        # Extract metadata
        metadata = transcript_data.get("metadata", {})
        title = metadata.get("title", "this video")
        author = metadata.get("author", "the creator")
        
        # Create system prompt
        system_prompt = f"""You are a helpful assistant analyzing a transcript of the video "{title}" by {author}.
Your job is to help the user understand and learn from this content by responding to any request they have.

You can:
- Answer questions about the content
- Summarize parts or all of the video
- Create flashcards (format as "Card 1: Question: ... Answer: ...")
- Explain concepts mentioned in the video
- Create study guides or outlines
- Generate practice questions
- Or handle any other reasonable request

Base your responses only on the transcript information provided. If the transcript doesn't cover something, say so.
Always format your response clearly with appropriate headings, bullet points, or numbering as needed."""

        return system_prompt

