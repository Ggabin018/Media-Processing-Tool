import functools


def exception_as_str(n_return_value: int = 1):
    """
    Catch any exception and return it as an "Error: ..." string, so Gradio shows it instead of crashing.
    Always use it with parentheses: @exception_as_str() or @exception_as_str(2).

    :param n_return_value: number of values the function returns (Gradio outputs);
                           the error goes in the first one, the others are None
    """
    def dec(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                msg = f"Error: {e}"
                if n_return_value > 1:
                    return msg, *([None] * (n_return_value - 1))
                return msg
        return wrap
    return dec
