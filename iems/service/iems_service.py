import logging
import os
import traceback
from datetime import datetime

from full_tooling.models import recipe_file_info, recipe_files
from iems.models import iems_execute_result
from iems.service.iems_base_service import IEMSBaseService

log = logging.getLogger('log')
cpu_num = 40


class IEMSService:
    """执行iems指令的方法"""

    def do_mopc(self, is_test, stage_name, recipe_id):
        """执行mopc相关方法"""
        try:
            if is_test:  # recipe测试方法
                r_f_list = recipe_file_info.objects.filter(recipe_id=recipe_id, upload_status=1, is_delete=0)
                deck = r_f_list.get(file_type='deck', stage_name=stage_name)
                remote = r_f_list.get(file_type='remote', stage_name=stage_name)
                r_f = recipe_files.objects.get(pk=deck.file_id)
                path, tail = os.path.split(r_f.file_path)
                config_file_path = remote.file_name
                drc_file_path = deck.file_name
                result_file_path = os.path.join(path, (r_f.recipe_name + '.log'))
                flag, record_no, instruction = IEMSBaseService().execute_calibre(path, cpu_num, config_file_path,
                                                                                 drc_file_path, result_file_path)
                i_e_r = iems_execute_result()
                i_e_r.result_log_file_path = result_file_path
                if flag:
                    i_e_r.record_no = record_no
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 1
                else:
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 2
                i_e_r.save()
                return flag, record_no, instruction
            else:  # TODO 站点实际执行方法
                pass
        except Exception as e:
            print(e)
            return False, str(e), ""

    def db_diff(self, is_test, recipe_id, execution_record_no):
        """执行diff命令判断是否noclean"""
        try:
            if is_test:
                file_type = "OASIS"
                stage_name = recipe_file_info.objects.get(recipe_id=recipe_id, upload_status=1, is_delete=0,
                                                          execution_record_no=execution_record_no).stage_name
                log.info(stage_name + '_' + recipe_id + '_' + execution_record_no)
                test_output = recipe_file_info.objects.get(upload_type='test', file_type='test_output',
                                                           recipe_id=recipe_id, upload_status=1, is_delete=0,
                                                           stage_name=stage_name)
                output = recipe_file_info.objects.get(file_type='output',
                                                      recipe_id=recipe_id, upload_status=1, is_delete=0,
                                                      stage_name=stage_name)
                path = output.file_base_path
                topcell = output.top_cell
                output_path = os.path.join(path, output.file_name)
                _base, _ext = os.path.splitext(output_path)
                if _ext == ".gds":
                    file_type = "GDS"
                test_output_path = os.path.join(path, test_output.file_name)
                result_file_path = os.path.join(path, 'diff.log')
                flag, record_no, instruction = IEMSBaseService().execute_dbdiff(file_type, output_path,
                                                                                test_output_path, topcell,
                                                                                result_file_path)
                i_e_r = iems_execute_result()
                i_e_r.result_log_file_path = result_file_path
                if flag:
                    i_e_r.record_no = record_no
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 1
                else:
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 2
                i_e_r.save()
                return flag, record_no, instruction
            else:  # TODO 站点实际执行方法
                pass
        except Exception as e:
            traceback.print_exc()
            return False, str(e), ""

    def do_mrclvl(self, is_test, recipe_id, stage_name, file_type):
        """执行mrclvl指令"""
        try:
            if is_test:
                diff_file_info = recipe_file_info.objects.get(recipe_id=recipe_id, upload_status='1', is_delete=0,
                                                              stage_name=stage_name, file_type=file_type)
                path = diff_file_info.file_base_path
                prj_file_path = os.path.join(path, diff_file_info.file_name)
                log_base, ext = os.path.splitext(prj_file_path)
                log_file_path = log_base + '.log'
                flag, record_no, instruction = IEMSBaseService().execute_mrclvl(path, prj_file_path, log_file_path)
                i_e_r = iems_execute_result()
                i_e_r.result_log_file_path = log_file_path
                if flag:
                    i_e_r.record_no = record_no
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 1
                else:
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 2
                i_e_r.save()
                return flag, record_no, instruction
            else:
                pass  # TODO 站点实际执行方法
        except Exception as e:
            traceback.print_exc()
            return False, str(e), ""

    def do_smrc(self, is_test, recipe_id, stage_name):
        """执行smartMRC命令"""
        try:
            if is_test:
                r_f_i_list = recipe_file_info.objects.filter(recipe_id=recipe_id, upload_status=1, is_delete=0,
                                                             stage_name=stage_name)
                sh = r_f_i_list.get(file_type="models")
                prj = r_f_i_list.get(file_type="deck")
                sh_file_path = os.path.join(sh.file_base_path, sh.file_name)
                prj_file_path = os.path.join(prj.file_base_path, prj.file_name)
                log_base, ext = os.path.splitext(prj_file_path)
                log_file_path = log_base + '.log'
                flag, record_no, instruction = IEMSBaseService().execute_bsub(prj.file_base_path, sh_file_path,
                                                                              prj_file_path, log_file_path)
                i_e_r = iems_execute_result()
                i_e_r.result_log_file_path = log_file_path
                if flag:
                    i_e_r.record_no = record_no
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 1
                else:
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 2
                i_e_r.save()
                return flag, record_no, instruction
            else:  # TODO 实际站点
                pass
        except Exception as e:
            traceback.print_exc()
            return False, str(e), ""

    def do_cats(self, is_test, recipe_id, stage_name):
        """执行cats命令"""
        try:
            if is_test:
                r_f_i_list = recipe_file_info.objects.filter(recipe_id=recipe_id, upload_status=1, is_delete=0,
                                                             stage_name=stage_name)
                sh = r_f_i_list.get(file_type="deck")
                sh_file_path = os.path.join(sh.file_base_path, sh.file_name)
                log_base_path, ext = os.path.splitext(sh_file_path)
                log_file_path = log_base_path + '.log'
                flag, record_no, instruction = IEMSBaseService().execute_cats(sh.file_base_path, sh_file_path,
                                                                              log_file_path)
                i_e_r = iems_execute_result()
                i_e_r.result_log_file_path = log_file_path
                if flag:
                    i_e_r.record_no = record_no
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 1
                else:
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 2
                i_e_r.save()
                return flag, record_no, instruction
            else:  # TODO 实际站点
                pass
        except Exception as e:
            traceback.print_exc()
            return False, str(e), ""

    def do_drv(self, is_test, recipe_id, stage_name):
        """执行drv指令"""
        try:
            if is_test:
                r_f_i_list = recipe_file_info.objects.filter(recipe_id=recipe_id, upload_status=1, is_delete=0,
                                                             stage_name=stage_name)
                tcl = r_f_i_list.get(file_type="deck")
                tcl_path = os.path.join(tcl.file_base_path, tcl.file_name)
                log_base_path, ext = os.path.splitext(tcl_path)
                log_file_path = log_base_path + '.log'
                print(log_file_path+'---------------------')
                flag, record_no, instruction = IEMSBaseService().execute_calibredrv(tcl.file_base_path, cpu_num,
                                                                                    tcl_path, log_file_path)
                i_e_r = iems_execute_result()
                i_e_r.result_log_file_path = log_file_path
                if flag:
                    i_e_r.record_no = record_no
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 1
                else:
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 2
                i_e_r.save()
                return flag, record_no, instruction
            else:  # TODO 实际站点
                pass
        except Exception as e:
            traceback.print_exc()
            return False, str(e), ""

    def do_drv2(self, is_test, recipe_id, stage_name):
        """执行drv2指令"""
        try:
            if is_test:
                r_f_i_list = recipe_file_info.objects.filter(recipe_id=recipe_id, upload_status=1, is_delete=0,
                                                             stage_name=stage_name)
                cfg = r_f_i_list.get(file_type="deck")
                tcl = r_f_i_list.get(file_type="models", file_name__contains='tcl')
                cfg_path = os.path.join(cfg.file_base_path, cfg.file_name)
                tcl_path = os.path.join(cfg.file_base_path, tcl.file_name)

                file_path = tcl_path + " " + cfg_path

                log_base_path, ext = os.path.splitext(cfg_path)
                log_file_path = log_base_path + '.log'
                print(log_file_path+'---------------------')
                flag, record_no, instruction = IEMSBaseService().execute_calibredrv(cfg.file_base_path, cpu_num,
                                                                                    file_path, log_file_path)
                i_e_r = iems_execute_result()
                i_e_r.result_log_file_path = log_file_path
                if flag:
                    i_e_r.record_no = record_no
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 1
                else:
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 2
                i_e_r.save()
                return flag, record_no, instruction
            else:  # TODO 实际站点
                pass
        except Exception as e:
            traceback.print_exc()
            return False, str(e), ""

    def do_brion(self, is_test, recipe_id, stage_name):
        """执行BrionOPC指令"""
        try:
            if is_test:
                r_f_i_list = recipe_file_info.objects.filter(recipe_id=recipe_id, upload_status=1, is_delete=0,
                                                             stage_name=stage_name)
                deck = r_f_i_list.get(file_type="deck")
                config = r_f_i_list.get(file_type="remote")
                path = deck.file_base_path
                create_path = deck.file_name.split(".")[0]
                flag, record, result = IEMSBaseService().execute_jobsetup(path, deck.file_name, create_path)
                i_e_r = iems_execute_result()
                if flag:
                    if "Successfully" in result:  # jobsetup执行完成
                        _create_path = os.path.join(path, create_path)
                        log_file_path = _create_path + "/h/work/runtachyon/status.log"
                        flag, record, result = IEMSBaseService().execute_jobsubmit(path, create_path,
                                                                                   log_file_path,
                                                                                   config.file_name)
                        i_e_r.result_log_file_path = log_file_path
                        if flag:
                            i_e_r.record_no = record
                            i_e_r.execute_start_time = datetime.now()
                            i_e_r.status = 1
                        else:
                            i_e_r.record_no = record
                            i_e_r.execute_start_time = datetime.now()
                            i_e_r.status = 2
                    else:
                        i_e_r.record_no = record
                        i_e_r.execute_start_time = datetime.now()
                        i_e_r.status = 2
                        i_e_r.err_message = result
                else:
                    i_e_r.record_no = record
                    i_e_r.execute_start_time = datetime.now()
                    i_e_r.status = 2
                    i_e_r.err_message = result
                i_e_r.save()
                return flag, record, result
            else:  # TODO 实际站点执行方法
                pass
        except Exception as e:
            traceback.print_exc()
            return False, str(e), ""
