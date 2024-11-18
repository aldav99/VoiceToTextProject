import os
import tkinter as tk
from tkinter import filedialog, messagebox
import moviepy.editor as mp
from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment
import json

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

MODEL_PATH = "c:\\vosk-model-en-us-0.22"

if not os.path.exists(MODEL_PATH):
    messagebox.showerror("Ошибка", "Модель Vosk не найдена.")
    exit(1)

model = Model(MODEL_PATH)

def format_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    hours = minutes // 60
    minutes %= 60
    return f"{hours:02}:{minutes:02}:{seconds % 60:02},{millis:03}"

def process_video(video_path):
    try:
        audio_path = video_path.replace('.mp4', '.wav')
        video_clip = mp.VideoFileClip(video_path)
        
        if video_clip.audio is not None:
            temp_audio_path = video_path.replace('.mp4', '_temp.wav')
            video_clip.audio.write_audiofile(temp_audio_path, codec='pcm_s16le')

            audio = AudioSegment.from_wav(temp_audio_path)
            audio = audio.set_channels(1)
            audio.export(audio_path, format='wav')

            os.remove(temp_audio_path)
        else:
            messagebox.showerror("Ошибка", "Видео не содержит аудиодорожки.")
            return

        wf = wave.open(audio_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            messagebox.showerror("Ошибка", "Аудиофайл должен быть в формате WAV моно PCM.")
            return

        recognizer = KaldiRecognizer(model, wf.getframerate())
        recognizer.SetWords(True)
        srt_file_path = video_path.replace('.mp4', '.srt')
        
        result_text = ""
        subtitle_index = 1

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if "result" in result:
                    words = result["result"]
                    if words:
                        # Получаем начало и конец
                        start_time = words[0]["start"]
                        end_time = words[-1]["end"]
                        text = result.get("text", "")

                        # Форматируем время в SRT
                        start_time_srt = format_time(start_time)
                        end_time_srt = format_time(end_time)
                        result_text += f"{subtitle_index}\n{start_time_srt} --> {end_time_srt}\n{text}\n\n"
                        subtitle_index += 1

                print("Intermediate result:", {"start": start_time, "end": end_time, "text": text})  # Отладочный вывод

        with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
            srt_file.write(result_text.strip())  # Убираем последний пустой перевод строки
        
        messagebox.showinfo("Успех", f"Распознанный текст сохранен в {srt_file_path}.")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    finally:
        video_clip.close()
        wf.close()
        if os.path.exists(audio_path):
            os.remove(audio_path)

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if file_path:
        process_video(file_path)

root = tk.Tk()
root.title("Распознавание речи из видео")

select_button = tk.Button(root, text="Выбрать MP4 файл", command=select_file)
select_button.pack(pady=20)

close_button = tk.Button(root, text="Закрыть", command=root.quit)
close_button.pack(pady=10)

root.mainloop()