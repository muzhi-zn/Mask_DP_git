# coding:utf-8
import hashlib
from django.http import JsonResponse

from tooling_form.service.tooling_service import switch
from utilslibrary.base.base import BaseService
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from django.core.files.storage import default_storage
from django.shortcuts import render_to_response
from django.core.files.base import ContentFile
from utilslibrary.decorators.catch_exception_decorators import catch_exception
from utilslibrary.utils.file_utils import *
from system.models import upload_info


class upload_service(BaseService):

    # def __init__(self, file_path):
    #     self.file_path = file_path  # 上傳目的地路徑

    @catch_exception
    def file_upload_check(self, request):
        """判断文件是否允许上传"""
        if request.method == 'POST':
            type = request.POST.get('type')
            if type == '0':
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False})

    @catch_exception
    def file_upload(self, request):
        """文件分片上传"""
        if request.method == 'POST':
            upload_file = request.FILES.get('file')
            file_name = upload_file.name
            task = request.POST.get('task_id')  # 获取文件唯一标识符
            chunk = request.POST.get('chunk', 0)  # 获取该分片在所有分片中的序号
            filename = '%s%s' % (task, chunk)  # 构成该分片唯一标识符
            server_path = request.POST.get('server_path')

            print(file_name, task, chunk, filename, server_path)

            if not os.path.exists(server_path):
                os.mkdir(server_path)
            file_path = os.path.join(server_path, filename)
            default_storage.save(file_path, ContentFile(upload_file.read()))

            # 更新upload表中的check_status状态
            # upd_tip_no_status(tip_no, Constant.CHECK_STATUS_UPLOADING_3)
        return render_to_response('system_upload.html', locals())

    @catch_exception
    def file_check(self, request):
        """检查文件是否已经上传过"""
        if request.method == 'POST':
            tip_no = request.POST.get('tip_no')
            task_id = request.POST.get('task_id')
            chunk = request.POST.get('chunk', 0)
            chunkSize = request.POST.get('chunkSize')
            file_name = request.POST.get('file_name')
            server_path = request.POST.get('server_path')

            if os.path.exists(server_path):
                if os.path.getsize(server_path) == int(chunkSize):
                    return {'isExist': True}
            return {'isExist': False}

    @catch_exception
    def file_merge(self, request):
        """文件分片合并方法"""
        # id = request.POST.get('id')
        sub_id = request.POST.get('sub_id')
        task = request.POST.get('task_id')
        ext = request.POST.get('filename', '')
        upload_type = request.POST.get('type')
        server_path = request.POST.get('server_path')
        check_type = request.POST.get('check_type')
        print('sub_id = ', sub_id)
        if len(ext) == 0 and upload_type:
            ext = upload_type.split('/')[1]
        ext = '' if len(ext) == 0 else '%s' % ext  # 构建文件后缀名
        chunk = 0
        file_size = 0
        hash_f = hash_check(check_type).hash_func()

        with open(join_path(server_path, ext), 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = (server_path + '%s%d') % (task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    data = source_file.read()
                    hash_f.update(data)
                    print('test_hash ', hash_f.hexdigest())
                    file_size += os.path.getsize(filename)
                    target_file.write(data)  # 读取分片内容写入新文件
                    source_file.close()
                except IOError:
                    break
                chunk += 1

                os.remove(filename)  # 删除该分片，节约空间

        _o = upload_info()
        _o.sub_id = sub_id
        _o.file_name = ext
        _o.file_size = file_size
        _o.file_path = server_path
        _o.file_type = check_type
        _o.file_value = hash_f.hexdigest()

        _s = upload_info_service()
        re = _s.add_upload_info(_o)

        return JsonResponse({'id': re})


class hash_check:
    def __init__(self, check_type):
        self.check_type = check_type
        self.md5 = 'md5'
        self.sha1 = 'sha1'
        self.sha224 = 'sha224'
        self.sha256 = 'sha256'
        self.sha384 = 'sha384'
        self.sha512 = 'sha512'
        self.blake2b = 'blake2b'
        self.blake2s = 'blake2s'
        self.sha3_224 = 'sha3_224'
        self.sha3_256 = 'sha3_256'
        self.sha3_384 = 'sha3_384'
        self.sha3_512 = 'sha3_512'
        self.shake_128 = 'shake_128'
        self.shake_256 = 'shake_256'

    def hash_func(self):
        for case in switch(self.check_type):
            if case(self.md5):
                return hashlib.md5()

            if case(self.sha1):
                return hashlib.sha1()

            if case(self.sha224):
                return hashlib.sha224()

            if case(self.sha256):
                return hashlib.sha256()

            if case(self.sha384):
                return hashlib.sha384()

            if case(self.sha512):
                return hashlib.sha512()

            if case(self.blake2b):
                return hashlib.blake2b()

            if case(self.blake2s):
                return hashlib.blake2s()

            if case(self.sha3_224):
                return hashlib.sha3_224()

            if case(self.sha3_256):
                return hashlib.sha3_256()

            if case(self.sha3_384):
                return hashlib.sha384()

            if case(self.sha3_512):
                return hashlib.sha3_512()

            if case(self.shake_128):
                return hashlib.shake_128()

            if case(self.shake_256):
                return hashlib.shake_256()


@ProxyFactory(InvocationHandler)
class upload_info_service(BaseService):

    def add_upload_info(self, upload_info):
        data = {}
        try:
            upload_info.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"
        # return JsonResponse(data, safe=False)
        return upload_info.id

    def upd_upload_info(self, upload_info):
        data = {}
        try:
            upload_info.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)
