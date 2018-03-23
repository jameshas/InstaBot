''' Simple module for text spinning in Python
Format: {choice1|choice2|...}
Supports nested spintax
'''

import random
import re

def _select(m):
    choices = m.group(1).split("|")
    return choices[random.randint(0, len(choices) - 1)]

def spin(text):
    r = re.compile("{([^{}]*)}")
    while True:
        text, n = r.subn(_select, text)
        if n == 0: break
    return text.strip()
