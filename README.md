# Xvoice: Automated Transcription and Processing of Audio and Video Content

## 1. Overview
Xvoice is an advanced transcription system designed to efficiently convert audio and video content into structured text. The project leverages OpenAI's Whisper model to perform automatic speech recognition (ASR) while implementing preprocessing techniques to enhance transcription quality and processing efficiency. The system is built with scalability and modularity in mind, making it adaptable for various applications, including research, documentation, and content creation.

## 2. Objectives
- **Automate transcription from various audio and video sources with high accuracy.**
- **Optimize computational efficiency through preprocessing and parallelization.**
- **Enhance transcription quality by applying noise reduction techniques.**
- **Provide structured and searchable output formats (JSON, Markdown, plain text).**
- **Enable seamless integration with Notion, Obsidian, or other knowledge management tools.**

## 3. System Architecture
The Xvoice system is structured into multiple components, each serving a distinct function in the transcription pipeline.

### 3.1. Preprocessing Module
- **File Format Standardization:** All audio and video inputs are converted into the `.wav` format to ensure consistency in processing.
- **Noise Reduction:** Leveraging advanced filtering techniques, noise reduction improves speech clarity, leading to more accurate transcriptions.
- **Segmentation:** Long audio files are divided into smaller segments for parallelized processing, reducing latency and optimizing performance.

### 3.2. Transcription Engine
- **Whisper Model:** OpenAI's Whisper is an end-to-end ASR system trained on a diverse multilingual dataset. It utilizes a transformer-based architecture to generate highly accurate speech-to-text transcriptions.
- **Language Adaptability:** The model supports multiple languages and adapts well to various accents and dialects.
- **Optimized Processing:** By leveraging GPU acceleration, transcription speed is enhanced without compromising accuracy.

### 3.3. Post-Processing and Structuring
- **Formatting:** The transcribed text is structured into paragraphs and sections to improve readability.
- **Timestamping:** Each segment retains its timestamp to facilitate reference and alignment with the original audio.
- **Text Cleaning:** spaCy-based NLP processing is used to enhance structure and clarity of transcriptions.

### 3.4. Logging and Error Handling
- **Logging System:** All processing steps are logged to ensure traceability and facilitate debugging.
- **Error Detection:** The system identifies and flags potential transcription errors, such as incomplete words or unclear speech segments.

## 4. Whisper Model: Algorithm and Justification
Whisper is an ASR model trained on a vast dataset of diverse speech samples. It employs:
- **Encoder-Decoder Transformer Architecture:** Uses a transformer-based approach where an encoder processes the input audio spectrogram, and a decoder generates the transcription.
- **Log-Mel Spectrograms:** The model converts audio into log-Mel spectrograms, allowing it to capture frequency patterns crucial for accurate speech recognition.
- **Multilingual Training:** Trained on multiple languages, enabling high adaptability and robustness.
- **Robust to Background Noise:** Due to its diverse dataset, Whisper performs well even in noisy environments.

These characteristics make Whisper ideal for Xvoice, as it ensures high transcription fidelity across different audio conditions and languages.

## 5. Project Folder Structure
To maintain modularity and ease of use, Xvoice follows a structured directory layout:

```
/xvoice
│── /src
│   │── transcription.py       # Core module for Whisper-based transcription
│   │── preprocessing.py       # Audio preprocessing (conversion, noise reduction, segmentation)
│   │── youtube_downloader.py  # Module for downloading and extracting audio from YouTube videos
│   │── utils.py               # Utility functions (logging, timestamping, etc.)
│── /data
│   │── /raw                   # Original unprocessed audio files
│   │── /processed             # Processed audio ready for transcription
│   │── /split                 # Segmented audio files for parallel processing
│   │── /transcriptions        # Final transcription outputs
│── /logs
│── config.yaml                # Configurable parameters (Whisper model size, chunk size, etc.)
│── requirements.txt            # List of required dependencies
│── README.md                   # Project documentation
```

## 6. Installation and Setup
To set up Xvoice, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/your-repository/xvoice.git
cd xvoice
pip install -r requirements.txt
```

## 7. Execution Pipeline
The Xvoice workflow consists of the following sequential steps:

1. **Audio/Video Input Handling:**
   - If the input is a video file, extract the audio and convert it to `.wav`.
   - If the input is an audio file, ensure it is in `.wav` format for consistency.

2. **Preprocessing:**
   - Apply noise reduction techniques to improve clarity.
   - Segment long audio files into smaller chunks for efficient processing.

3. **Transcription:**
   - Whisper processes each chunk separately to maximize GPU utilization.
   - Merge transcribed chunks into a cohesive output.

4. **Post-Processing:**
   - Structure the transcription output (paragraph formatting, timestamp alignment, text cleaning with spaCy NLP).
   - Generate structured logs to ensure traceability.

## 8. Justification of Techniques Used
### 8.1. Noise Reduction
Noise reduction is applied using spectral subtraction and filtering techniques. These help:
- **Enhance speech clarity** by removing background noise components.
- **Improve Whisper's accuracy**, especially in noisy environments.
- **Reduce false transcriptions** caused by static, echoes, or low-quality recordings.

### 8.2. Parallelized Processing
Audio files are split into smaller chunks to:
- **Leverage multi-core CPU and GPU processing**, reducing execution time.
- **Ensure Whisper handles long files efficiently** without memory constraints.
- **Maintain sequential integrity** by reassembling segments after transcription.

### 8.3. NLP-Based Text Cleaning
- **Uses spaCy for sentence segmentation and cleaning.**
- **Ensures grammatical structure and readability in transcriptions.**
- **Handles punctuation, stopwords, and structured formatting.**

## 9. License
Xvoice is distributed under the MIT License.

## 10. Contact
For inquiries, contributions, or collaborations, please reach out to the repository maintainer.
