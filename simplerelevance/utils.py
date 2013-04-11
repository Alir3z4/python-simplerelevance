import inspect


def arg_name(arg):
    return inspect.getargspec(arg)[0]


def pair_required(first, second):
    if (first or second) and (not first or not second):
            raise ValueError(
                "'%s', '%s' required to both be provided" % (arg_name(first),
                                                             arg_name(second))
            )

