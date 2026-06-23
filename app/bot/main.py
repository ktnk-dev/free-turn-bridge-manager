from telebot.types import Message
from telebot.handler_backends import ContinueHandling

from .bot import bot, ADMINS
from .convert import convert
from server.config import getConfig

@bot.message_handler(content_types=['text'], func=lambda message: str(message.from_user.id) in ADMINS)
def handler(message: Message):
    if not message.text: return ContinueHandling()
    print(message.text)
    if 'start' in message.text:
        return bot.reply_to(message, 'Отправь <code>freeturn://</code> ссылку, и она будет сконвертирована')
        
    config = getConfig()
    try: vkturnproxy = convert(message.text, config.legacy_server_port, config.wrap_key)
    except Exception as error:
        return bot.reply_to(message, f'<b>Произошла ошибка</b>\n<code>{error}</code>')
    
    struct = {
        'freeturn_url': message.text,
        'vkturnproxy_url': vkturnproxy
    }
    
    with open('text.txt', 'r') as text:
        content = text.read().format(**struct)

    return bot.send_message(message.chat.id, content, disable_web_page_preview=True)