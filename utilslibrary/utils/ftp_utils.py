# -*- coding: utf-8 -*-
import paramiko

def sftp_file_to(localpath,remotepath):
    t = paramiko.Transport(('172.16.20.242', 22))
    t.connect(username='root', password='QXeda@2019')
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get(remotepath='/home/test.txt',localpath="/upload/test111.txt")

#---------
def sftp_file_from():
    t = paramiko.Transport(('172.16.20.242', 22))
    t.connect(username='root', password='QXeda@2019')
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(localpath='/upload/test111.txt',remotepath="/home/test222.txt")
    
if __name__ == '__main__':
#     sftp_file_to()
    sftp_file_from()