import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def select_mp4_file():
    mp4_file_path = filedialog.askopenfilename(title="Выберите MP4 файл", filetypes=[("MP4 files", "*.mp4")])
    if mp4_file_path:
        mp4_label.config(text=mp4_file_path)

def select_srt_file():
    srt_file_path = filedialog.askopenfilename(title="Выберите SRT файл", filetypes=[("SRT files", "*.srt")])
    if srt_file_path:
        srt_label.config(text=srt_file_path)

def process_files():
    mp4_file = mp4_label.cget("text")
    srt_file = srt_label.cget("text")
    if not mp4_file or mp4_file == "Выберите MP4 файл":
        messagebox.showerror("Ошибка", "Пожалуйста, выберите MP4 файл.")
        return
    if not srt_file or srt_file == "Выберите SRT файл":
        messagebox.showerror("Ошибка", "Пожалуйста, выберите SRT файл.")
        return
    
    # Здесь вы можете добавить код для обработки выбранных файлов
    messagebox.showinfo("Информация", "Файлы успешно выбраны:\nMP4: {}\nSRT: {}".format(mp4_file, srt_file))

# Создание основного окна
root = tk.Tk()
root.title("Выбор файлов MP4 и SRT")

# Кнопки для выбора файлов
mp4_button = tk.Button(root, text="Выбрать MP4 файл", command=select_mp4_file)
mp4_button.pack(pady=10)

mp4_label = tk.Label(root, text="Выберите MP4 файл")
mp4_label.pack(pady=5)

srt_button = tk.Button(root, text="Выбрать SRT файл", command=select_srt_file)
srt_button.pack(pady=10)

srt_label = tk.Label(root, text="Выберите SRT файл")
srt_label.pack(pady=5)

process_button = tk.Button(root, text="Обработать файлы", command=process_files)
process_button.pack(pady=20)

# Запуск основного цикла
root.mainloop()