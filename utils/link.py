from urllib.parse import urlparse


def parse_message_link(link: str):
    """
    Return dict:
      - for private: {"chat_id": int, "message_id": int, "is_private": True}
      - for public:  {"username": str, "message_id": int, "is_private": False}
    Supported:
      https://t.me/c/<internal_id>/<msg_id>
      https://t.me/username/<msg_id>
    """
    if not link.startswith("http"):
        link = "https://" + link

    parsed = urlparse(link)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid Telegram link")

    if parts[0] == "c":
        internal_id = parts[1]
        msg_id = int(parts[2])
        chat_id = int("-100" + internal_id)
        return {"chat_id": chat_id, "message_id": msg_id, "is_private": True}
    else:
        username = parts[0]
        msg_id = int(parts[1])
        return {"username": username, "message_id": msg_id, "is_private": False}
