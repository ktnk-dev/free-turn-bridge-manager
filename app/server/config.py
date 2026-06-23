import json
from pydantic import BaseModel
from .common import getLegacyFolder


class Config(BaseModel):
    wireguard_port: int
    legacy_server_port: int
    wrap_key: str

def getConfig() -> Config:
    path = getLegacyFolder()
    with open(f'{path}/config.json', 'r') as f:
        data = json.load(f)
    return Config(**data)

def setConfig(config: Config):
    path = getLegacyFolder()
    with open(f'{path}/config.json', 'w') as f:
        json.dump(config.model_dump(), f)