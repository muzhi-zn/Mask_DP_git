from utilslibrary.utils.iems_utils import execute_cmd_url


class IEMSBaseService:
    """IEMS基础服务"""

    execute_url = "http://172.16.20.242:8089/api/execute_cmd/"
    query_result_url = "http://172.16.20.242:8089/api/query_result/"
    query_process_url = "http://172.16.20.242:8089/api/query_process/"
    query_tail_result_url = "http://172.16.20.242:8089/api/query_tail_result/"

    def query_result(self, record_no):
        """执行查询结果接口"""
        param = dict()
        param['record_no'] = record_no
        result_json = execute_cmd_url(self.query_result_url, param)
        if result_json:
            return result_json
        else:
            return ""

    def query_process_result(self, record_no):
        """执行查询中间结果接口"""
        param = dict()
        param['record_no'] = record_no
        result_json = execute_cmd_url(self.query_process_url, param)
        if result_json:
            return result_json
        else:
            return ""

    def query_tail_result(self, log_num, record_no):
        """执行查询结果日志后n行的结果记录"""
        param = dict()
        param['record_no'] = record_no
        param['log_num'] = log_num
        result_json = execute_cmd_url(self.query_tail_result_url, param)
        if result_json:
            return result_json
        else:
            return ""

    def execute_calibre(self, path, cpu_num, config_file_path, drc_file_path, result_file_path):
        """执行calibre指令"""
        temp_no = 'T00008'
        param = dict()
        param['temp_no'] = temp_no  # IEMS指令模板编号
        param['params'] = path + ',' + str(cpu_num) + ',' + config_file_path + ',' + drc_file_path  # 执行参数
        param['result_file_path'] = result_file_path  # 指令结果log路径
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:  # 成功状态
                return True, result_json.get("record_no"), result_json.get("instruction")
            else:
                return False, "", ""
        else:
            return False, "", ""

    def execute_dbdiff(self, file_type, output_file_path, test_file_path, topcell, result_file_path):
        """执行dbdiff指令"""
        temp_no = 'T00009'
        param = dict()
        param['temp_no'] = temp_no
        param['params'] = file_type + "," + test_file_path + ',' + topcell + ',' + output_file_path + ',' + topcell
        param['result_file_path'] = result_file_path
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:  # 成功状态
                return True, result_json.get("record_no"), result_json.get("instruction")
            else:
                return False, "", ""
        else:
            return False, "", ""

    def execute_mrclvl(self, path, prj_file_path, log_file_path):
        """执行mrclvl指令"""
        temp_no = 'T00014'
        param = dict()
        param['temp_no'] = temp_no
        param['params'] = path + ',' + prj_file_path
        param['result_file_path'] = log_file_path
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:
                return True, result_json.get("record_no"), result_json.get("instruction")
            else:
                return False, "", ""
        else:
            return False, "", ""

    def execute_bsub(self, path, sh_file_path, prj_file_path, log_file_path):
        """执行bsub指令"""
        temp_no = 'T00006'
        param = dict()
        param['temp_no'] = temp_no
        param['params'] = path + ',' + sh_file_path + ',' + prj_file_path
        param['result_file_path'] = log_file_path
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:
                return True, result_json.get("record_no"), result_json.get("instruction")
            else:
                return False, "", ""
        else:
            return False, "", ""

    def execute_cats(self, path, sh_file_path, log_file_path):
        """执行cats命令"""
        temp_no = 'T00005'
        param = dict()
        param['temp_no'] = temp_no
        param['params'] = path + ',' + sh_file_path
        param['result_file_path'] = log_file_path
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:
                return True, result_json.get("record_no"), result_json.get("instruction")
            else:
                return False, "", ""
        else:
            return False, "", ""

    def execute_calibredrv(self, path, cpu_num, tcl_path, log_file_path):
        """执行calibredrv指令"""
        temp_no = "T00013"
        param = dict()
        param['temp_no'] = temp_no
        param['params'] = path + "," + str(cpu_num) + ',' + tcl_path
        param['result_file_path'] = log_file_path
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:
                return True, result_json.get("record_no"), result_json.get("instruction")
            else:
                return False, "", ""
        else:
            return False, "", ""

    def execute_deletejob(self, path, create_path):
        """执行deletejob指令"""
        temp_no = 'T00016'
        param = dict()
        param['temp_no'] = temp_no
        param['params'] = path + "," + create_path + "," + create_path
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:
                return True, result_json.get("record_no"), result_json.get("result")
            else:
                return False, "", ""
        else:
            return False, "", ""

    def execute_jobsetup(self, path, lua_file_path, create_path):
        """执行jobsetup指令"""
        self.execute_deletejob(path, create_path)
        temp_no = 'T00010'
        param = dict()
        param['temp_no'] = temp_no
        param['params'] = path + "," + lua_file_path + "," + create_path
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:
                return True, result_json.get("record_no"), result_json.get("result")
            else:
                return False, "", ""
        else:
            return False, "", ""

    def execute_jobsubmit(self, path, create_path, log_file_path, config_file_path):
        """执行jobsubmit指令"""
        temp_no = 'T00011'
        param = dict()
        param['temp_no'] = temp_no
        param['params'] = path + "," + create_path + "," + config_file_path
        param['result_file_path'] = log_file_path
        result_json = execute_cmd_url(self.execute_url, param)
        if result_json:
            if result_json.get("code") == 200:
                return True, result_json.get("record_no"), result_json.get("result")
            else:
                return False, "", ""
        else:
            return False, "", ""


if __name__ == "__main__":
    """执行calibredrv指令"""
    temp_no = "T00011"
    param = dict()
    param['temp_no'] = temp_no
    param['params'] = "/qxic/qxic/MaskData/Engineering/example/QEN001/Device/MP001/layer/139A1/BOPC,dr81509769_MP001_139A1_BOPC,config.xml"
    param['result_file_path'] = "/qxic/qxic/MaskData/Engineering/example/QEN001/Device/MP001/layer/139A1/BOPC/dr81509769_MP001_139A1_BOPC/h/work/runtachyon/status.log"
    result_json = execute_cmd_url("http://172.16.20.242:8089/api/execute_cmd/", param)
    print(result_json)