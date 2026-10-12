import json


def messages_to_db_form(messages):
    return json.dumps(messages, ensure_ascii=False, separators=(",", ":"))

def messages_from_db_form(message_str):
    if not message_str:
        return []

    try:
        messages = json.loads(message_str)
    except json.JSONDecodeError:
        messages = []
        for line in message_str.split("/n"):
            if not line:
                continue
            try:
                role, content = line.removeprefix("Role: ").split(" Content: ", 1)
            except ValueError:
                continue
            messages.append({"role": role.strip(), "content": content.strip()})

    if not isinstance(messages, list):
        return []
    return [
        {
            "role": "assistant" if message.get("role") == "bot" else message["role"],
            "content": message["content"],
        }
        for message in messages
        if isinstance(message, dict)
        and isinstance(message.get("role"), str)
        and isinstance(message.get("content"), str)
    ]