import logging

LEVEL = logging.DEBUG
LOGFILE = "morph.log"

logging.basicConfig(level=LEVEL, filename=LOGFILE)


def logged(func, level=logging.INFO):

    def wrap(*args, **kwargs):
        fqn = ""
        if func.__module__ is not None:
            fqn += func.__module__ + "."
        if func.__class__ is not None:
            fqn += func.__class__.__name__ + "."
        fqn += func.__name__ + "( " + repr(*args) + " )"
        logging.log(level, "going go call %s", fqn)
        result = func(*args, **kwargs)
        logging.log(level, "result of %s was %s", fqn, str(result))
        return result

    return wrap