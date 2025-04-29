import os
import re
from pytube import YouTube
import yt_dlp
from datetime import datetime

def is_valid_youtube_url(url):
    """
    Validates if the provided URL is a valid YouTube URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    
    match = re.match(youtube_regex, url)
    return match is not None

def get_video_info(url):
    """
    Gets basic information about the YouTube video using yt-dlp.
    
    Args:
        url (str): The YouTube video URL
        
    Returns:
        dict: Dictionary containing video information
    """
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'format': 'bestaudio/best',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        # Format the data to match your expected structure
        video_info = {
            'title': info.get('title'),
            'author': info.get('uploader'),
            'length_seconds': info.get('duration'),
            'views': info.get('view_count'),
            'publish_date': datetime.fromtimestamp(info.get('timestamp')).strftime('%Y-%m-%d') if info.get('timestamp') else None,
            'video_id': info.get('id')
        }
        
        return video_info
    except Exception as e:
        print(f"Error getting video info: {str(e)}")
        return None

def download_audio(url, output_dir, filename=None):
    """
    Downloads the audio from a YouTube video using yt-dlp.
    
    Args:
        url (str): The YouTube video URL
        output_dir (str): Directory to save the audio file
        filename (str, optional): Custom filename without extension
        
    Returns:
        str: Path to the downloaded audio file
    """
    if not is_valid_youtube_url(url):
        raise ValueError("Invalid YouTube URL")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get video info for metadata
    video_info = get_video_info(url)
    
    if not video_info:
        raise ValueError("Could not retrieve video information")
    
    # Create a filename if not provided
    if not filename:
        # Clean title to use as filename (remove special characters)
        clean_title = re.sub(r'[^\w\-_\. ]', '', video_info['title'])
        filename = f"{clean_title}_{video_info['video_id']}"
    
    output_path = os.path.join(output_dir, filename)
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'no_warnings': False
    }
    
    # Download the audio
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Return the full path to the downloaded file
        final_path = f"{output_path}.mp3"
        
        # Save metadata
        save_video_metadata(video_info, output_dir, filename)
        
        return final_path
    except Exception as e:
        print(f"Error downloading audio: {str(e)}")
        raise

def save_video_metadata(video_info, output_dir, filename):
    """
    Saves video metadata to a JSON file.
    
    Args:
        video_info (dict): Dictionary containing video information
        output_dir (str): Directory to save the metadata file
        filename (str): Base filename
    """
    import json
    
    # Add timestamp for when the video was downloaded
    video_info['downloaded_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save metadata to JSON file
    metadata_path = os.path.join(output_dir, f"{filename}_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(video_info, f, indent=4)

if __name__ == "__main__":
    print("YouTube Audio Downloader")
    print("=" * 50)
    
    # Get URL from user
    url = input("Enter YouTube URL: ")
    
    # Validate URL
    print("\nValidating URL...")
    is_valid = is_valid_youtube_url(url)
    print(f"Is valid YouTube URL: {is_valid}")
    
    if not is_valid:
        print("Invalid YouTube URL. Exiting.")
        exit(1)
    
    # Get video info
    print("\nRetrieving video information...")
    info = get_video_info(url)
    if info:
        print("Video information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    else:
        print("Failed to retrieve video information. Exiting.")
        exit(1)
    
    # Download audio
    print("\nDownloading audio...")
    try:
        output_dir = os.path.join(os.getcwd(), "downloads")
        audio_path = download_audio(url, output_dir)
        print(f"Audio downloaded successfully to: {audio_path}")
    except Exception as e:
        print(f"Audio download failed: {str(e)}")