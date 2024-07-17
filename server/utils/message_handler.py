def messages_to_db_form(messages):
    str = ""
    for message in messages:
        str += "Role: " + message["role"] + \
            " Content: " + message["content"] + "/n"
    return str

def messages_from_db_form(message_str):
    if not message_str:
        return []
    else:
        messages = []
        for line in message_str.split("/n"):
            if line == "": continue
            role = line.split("Role: ")[1].split(" Content: ")[0].strip()
            content = line.split("Role: ")[1].split(" Content: ")[1].strip()
            messages.append({"role": role, "content": content})
        return messages