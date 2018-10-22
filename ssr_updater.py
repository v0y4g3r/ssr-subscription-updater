#! /usr/bin/python3

import base64
from urllib import request
import json
import os

default_options = {
    'local_address': '0.0.0.0',
    'local_port': 1080,
    'enable': True
}


def http_get(url):
    """
    读取ssr订阅目录
    :param url:
    :return:
    """
    res = request.urlopen(url).readlines()
    return b64decode_to_string(res[0].decode())


def b64decode_to_string(string):
    """
    base64解码
    :param string: 输入的base64字符串
    :return:
    """
    string = replace(string)
    string = padding_b64_encoded_string(string)
    try:
        dec = base64.b64decode(string)
        decode = dec.decode()
        # print(decode)
        return decode
    except BaseException as e:
        print(e)
        print(string)
        return None


def padding_b64_encoded_string(string):
    missing_padding_len = 4 - len(string) % 4
    if missing_padding_len != 0 and missing_padding_len != 4:
        return string + '=' * missing_padding_len
    return string


def handle_parts(part1_string, part2_string):
    """
    处理两部分字符串
    :param part1_string: like jp1.doubledou.win:8657:auth_sha1_v4:rc4-md5:http_simple:QVNFNUxt/
    :param part2_string: like obfsparam=&protoparam=&remarks=44CQ5YWo6IO944CR4pOq5pel5pysdnVsdHI&group=RG91YmxlRG91
    :return:
    """
    config = {}
    part1_entries = part1_string.split(':')
    config['server'] = part1_entries[0]
    config['server_port'] = int(part1_entries[1])
    config['protocol'] = part1_entries[2]
    config['method'] = part1_entries[3]
    config['obfs'] = part1_entries[4]
    config['password'] = b64decode_to_string(part1_entries[5])
    config['local_address'] = default_options['local_address']
    config['local_port'] = default_options['local_port']
    config['enable'] = default_options['enable']
    part2_dict = dict(pair.split('=') for pair in part2_string.split('&'))
    config['remarks'] = b64decode_to_string(part2_dict['remarks'])
    return config


def replace(string):
    """
    把_替换为/,-替换为+
    :param string:
    :return:
    """
    return string.replace('_', '/').replace('-', '+')


def handle_link_entry(link):
    """
    处理单个ssr链接
    :param link:
    :return:
    """
    parts = b64decode_to_string(link).split('/?')
    return handle_parts(parts[0], parts[1])


def process(response):
    """
    处理base64解码后的ssr链接列表
    :param response:
    :return:
    """
    config_list = []
    current_entry = ''
    try:
        for ssr_link in response.split():
            link_entry = ssr_link.split('://')[1]
            current_entry = link_entry
            config_list.append(handle_link_entry(link_entry))
    except Exception as e:
        print(e)
        print(current_entry)
        return None
    return config_list


def dump(configs):
    """
    将配置项导出到文件夹
    :param configs:
    :return:
    """
    for config in configs:
        filename = './config/' + config['remarks'] + '.json'
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)


if __name__ == '__main__':
    subscribe_url = input('Please input ShadowsocksR subscribe link:')
    if not subscribe_url.startswith('http'):
        print('Bad subscribe URL format, exiting.')
        exit(1)
    response = http_get(subscribe_url)
    # print(response)
    configs = process(response)
    print(json.dumps(configs, indent=2))
    dump(configs)
    print('Total: {} config files updated.'.format(len(configs)))
