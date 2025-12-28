from toolbox.exceptions import FileTypeError

# TODO: oneline exception maybe 
def exception_as_str(n_return_value=1):
    """
    catch the exception, return it as a string (first value)
    
    :param n_return_value: the number of string to return
    """
    def dec(f):
        def wrap(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                e = str(e)
                if n_return_value > 1:
                    return e, *([None] * (n_return_value - 1))
                return e
            
        return wrap
    return dec