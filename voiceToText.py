import os
import tkinter as tk
from tkinter import filedialog, messagebox
import moviepy.editor as mp
from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment
import json

# Путь для сохранения загруженных файлов
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Укажите путь к модели Vosk
MODEL_PATH = "c:\\vosk-model-small-en-us-0.15"

# Загрузите модель Vosk
if not os.path.exists(MODEL_PATH):
    messagebox.showerror("Ошибка", "Модель Vosk не найдена.")
    exit(1)

model = Model(MODEL_PATH)

def process_video(video_path):
    # Извлекаем аудио из видео
    audio_path = video_path.replace('.mp4', '.wav')
    video_clip = mp.VideoFileClip(video_path)
    if video_clip.audio is not None:  # Проверяем, есть ли аудиодорожка
        temp_audio_path = video_path.replace('.mp4', '_temp.wav')
        video_clip.audio.write_audiofile(temp_audio_path, codec='pcm_s16le')

        # Преобразуем аудио в моно с помощью pydub
        audio = AudioSegment.from_wav(temp_audio_path)
        audio = audio.set_channels(1)
        audio.export(audio_path, format='wav')

        # Удаляем временный файл
        os.remove(temp_audio_path)
    else:
        messagebox.showerror("Ошибка", "Видео не содержит аудиодорожки.")
        return

    # Распознаем речь с использованием Vosk
    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        messagebox.showerror("Ошибка", "Аудиофайл должен быть в формате WAV моно PCM.")
        return

    recognizer = KaldiRecognizer(model, wf.getframerate())
    text_file_path = video_path.replace('.mp4', '.txt')

    result_text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            # Проверяем наличие ключа 'result'
            if 'result' in result:
                for word_info in result['result']:
                    start_time = word_info['start']
                    end_time = word_info['end']
                    word = word_info['word']
                    result_text += f"[{start_time:.2f}-{end_time:.2f}] {word}\n "

    # Обрабатываем финальный результат
    final_result = json.loads(recognizer.FinalResult())
    if 'result' in final_result:
        for word_info in final_result['result']:
            start_time = word_info['start']
            end_time = word_info['end']
            word = word_info['word']
            result_text += f"[{start_time:.2f}-{end_time:.2f}] {word} "

    with open(text_file_path, 'w') as text_file:
        text_file.write(result_text)

    messagebox.showinfo("Успех", f"Распознанный текст сохранен в {text_file_path}.")

    # Удаляем временные файлы
    video_clip.close()
    wf.close()
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

# Добавляем кнопку для закрытия программы
close_button = tk.Button(root, text="Закрыть", command=root.quit)
close_button.pack(pady=10)

root.mainloop()