import logging

# TODO: Docu

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
    if message in buffer[level]:
        return True
    else:
        buffer[level].append(message)


def debug(message, repeat=True):
    if not repeat and check_already_sent(message, 'debug'):
        return
    else:
        print('[DEBUG] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.debug(message)
        else:
            pre_start_buffer['debug'].append(message)


def info(message, repeat=True):
    if not repeat and check_already_sent(message, 'info'):
        return
    else:
        print('[INFO] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.info(message)
        else:
            pre_start_buffer['info'].append(message)


def warning(message, repeat=True):
    if not repeat and check_already_sent(message, 'warning'):
        return
    else:
        print('[WARNING] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.warning(message)
        else:
            pre_start_buffer['warning'].append(message)


def error(message, repeat=True):
    if not repeat and check_already_sent(message, 'error'):
        return
    else:
        print('[ERROR] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.error(message)
        else:
            pre_start_buffer['error'].append(message)


def critical(message, repeat=True):
    if not repeat and check_already_sent(message, 'critical'):
        return
    else:
        print('[CRITICAL] ' + message)
        if len(logging.getLogger().handlers) > 0:
            logging.critical(message)
        else:
            pre_start_buffer['critical'].append(message)