import inspect


def arg_name(arg):
    return inspect.getargspec(arg)[0]


def pair_required(first, second):
    if (first or second) and (not first or not second):
            raise ValueError(
                "'%s', '%s' required to both be provided" % (arg_name(first),
                                                             arg_name(second))
            )


def expected_be(p_object, class_or_type_or_tuple):
    if not isinstance(p_object, class_or_type_or_tuple):
        raise TypeError("'%s' expected to be '%s'."
                        % (arg_name(p_object), type(class_or_type_or_tuple)))
