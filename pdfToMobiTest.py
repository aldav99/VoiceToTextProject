import os
import subprocess
import time
import telebot
from gtts import gTTS
from openai import OpenAI

API_KEY = '7432911185:AAFQpTAW2LBeclTNCYXc4GCL9fl43YgmAYA'

client = OpenAI(
    api_key="sk-eojihWMYuwlwO4oNjNMX8DbkkkBtLg7I",
    base_url="https://api.proxyapi.ru/openai/v1",
)

bot = telebot.TeleBot(API_KEY)

def convert_to_mobi(input_file, output_file):
    try:
        subprocess.run(['ebook-convert', input_file, output_file], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def generate_text_with_gpt(filename, conversion_time):
    prompt = f"Create a message to inform the user that the file '{filename}' has been successfully converted in {conversion_time:.2f} seconds."
    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "отвечай в стиле веселого клоуна"},
            {"role": "user", "content": prompt}
        ]
    )
    response = chat_completion.choices[0].message.content
    return response

def text_to_speech(text, filename='output.mp3'):
    tts = gTTS(text=text, lang='ru')
    tts.save(filename)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать! Отправьте мне файл в формате PDF, FB2 или EPUB, и я сконвертирую его в MOBI.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        input_file_path = f"./{message.document.file_name}"
        output_file_path = input_file_path.rsplit('.', 1)[0] + '.mobi'

        with open(input_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        start_time = time.time()
        if convert_to_mobi(input_file_path, output_file_path):
            conversion_time = time.time() - start_time
            with open(output_file_path, 'rb') as mobi_file:
                bot.send_document(message.chat.id, mobi_file)
            # Создаем сообщение с помощью GPT-3.5
            speech_text = generate_text_with_gpt(message.document.file_name, conversion_time)
            text_to_speech(speech_text)

            with open('output.mp3', 'rb') as audio:
                bot.send_voice(message.chat.id, audio)

            os.remove(output_file_path)
            os.remove('output.mp3')
        else:
            bot.reply_to(message, "Не удалось конвертировать файл.")

        os.remove(input_file_path)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {str(e)}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Отправьте файл для конвертации.")

bot.polling()