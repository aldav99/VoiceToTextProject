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

# MODEL_PATH = "c:\\vosk-model-small-en-us-0.15"
MODEL_PATH = "c:\\vosk-model-en-us-0.22"

if not os.path.exists(MODEL_PATH):
    messagebox.showerror("Ошибка", "Модель Vosk не найдена.")
    exit(1)

model = Model(MODEL_PATH)

def process_video(video_path):
    try:
        audio_path = video_path.replace('.mp4', '.wav')
        # audio_path = r"E:\1 Getting Started (01-07)\python_example_test.wav"
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
        text_file_path = video_path.replace('.mp4', '.txt')
        
        result_text = ""

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                # print("Intermediate result structure:", json.dumps(result, indent=4, ensure_ascii=False))
                if "result" in result:
                    words = result["result"]
                    if words:
                        # Получаем начало и конец
                        start_time = words[0]["start"]
                        end_time = words[-1]["end"]
                        
                        processed_result = {
                            "start": start_time,
                            "end": end_time,
                            "text": result.get("text", "")
                        }

                        start_time = processed_result['start']
                        end_time = processed_result['end']
                        word = processed_result['text']
                        result_text += f"[{start_time:.2f}-{end_time:.2f}] {word}\n "
                        # Добавляем текст к финальному результату
                        # final_text += processed_result["text"] + " "
                        # Здесь можно дополнительно обработать processed_result, например, записать в файл или вывести на экран
                print("Intermediate result:", processed_result)  # Отладочный вывод
                # if 'result' in result:
                #     for word_info in result['result']:
                #         start_time = word_info['start']
                #         end_time = word_info['end']
                #         word = word_info['text']
                #         result_text += f"[{start_time:.2f}-{end_time:.2f}] {word} "

        # final_result = json.loads(recognizer.FinalResult())
        # print("Final result:", final_result)  # Отладочный вывод
        # if 'result' in final_result:
        #     for word_info in final_result['result']:
        #         start_time = word_info['start']
        #         end_time = word_info['end']
        #         word = word_info['text']
        #         result_text += f"[{start_time:.2f}-{end_time:.2f}] {word} "

        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(result_text)

        messagebox.showinfo("Успех", f"Распознанный текст сохранен в {text_file_path}.")

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