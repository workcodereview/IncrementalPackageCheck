# coding: utf8

import os
import codecs
import logging
import argparse
from qb_module import QB

# 保存传入的文件
FILE_LIST = []

# 传入文本文件即可
def read_file_list(file_list_path):
    if not os.path.exists(file_list_path):
        logging.error('file list path not exist!!!')
    with codecs.open(file_list_path, 'r', 'utf-8') as f_file:
        file_content = f_file.read().strip().splitlines()
    for line in file_content:
        if line.find('\\'):
            line = line.replace('\\', '/')
        index = line.lower().find('assets')
        line = line[index:].strip()
        FILE_LIST.append(line)

# 保存文件所在bundle和bundle大小
bundle_and_file = {}
def save_file_and_bundle(bundle_info):
    for bundle_name, bundle_size in bundle_info.items():
        if bundle_name not in bundle_and_file:
            bundle_and_file[bundle_name] = {
                'name': bundle_name,
                'size': bundle_size,
                'files': [file]
            }
        else:
            bundle_and_file[bundle_name]['files'].append(file)

# 将结果写入文件中
def write_result_file(out_path):
    w_file = codecs.open(out_path+'/bundleResult.tab', 'w', 'utf-8')
    w_file.write(u'bundle名\t大小(MB)\t大小(B)\t文件\n')
    for bundle_name, bundle_info in bundle_and_file.items():
        for index, file in enumerate(bundle_info['files']):
            w_file.write(bundle_info['name']+'\t'+str(round(bundle_info['size']/1024/1024, 2))+'\t' +
                         str(bundle_info['size'])+'\t'+file+'\n')
    w_file.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-B', '--baseline-buildid', help="baseline buildid", type=int, required=True)
    parser.add_argument('-F', '--input-file', help="input check file list", type=str, required=True)
    parser.add_argument('-A', '--input-aba-file', help="input aba file", type=str, required=False)
    parser.add_argument('-O', '--out-result-file', help="out result file", type=str, required=True)
    args = parser.parse_args()

    print('build id: '+str(args.baseline_buildid))
    print('input file: '+args.input_file)
    print('input aba file: '+args.input_aba_file)
    print('out result file path: '+args.out_result_file)

    qb_baseline = QB(args.baseline_buildid, args.input_aba_file)
    input_file = args.input_file
    read_file_list(input_file)
    for index, file in enumerate(FILE_LIST):
        bundle_info = qb_baseline.asset2bundle(file)
        print('file: '+file)
        for k, v in bundle_info.items():
            print(k)
        save_file_and_bundle(bundle_info)
    if args.out_result_file.find('\\'):
        out_path = args.out_result_file.replace('\\', '/')
    write_result_file(out_path)



