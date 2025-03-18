import os
import subprocess
import uuid
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

def download_youtube_audio(video_url, output_dir="./data/raw", start_time=None, end_time=None, processed_urls=set(), index=None):
    """
    Downloads a specific segment of audio from a YouTube video using yt-dlp and converts it to WAV format.
    Ensures unique filenames and avoids reprocessing duplicate URLs.

    Parameters:
    - video_url (str): The YouTube video URL.
    - output_dir (str): Directory where the audio file will be saved.
    - start_time (str or None): Start time of the desired segment (e.g., "10:30"). If None, starts from 0.
    - end_time (str or None): End time of the desired segment (e.g., "15:45"). If None, downloads the rest.
    - processed_urls (set): Set of URLs that have already been processed.
    - index (int or None): Index of the video in batch processing, assigned dynamically if None.

    Returns:
    - str: Path to the extracted WAV file.
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

        # Definir nome do arquivo com start_time para identificar trechos diferentes
        time_suffix = f"_{start_time.replace(':', '')}" if start_time else ""
        output_filename = f"video_{index:02d}_{video_id}{time_suffix}.wav"
        output_path = os.path.join(output_dir, output_filename)

        print(f"[INFO] Processing file {index}...")

        # Define a seção a ser baixada, se os tempos foram fornecidos
        yt_dlp_command = [
            "yt-dlp", "-f", "bestaudio", "--extract-audio", "--audio-format", "wav",
            "-o", output_path, video_url
        ]
        
        if start_time and end_time:
            yt_dlp_command.insert(1, "--download-sections")
            yt_dlp_command.insert(2, f"*{start_time}-{end_time}")

        # Executa o comando corretamente formatado
        subprocess.run(yt_dlp_command, check=True)

        print(f"[SUCCESS] File {index} processed successfully: {output_path}")
        processed_urls.add(video_url)
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to process file {index}: {e}")
        return None
