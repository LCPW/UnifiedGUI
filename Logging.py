# https://docs.python.org/3/library/logging.html

# LOG_LEVELS = ['ERROR', 'WARNING']

def log(message, log_level):
    # TODO: Let user define a log level threshold?
    # Console logging
    # TODO: use warning instead of print
    print('[' + str(log_level) + '] ' + message)
    # TODO: Log in GUI