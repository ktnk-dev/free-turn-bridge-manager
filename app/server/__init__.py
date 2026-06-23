import os
from dotenv import load_dotenv
load_dotenv()

from .config import getConfig
from .install import installLegacyProxy
from .common import getLegacyFolder

def run():
    installLegacyProxy()
    path = getLegacyFolder()
    config = getConfig()
    os.system(f"{path}/server-linux-amd64 -listen 0.0.0.0:{config.legacy_server_port} -connect 127.0.0.1:{config.wireguard_port} -wrap -wrap-key {config.wrap_key}")
    