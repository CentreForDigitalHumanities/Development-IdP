import os

def discover(key, default=None):
    """
    Discovers a variable from a docker-compose secret or
    environment variable, in that order.
    """
    key = str(key)
    if os.path.isdir("/run/secrets") and key in os.listdir('/run/secrets/'):
        with open('/run/secrets/' + key) as file:
            return file.read().strip()
    elif key in os.environ:
        return os.environ.get(key)
    else:
        if default is not None:
            return default
        raise Exception("Failure: " + key + ' not found')


def discover_list(key, default=None):
    """
    Discovers a list-like variable from a docker-compose secret
    or environment variable, in that order. It expects the variable
    to be formatted as a newline-separated list.
    """
    try:
        raw = discover(key)
    except Exception as e:
        if default is not None:
            return default
        else:
            raise e
    return "\n".split(raw)
