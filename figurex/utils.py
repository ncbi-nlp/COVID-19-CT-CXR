import os


def is_file_empty(pathanme):
    return os.path.exists(pathanme) and os.stat(pathanme).st_size == 0

def is_file_not_empty(pathanme):
    return os.path.exists(pathanme) and os.stat(pathanme).st_size != 0