import os
import random
import requests
from .common import getLegacyFolder
from .config import Config, setConfig

def installLegacyProxy():
    path = getLegacyFolder()
    if len(os.getenv('TELEGRAM_BOT_PROXY', '')) < 2:
        proxy = None
    else:
        proxy = {'http': os.getenv('TELEGRAM_BOT_PROXY', ''), 'https': os.getenv('TELEGRAM_BOT_PROXY', '')}
    response = requests.get('https://github.com/samosvalishe/vk-turn-proxy/releases/latest/download/server-linux-amd64', proxies=proxy)
    with open(f'{path}/server-linux-amd64', 'wb') as f:
        f.write(response.content)
    
    os.system(f'chmod +x {path}/server-linux-amd64')
        
    if 'config.json' in os.listdir(path): return
    
    os.system(f'{path}/server-linux-amd64 -gen-wrap-key > {path}/wrapkey.txt')
    with open(f'{path}/wrapkey.txt', 'r') as f:
        wrap_key = f.read().strip()
    
    if len(wrap_key) == 0:
        raise ValueError("Failed to generate wrap key")

    with open(f'{os.getenv("FREE_TURN_PROXY_INSTALLATION", "/opt/free-turn-proxy")}/run.args', 'r') as f:
        run_args = f.read().strip()
        
        for i, line in enumerate(run_args.split('\n')):
            if '-connect' in line or '127.0.0.1' in line:
                next_line = line if '127.0.0.1' in line else run_args.split('\n')[i+1]
                wireguard_port = int(next_line.split(':')[-1].strip())

    setConfig(
        Config(
            wireguard_port=wireguard_port, 
            legacy_server_port=random.randint(56000, 59999), 
            wrap_key=wrap_key
        )
    )