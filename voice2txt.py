import imageio_ffmpeg as ffmpeg
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pydub.utils
import speech_recognition as sr
from pydub import AudioSegment
import os
import time
import subprocess
import pydub
from pydub.effects import normalize
from pydub.utils import which

ffmpeg_bin_path = r"D:\king\voice2text\src\ffmpeg"  # Adjust as needed

# Add ffmpeg directory to the PATH
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path

# Set the ffmpeg path explicitly for pydub
AudioSegment.converter = os.path.join(ffmpeg_bin_path, "ffmpeg.exe")

# Check if ffmpeg is found
print("ffmpeg found at:", AudioSegment.converter)
print("ffmpeg:", which("ffmpeg"))


if not os.path.exists("src/temp"):
    os.makedirs("src/temp")
if not os.path.exists("output"):
    os.makedirs("output")

output_filename = None

uploaded_file_path = None


def on_close():
    global output_filename
    root.destroy()
    temp_folder_path = "src/temp"
    if output_filename:
        os.remove(output_filename)
    try:
        if os.path.exists(temp_folder_path):
            for file_name in os.listdir(temp_folder_path):
                file_path = os.path.join(temp_folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                else:
                    print(f"Skipped: {file_path} (Not a file)")
        else:
            print(f"Folder '{temp_folder_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while clearing the temp folder: {e}")
    os._exit(0)

def fix_mp4_file(input_file, output_file):
    """
    ซ่อมแซมไฟล์ MP4 ด้วย ffmpeg
    """
    try:
        command = [
            "ffmpeg",
            "-y",  
            "-i", input_file,
            "-c", "copy",
            "-loglevel", "quiet",  
            "-nostats", 
            "-hide_banner", 
            output_file
        ]
        subprocess.run(command, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"ข้อผิดพลาดในการซ่อมไฟล์ MP4: {e}")
        # raise ValueError(f"ข้อผิดพลาดในการซ่อมไฟล์ MP4: {e}")

def normalize_audio_for_recognition(audio, target_dbfs=-20):
    """
    ปรับระดับเสียงให้อยู่ในช่วงที่เหมาะสมสำหรับการแปลงเสียงเป็นข้อความ
    """
    current_dbfs = audio.dBFS
    change_in_db = target_dbfs - current_dbfs
    return audio.apply_gain(change_in_db)

def audio_to_wav(file_path, target_dbfs=-20):
    """
    แปลงไฟล์ MP3/MP4 เป็น WAV พร้อมปรับปรุงเสียง
    """
    if file_path.lower().endswith(".mp4"):
        fixed_file = f"src/temp/fixed_{os.path.basename(file_path)}"
        file_path = fix_mp4_file(file_path, fixed_file)

    if file_path.lower().endswith(".mp3"):
        audio = AudioSegment.from_mp3(file_path)
    elif file_path.lower().endswith(".mp4"):
        audio = AudioSegment.from_file(file_path, format="mp4")
    else:
        messagebox.showerror("Error", "Unsupported file format. Please upload an MP3 or MP4 file.")
        # raise ValueError("Unsupported file format. Please upload an MP3 or MP4 file.")

    # ปรับระดับเสียงให้อยู่ในช่วงที่เหมาะสม
    audio = normalize_audio_for_recognition(audio, target_dbfs)

    # บันทึกไฟล์เป็น WAV ในโฟลเดอร์ src/temp
    wav_file = f"src/temp/temp_audio.wav"
    audio.export(wav_file, format="wav")
    return wav_file, len(audio) / 1000  # Return WAV path and duration in seconds

def split_audio(audio, chunk_length_ms=120000):  # 30 นาที = 1800000 ms , 10 นาที = 600000
    """
    แบ่งไฟล์เสียงออกเป็นส่วนย่อยๆ
    """
    chunks = []
    for start_ms in range(0, len(audio), chunk_length_ms):
        end_ms = min(start_ms + chunk_length_ms, len(audio))  # ตรวจสอบว่า end_ms ไม่เกินความยาวของ audio
        chunk = audio[start_ms:end_ms]
        chunks.append(chunk)
    return chunks


def mp3_to_text_with_progress(wav_file, duration_seconds, language="th-TH", update_progress=None):
    """
    แปลงไฟล์ WAV เป็นข้อความและอัปเดตความคืบหน้า
    """
    recognizer = sr.Recognizer()

    with sr.AudioFile(wav_file) as source:
        audio_data = recognizer.record(source)
    print("start simulate progress") 
    try:
        # if update_progress:
        #     for i in range(101):
        #         time.sleep(duration_seconds / 100)  # Simulate progress
        #         update_progress(i, duration_seconds)
        print("end simulate progress")
        print("start recognize")
        text = recognizer.recognize_google(audio_data, language=language)
        print("end recognize")
        return text
    except sr.UnknownValueError:
        text = "Speech recognition could not understand the audio."
        # messagebox.showerror("Error", "Speech recognition could not understand the audio.")
        return text
    except sr.RequestError as e:
        messagebox.showerror("Error", f"Speech recognition request failed: {e}")
        text = f"Speech recognition request failed: {e}"
        return text
    finally:
        os.remove(wav_file)  # ลบไฟล์ชั่วคราว

def save_to_txt(text, original_filename, append=False):
    """
    บันทึกข้อความลงไฟล์ที่ชื่อเดียวกับไฟล์ต้นฉบับ
    โดยจะใช้ append เป็นตัวเลือกในการเขียนข้อมูลใหม่หรือลงไฟล์ใหม่
    """
    # เปลี่ยนชื่อไฟล์ให้เป็น .txt แทน .mp3 หรือ .mp4
    base_filename = os.path.splitext(os.path.basename(original_filename))[0]
    output_filename = f"output/transcribed_{base_filename}.txt"
    
    # ใช้โหมด append หากต้องการเพิ่มข้อมูลลงไป
    mode = "a" if append else "w"
    
    with open(output_filename, mode, encoding="utf-8") as file:
        file.write(text)  # เพิ่มข้อความและบรรทัดใหม่
    return output_filename



def process_large_audio(progress_label, progress_bar):
    global uploaded_file_path
    if not uploaded_file_path:
        messagebox.showerror("Error", "Please upload a file before converting.")
        return

    try:
        # แปลงไฟล์ MP3/MP4 เป็น WAV
        wav_file, duration_seconds = audio_to_wav(uploaded_file_path)

        # โหลดไฟล์เสียงทั้งหมด
        audio = AudioSegment.from_wav(wav_file)

        # แบ่งไฟล์เสียงเป็นส่วนๆ
        chunks = split_audio(audio)
        print("chunks len",len(chunks))
        # ตัวแปรเก็บข้อความที่แปลง
        transcribed_text = ""
        

        def update_progress(percent, duration_seconds):
                progress_bar["value"] = percent
                remaining_time = duration_seconds * (1 - percent / 100)  # ใช้เวลาของไฟล์ทั้งหมด
                progress_label.config(
                    text=f"Progress: {int(percent)}%\nEstimated time left: {int(remaining_time)} seconds"
                )
                root.update_idletasks()

        # แปลงแต่ละส่วนและบันทึกผล
        total_duration = len(audio) / 1000
        chunk_duration = total_duration / len(chunks)
        start_time = time.time() 
        chunks_processed = 0
        chunks_to_update = 1
        update_progress(0, total_duration)
        for idx, chunk in enumerate(chunks):
                # ปรับระดับเสียง
            chunk = normalize_audio_for_recognition(chunk)

            # บันทึกไฟล์ชั่วคราวในโฟลเดอร์ src/temp
            print("temp_wav_file", f"src/temp/temp_audio_{idx}.wav")
            temp_wav_file = f"src/temp/temp_audio_{idx}.wav"
            chunk.export(temp_wav_file, format="wav")

            # แปลงเสียงเป็นข้อความ
            
            print("mp3_to_text_with_progress",temp_wav_file)
            chunk_text = mp3_to_text_with_progress(temp_wav_file, chunk_duration, language="th-TH")
            print("chunk_text", chunk_text)
            if chunk_text:
                save_to_txt(chunk_text, uploaded_file_path, append=True)  # เขียนลงไฟล์ทันที

            # ลบไฟล์ชั่วคราว
            # os.remove(temp_wav_file)

            print("update progress ui")
            chunks_processed += 1
            if chunks_processed % chunks_to_update == 0 or chunks_processed == len(chunks):
                percent = min(100, round((chunks_processed / len(chunks)),1) * 100)
                print("update progress ui",percent, total_duration)
                update_progress(percent, total_duration)
        # แจ้งเตือนเมื่อเสร็จสิ้น
        messagebox.showinfo("Conversion Complete", "Text has been saved successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")
        return
    finally:
        progress_label.config(text="Done!")
        progress_bar["value"] = 100


def process_audio(progress_label, progress_bar):
    def update_progress(percent, duration_seconds):
                progress_bar["value"] = percent
                remaining_time = duration_seconds * (1 - percent / 100)
                progress_label.config(
                    text=f"Progress: {percent}%\nEstimated time left: {int(remaining_time)} seconds"
                )
                root.update_idletasks()
    global uploaded_file_path
    if not uploaded_file_path:
        messagebox.showerror("Error", "Please upload a file before converting.")
        return

    try:
        progress_label.config(
            text=f"Processing file {os.path.basename(uploaded_file_path)}\n--> don't close this window <--"
            )
        # update_progress(0, 0)
        # แปลงไฟล์ MP3/MP4 เป็น WAV
        wav_file, duration_seconds = audio_to_wav(uploaded_file_path)
        print(duration_seconds)
        progress_label.config(
            text=f"Split file '{os.path.basename(uploaded_file_path)}' into {int((duration_seconds//120)+1)} chunks\n--> don't close this window <--"
            )
        if duration_seconds > 120: 
            process_large_audio(progress_label, progress_bar)
        else:
            # แปลงไฟล์เสียงขนาดเล็ก
            # def update_progress(percent, duration_seconds):
            #     progress_bar["value"] = percent
            #     remaining_time = duration_seconds * (1 - percent / 100)
            #     progress_label.config(
            #         text=f"Progress: {percent}%\nEstimated time left: {int(remaining_time)} seconds"
            #     )
            #     root.update_idletasks()

            transcribed_text = mp3_to_text_with_progress(wav_file, duration_seconds, language="th-TH", update_progress=update_progress)

            # บันทึกข้อความลงไฟล์ในโฟลเดอร์ output
            saved_file = save_to_txt(transcribed_text, uploaded_file_path,append=True)

            # แจ้งเตือนเมื่อเสร็จสิ้น
            messagebox.showinfo("Conversion Complete", f"Text has been saved to {saved_file}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return
    finally:
        progress_label.config(text="Done!")
        progress_bar["value"] = 100

def upload_file():
    def update_progress(percent, duration_seconds):
                progress_bar["value"] = percent
                remaining_time = duration_seconds * (1 - percent / 100)
                progress_label.config(
                    text=f"Progress: {percent}%\nEstimated time left: {int(remaining_time)} seconds"
                )
                root.update_idletasks()
    global uploaded_file_path
    uploaded_file_path = filedialog.askopenfilename(filetypes=[("Audio/Video Files", "*.mp3 *.mp4")])
    if uploaded_file_path:
        file_label.config(text=f"Uploaded: '{os.path.basename(uploaded_file_path)}'")
        progress_label.config(
            text=f"--> Click 'Convert to Text' to start processing <--"
            )
        progress_bar["value"] = 0
        print("uploaded") 
    else:
        file_label.config(text="No file uploaded.")

# GUI
root = tk.Tk()
root.title("Audio to Text Converter")
root.geometry("400x300")
root.iconbitmap("src/icon/icon3.ico")

label = tk.Label(root, text="Audio to Text Converter")
label.pack(pady=10)

file_label = tk.Label(root, text="No file uploaded.", anchor="w")
file_label.pack(pady=5)

upload_button = tk.Button(root, text="Upload Audio File", command=upload_file)
upload_button.pack(pady=10)

progress_label = tk.Label(root, text="")
progress_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, length=300, maximum=100)
progress_bar.pack(pady=5)

convert_button = tk.Button(root, text="Convert to Text", command=lambda: threading.Thread(target=process_audio, args=(progress_label, progress_bar)).start())
convert_button.pack(pady=20)
root.protocol("WM_DELETE_WINDOW", on_close) 
root.mainloop()
