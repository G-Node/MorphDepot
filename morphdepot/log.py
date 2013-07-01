from __future__ import division, unicode_literals, print_function

import logging

LEVEL = logging.DEBUG
LOGFILE = "morph.log"

logging.basicConfig(level=LEVEL)


def logged(func):

    def make_fqn(func, *args):
        fqn = ""

        if func.__module__ is not None:
            fqn += func.__module__ + "."
        if func.__class__ is not None:
            fqn += func.__class__.__name__ + "."
        fqn += func.__name__ + "(" + repr(*args) + ")"

        return fqn

    def wrap(*args, **kwargs):
        fqn = make_fqn(func, *args)
        logging.log(LEVEL, "going go call %s", fqn)

        result = func(*args, **kwargs)

        logging.log(LEVEL, "result of %s was %s", fqn, str(result))
        return result

    return wrap