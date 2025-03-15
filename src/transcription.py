import os
import whisper
import torch
import json
import re
import spacy
import gc
import subprocess
from concurrent.futures import ThreadPoolExecutor
from src.preprocessing import split_audio

# Load spaCy model for text processing
def load_spacy_model(model):
    """Verifica e carrega o modelo do spaCy, instalando se necessário."""
    try:
        return spacy.load(model)
    except OSError:
        print(f"[INFO] Installing spaCy model: {model}...")
        subprocess.run(["python", "-m", "spacy", "download", model])
        return spacy.load(model)

def transcribe_audio(file_path, model, nlp, language="pt", accumulated_time=0):
    """
    Transcribes an audio file using Whisper and maintains accumulated timestamps.

    Parameters:
    - file_path (str): Path to the audio file.
    - model: Whisper model instance.
    - nlp: spaCy model instance for text processing.
    - language (str): Expected transcription language (default: "pt").
    - accumulated_time (float): Running time from previous segments.

    Returns:
    - dict: Transcription results with timestamps.
    - float: Updated accumulated time after processing the segment.
    """
    try:
        print(f"[INFO] Transcribing: {file_path}")

        # Ensure audio file exists
        if not os.path.exists(file_path):
            print(f"[ERROR] Audio file not found: {file_path}")
            return None, accumulated_time

        # Transcribe using Whisper
        result = model.transcribe(file_path, language=language)

        if "text" not in result:
            print(f"[WARNING] Whisper did not return text for {file_path}")
            return None, accumulated_time

        # Extract timestamps
        segments = result.get("segments", [])
        if segments:
            start_timestamp = accumulated_time  
            segment_duration = float(segments[-1].get("end", 0))  
            accumulated_time += segment_duration  # Update accumulated time

            # Format timestamps
            formatted_timestamp = format_timestamp(start_timestamp)
            cleaned_text = clean_transcription(result["text"], nlp)  # ✅ Passando `nlp`

            return {"start": formatted_timestamp, "text": cleaned_text, "duration": segment_duration}, accumulated_time

    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            print("[WARNING] GPU memory issue, retrying on CPU...")
            model.to("cpu")  
            return transcribe_audio(file_path, model, nlp, language, accumulated_time)
        else:
            print(f"[ERROR] Failed to transcribe {file_path}: {e}")

    except Exception as e:
        print(f"[ERROR] Failed to transcribe {file_path}: {e}")

    return None, accumulated_time

