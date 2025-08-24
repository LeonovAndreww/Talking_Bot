import requests
import telebot
from bs4 import BeautifulSoup
from transliterate import translit

bot = telebot.TeleBot('empty')
urlquotes = 'https://citaty.info/random'
urlimages = 'https://www.generatormix.com/random-image-generator'
urljokes = 'https://newostrie.ru/anec-random'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.141 YaBrowser/22.3.3.852 Yowser/2.5 Safari/537.36'}

WEATHER_API_KEY = 'empty'


@bot.message_handler(content_types=['text', 'document', 'audio'])
def get_text_messages(message):
    text = message.text.lower()
    if text == "привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif text == "/help":
        bot.send_message(message.from_user.id,
                         "Все функции бота управляются при помощи кнопок, но, в случае чего, ниже есть список команд: \n /help \n Привет \n Цитата \n Картинка \n Анекдот \n Погода")
    elif text == "цитата":
        qresponse = requests.get(urlquotes, headers=headers)
        qsoup = BeautifulSoup(qresponse.text, 'lxml')
        quotes_block = qsoup.find('div', class_='field-name-body')
        if quotes_block:
            p_tag = quotes_block.find('p')
            if p_tag:
                quote_text = p_tag.get_text(strip=True)
                bot.send_message(message.from_user.id, quote_text)
            else:
                bot.send_message(message.from_user.id, "Не удалось получить цитату. Попробуй позже.")
        else:
            bot.send_message(message.from_user.id, "Не удалось получить цитату. Попробуй позже.")

    elif text == 'картинка':
        iresponse = requests.get(urlimages)
        isoup = BeautifulSoup(iresponse.text, 'lxml')
        iimage = isoup.find('img', class_='lazy thumbnail')
        if iimage and 'data-src' in iimage.attrs:
            bot.send_photo(message.from_user.id, iimage['data-src'])
        else:
            bot.send_message(message.from_user.id, "Не удалось получить картинку.")

    elif text == 'анекдот':
        jresponse = requests.get(urljokes)
        jsoup = BeautifulSoup(jresponse.text, 'lxml')
        joke = jsoup.find('div', class_='value p-3')
        if joke:
            bot.send_message(message.from_user.id, joke.text)
        else:
            bot.send_message(message.from_user.id, "Не удалось получить анекдот.")

    elif text == 'погода':
        weather_message = bot.send_message(message.from_user.id,
                                           'Введи город, в котором хочешь узнать погоду: ')
        bot.register_next_step_handler(weather_message, get_city)
    else:
        bot.send_message(message.from_user.id,
                         "Извиняюсь, но я не понимаю, что вы говорите. Для получения списка команд напишите /help")


def get_city(message):
    city = message.text.strip()

    if any('а' <= c <= 'я' or 'А' <= c <= 'Я' for c in city):
        city_eng = translit(city, 'ru', reversed=True)
    else:
        city_eng = city

    urlweather = f'https://api.openweathermap.org/data/2.5/weather?q={city_eng}&units=metric&appid={WEATHER_API_KEY}&lang=ru'

    try:
        resp = requests.get(urlweather, timeout=5)
        data = resp.json()
        if resp.status_code == 200:
            weather = data['weather'][0]['description'].capitalize()
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            icon = data['weather'][0]['icon']
            weather_image = f"http://openweathermap.org/img/wn/{icon}@2x.png"

            weather_message = f"Погода: {weather}\nТемпература: {temp}°C\nВлажность: {humidity}%\nВетер: {wind} м/с"
            bot.send_photo(message.from_user.id, weather_image, caption=weather_message)
        else:
            bot.send_message(message.from_user.id,
                             f"Не удалось получить погоду для города {city}. Код ошибки: {resp.status_code}")
    except Exception as e:
        bot.send_message(message.from_user.id, f"Произошла ошибка при получении погоды: {e}")


bot.polling(none_stop=True, interval=0)
