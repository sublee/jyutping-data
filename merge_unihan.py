# -*- coding: utf-8 -*-
import collections


def code_to_hanzi(code):
    hanzi = chr(int(code.replace('U+', '0x'), 16))
    return hanzi


def sort_pinyin_dict(pinyin_dict):
    return collections.OrderedDict(
        sorted(pinyin_dict.items(),
               key=lambda item: int(item[0].replace('U+', '0x'), 16))
    )


def remove_dup_items(lst):
    new_lst = []
    for item in lst:
        if item not in new_lst:
            new_lst.append(item)
    return new_lst


def parse_pinyins(fp):
    pinyin_map = {}
    for line in fp:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        code, pinyin = line.split('#')[0].split(':')
        pinyin = ','.join([x.strip() for x in pinyin.split() if x.strip()])
        pinyin_map[code.strip()] = pinyin.split(',')
    return pinyin_map


def merge(raw_pinyin_map, adjust_pinyin_map, overwrite_pinyin_map):
    new_pinyin_map = {}
    for code, pinyins in raw_pinyin_map.items():
        if code in overwrite_pinyin_map:
            pinyins = overwrite_pinyin_map[code]
        elif code in adjust_pinyin_map:
            pinyins = adjust_pinyin_map[code] + pinyins
        new_pinyin_map[code] = remove_dup_items(pinyins)

    return new_pinyin_map


def save_data(pinyin_map, writer):
    for code, pinyins in pinyin_map.items():
        hanzi = code_to_hanzi(code)
        line = '{code}: {pinyin}  # {hanzi}\n'.format(
            code=code, pinyin=','.join(pinyins), hanzi=hanzi
        )
        writer.write(line)


def extend_pinyins(old_map, new_map, only_no_exists=False):
    for code, pinyins in new_map.items():
        if only_no_exists:   # 只当 code 不存在时才更新
            if code not in old_map:
                old_map[code] = pinyins
        else:
            old_map.setdefault(code, []).extend(pinyins)

if __name__ == '__main__':
    raw_pinyin_map = {}
    with open('kCantonese.txt') as fp:
        kCantonese = parse_pinyins(fp)
        raw_pinyin_map.update(kCantonese)

    with open('overwrite.txt') as fp:
        overwrite_pinyin_map = parse_pinyins(fp)
        extend_pinyins(raw_pinyin_map, overwrite_pinyin_map)

    new_pinyin_map = merge(raw_pinyin_map, {}, overwrite_pinyin_map)
    new_pinyin_map = sort_pinyin_dict(new_pinyin_map)

    assert len(new_pinyin_map) == len(raw_pinyin_map)
    code_set = set(new_pinyin_map.keys())
    assert set(kCantonese.keys()) - code_set == set()
    with open('jyutping.txt', 'w') as fp:
        fp.write('# version: 0.6.1-jyutping\n')
        fp.write('# source: https://github.com/sublee/jyutping-data\n')
        save_data(new_pinyin_map, fp)
