from multiprocessing import Process

import bot, server

if __name__ == '__main__':
    bot_process = Process(target=bot.run)
    server_process = Process(target=server.run)

    bot_process.start()
    server_process.start()

    bot_process.join()
    server_process.join()