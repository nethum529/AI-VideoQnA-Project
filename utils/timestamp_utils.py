import re
import json
from datetime import datetime, timedelta

def parse_timestamp(timestamp_str):
    """
    Parse a timestamp string in HH:MM:SS or MM:SS format to seconds.
    
    Args:
        timestamp_str (str): Timestamp string
        
    Returns:
        float: Time in seconds
    """
    # Handle different formats
    if timestamp_str.count(':') == 2:  # HH:MM:SS
        h, m, s = timestamp_str.split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif timestamp_str.count(':') == 1:  # MM:SS
        m, s = timestamp_str.split(':')
        return int(m) * 60 + float(s)
    else:
        try:
            return float(timestamp_str)  # Just seconds
        except ValueError:
            return 0.0

def format_seconds_to_timestamp(seconds, include_ms=True):
    """
    Format seconds to HH:MM:SS[.mmm] format.
    
    Args:
        seconds (float): Time in seconds
        include_ms (bool): Whether to include milliseconds
        
    Returns:
        str: Formatted timestamp
    """
    if seconds is None:
        return "00:00:00"
    
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if include_ms:
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d}.{milliseconds:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d}"

def extract_time_range(query):
    """
    Extract time range from a query string.
    
    Args:
        query (str): Query containing time references
        
    Returns:
        tuple: (start_time, end_time) in seconds, or (None, None) if not found
    """
    # Look for patterns like "from 5:30 to 10:45" or "between 1:20:15 and 1:45:30"
    time_range_patterns = [
        r'from\s+(\d+:?\d*:?\d*)\s+to\s+(\d+:?\d*:?\d*)',
        r'between\s+(\d+:?\d*:?\d*)\s+and\s+(\d+:?\d*:?\d*)',
        r'(\d+:?\d*:?\d*)\s*-\s*(\d+:?\d*:?\d*)',
    ]
    
    for pattern in time_range_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            start_str, end_str = match.groups()
            start_time = parse_timestamp(start_str)
            end_time = parse_timestamp(end_str)
            return start_time, end_time
    
    # Look for patterns like "at 5 minute mark" or "at 5:30"
    single_time_pattern = r'at\s+(?:the\s+)?(\d+:?\d*:?\d*)(?:\s+minute)?\s+mark'
    match = re.search(single_time_pattern, query, re.IGNORECASE)
    if match:
        time_str = match.group(1)
        time_point = parse_timestamp(time_str)
        # Create a small window around the time point
        return time_point - 30, time_point + 30
    
    # Look for patterns like "first 5 minutes" or "last 10 minutes"
    first_last_pattern = r'(first|last)\s+(\d+)\s+minutes'
    match = re.search(first_last_pattern, query, re.IGNORECASE)
    if match:
        position, duration = match.groups()
        duration_seconds = int(duration) * 60
        
        if position.lower() == 'first':
            return 0, duration_seconds
        else:
            # For "last X minutes", we'll need the total duration, which we don't have here
            # This will be handled by the calling function
            return -duration_seconds, None
    
    return None, None

def find_segments_in_time_range(transcript_data, start_time, end_time):
    """
    Find transcript segments within a specific time range.
    
    Args:
        transcript_data (dict): Transcript data
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        
    Returns:
        list: List of segments within the range
    """
    matching_segments = []
    
    for segment in transcript_data.get("segments", []):
        seg_start = segment.get("start", 0)
        seg_end = segment.get("end", 0)
        
        # Check if segment overlaps with the specified range
        if (seg_end >= start_time and seg_start <= end_time):
            matching_segments.append(segment)
    
    return matching_segments

def extract_text_from_segments(segments):
    """
    Extract text from a list of segments.
    
    Args:
        segments (list): List of transcript segments
        
    Returns:
        str: Concatenated text
    """
    return " ".join([segment.get("text", "") for segment in segments])

def get_context_around_timestamp(transcript_data, timestamp, window_seconds=60):
    """
    Get transcript context around a specific timestamp.
    
    Args:
        transcript_data (dict): Transcript data
        timestamp (float): Timestamp in seconds
        window_seconds (int): Window size in seconds (before and after)
        
    Returns:
        str: Text context around the timestamp
    """
    start_time = max(0, timestamp - window_seconds)
    end_time = timestamp + window_seconds
    
    segments = find_segments_in_time_range(transcript_data, start_time, end_time)
    return extract_text_from_segments(segments)