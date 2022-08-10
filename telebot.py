import requests
import telebot
from bs4 import BeautifulSoup

bot = telebot.TeleBot('empty')
urlquotes = 'https://citaty.info/random'
urlimages = 'https://www.generatormix.com/random-image-generator'
urljokes = 'https://newostrie.ru/anec-random'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.141 YaBrowser/22.3.3.852 Yowser/2.5 Safari/537.36'}


@bot.message_handler(content_types=['text', 'document', 'audio'])
def get_text_messages(message):
    if message.text.lower() == "привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Все функции бота управляются при помощи кнопок, но, в случае чего, ниже есть список команд: \n /help \n Привет \n Цитата \n Картинка \n Анекдот \n Погода")
    elif message.text.lower() == "цитата":
        qresponse = requests.get(urlquotes)
        qsoup = BeautifulSoup(qresponse.text, 'lxml')
        quotes = qsoup.find('div', class_='field-item even last')
        bot.send_message(message.from_user.id, quotes.text)
    elif message.text.lower() == 'картинка':
        iresponse = requests.get(urlimages)
        isoup = BeautifulSoup(iresponse.text, 'lxml')
        iimage = isoup.find('img', class_='lazy thumbnail')
        bot.send_photo(message.from_user.id, iimage['data-src'])
    elif message.text.lower() == 'анекдот':
        jresponse = requests.get(urljokes)
        jsoup = BeautifulSoup(jresponse.text, 'lxml')
        joke = jsoup.find('div', class_='value p-3')
        bot.send_message(message.from_user.id, joke.text)
    elif message.text.lower() == 'погода':
        weather_message = bot.send_message(message.from_user.id, 'Введи город, в котором хочешь узнать погоду: ')
        bot.register_next_step_handler(weather_message, get_city)
    else:
        bot.send_message(message.from_user.id, "Извиняюсь, но я не понимаю, что вы говорите. Для получения списка команд напишите /help")


def get_city(message):
    city = message.text
    urlweather = 'https://www.google.com/search?q=google+погода+' + city + '&sxsrf=ALiCzsZsJDdrnxCRqMgSBfmnQf_X7ebpAg%3A1651476478993&ei=_odvYt31O5T8rgSN3b6IBQ&ved=0ahUKEwjd7ImnpcD3AhUUvosKHY2uD1EQ4dUDCA4&uact=5&oq=google+погода+волгодонск&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIGCAAQFhAeMgkIABDJAxAWEB4yBggAEBYQHjIGCAAQFhAeMgYIABAWEB46CggAEEcQsAMQyQM6BwgAEEcQsAM6BwgAELADEEM6CAgAEIAEEMkDOgUIABCABDoICAAQDRAFEB5KBAhBGABKBAhGGABQyAFYsxBghBRoAXABeACAAWmIAYQIkgEDOS4ymAEAoAEByAEKwAEB&sclient=gws-wiz-serp'
    wresponse = requests.get(urlweather, headers=headers)
    # wresponse - 1) url 2) заголовки(типа хар-ка устройства)!
    wsoup = BeautifulSoup(wresponse.content, 'html.parser')
    weather_raw = wsoup.find("span", {'id': 'wob_dc'}).text
    temperature_raw = wsoup.find('span', {'class': 'wob_t q8U8x', 'id': 'wob_tm' }).text
    wind_raw = wsoup.find('span', {'class': 'wob_t', 'id': 'wob_ws'}).text
    rain_raw = wsoup.find('span', {'id': 'wob_pp'}).text
    wetness_raw = wsoup.find('span', {'id': 'wob_hm'}).text
    weather_image = 'https:' + wsoup.find('img', {'class': 'wob_tci'})['src']
    weather = 'Погода: ' + weather_raw
    temperature = 'Температура: ' + temperature_raw + '°C'
    wind = 'Ветер: ' + wind_raw
    rain = 'Вероятность дождя: ' + rain_raw
    wetness = 'Влажность: ' + wetness_raw
    weather_message = (weather + '\n' + temperature + '\n' + wind + '\n' + rain + '\n' + wetness)
    print(weather_image)
    bot.send_photo(message.from_user.id, weather_image, caption=weather_message)
    print(weather, '\n', temperature, '\n', wind)


bot.polling(none_stop=True, interval=0)
