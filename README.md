# FreeTurn Bridge Manager
Проект, нацеленный на запуск дополнительного старого ядра для поддержки iOS клиентов в единой FreeTurn "экосистеме", позволяя управлять ключами из приложения на андроид, автоматически генерировать их iOS версию, *и, потенцаильно, с управлением через Telegram бота*

- Основное ядро: [samosvalishe/free-turn-proxy](https://github.com/samosvalishe/free-turn-proxy)
- Старое ядро: [samosvalishe/vk-turn-proxy](https://github.com/samosvalishe/vk-turn-proxy)

- Клиент на Android: [samosvalishe/turn-proxy-android](https://github.com/samosvalishe/turn-proxy-android/)
- Клиент на iOS: [anton48/vk-turn-proxy-ios](https://github.com/anton48/vk-turn-proxy-ios/)

## Отправка ключей
Боту можно отправить `freeturn://` ссылку, и он автоматически сконвертирует ее в `vkturnproxy://` формат, текст можно отредактировать в файле [`text.txt`](./text.txt), он поддерживает следующие переменные:
- `{freeturn_url}`: Ключ формата `freeturn://` для Android клиента
- `{vkturnproxy_url}`: Ключ формата `vkturnproxy://` для iOS клиента

## Зависимости
- Ожидается, что Вы уже установили Freeturn на сервер в *АВТОМАТИЧЕСКОМ* режиме
- Python зависимости: `pytelegrambotapi`, `pysocks`, `pydantic`, `dotenv` (подробнее [тут](./pyproject.toml))
- Старое ядро установится автоматически, также будут сгенерированы все правильные параметры

## Как запустить?
1. Автоматически в докере `не тестировалось`
2. Самостоятельно установить зависимости и запустить через `-m app`

В обоих случаях нужно предварительно заполнить `.env`, подробнее [тут](./.env.example)

