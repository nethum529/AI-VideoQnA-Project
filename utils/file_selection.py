"""
File selection utilities for the Video QnA
Provides functions to manage and select transcript files
"""

import os
import json
from datetime import datetime

def get_recent_files(directory, extension=".json", count=5):
    """
    Get the most recent files in a directory.
    
    Args:
        directory (str): Directory to search
        extension (str): File extension to filter by
        count (int): Maximum number of files to return
        
    Returns:
        list: List of file paths, sorted by modification time (newest first)
    """
    if not os.path.exists(directory):
        return []
    
    # Get all files with the specified extension
    files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.endswith(extension)
    ]
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Return at most 'count' files
    return files[:count]

def format_file_info(file_path):
    """
    Format file information for display.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict: Formatted file information
    """
    # Default info
    info = {
        "title": os.path.basename(file_path),
        "created": datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M"),
        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M"),
        "size_mb": os.path.getsize(file_path) / (1024 * 1024)
    }
    
    # Try to extract more info from JSON files
    if file_path.endswith(".json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                metadata = data.get("metadata", {})
                
                if "title" in metadata:
                    info["title"] = metadata["title"]
                if "created_at" in metadata:
                    info["created"] = metadata["created_at"]
                if "length_seconds" in metadata:
                    length = metadata["length_seconds"]
                    info["duration"] = f"{int(length/60)}m {int(length%60)}s"
        except:
            # If there's any error reading the JSON, just use the default info
            pass
    
    return info

def select_file_interactive(directory, extension=".json", prompt="Select a file"):
    """
    Interactive file selection.
    
    Args:
        directory (str): Directory to search
        extension (str): File extension to filter by
        prompt (str): Prompt to display
        
    Returns:
        str: Selected file path or None if cancelled
    """
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return None
    
    # Get all files with the specified extension
    files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.endswith(extension)
    ]
    
    if not files:
        print(f"No {extension} files found in {directory}")
        return None
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Display files
    print(f"\n{prompt} (most recent first):")
    print("Type 'q' to return to main menu")
    
    for i, file_path in enumerate(files, 1):
        info = format_file_info(file_path)
        print(f"{i}. {info['title']}")
        if "duration" in info:
            print(f"   Duration: {info['duration']}")
    
    # Get user selection
    while True:
        choice = input(f"\nEnter file number or press Enter for most recent: ")
        
        if choice.lower() == 'q':
            return None
        
        if choice.strip() == "":
            # Default to most recent
            return files[0]
        
        try:
            choice = int(choice)
            if 1 <= choice <= len(files):
                return files[choice-1]
            else:
                print(f"Please enter a number between 1 and {len(files)}")
        except ValueError:
            print("Please enter a valid number")
            
if __name__ == "__main__":
    # Test the module
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = input("Enter directory path: ")
    
    selected = select_file_interactive(directory)
    
    if selected:
        print(f"\nSelected: {selected}")
        print(f"Info: {format_file_info(selected)}")