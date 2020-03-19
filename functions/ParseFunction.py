import sys
import re
import copy
import sqlite3
import numpy as np

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)  # Replace all strings in < > with empty
    cleantext = cleantext.replace('&nbsp;', ' ')  # Replace all strings "&nbsp" to space
    cleantext = cleantext.replace('%C2%A0', ' ')  # Replace all strings "%C2%A0" to space
    cleantext = cleantext.replace('armeabi-v7a ', '')  # Replace all strings "armeabi-v7a" to empty
    cleantext = cleantext.replace('\n', '')  # Remove processed strings with \n newline characters
    return cleantext

def clean_info(raw_html):
    clean = raw_html.split('<td>')
    clean = clean[1].split('</td>')
    return clean[0]

def get_info(result_path):
    l_info = []
    l_module = []
    l_fail_num = []
    l_item = []
    with open(result_path, 'r') as f:
        clean_m = 0
        for i in f.readlines():
            if 'class="rowtitle">Suite / Plan' in i:
                l_info.append(['Suite / Plan', clean_info(i)])
            if 'class="rowtitle">Suite / Build' in i:
                l_info.append(['Suite / Build', clean_info(i)])
            if 'class="rowtitle">Tests Passed' in i:
                l_info.append(['Tests Passed', clean_info(i)])
            if 'class="rowtitle">Tests Failed' in i:
                l_info.append(['Tests Failed', clean_info(i)])
            if 'class="rowtitle">Modules Done' in i:
                l_info.append(['Modules Done', clean_info(i)])
            if 'class="rowtitle">Modules Total' in i:
                l_info.append(['Modules Total', clean_info(i)])
            if 'class="rowtitle">Fingerprint' in i:
                l_info.append(['Fingerprint', clean_info(i)])
            if 'class="rowtitle">Security Patch' in i:
                l_info.append(['Security Patch', clean_info(i)])
            if 'class="rowtitle">Release (SDK)' in i:
                l_info.append(['Release (SDK)', clean_info(i)])
            if 'href="#armeabi-v7a%C2%A0' in i:
                clean_i = i.split('<td>')
                fail_num = clean_i[3].split('</td>')
                l_fail_num.append(fail_num[0])
            if 'class="module" colspan="3"' in i:
                clean_m = cleanhtml(i)
            if 'class="failed"' in i:
                clean_i = cleanhtml(i)
                l_module.append(clean_m)
                l_item.append(clean_i)

    return l_info, l_module, l_fail_num, l_item

def get_incomplete_modules(result_path):
    l_incomplete_m = []
    with open(result_path, 'r') as f:
        for i in f.readlines():
            if 'false' in i and '<td><a href="#armeabi-v7a%C2%A0' in i:
                clean_i = cleanhtml(i)
                clean_i = clean_i.split('Cases[instant]')
                if 'false' in clean_i[0]:
                    clean_i = clean_i[0].split('Cases')
                    clean_i = str(clean_i[0]) + 'Cases'
                    l_incomplete_m.append(clean_i)
                else:
                    clean_i = str(clean_i[0]) + 'Cases[instant]'
                    l_incomplete_m.append(clean_i)
    return l_incomplete_m

def get_total_fail(result_path):
    total_fail = 0
    with open(result_path, 'r') as f:
        for i in f.readlines():
            if 'class="rowtitle">Tests Failed' in i:
                total_fail = clean_info(i)
                break
    return total_fail

def my_set_list(my_list):
    if len(my_list) <= 1:
        return my_list

    output_list = []
    output_list.append(my_list[0])
    for i in range(0, len(my_list) - 1, 1):
        if my_list[i] == my_list[i+1]:
            pass
        else:
            output_list.append(my_list[i+1])

    return output_list