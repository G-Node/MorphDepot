from __future__ import division, unicode_literals, print_function

import logging

LEVEL = logging.DEBUG
LOGFILE = "morph.log"

logging.basicConfig(level=LEVEL)


def logged(func):

    def fnstringify(func, args):
        fnstr = func.__module__
        if len(args) > 0 and hasattr(args[0], '__class__'):
            fnstr = args[0].__class__.__name__
        fnstr += "." + func.__name__ + "(" + repr(args) + ")"
        return fnstr

    def wrap(*args, **kwargs):
        fnstr = fnstringify(func, args)
        logging.log(LEVEL, " --> calling %s", fnstr)
        result = func(*args, **kwargs)
        logging.log(LEVEL, " <-- %s returned %s", fnstr, repr(result))
        return result

    return wrap