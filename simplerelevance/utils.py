import inspect


def arg_name(arg):
    return inspect.getargspec(arg)[0]



