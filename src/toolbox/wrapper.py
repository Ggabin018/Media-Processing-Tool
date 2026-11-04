import functools
import inspect


def exception_as_str(n_return_value: int = 1):
    """
    Catch any exception and return it as an "Error: ..." string, so Gradio shows it instead of crashing.
    Works on functions and on generators (the error becomes the last yielded value).
    Always use it with parentheses: @exception_as_str() or @exception_as_str(2).

    :param n_return_value: number of values the function returns (Gradio outputs);
                           the error goes in the first one, the others are None
    """
    def as_error(e: Exception):
        msg = f"Error: {e}"
        if n_return_value > 1:
            return msg, *([None] * (n_return_value - 1))
        return msg

    def dec(f):
        if inspect.isgeneratorfunction(f):
            @functools.wraps(f)
            def gen_wrap(*args, **kwargs):
                try:
                    yield from f(*args, **kwargs)
                except Exception as e:
                    yield as_error(e)
            return gen_wrap

        @functools.wraps(f)
        def wrap(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                return as_error(e)
        return wrap
    return dec
