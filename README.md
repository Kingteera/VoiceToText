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

### Prerequisites
Before running or building the project, you need to download **FFmpeg**.
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html).
2. Extract the `ffmpeg.exe` file.
3. Place `ffmpeg.exe` inside the project folder at: `src/ffmpeg/ffmpeg.exe`.
   *(Create the `ffmpeg` folder inside `src` if it doesn't exist)*

---

### Option 1: Run from Source (For Developers)
If you want to run the python script directly:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Kingteera/Your-Repo-Name.git](https://github.com/Kingteera/Your-Repo-Name.git)
   cd Your-Repo-Name
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
3. **Run the application**
   ```bash
   python voice2txt.py
   
### Option 2: Build Executable (Create .exe)
If you want to build a standalone .exe file to use on Windows without Python:
1. **Ensure FFmpeg is placed correctly: Make sure src/ffmpeg/ffmpeg.exe exists (as mentioned in Prerequisites).**
2. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
3. **Run the build script: Run the setup script to compile the application.**
   ```bash
   python setup.py
