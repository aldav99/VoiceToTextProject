import os
import tkinter as tk
from tkinter import filedialog, messagebox
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment

# Путь для сохранения загруженных файлов
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


def process_video(video_path):
    # Извлекаем аудио из видео
    audio_path = video_path.replace('.mp4', '.wav')
    video_clip = mp.VideoFileClip(video_path)
    if video_clip.audio is not None:  # Проверяем, есть ли аудиодорожка
        video_clip.audio.write_audiofile(audio_path, codec='pcm_s16le')
    else:
        messagebox.showerror("Ошибка", "Видео не содержит аудиодорожки.")
        return

    # Распознаем речь
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(audio_path)
    audio.export(audio_path, format="wav")  # Преобразуем в нужный формат
    text_file_path = video_path.replace('.mp4', '.txt')

    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            # Используем Google Cloud для распознавания речи
            text = recognizer.recognize_google_cloud(audio_data,
                                                     language='en-US')
            with open(text_file_path, 'w') as text_file:
                text_file.write(text)

            messagebox.showinfo(
                "Успех", f"Распознанный текст сохранен в {text_file_path}.")
        except sr.UnknownValueError:
            messagebox.showerror("Ошибка", "Не удалось распознать речь.")
        except sr.RequestError as e:
            messagebox.showerror("Ошибка",
                                 f"Ошибка сервиса распознавания речи: {e}")

    # Удаляем временные файлы
    video_clip.close()
    os.remove(audio_path)



def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
    if file_path:
        process_video(file_path)


# Настройка интерфейса
root = tk.Tk()
root.title("Распознавание речи из видео")

select_button = tk.Button(root, text="Выбрать MP4 файл", command=select_file)
select_button.pack(pady=20)

root.mainloop()
