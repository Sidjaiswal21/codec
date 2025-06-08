import tkinter as tk
from tkinter import filedialog, messagebox
import speech_recognition as sr
import threading

recognizer = sr.Recognizer()
mic = sr.Microphone()

# Global variable to control recording thread
recording = False
audio_data = None
record_thread = None

def transcribe_audio(file_path):
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except sr.RequestError:
        return "Speech recognition service is unavailable."
    except Exception as e:
        return f"Error: {str(e)}"

def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
    )
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def transcribe():
    file_path = entry_file.get()
    if not file_path:
        messagebox.showwarning("No file", "Please select an audio file first.")
        return
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Transcribing from file...")
    root.update()
    text = transcribe_audio(file_path)
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, text)

def start_recording():
    global recording, audio_data, record_thread
    if recording:
        messagebox.showinfo("Recording", "Already recording!")
        return

    recording = True
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Adjusting for ambient noise, please wait...")
    root.update()

    def record():
        global recording, audio_data
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                text_output.delete(1.0, tk.END)
                text_output.insert(tk.END, "Recording... Speak now.")
                root.update()
                audio_data = recognizer.listen(source, phrase_time_limit=10)
            if recording:
                text_output.delete(1.0, tk.END)
                text_output.insert(tk.END, "Recording stopped. You can transcribe or retake.")
        except Exception as e:
            text_output.delete(1.0, tk.END)
            text_output.insert(tk.END, f"Error during recording: {str(e)}")

    record_thread = threading.Thread(target=record)
    record_thread.start()

def stop_recording():
    global recording
    if not recording:
        messagebox.showinfo("Recording", "Not currently recording.")
        return
    recording = False
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Stopping recording...")
    root.update()
    # Wait for thread to finish
    if record_thread is not None:
        record_thread.join()
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Recording stopped. You can transcribe or retake.")

def transcribe_live():
    global audio_data
    if audio_data is None:
        messagebox.showwarning("No recording", "Please record audio first.")
        return
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Recognizing...")
    root.update()
    try:
        text = recognizer.recognize_google(audio_data)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, text)
    except sr.UnknownValueError:
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, "Sorry, I could not understand your speech.")
    except sr.RequestError:
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, "Speech recognition service unavailable.")

def retake():
    global audio_data, recording
    if recording:
        messagebox.showwarning("Recording in progress", "Stop recording before retaking.")
        return
    audio_data = None
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, "Ready to record new audio.")

# Setup GUI window
root = tk.Tk()
root.title("Speech-to-Text Transcription")

# File input frame
frame = tk.Frame(root)
frame.pack(pady=10, padx=10, fill=tk.X)

entry_file = tk.Entry(frame, width=50)
entry_file.pack(side=tk.LEFT, padx=(0,5))

btn_browse = tk.Button(frame, text="Browse File", command=browse_file)
btn_browse.pack(side=tk.LEFT)

btn_transcribe = tk.Button(root, text="Transcribe File", command=transcribe)
btn_transcribe.pack(pady=5)

# Live recording controls frame
frame_live = tk.Frame(root)
frame_live.pack(pady=10)

btn_start = tk.Button(frame_live, text="Start Recording", command=start_recording)
btn_start.pack(side=tk.LEFT, padx=5)

btn_stop = tk.Button(frame_live, text="Stop Recording", command=stop_recording)
btn_stop.pack(side=tk.LEFT, padx=5)

btn_transcribe_live = tk.Button(frame_live, text="Transcribe Live", command=transcribe_live)
btn_transcribe_live.pack(side=tk.LEFT, padx=5)

btn_retake = tk.Button(frame_live, text="Retake", command=retake)
btn_retake.pack(side=tk.LEFT, padx=5)

# Text output
text_output = tk.Text(root, height=15, width=60)
text_output.pack(padx=10, pady=10)

root.mainloop()
