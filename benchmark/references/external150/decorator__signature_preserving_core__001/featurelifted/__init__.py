import functools, inspect
def decorate(func, caller):
    signature = inspect.signature(func)
    if inspect.iscoroutinefunction(caller):
        async def wrapped(*args, **kwargs):
            signature.bind(*args, **kwargs)
            return await caller(func, *args, **kwargs)
    else:
        def wrapped(*args, **kwargs):
            signature.bind(*args, **kwargs)
            return caller(func, *args, **kwargs)
    functools.update_wrapper(wrapped, func)
    wrapped.__signature__ = signature
    return wrapped
def decorator(caller, func=None):
    if func is not None: return decorate(func, caller)
    return lambda target: decorate(target, caller)
