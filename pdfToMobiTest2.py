import os
import tkinter as tk
from tkinter import filedialog, messagebox
from ebooklib import epub
from pathlib import Path
import subprocess

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'fb2', 'epub'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_mobi(input_file):
    output_file = input_file.with_suffix('.mobi')
    # Используем Calibre для конвертации
    # Убедитесь, что Calibre установлен и доступен в командной строке
    subprocess.run(['ebook-convert', str(input_file), str(output_file)], check=True)
    return output_file

def upload_file():
    file_path = filedialog.askopenfilename(title="Выберите файл для конвертации", 
                                           filetypes=[("Ebook files", "*.pdf *.fb2 *.epub")])
    if not file_path:
        return

    filename = Path(file_path).name
    if not allowed_file(filename):
        messagebox.showerror("Ошибка", "Неподдерживаемый формат файла")
        return

    # Сохраняем файл в папке uploads
    save_path = Path(UPLOAD_FOLDER) / filename
    with open(file_path, 'rb') as fsrc:
        with open(save_path, 'wb') as fdst:
            fdst.write(fsrc.read())

    try:
        mobi_file = convert_to_mobi(save_path)
        messagebox.showinfo("Успех", f"Конвертация завершена! MOBI файл: {mobi_file}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при конвертации: {e}")

# Создаем основной интерфейс
root = tk.Tk()
root.title("Конвертер в MOBI")
root.geometry("400x200")

upload_button = tk.Button(root, text="Выбрать файл для конвертации", command=upload_file)
upload_button.pack(pady=20)

exit_button = tk.Button(root, text="Выход", command=root.quit)
exit_button.pack(pady=20)

root.mainloop()