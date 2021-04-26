import traceback

import paramiko
import os


def sftp_upload(host, port, username, password, local, remote):
    sf = paramiko.Transport((host, port))
    sf.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    try:
        if os.path.isdir(local):  # 判断本地参数是目录还是文件
            for f in os.listdir(local):  # 遍历本地目录
                sftp.put(os.path.join(local + f), os.path.join(remote + f))  # 上传目录中的文件
        else:
            sftp.put(local, remote)  # 上传文件
    except Exception as e:
        traceback.print_exc()
        print('sftp upload exception:', e)
    sf.close()


def sftp_download(host, port, username, password, local, remote):
    sf = paramiko.Transport((host, port))
    sf.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(sf)
    try:
        if os.path.isdir(local):  # 判断本地参数是目录还是文件
            for f in sftp.listdir(remote):  # 遍历远程目录
                sftp.get(os.path.join(remote + f), os.path.join(local + f))  # 下载目录中文件
        else:
            sftp.get(remote, local)  # 下载文件
    except Exception as e:
        print('sftp download exception:', e)
    sf.close()


if __name__ == "__main__":
    sftp_upload("172.16.50.243", 22, "E2MW8U", "5iSix600", "C:\\test.jb", "./")
    # sftp_upload("172.16.50.243", 22, "root", "MKeda@2020", "C:\\test.pdf", "/test.pdf")
