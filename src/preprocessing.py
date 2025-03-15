import os
import subprocess
import math
from pydub import AudioSegment

def normalize_audio(input_path, output_path, sample_rate=16000, channels=1, noise_reduction=True):
    """
    Normaliza o áudio, converte para o formato correto e reduz ruído (se ativado).
    
    Parâmetros:
    - input_path (str): Caminho do arquivo de entrada.
    - output_path (str): Caminho do arquivo de saída.
    - sample_rate (int): Taxa de amostragem desejada.
    - channels (int): Número de canais (1 para mono, 2 para estéreo).
    - noise_reduction (bool): Se True, aplica redução de ruído.
    
    Retorna:
    - None
    """
    try:
        print(f"[INFO] Normalizing audio: {input_path}")

        # **1. Ajuste de Formato e Normalização**
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", input_path, "-ar", str(sample_rate), "-ac", str(channels),
            "-b:a", "128k", "-threads", "4", "-filter:a", "loudnorm", output_path
        ]

        subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        
        if noise_reduction:
            print(f"[INFO] Applying noise reduction: {output_path}")

            # **2. Aplicar Filtros High-Pass e Low-Pass para Remover Ruído**
            noise_reduction_cmd = [
                "ffmpeg", "-y", "-i", output_path,
                "-af", "highpass=f=200, lowpass=f=3000",
                "-threads", "4",
                output_path.replace(".wav", "_denoised.wav")
            ]

            subprocess.run(noise_reduction_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            # Substituir pelo arquivo denoised
            os.replace(output_path.replace(".wav", "_denoised.wav"), output_path)

        print(f"[SUCCESS] Normalized and denoised audio saved: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg failed: {e}")
                
def split_audio(input_path, output_dir, max_duration=300):
    """
    Splits the audio file into smaller parts if it exceeds max_duration (in seconds).
    
    Parameters:
    input_path (str): Path to the input .wav file.
    output_dir (str): Directory where the split files will be saved.
    max_duration (int): Maximum duration for each split file (default: 5 minutes).
    
    Returns:
    list: List of file paths to the split audio files.
    """
    print(f"[INFO] Checking if audio needs to be split: {input_path}")
    
    audio = AudioSegment.from_wav(input_path)
    duration = len(audio) / 1000  # Convert to seconds

    if duration <= max_duration:
        print("[INFO] Audio duration is within limits. No splitting needed.")
        return [input_path]

    os.makedirs(output_dir, exist_ok=True)
    num_parts = math.ceil(duration / max_duration)
    file_paths = []

    for i in range(num_parts):
        start_time = i * max_duration * 1000  # Convert to milliseconds
        end_time = min((i + 1) * max_duration * 1000, len(audio))
        part = audio[start_time:end_time]
        part_filename = os.path.join(output_dir, f"{os.path.basename(input_path).replace('.wav', '')}_part{i+1}.wav")
        part.export(part_filename, format="wav")
        file_paths.append(part_filename)
        print(f"[SUCCESS] Created split file: {part_filename}")

    return file_paths
