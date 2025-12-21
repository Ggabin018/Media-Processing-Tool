from toolbox.exceptions import FileTypeError

def exception_as_str(n_return_value=1):
    def dec(f):
        def wrap(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                e = str(e)
                if n_return_value > 1:
                    return e, *([""] * (n_return_value - 1))
                return e
            
        return wrap
    return dec