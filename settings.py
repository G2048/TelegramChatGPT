LogConfig = {
    'version': 1,
    'formatters': {
        'details': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s::%(levelname)s::%(name)s::%(levelno)s::%(lineno)s::%(message)s',
            'incremental': True,
        },
    },
    'handlers': {
        'rotate': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'telegram.log',
            'mode': 'w',
            'level': 'DEBUG',
            'maxBytes': 204800,
            'backupCount': 3,
            'formatter': 'details',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'details',
        },
    },
    'loggers': {
        '': {
            'level': 'NOTSET',
            'handlers': ['rotate', 'console'],
        },
        'consolemode': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    }
}
