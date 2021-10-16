# Telegram Bot Translator
```
Версия 1.0 (skeleton)
```
Бот-переводчик. Умеет переводить с русского на английский и наоборот. При
желании количество доступных языков можно увеличить в файле translators.py.
Ещё бот умеет показывать котиков для поднятия настроения.
Бот написан в личных целях и находится на стадии тестирования.

## Технологии
- Python 3.8
- Aiogram 2.15
- Googletrans 4.0.0rc1
- Docker 3.8

## Запуск проекта
Для запуска проекта нужен телеграм-бот.

### Первый способ
1. Клонируйте репозиторий
```
https://github.com/Darya-Kuzmich/telegram-bot-translator.git
```
2. В директории telegram-bot-translator создайте файл .env и поместите туда
   переменные окружения в формате имя_переменной=значение. Пример:
```
TRANSLATE_BOT_TELEGRAM_TOKEN=your_bot_telegram_token
```
3. Активируйте виртуальное окружение.
4. Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
5. Отправьте на исполнение

### Второй способ
В этом случае потребуется Docker https://docs.docker.com/engine/install/
1. Клонируйте репозиторий
```
https://github.com/Darya-Kuzmich/telegram-bot-translator.git
```
2. В директории telegram-bot-translator создайте файл .env и поместите туда
   переменные окружения в формате имя_переменной=значение. Пример:
```
TRANSLATE_BOT_TELEGRAM_TOKEN=your_bot_telegram_token
```
3. В директории telegram-bot-translator выполните команду
```
docker build -t <some_image_name> .
```
4. После сборки образа запустите контейнер командой
```
docker run -it <some_image_name>
```

## Разработчик
Дарья Кузьмич