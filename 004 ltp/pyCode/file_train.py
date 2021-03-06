# -*- coding: utf-8 -*-
import os
import re
import nlp


"""
这个文件用来处理训练数据
"""


def sorted_dict_values(adict):
    keys = list(adict.keys())
    keys.sort()
    return keys


def name_unique_and_sort(file):
    """
    对训练数据，名称进行去重并排序，输出.unique_sort文件
    :param file:
    :return:
    """
    if not os.path.exists(file):
        return

    try:
        f_in = open(file, mode="r", encoding="utf-8")
        f_out = open(file + '.unique_sort', mode="w+", encoding="utf-8")

        line = f_in.readline().strip()
        match_pattern = re.compile('(.+)\s+(\d+)$')
        count = 0
        code_dict = {}
        nocode_dict = {}
        while line:
            line = line.strip()
            count += 1
            if len(line) > 0:
                ma = re.match(match_pattern, line)
                if ma:
                    key = ma.group(1).strip()
                    if key not in code_dict.keys():
                        code_dict[key] = ma.group(2).strip()
                else:
                    if line not in nocode_dict.keys():
                        nocode_dict[line] = ''

            line = f_in.readline()

        print('count:', count)
        code_keys = sorted_dict_values(code_dict)
        nocode_keys = sorted_dict_values(nocode_dict)

        new_code_dict = {}
        for key in code_keys:
            new_code_dict[key] = code_dict[key]

        new_nocode_dict = {}
        for key in nocode_keys:
            new_nocode_dict[key] = nocode_dict[key]

        for key, value in new_nocode_dict.items():
            f_out.write(key + ' ' + value + '\r')

        for key, value in new_code_dict.items():
            f_out.write(key + ' ' + value + '\r')

    except IOError:
        print('IOError')
    finally:
        if f_in:
            f_in.close()
        if f_out:
            f_out.close()


def patch_taxcode_jc(file_map, file_patch):
    """
    有部分数据有税收分类编码但没有简称，现在把简称补上
    借助 file_map 进行补齐
    :param file:
    :return:
    """
    try:
        f_map = open(file_map, mode="r", encoding="utf-8")

        line = f_map.readline()
        jc_map = dict()
        com_match = re.compile('^(\d+)\s+(\S+)\s+(\S+)')
        while line:
            ma = re.match(com_match, line)
            if ma:
                jc_map[ma.group(1)] = ma.group(3)
            line = f_map.readline()

        # 开始读取待处理文件并补齐
        f_in = open(file_patch, mode="r", encoding="utf-8")
        f_out = open(file_patch + '.patch', mode="w+", encoding="utf-8")

        line = f_in.readline()
        write_out = list()
        com_match = re.compile('(.+)\s+(\d+)\s*')
        while line:
            if len(line) > 0:
                if line[0] != '*':
                    ma = re.match(com_match, line)
                    if ma:
                        code = ma.group(2)
                        if code in jc_map.keys():
                            line = '*' + jc_map[code] + '*' + line
                            write_out.append(line)
                        else:
                            write_out.append(line)
                    else:
                        write_out.append(line)
                else:
                    write_out.append(line)

            line = f_in.readline()

        for line in write_out:
            f_out.write(line)

    except IOError:
        print('IOError')
    finally:
        if f_map:
            f_map.close()
        if f_in:
            f_in.close()
        if f_out:
            f_out.close()


def check_taxcode_match_jc(file_src, file_map):
    """
    用来检查训练数据集的简称和税收分类编码是否对的上
    :param file_src:  训练集文件
    :param file_map:  税收分类编码和简称的映射文件
    :return:
    """
    if not os.path.exists(file_src) or not os.path.exists(file_map):
        print('file not exist')
        return

    # 处理映射文件
    f_map = open(file_map, mode="r", encoding="utf-8")
    line = f_map.readline().strip()
    src_map = dict()
    com_match = re.compile('\[(\S+)\]\s+\[([0-9\', ]+)')
    while line:
        ma = re.match(com_match, line)
        if ma:
            src_map[ma.group(1)] = ma.group(2)
        line = f_map.readline().strip()

    f_map.close()

    # 检查简称和税收分类编码是否匹配
    count = 0
    f_src = open(file_src, mode="r", encoding="utf-8")
    f_out = open(file_src + '.check', mode="w+", encoding="utf-8")
    line = f_src.readline().strip()
    com_match = re.compile('\*([^*\]]+)\*.*\s+(\d+)')
    while line:
        is_wrong = True
        count += 1
        ma = re.match(com_match, line)
        if ma:
            jc = ma.group(1)
            code = ma.group(2)
            # print('jc:', jc, ' code:', code)
            if jc in src_map.keys():
                # print('jc in the map')
                codes = src_map[jc] + ''
                index = codes.find(code)
                if index != -1:
                    is_wrong = False

        if is_wrong:
            line = 'wwrong' + line
        f_out.write(line + '\n')

        line = f_src.readline().strip()

    if f_src:
        f_src.close()
    if f_out:
        f_out.close()

if __name__ == "__main__":
    check_taxcode_match_jc('./data_train/01 train_new.txt.unique_sort.part2.patch.check', './clean_tax_code/final.merge')
    # patch_taxcode_jc('./data_train/00 pwy_taxcode.txt', './data_train/01 train_new.txt.unique_sort.part2')
    # name_unique_and_sort('./data_train/01 train_new.txt')

