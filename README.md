# AI-VideoQnA-Project
A tool designed to help students interact with (ideally) lecture content on Youtube.

# User Experience
A user will upload a youtube video of their choice via URL, this video is ideally some sort of a lecture format.
After which the user will be asked if they want to download and transcribe the video, 
once confirmed the program will then transcribe the video and store all relevant information across data and downloads.
After the transcribing process is completed the user will be snet to the main menu, where they are given three options.
1. Add new Youtube video
2. Select previously uploaded video
3. View question history

The user at this point should pick "2. Select previously uploaded youtube video" where they can select the transcript of the youtube video they have uploaded. After this point they have a new set of options
1. Ask a question
2. Add a note
3. View notes
4. View Question history

Selecting 1. will allow the user to now question the AI, which is ollama 7b, over the contents of the youtube video. 
Selecting 2. will allow the user to add a note under that specific video for future reference.
Selecting 3. will allow the user to view previous notes that they have made.
Selecting 4. will allow the user to ses previous questions it has asked the AI and see the AI responses.


# How it works (only mentioning src)

* first you must locally download ollama 7b

## youtube_downloader.py ##

function is_valid_url(url)
Checks for YouTube URL formats like standard, shortened, or embedded and makes sure there is a valid 11-character video ID.

function get_video_info(url)
Uses yt_dlp library to extract metadata of the provided youtube video without downloading it. Collects important information.

function download_audio(url, output_dir, filename=None)
this function validates the URL using is_valid_youtube_url, creates an output directory if it's necessary, will retrieve metadata, will create a clean filename, configures the yt_dlp library to extract quality audio, then downloads, processes the audio and saves the metadata and audio file.

function save_video_metadata(video_info, output_dir, filename)
records the time the download happened, formnats the data as JSON, saves it along with the audio file.

## transcriber.py ## 

class AudioTranscriber
A class that manages the transcription of audio files into a text with timestamps using OpenAI's Whisper model.

function __init__(self, model_name=config.DEFAULT_TRANSCRIPT_MODEL, language=config.DEFAULT_LANGUAGE)
initializes transcriber with specific model parameters, this detects whether it should use GPU or CPU for processing.

function load_model(self)
Loads a specified whisper model into memory, only when needed. This optimizes resource usage.

function transcribe_audio(self, audio_path, output_path=None, metadata=None)
Processes an audio file to make a transcript. Will validate input file, loads the model if needed, performs the transcription with timestamps, processes the output and then saves them to a JSON file.

function _process_transcript(self, result, metadata=None)
Will transform the whisper output into a more structured format which will contain the full transcript text, and individual segments with timestamps.

function _format_timestamp(self, seconds)
converts time values into a readable-format which makes it easier to navigate the transcript.

## transcript_manager.py ##

class Transcript AudioTranscriber
A class that manages storing, and retrieving transcript files.

function __init__(self, transcript_dir=None)
sets up transcript manager by specifying where transcript files will be stored, creating the directory if it doesn't exist.

function save_transcript(self, transcript_data, audio_path=None)
stores transcript data into a JSON file with a relevant file name and a unique identifier.

function load_transcript(self, path)
loads transcript data from a specified file path, handles potential errors and ensures metadata is properly structured.

function list_transcripts(self)
scans transcript directory and compiles a list of available transcripts. The output is sorted with newest transcripts first so recent uploads are easier to access.

function get_transcript_text(self, transcript_data)
Extracts the full text content from a transcript.

function display_transcript_info(self, transcript_data)
prints out some information about a transcript: title, number of segments.

## notes_manager.py ##

class NotesManager
enables user to create, store and access notes under respective transcripts.

fuction __init__(self, notes_dir=None)
establishes where note files will be storedm creates the directory structure if it doesn't already exist.

function add_note(self, transcript_path, note_text, timestamp_seconds=None, tags=None)
Creates and saves a note connected to a certain transcript. The user has the option to add tags to their note for easier categorization. 

function get_notes(self, transcript_path)
retrieves notes associated with a specified transcript, returns them as a structured list.

function search_notes(self, transcript_path, search_term=None, tag=None)
allows users to find specific notes based on the content in the note or by tags.

## I will not mention update_notes or delete_notes as they are for future development ##

## history_manager.py ##

class HistoryManager
tracks and records questions asked by a user and the corresponding AI response.

function __init__(self, history_dir=None)
establishes where question records will be stored, creates directory structury if necessary.

function add_to_history(self, transcript_path, question, answer)
saves each question asked by the user and the ai response to the question. Each entry is timestamped and linked to the respective transcript

function get_history(self, transcript_path)
retrieves complete interaction history for a specific transcript.

function search_history(self, transcript_path, search_term)
helps users quickly locate previous explanations on particulr topics without going over entire history.

function clear_history(self, transcript_path)
provides the option to remove all previously recorded questions and answers.

## ai_handler.py ##

class AIHandler
interfaces with the Ollama API to process questions about the content of uploaded videos and generate relevant and valuable responses.

function __init__(self, model_name=None)
initializes the AI engine with a specific language model, this defaults to mistral:7b. Checks for GPU availability and verifies the Ollama service is running with the required model loaded.

function process_any_request(self, user_request, transcript_data)
This is the primary function that handles the AI interactions. It will analyze user questions, extract any references to tiem and prepare relevant context from the transcript. It will then construct a system prompt and send a request to the Ollama API.

function _prepare_context(self, transcript_data, start_time=None, end_time=None)
A function that extracts relevant portions of the transcript based on the user's question. If specific timestamps are mentioned it will only retrieve content from that time range; otherwise it uses the full transcript.

function _create_flexible_system_prompt(self, transcript_data)
creates a specialized instruction for the AI model based on the video's metadata.






