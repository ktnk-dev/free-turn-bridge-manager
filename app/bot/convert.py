import base64
import binascii
import json
from typing import Any, Dict, Optional

SCHEME = "freeturn://"
SCHEMA_VERSION = 1


def convert(free_turn_url_format: str, override_port: int | bool = False, wrap: str | bool = False, require_vk_link: bool = False) -> str:
    """Convert `freeturn://...` payload into a `vkturnproxy://` import link.

    Args:
        require_vk_link: if True, raise when the FreeTurn link omits a vk.me/join token.
    """
    metadata = _decode_free_turn(free_turn_url_format)
    _ensure_udp_transport(metadata)
    settings = _build_turn_proxy_settings(metadata, override_port, wrap, require_vk_link)
    return _build_vkturnproxy_link(settings)


def _decode_free_turn(payload: str) -> Dict[str, Any]:
    if not payload.strip().startswith(SCHEME):
        raise ValueError(f"Ссылка должна начинаться с {SCHEME}")
    raw = payload.strip()[len(SCHEME) :]
    if not raw:
        raise ValueError("Ссылка не имеет данных")
    padded = raw + "=" * ((4 - len(raw) % 4) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded).decode("utf-8")
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Не удалось расшифровать ссылку") from exc
    return json.loads(decoded)


def _ensure_udp_transport(metadata: Dict[str, Any]) -> None:
    transport = str(metadata.get("transport", "")).lower()
    mode = str(metadata.get("mode", "")).lower()
    if "udp" not in transport and "udp" not in mode:
        raise ValueError("FreeTurn ссылка обязана использовать UDP transport и mode. Нужно перейти в настройки сервера и везде указать UDP (кроме DNS)")


def _build_turn_proxy_settings(metadata: Dict[str, Any], override_port: int | bool = False, wrap: str | bool = False, require_vk_link: bool = False) -> Dict[str, Any]:
    wg_conf = str(metadata.get("wg", "")).strip()
    if not wg_conf:
        raise ValueError("FreeTurn ссылка не содержит конфигурацию WireGuard")

    sections = _parse_wg_conf(wg_conf)
    interface = sections.get("interface")
    if not interface:
        raise ValueError("Конфигурация WireGuard не имеет секции [Interface]")
    peer_section = _extract_peer_section(sections)

    private_key = interface.get("privatekey")
    if not private_key:
        raise ValueError("В секции [Interface] конфигурации WireGuard отсутствует PrivateKey")

    address = interface.get("address")
    if not address:
        raise ValueError("В секции [Interface] конфигурации WireGuard отсутствует Address")
    tunnel_address = address.split(",")[0].strip()

    peer_public_key = peer_section.get("publickey")
    if not peer_public_key:
        raise ValueError("В секции [Peer] конфигурации WireGuard отсутствует PublicKey")

    endpoint = peer_section.get("endpoint")
    if not endpoint:
        raise ValueError("В секции [Peer] конфигурации WireGuard отсутствует Endpoint")

    vk_link: Optional[str] = None
    if require_vk_link:
        vk_link = _find_vk_join_link(metadata)
    else:
        try:
            vk_link = _find_vk_join_link(metadata)
        except ValueError:
            vk_link = None
            
    peer = metadata.get("peer")
    if not peer: 
        raise ValueError("FreeTurn ссылка не содержит адрес пира")
    
    if override_port:
        peer = peer.rsplit(":", 1)[0] + f":{override_port}"
    
        

    settings: Dict[str, Any] = {
        # Required fields
        "privateKey": private_key,
        "peerPublicKey": peer_public_key,
        "tunnelAddress": tunnel_address,
        "vkLink": vk_link if vk_link else 'REPLACE_ME',
        "peerAddress": peer,
        
        # Optional fields (backward compatablility with < 129 builds)
        "useDTLS": True,
        "useWrap": True if wrap else False,
        "wrapKeyHex": wrap if wrap else '',  
        "numConnections": 15,
        "useUDP": True,
        "useWrapA": False,
    }
    print(json.dumps(metadata, indent=2))
    print(json.dumps(settings, indent=2))

    preshared = peer_section.get("presharedkey")
    if preshared:
        settings["presharedKey"] = preshared

    dns = metadata.get("dnss") or interface.get("dns")
    if dns:
        settings["dnsServers"] = dns

    return settings


def _parse_wg_conf(conf: str) -> Dict[str, Dict[str, str]]:
    sections: Dict[str, Dict[str, str]] = {}
    current = ""
    for line in conf.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1].strip().lower()
            sections.setdefault(current, {})
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        target = sections.setdefault(current, {})
        target[key.strip().lower()] = value.strip()
    return sections


def _extract_peer_section(sections: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    peers = [section for name, section in sections.items() if name.startswith("peer")]
    if not peers:
        raise ValueError("Конфигурация WireGuard не имеет секции [Peer]")
    return peers[0]


def _find_vk_join_link(metadata: Dict[str, Any]) -> str:
    candidates = (
        metadata.get("peer"),
        metadata.get("vkLink"),
        metadata.get("provider"),
        metadata.get("name"),
    )
    for raw in candidates:
        if not raw:
            continue
        lower = str(raw).lower()
        if "vk.me/join/" in lower:
            return raw if raw.startswith("https://") else f"https://{raw}".replace("https://https://", "https://")
    raise ValueError("FreeTurn ссылка должна содержать ссылку на звонок для параметра vkLink формата vkturnproxy")


def _build_vkturnproxy_link(settings: Dict[str, Any]) -> str:
    payload = {
        "version": SCHEMA_VERSION,
        "type": "connection",
        "settings": settings,
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    return f"vkturnproxy://import?data={b64}"


import sys
if __name__ == "__main__":
    try: print(convert(sys.argv[3], override_port=int(sys.argv[1]), wrap=sys.argv[2]))
    except IndexError:
        print("Usage: python freeturn-to-vkturnproxy.py <port> <wrap-key> <freeturn_url>")