import urllib.parse


def php_encode(data):
    params = {}

    for key, value in data.items():
        if value is None:
            continue

        if isinstance(value, str):
            params[key] = value
        elif isinstance(value, list):
            for index, v in enumerate(value):
                if isinstance(v, dict):
                    for dk, dv in v.items():
                        if dv is None:
                            continue

                        params['{0}[{1}][{2}]'.format(key, index, dk)] = dv
                else:
                    params['{0}[{1}]'.format(key, index)] = v
        elif isinstance(value, dict):
            for dk, dv in value.items():
                if dv is None:
                    continue

                params['{0}[{1}]'.format(key, dk)] = dv

    return urllib.parse.urlencode(params)
