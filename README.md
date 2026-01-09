# 🎙️ Audio to Text Converter

A desktop application designed to transcribe audio and video files (MP3, MP4) into text using Google Speech Recognition API. The application is built with Python and Tkinter, featuring a user-friendly GUI, automatic audio chunking for long files, and export functionality.

## 🚀 Features

* **File Support:** Compatible with `.mp3` audio and `.mp4` video files.
* **Large File Handling:** Includes a smart chunking algorithm that splits long audio files (default 2 minutes/chunk) to ensure stable processing and prevent API timeouts.
* **Audio Normalization:** Automatically adjusts audio levels to optimal decibels (-20 dBFS) for better recognition accuracy.
* **Real-time Progress:** Multi-threaded architecture ensures the UI remains responsive with a real-time progress bar and time estimation.
* **Thai Language Support:** Optimized for Thai speech-to-text transcription (`th-TH`).
* **Auto-Export:** Automatically saves the transcribed text to a `.txt` file in the `output/` directory.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **GUI:** Tkinter
* **Audio Processing:** Pydub, FFmpeg
* **Speech Recognition:** Google Speech Recognition API
* **Threading:** Python `threading` module for background processing

## 📥 Installation & Usage

### Option 1: Run via Executable (Windows)
You can run the application without installing Python.
1. Go to the [`build/`](./build) folder in this repository.
2. Download and run `voice2txt.exe`.

### Option 2: Run from Source
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Kingteera/Your-Repo-Name.git](https://github.com/Kingteera/Your-Repo-Name.git)
   cd Your-Repo-Name

