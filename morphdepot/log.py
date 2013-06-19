import logging

logging.basicConfig(level=logging.DEBUG)


def logged(func, level=logging.INFO):

    def wrap(*args, **kwargs):
        fqn = ""
        if func.__module__ is not None:
            fqn += func.__module__ + "."
        if func.__class__ is not None:
            fqn += func.__class__.__name__ + "."
        fqn += func.__name__ + "( " + repr(kwargs) + " )"
        logging.log(level, "going go call %s", fqn)
        func(*args, **kwargs)
        logging.log(level, "%s was called without errors", fqn)

    return wrap