def transcribe_audio_batch(audio_files, model, nlp, language="pt", accumulated_time=0):
    """
    Transcribes a batch of audio files using Whisper and maintains accumulated timestamps.

    Parameters:
    - audio_files (list): List of paths to audio files.
    - model: Whisper model instance.
    - nlp: spaCy model instance for text processing.
    - language (str): Expected transcription language (default: "pt").
    - accumulated_time (float): Running time from previous segments.

    Returns:
    - List[dict]: List of transcription results with timestamps.
    - float: Updated accumulated time after processing all segments.
    """
    transcriptions = []
    
    for file_path in audio_files:
        print(f"[INFO] Transcribing: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"[ERROR] Audio file not found: {file_path}")
            continue

        try:
            # Transcribe the segment
            result = model.transcribe(file_path, language=language)

            if "text" not in result:
                print(f"[WARNING] Whisper did not return text for {file_path}")
                continue

            # Extract timestamps
            segments = result.get("segments", [])
            if segments:
                start_timestamp = accumulated_time
                segment_duration = float(segments[-1].get("end", 0))  
                accumulated_time += segment_duration  # Update accumulated time

                # Format timestamps
                formatted_timestamp = format_timestamp(start_timestamp)
                cleaned_text = clean_transcription(result["text"], nlp)  # ✅ Passando `nlp`

                transcriptions.append({"start": formatted_timestamp, "text": cleaned_text, "duration": segment_duration})

        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
                print("[WARNING] GPU memory issue, retrying on CPU...")
                model.to("cpu")
                return transcribe_audio_batch(audio_files, model, nlp, language, accumulated_time)
            else:
                print(f"[ERROR] Failed to transcribe {file_path}: {e}")

        except Exception as e:
            print(f"[ERROR] Failed to transcribe {file_path}: {e}")

    return transcriptions, accumulated_time

def process_audio_file(file, input_dir, processed_dir, split_dir, transcription_dir, whisper_model, nlp, use_normalization):
    """
    Processes an audio file, splitting it into segments and transcribing each segment sequentially.

    Parameters:
    - file (str): The audio file name.
    - input_dir (str): Directory containing raw audio files.
    - processed_dir (str): Directory for processed audio files.
    - split_dir (str): Directory for split audio segments.
    - transcription_dir (str): Directory to save transcriptions.
    - whisper_model: Loaded Whisper model for transcription.
    - nlp: spaCy model instance for text processing.
    - use_normalization (bool): Whether to apply normalization and noise reduction.
    """
    input_path = os.path.join(input_dir, file)
    output_path = os.path.join(processed_dir, file.replace(".m4a", ".wav").replace(".mp3", ".wav"))

    print(f"[INFO] Processing file: {file}")

    try:
        # Step 1: Normalize audio and apply noise reduction (Optional)
        if use_normalization:
            print(f"[INFO] Normalizing and denoising audio: {input_path}")
            normalize_audio(input_path, output_path, sample_rate=16000, channels=1, noise_reduction=True)
        else:
            print(f"[INFO] Skipping normalization. Using raw audio: {input_path}")
            output_path = input_path  

        # Step 2: Split long audio files into smaller parts
        split_files = split_audio(output_path, split_dir, max_duration=300)

        # Step 3: Transcription using transcribe_audio_batch()
        transcriptions, _ = transcribe_audio_batch(split_files, whisper_model, nlp, language="pt")

        # Step 4: Save the final transcription
        if isinstance(transcriptions, list):
            txt_output = os.path.join(transcription_dir, os.path.basename(file).replace(".wav", ".txt"))
            save_transcription(transcriptions, txt_output)
        else:
            print(f"[WARNING] Unexpected format in transcription output: {type(transcriptions)}")

        # Step 5: Remove intermediate split files
        for split_file in split_files:
            os.remove(split_file)
            print(f"[INFO] Deleted intermediate split file: {split_file}")

        # Step 6: Free GPU memory
        torch.cuda.empty_cache()
        gc.collect()

    except Exception as e:
        print(f"[ERROR] Failed to process {file}: {e}")

def format_time(seconds):
    """
    Converts time in seconds to HH:MM:SS format.

    Parameters:
    seconds (float): Time in seconds.

    Returns:
    str: Formatted time string.
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def clean_transcription(text, nlp, sentence_segmentation=True, remove_stopwords=False):
    """
    Cleans and formats the transcribed text using a preloaded spaCy model.

    Parameters:
    text (str): Raw transcribed text.
    nlp: Preloaded spaCy model.
    sentence_segmentation (bool): If True, segments text into well-structured sentences.
    remove_stopwords (bool): If True, removes common stopwords.

    Returns:
    str: Cleaned and formatted text.
    """
    try:
        # Garante que o texto não seja None
        if not text or not isinstance(text, str):
            print("[ERROR] Transcription text is invalid!")
            return ""

        # Remove espaços extras
        text = re.sub(r"\s+", " ", text).strip()

        # Processa com spaCy
        doc = nlp(text)

        cleaned_sentences = []
        for sent in doc.sents:
            processed_text = sent.text.capitalize()

            if remove_stopwords:
                processed_text = " ".join([token.text for token in sent if not token.is_stop])
                processed_text = processed_text.capitalize()

            cleaned_sentences.append(processed_text)

        formatted_text = " ".join(cleaned_sentences)

        print("[SUCCESS] Transcription cleaned and formatted.")
        return formatted_text

    except Exception as e:
        print(f"[ERROR] Failed to clean transcription: {e}")
        return text

def save_transcription(transcriptions, output_txt):
    """
    Saves the final transcription in a structured text format.

    Parameters:
    - transcriptions (list of dict): List of transcriptions with "start" and "text".
    - output_txt (str): Path to the output text file.
    """
    try:
        os.makedirs(os.path.dirname(output_txt), exist_ok=True)

        with open(output_txt, "w", encoding="utf-8") as txt_file:
            for transcription in transcriptions:
                if isinstance(transcription, list):  # Se for uma lista dentro da lista, desfaz o aninhamento
                    for sub_transcription in transcription:
                        if isinstance(sub_transcription, dict):
                            start_time = sub_transcription.get("start", "[00:00:00]")
                            text = sub_transcription.get("text", "").strip()
                            txt_file.write(f"{start_time} {text}\n")
                elif isinstance(transcription, dict):  # Caso normal, processa normalmente
                    start_time = transcription.get("start", "[00:00:00]")
                    text = transcription.get("text", "").strip()
                    txt_file.write(f"{start_time} {text}\n")
                else:
                    print(f"[WARNING] Unexpected format in transcription output: {type(transcription)}")

        print(f"[SUCCESS] Transcription saved: {output_txt}")

    except Exception as e:
        print(f"[ERROR] Failed to save transcription: {e}")

def cleanup_directory(directory):
    """
    Removes all files in the specified directory.
    
    Parameters:
    - directory (str): Path to the directory to clean.
    """
    try:
        if not os.path.exists(directory):
            print(f"[WARNING] Directory does not exist: {directory}")
            return
        
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            os.remove(file_path)
        
        print(f"[INFO] Cleaned directory: {directory}")
    
    except Exception as e:
        print(f"[ERROR] Failed to clean directory {directory}: {e}")

def format_timestamp(seconds):
    try:
        seconds = int(float(seconds))  # Ensure it is a number
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"[{hours:02}:{minutes:02}:{seconds:02}]"
    except ValueError:
        print(f"[ERROR] Invalid timestamp value: {seconds}")
        return "[00:00:00]"  # Return default if error occurs
