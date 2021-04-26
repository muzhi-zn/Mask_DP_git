# -*- coding: utf-8 -*-
import os
import traceback

import paramiko
from functools import wraps
from datetime import datetime
import re
from ftplib import FTP


def timethis(func):
    """
    时间装饰器，计算函数执行所消耗的时间
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        print(func.__name__, end - start)
        return result

    return wrapper


class SSHManager:
    def __init__(self, host, usr, passwd, is_ftp=False):
        self._host = host
        self._usr = usr
        self._passwd = passwd
        self._ssh = None
        self._sftp = None
        self._ftp = None
        if is_ftp:
            self._ftp_connect()
        else:
            self._sftp_connect()
            self._ssh_connect()

    def __del__(self):
        if self._ssh:
            self._ssh.close()
        if self._sftp:
            self._sftp.close()
        if self._ftp:
            self._ftp.set_debuglevel(0)
            self._ftp.quit()

    def _sftp_connect(self):
        try:
            transport = paramiko.Transport((self._host, 22))
            transport.connect(username=self._usr, password=self._passwd)
            self._sftp = paramiko.SFTPClient.from_transport(transport)
            self._sftp.getcwd()
        except Exception as e:
            raise RuntimeError("sftp connect failed [%s]" % str(e))

    def _ssh_connect(self):
        try:
            # 创建ssh对象
            self._ssh = paramiko.SSHClient()
            # 允许连接不在know_hosts文件中的主机
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接服务器
            self._ssh.connect(hostname=self._host,
                              port=22,
                              username=self._usr,
                              password=self._passwd,
                              timeout=5)
        except Exception:
            raise RuntimeError("ssh connected to [host:%s, usr:%s, passwd:%s] failed" %
                               (self._host, self._usr, self._passwd))

    def _ftp_connect(self):
        try:
            self._ftp = FTP()  # 初始化一个对象
            self._ftp.set_debuglevel(2)  # 打开调试级别2，显示详细信息
            self._ftp.connect(self._host, 21)  # 链接ftp server 和端口
            self._ftp.login(self._usr, self._passwd)
        except Exception:
            raise RuntimeError("ftp connected to [host:%s, usr:%s, passwd:%s] failed" %
                               (self._host, self._usr, self._passwd))

    def ssh_exec_cmd(self, cmd, path='~'):
        """
        通过ssh连接到远程服务器，执行给定的命令
        :param cmd: 执行的命令
        :param path: 命令执行的目录
        :return: 返回结果
        """
        try:
            result = self._exec_command('cd ' + path + ';' + cmd)
            return result
        except Exception:
            raise RuntimeError('exec cmd [%s] failed' % cmd)

    def __clear_lines(self):
        self.lines = []

    def __save_line(self, line):
        self.lines.append(line)

    def ftp_rmd_file(self, path):
        """
        删除一个目录及其中全部的文件
        由于FTP只能删除空目录，要递归删除
        :param path:
        :return:
        """
        try:
            self.__clear_lines()
            self._ftp.cwd(path)
            self._ftp.retrlines("LIST", callback=self.__save_line)
            self._ftp.cwd('/')
            for line in self.lines:
                name = path + "/" + line.split(" ")[-1]
                if line[0] == "d":
                    self.ftp_rmd_file(name)
                else:
                    self._ftp.delete(name)
            self._ftp.rmd(path)
            return True, 'delete success'
        except Exception as e:
            if 'change' in str(e):
                return True, 'no need to delete'
            else:
                return False, str(e)

    def ssh_exec_shell(self, local_file, remote_file, exec_path):
        """
        执行远程的sh脚本文件
        :param local_file: 本地shell文件
        :param remote_file: 远程shell文件
        :param exec_path: 执行目录
        :return:
        """
        try:
            if not self.is_file_exist(local_file):
                raise RuntimeError('File [%s] not exist' % local_file)
            if not self.is_shell_file(local_file):
                raise RuntimeError('File [%s] is not a shell file' % local_file)

            self._check_remote_file(local_file, remote_file)

            result = self._exec_command('chmod +x ' + remote_file + '; cd' + exec_path + ';/bin/bash ' + remote_file)
            print('exec shell result: ', result)
        except Exception as e:
            raise RuntimeError('ssh exec shell failed [%s]' % str(e))

    @staticmethod
    def is_shell_file(file_name):
        return file_name.endswith('.sh')

    @staticmethod
    def is_file_exist(file_name):
        try:
            with open(file_name, 'r'):
                return True
        except Exception as e:
            return False

    def _check_remote_file(self, local_file, remote_file):
        """
        检测远程的脚本文件和当前的脚本文件是否一致，如果不一致，则上传本地脚本文件
        :param local_file:
        :param remote_file:
        :return:
        """
        try:
            result = self._exec_command('find' + remote_file)
            if len(result) == 0:
                self._upload_file(local_file, remote_file)
            else:
                lf_size = os.path.getsize(local_file)
                result = self._exec_command('du -b' + remote_file)
                rf_size = int(result.split('\t')[0])
                if lf_size != rf_size:
                    self._upload_file(local_file, remote_file)
        except Exception as e:
            raise RuntimeError("check error [%s]" % str(e))

    @timethis
    def _upload_file(self, local_file, remote_file):
        """
        通过sftp上传本地文件到远程
        :param local_file:
        :param remote_file:
        :return:
        """
        try:
            self._sftp.put(local_file, remote_file)
        except Exception as e:
            raise RuntimeError('upload failed [%s]' % str(e))

    @timethis
    def _mkdir(self, path):
        """
        通过sftp上传本地文件到远程
        :param local_file:
        :param remote_file:
        :return:
        """
        try:
            self._sftp.mkdir(path)
        except Exception as e:
            raise RuntimeError('upload failed [%s]' % str(e))

    @timethis
    def _exec_command(self, cmd):
        """
        通过ssh执行远程命令
        :param cmd:
        :return:
        """
        try:
            stdin, stdout, stderr = self._ssh.exec_command(cmd)
            return stdout.read().decode()
        except Exception as e:
            raise RuntimeError('Exec command [%s] failed' % str(cmd))
    def _mkdirs(self, path):
        try:
            self._sftp.chdir(path)  # 切换工作路径
        except Exception as e:
            self._sftp.chdir('/')  # 切换到远程根目录下(不一定时盘符, 服务器)
            base_dir, part_path = self._sftp.getcwd(), path.split('/')  # 分割目录名
            for p in part_path[1:-1]:  # 根据实际target_dir决定切片位置, 如果是目录, 使用[1:], 文件绝对路径使用[1:-1], 列表第0个切割之后为空串
                base_dir = os.path.join(base_dir, p)  # 拼接子目录
                try:
                    self._sftp.chdir(base_dir)  # 切换到子目录, 不存在则异常
                except Exception as e:
                    print('INFO:', e)
                    self._sftp.mkdir(base_dir)
    @property
    def ssh(self):
        return self._ssh


class SGD_Account:
    def __init__(self, host, usr, passwd):
        self._host = host
        self._usr = usr
        self._passwd = passwd
        self._ssh = None
        self._sftp = None
        self._ssh_connect()

    def __del__(self):
        if self._ssh:
            self._ssh.close()
        if self._sftp:
            self._sftp.close()

    def _ssh_connect(self):
        try:
            # 创建ssh对象
            self._ssh = paramiko.SSHClient()
            # 允许连接不在know_hosts文件中的主机
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接服务器
            self._ssh.connect(hostname=self._host,
                              port=22,
                              username=self._usr,
                              password=self._passwd,
                              timeout=5)
        except Exception:
            raise RuntimeError("ssh connected to [host:%s, usr:%s, passwd:%s] failed" %
                               (self._host, self._usr, self._passwd))

    def ssh_exec_cmd(self, cmd, path='~'):
        """
        通过ssh连接到远程服务器，执行给定的命令
        :param cmd: 执行的命令
        :param path: 命令执行的目录
        :return: 返回结果
        """
        try:
            result = self._exec_command('cd ' + path + ';' + cmd)
            return result
        except Exception:
            raise RuntimeError('exec cmd [%s] failed' % cmd)

    @timethis
    def _exec_command(self, cmd):
        """
        通过ssh执行远程命令
        :param cmd:
        :return:
        """
        try:
            stdin, stdout, stderr = self._ssh.exec_command(cmd)
            stdout = stdout.read().decode()
            s_stderr = stderr.read().decode()
            if stdout:
                return stdout
            else:
                return s_stderr

            # return stdout.read().decode(), stderr.read().decode()
        except Exception as e:
            raise RuntimeError('Exec command [%s] failed' % str(cmd))
