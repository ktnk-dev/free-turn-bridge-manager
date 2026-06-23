import os

def getLegacyFolder():
    path = os.getenv("VK_TURN_PROXY_INSTALLATION", '/opt/vk-turn-proxy-legacy')
    try: os.mkdir(path)
    except FileExistsError: pass  
    return path