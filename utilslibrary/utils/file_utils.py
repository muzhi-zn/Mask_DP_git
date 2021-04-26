# -*- coding: utf-8 -*-
'''file utils
'''
import os
import shutil
from shutil import copyfile
from utilslibrary.system_constant import Constant


def copy_all_file(sourceDir, destDir):
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(destDir, f)
        if os.path.isfile(sourceF):
            copyfile(sourceF, targetF)


def file_readline(file):
    f = open(file, 'r')
    result = list()
    for line in open(file):
        line = f.readline()
        result.append(line)
    f.close()
    return result


def create_file(path, msg):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(msg)
        os.chmod(path, 0o777)


def makdirs(path):
    if not os.path.exists(path):
        os.makedirs(path, )
        os.chmod(path, 0o777)


# mak=0 :dont makdirs  mak=1:makdirs
def get_work_path(product='', device='', layer='', mak=0):
    if product != '' and device == '' and layer == '':
        _path = os.path.join(Constant.TEMPLATE_FILE_GENERATE_PATH, product)
        if mak == 1:
            makdirs(_path)
        return _path
    elif product != '' and device != '' and layer == '':
        _path = os.path.join(Constant.TEMPLATE_FILE_GENERATE_PATH, product, Constant.FILE_PATH_DEVICE, device)
        if mak == 1:
            makdirs(_path)
        return _path
    elif product != '' and device != '' and layer != '':
        _path = os.path.join(Constant.TEMPLATE_FILE_GENERATE_PATH, product, Constant.FILE_PATH_DEVICE, device,
                             Constant.FILE_PATH_LAYER, layer)
        if mak == 1:
            makdirs(_path)
        return _path
    return ''


def get_device_path(basepath, device, mak=0):
    if device != '':
        _path = os.path.join(basepath, device)
        if mak == 1:
            makdirs(_path)
        return _path


def get_layer_path(basepath, layer, mak=0):
    if layer != '':
        _path = os.path.join(basepath, layer)
        if mak == 1:
            makdirs(_path)
        return _path


def get_fracture_path(basepath, mak=0):
    if basepath != '':
        _path = os.path.join(basepath, Constant.FILE_PATH_FRACTURE)
        if mak == 1:
            makdirs(_path)
        return _path


def get_fracture_XOR_path(basepath, mak=0):
    if basepath != '':
        _path = os.path.join(basepath, Constant.FILE_PATH_FRACTURE_XOR)
        if mak == 1:
            makdirs(_path)
        return _path


def get_db_path(basepath, mak=0):
    if basepath != '':
        _path = os.path.join(basepath, Constant.FILE_PATH_DB)
        if mak == 1:
            makdirs(_path)
        return _path
    return ''


def get_db_path_by_device(product, device, mak=0):
    if product != '' and device != '':
        _path = os.path.join(Constant.TEMPLATE_FILE_GENERATE_PATH, product, Constant.FILE_PATH_DEVICE, device,
                             Constant.FILE_PATH_DB)
        if mak == 1:
            makdirs(_path)
        return _path
    return ''


def join_path(path1, path2, mak=0):
    if path1 != '' and path2 != '':
        _path = os.path.join(path1, path2)
        if mak == 1:
            makdirs(_path)
        return _path
    return ''


def get_fracture_file_name(product, layer, device, machine_type):
    if machine_type == Constant.WRITER_TYPE_VSB:
        return ''.join([product, '_', layer, '_', device, '_fracture.sh'])
    elif machine_type == Constant.WRITER_TYPE_MODE5:
        return ''.join([product, '_', layer, '_', device, '_MEBES.sh'])


def get_fracture_log_file_name(product, layer, device):
    return ''.join([product, '_', layer, '_', device, '_fracture.log'])


def get_fracture_xor_file_name(product, layer, device):
    return ''.join([product, '_', layer, '_', device, '_fracture_XOR.prj'])


def get_fracture_xor_log_file_name(product, layer, device):
    return ''.join([product, '_', layer, '_', device, '_fracture_XOR.log'])


def check_file_exists(file_path):
    if not os.path.exists(file_path):
        return False
    return True


def del_file(filepath):
    """
    删除某一目录下的所有文件或文件夹
    :param filepath: 路径
    :return:
    """
    print("--------------del_file----------------1")
    if filepath.endswith(Constant.FILE_PATH_FRACTURE) or filepath.endswith(Constant.FILE_PATH_FRACTURE_XOR):
        del_list = os.listdir(filepath)
        for f in del_list:
            file_path = os.path.join(filepath, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path, ignore_errors=True)
    print("--------------del_file----------------2")


if __name__ == "__main__":
    print(get_db_path(get_work_path(product='product', device='device')))
