from funcy import decorator


@decorator
async def log_fetch(call, print_func=print):
    print_func('FETCH ' + call.url)
    resp = await call()
    print_func(resp)
    return resp
