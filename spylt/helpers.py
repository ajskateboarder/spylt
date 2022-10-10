def js_list(encoder, data):
    pairs = []
    for v in data:
        pairs.append(js_val(encoder, v))
    return "[" + ", ".join(pairs) + "]"


def js_dict(encoder, data):
    pairs = []
    for k, v in data.items():
        pairs.append(k + ": " + js_val(encoder, v))
    return "{" + ", ".join(pairs) + "}"


def js_val(encoder, data):
    if isinstance(data, dict):
        val = js_dict(encoder, data)
    elif isinstance(data, list):
        val = js_list(encoder, data)
    else:
        val = encoder.encode(data)
    return val


def replace_some(text, conversion_dict):
    for key, value in conversion_dict.items():
        text = text.replace(key, value)
    return text


def find_pointer(path):
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
        if not 'point' in lines[0]:
            raise RuntimeError(
                "No Python file is being pointed to. "
                "Please add a comment at the top of your Svelte code "
                "(ex: <!-- point App.py:app -->)"
            )
        pointer = lines[0].replace('point', '').replace('<!--', '').replace('-->', '').replace(' ', '').strip()
        return pointer
