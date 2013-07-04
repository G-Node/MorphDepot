from __future__ import division, unicode_literals, print_function

import logging

LEVEL = logging.DEBUG
LOGFILE = "morph.log"

logging.basicConfig(level=LEVEL)


def logged(func):

    def fnstringify(func, args):
        fnstr = func.__module__
        if len(args) > 0 and "__class__" in dir(args[0]):
            fnstr = args[0].__class__.__name__
        fnstr += "." + func.__name__ + "(" + str(args) + ")"
        return fnstr

    def wrap(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            fnstr = fnstringify(func, args)
            logging.log(LEVEL, "Called %s => %s", fnstr, str(result))
        except Exception as e:
            fnstr = fnstringify(func, args)
            logging.log(LEVEL, "Error while calling %s", fnstr)
            raise e
        return result

    return wrap