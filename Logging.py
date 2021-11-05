# https://docs.python.org/3/library/logging.html


# TODO: Log in GUI
# TODO: Let user define a log level threshold?
# TODO: use warning instead of print

buffer = {
    'debug': [],
    'info': [],
    'warning': [],
    'error': [],
    'critical': []
}


def check_already_sent(message, level):
    if message in buffer[level]:
        return True
    else:
        buffer[level].append(message)


def debug(message, repeat=True):
    if not repeat and check_already_sent(message, 'debug'):
        return
    else:
        print('[DEBUG] ' + message)


def info(message, repeat=True):
    if not repeat and check_already_sent(message, 'info'):
        return
    else:
        print('[INFO] ' + message)


def warning(message, repeat=True):
    if not repeat and check_already_sent(message, 'warning'):
        return
    else:
        print('[WARNING] ' + message)


def error(message, repeat=True):
    if not repeat and check_already_sent(message, 'error'):
        return
    else:
        print('[ERROR] ' + message)


def critical(message, repeat=True):
    if not repeat and check_already_sent(message, 'critical'):
        return
    else:
        print('[CRITICAL] ' + message)