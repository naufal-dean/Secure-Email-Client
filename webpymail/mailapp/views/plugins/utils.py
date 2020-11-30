import re
from hashlib import md5


def get_text_plain(message):
    text = ''
    for part in message.bodystructure.serial_message():
        if part.is_text() and part.is_plain():
            text += message.part(part)
    return text


def check_digital_signature(text):
    match = re.findall(r'^(.*)\n\n<ds>(.*)</ds>$', text, re.DOTALL)
    if len(match) == 0:
        return False
    message, hash = match[0]
    valid = md5(message.encode('utf-8')).hexdigest() == hash
    return valid
