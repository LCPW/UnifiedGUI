import logging


buffer = {
    'debug': [],
    'info': [],
    'warning': [],
    'error': [],
    'critical': []
}

pre_start_buffer = {
    'debug': [],
    'info': [],
    'warning': [],
    'error': [],
    'critical': []
}


def init(log_text_edit):
    """
    Initializes the log.
    :param log_text_edit: Text edit widget where the log output should be displayed to the user.
    """
    log_text_edit.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(log_text_edit)
    logging.getLogger().setLevel(logging.DEBUG)
    for message in pre_start_buffer['debug']:
        logging.debug(message)
    for message in pre_start_buffer['info']:
        logging.info(message)
    for message in pre_start_buffer['warning']:
        logging.warning(message)
    for message in pre_start_buffer['error']:
        logging.error(message)
    for message in pre_start_buffer['critical']:
        logging.critical(message)


def check_already_sent(message, level):
    """
    Checks if a given message has already been sent in a given log level.
    :param message: Message to be checked.
    :param level: Log level.
    :return: Whether the message has already been sent.
    """
    if message in buffer[level]:
        return True
    else:
        buffer[level].append(message)
        return False


def debug(message, repeat=True):
    """
    Logs a message on debug level.
    :param message: Message to be logged.
    :param repeat: Whether the message should be repeated.
    """
    if not repeat and check_already_sent(message, 'debug'):
        return
    else:
        print('[DEBUG] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.debug(message)
        else:
            pre_start_buffer['debug'].append(message)


def info(message, repeat=True):
    """
    Logs a message on info level.
    :param message: Message to be logged.
    :param repeat: Whether the message should be repeated.
    """
    if not repeat and check_already_sent(message, 'info'):
        return
    else:
        print('[INFO] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.info(message)
        else:
            pre_start_buffer['info'].append(message)


def warning(message, repeat=True):
    """
    Logs a message on warning level.
    :param message: Message to be logged.
    :param repeat: Whether the message should be repeated.
    """
    if not repeat and check_already_sent(message, 'warning'):
        return
    else:
        print('[WARNING] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.warning(message)
        else:
            pre_start_buffer['warning'].append(message)


def error(message, repeat=True):
    """
    Logs a message on error level.
    :param message: Message to be logged.
    :param repeat: Whether the message should be repeated.
    """
    if not repeat and check_already_sent(message, 'error'):
        return
    else:
        print('[ERROR] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.error(message)
        else:
            pre_start_buffer['error'].append(message)


def critical(message, repeat=True):
    """
    Logs a message on critical level.
    :param message: Message to be logged.
    :param repeat: Whether the message should be repeated.
    """
    if not repeat and check_already_sent(message, 'critical'):
        return
    else:
        print('[CRITICAL] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.critical(message)
        else:
            pre_start_buffer['critical'].append(message)