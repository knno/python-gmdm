import logging
from pprint import pformat
# -*- coding: utf-8 -*-
import coloredlogs

_FIELD_STYLES = {
    'asctime': {
        'color': 'white'
    },
    'hostname': {
        'color': 'magenta'
    },
    'levelname': {
        'color': 'black',
        'bold': True
    },
    'name': {
        'color': 'blue'
    },
    'programname': {
        'color': 'cyan'
    },
    'filename': {
        'color': 'green',
    },
    'lineno': {
        'color': 'green',
    },
}


def get_logger(verbosity=0, field_styles=None):
    """Return logger"""
    field_styles = field_styles if field_styles is not None else _FIELD_STYLES

    f_format = logging.Formatter(
        '%(asctime)s,%(msecs)03d %(name)s.%(levelname)-8s %(message)s', '%d-%b-%y %H:%M:%S')

    logging.basicConfig(level=verbosity)

    logger = logging.getLogger("GmDm")
    logger.propagate = False

    log_s_handler = logging.StreamHandler()
    log_s_handler.setLevel(verbosity)
    log_s_handler.setFormatter(f_format)
    logger.addHandler(log_s_handler)

    logger.setLevel(verbosity)

    logger.info_pretty = logger.pretty_info = lambda msg: logger.info(
        pformat(msg))
    logger.debug_pretty = logger.pretty_debug = lambda msg: logger.debug(
        pformat(msg))
    logger.warning_pretty = logger.pretty_warning = lambda msg: logger.warning(
        pformat(msg))
    logger.error_pretty = logger.pretty_error = lambda msg: logger.info(
        pformat(msg))

    if field_styles != False:
        coloredlogs.install(field_styles=field_styles,
                            level=verbosity, logger=logger, fmt=f_format._fmt,
                            datefmt=f_format.datefmt)

    return logger
