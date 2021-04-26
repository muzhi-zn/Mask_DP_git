import os
import random
import string
import tarfile


def compress_file(file_path):
    """压缩文件"""
    tar_file_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    with tarfile.open(tar_file_name + '.tar.gz', 'w:gz') as tar:  # 整个文件夹打包
        tar.add(file_path, arcname=os.path.basename(file_path))
    return tar_file_name  # 返回压缩包名称


def uncompress_file(tar_file_path, path):
    """解压缩文件"""
    t = tarfile.open(tar_file_path)
    t.extractall(path=path)
