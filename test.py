def create_remote_dir(ftp, target_dir):
    try:
        ftp.cwd(target_dir)  # 切换工作路径
    except Exception as e:
        ftp.cwd('~')  # 切换到远程根目录下(不一定时盘符, 服务器)
        base_dir, part_path = ftp.pwd(), target_dir.split('/')  # 分割目录名
        for p in part_path[1:-1]:  # 根据实际target_dir决定切片位置, 如果是目录, 使用[1:], 文件绝对路径使用[1:-1], 列表第0个切割之后为空串
            base_dir = base_dir + p + '/'  # 拼接子目录
        try:
            ftp.cwd(base_dir)  # 切换到子目录, 不存在则异常
        except Exception as e:
            print('INFO:', e)
            ftp.mkd(base_dir)  # 不存在创建当前子目录
    return ftp

path_list = '/test/test1/test2'.split('/')
for p in path_list[1:-1]:
    print(p)
