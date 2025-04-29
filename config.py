"""
Configuration file for VideoQnA
"""

import os

# Base directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")

# Data directories
AUDIO_DIR = os.path.join(DATA_DIR, "audio")
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")

# Transcription settings
DEFAULT_TRANSCRIPT_MODEL = "base"  # Options: tiny, base, small, medium, large
DEFAULT_LANGUAGE = "en"  # Default language code (English)

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)