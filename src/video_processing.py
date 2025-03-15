import os
import subprocess
import uuid
import re
import json

def get_video_metadata(video_url):
    """
    Uses yt-dlp to retrieve metadata such as video ID.
    If metadata extraction fails, generates a fallback unique ID.
    """
    try:
        result = subprocess.run(
            ["yt-dlp", "--print-json", "--skip-download", video_url],
            capture_output=True, text=True, check=True
        )
        metadata = json.loads(result.stdout)
        video_id = metadata.get("id", str(uuid.uuid4().hex[:6]))  # Use video ID or fallback
        return video_id
    except Exception:
        return str(uuid.uuid4().hex[:6])  # Generate unique ID if metadata retrieval fails

def download_youtube_audio(video_url, output_dir="./data/raw", processed_urls=set(), index=None):
    """
    Downloads the audio from a YouTube video using yt-dlp and converts it to WAV format.
    Ensures unique filenames and avoids reprocessing duplicate URLs.

    Parameters:
    video_url (str): The YouTube video URL.
    output_dir (str): Directory where the audio file will be saved.
    processed_urls (set): Set of URLs that have already been processed.
    index (int): Index of the video in batch processing, assigned dynamically if None.

    Returns:
    str: Path to the converted WAV file.
    """
    if video_url in processed_urls:
        print(f"[INFO] Skipping duplicate video: {video_url}")
        return None

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Determine index based on existing files if not provided
    if index is None:
        existing_files = [f for f in os.listdir(output_dir) if f.startswith("video_")]
        index = len(existing_files) + 1

    try:
        if index == 1:
            print("[INFO] Libraries and dependencies imported successfully.")

        video_id = get_video_metadata(video_url)
        output_filename = f"video_{index:02d}_{video_id}.wav"  # Two-digit numbering
        output_path = os.path.join(output_dir, output_filename)

        print(f"[INFO] Processing file {index}...")

        subprocess.run([
            "yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-format", "wav",
            "-o", output_path, video_url
        ], check=True)

        print(f"[SUCCESS] File {index} processed successfully: {output_path}")
        processed_urls.add(video_url)
        return output_path

    except Exception as e:
        print(f"[ERROR] Failed to process file {index}: {e}")
        return None
