import json


def to_json(name, *args):

    with open('codes.json', 'r', encoding='utf-8') as f:
        r_file = f.read()
        data = json.loads(r_file)

    if name not in data.keys():
        data[name.lower()] = list(set(args))
    else:
        for arg in args:
            if str(arg).isdigit() and \
                    arg not in data[name]:
                data[name].append(arg)

    with open('codes.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, sort_keys=True)


while True:
    data = input().split(maxsplit=1)
    tv_name, codes = data[0], data[1].split(', ')
    print(tv_name, codes)
    to_json(tv_name, *codes)
