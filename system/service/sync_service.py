import logging

from jdv.jobs import get_scheduler
from utilslibrary.proxy.log_db_proxy import ProxyFactory, InvocationHandler
from utilslibrary.base.base import BaseService
from django.db import transaction
from ldap3 import Server, Connection, ALL, SUBTREE, ServerPool, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES
import re
from Mask_DP.settings import DATABASES, LDAP
from system.models import user, sync_config, sync_log, sync_log_detail
from django.http.response import HttpResponseRedirect, JsonResponse
from django.db import transaction
from datetime import datetime
import time

log = logging.getLogger("log")


class LDAP_SYNC_SERVICE_TEST:

    def __init__(self,
                 LDAP_SERVER_POOL,
                 LDAP_SERVER_PORT,
                 ADMIN_DN,
                 ADMIN_PASSWORD,
                 SEARCH_BASE,
                 DP_Automation_User):

        self.LDAP_SERVER_POOL = LDAP_SERVER_POOL
        self.LDAP_SERVER_PORT = LDAP_SERVER_PORT
        self.ADMIN_DN = ADMIN_DN
        self.ADMIN_PASSWORD = ADMIN_PASSWORD
        self.SEARCH_BASE = SEARCH_BASE
        self.group = DP_Automation_User

    def ldap_sync(self):
        ldap_server_pool = ServerPool(self.LDAP_SERVER_POOL)
        conn = Connection(ldap_server_pool,
                          user=self.ADMIN_DN,
                          password=self.ADMIN_PASSWORD,
                          check_names=True,
                          lazy=False,
                          raise_exceptions=False)
        conn.open()
        conn.bind()

        # 查詢Active Directory特定Group
        res = conn.search(
            search_base=self.SEARCH_BASE,  # 域目錄位置(cn, dc)
            search_filter=f'(&(objectclass=group)(cn={self.group}))',  # 篩選條件
            search_scope=SUBTREE,
            attributes=[ALL_ATTRIBUTES]
        )

        # 判斷是否有回傳值
        if res:
            return True
        else:
            return False


class AD_SYNC_SERVICE:

    def __init__(self, config):
        # database
        self.DB_HOST = DATABASES['default']['HOST']
        self.DB_LOGIN_NAME = DATABASES['default']['USER']
        self.DB_PASSWORD = DATABASES['default']['PASSWORD']
        self.DB_TABLE = DATABASES['default']['NAME']

        self.CONFIG_ID = config.id
        self.LDAP_SERVER_POOL = config.ldap_server_pool
        self.LDAP_SERVER_PORT = config.ldap_server_port
        self.ADMIN_DN = config.admin_dn
        self.ADMIN_PASSWORD = config.admin_pwd
        self.SEARCH_BASE = config.search_base
        self.GROUP = config.group

    def ad_sync_main(self):
        log.info("Start sync Active Directory")

        # job start time
        started = float(time.time())
        print("Start =", started)

        # create a new record in sync_log
        sync_log_id = self.create_new_log()
        print("create_new_log =", sync_log_id[0])
        if not sync_log_id[0]:
            print(sync_log_id[1])
            exit()
        else:
            sync_log_id = sync_log_id[1]

        res_conn = self.ad_sync_conn()
        print("ad_sync_conn = ", res_conn[0])
        if not res_conn[0]:
            print(res_conn[1])
            SYNC_LOG_SERVICE().sync_log(sync_log_id, started, 2, res_conn[1])
            exit()

        ad_user_list = self.ad_sync_get_user_list(res_conn[1])
        print("ad_sync_get_user_list = ", ad_user_list[0])
        if not ad_user_list[0]:
            print(ad_user_list[1])
            SYNC_LOG_SERVICE().sync_log(sync_log_id, started, 2, ad_user_list[1])
            exit()

        db_user_list = self.get_db_ldap_user()
        print("get_db_ldap_user =", db_user_list[0])
        if not db_user_list[0]:
            print(db_user_list[1])
            SYNC_LOG_SERVICE().sync_log(sync_log_id, started, 2, db_user_list[1])
            exit()

        check_user = self.check_user(ad_user_list[1], db_user_list[1], sync_log_id)
        print("check_user", check_user[1])
        if not check_user[0]:
            print(check_user[1])
            SYNC_LOG_SERVICE().sync_log(sync_log_id, started, 2, check_user[1])
            exit()

        SYNC_LOG_SERVICE().sync_log(sync_log_id, started, 1, 'success')
        print('SYNC Done')

    def create_new_log(self):
        try:
            sync_log_data = sync_log()
            sync_log_data.config_id = self.CONFIG_ID
            sync_log_data.run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sync_log_data.save()
            sync_log_id = sync_log_data.id
            return True, sync_log_id
        except Exception as e:
            print(e)
            return False, 'Create new log error'

    def ad_sync_conn(self):
        try:
            ldap_server_pool = ServerPool(self.LDAP_SERVER_POOL)
            conn = Connection(ldap_server_pool,
                              user=self.ADMIN_DN,
                              password=self.ADMIN_PASSWORD,
                              check_names=True,
                              lazy=False,
                              raise_exceptions=False)
            conn.open()
            conn.bind()

            # 查詢，指定特定Group
            s = "ou=PRJ,ou=Groups,dc=qxic,dc=net"
            res = conn.search(
                # search_base=self.SEARCH_BASE,  # 域目錄位置(cn, dc)
                search_base=s,
                search_filter=f'(&(objectclass=group)(cn={self.GROUP}))',  # 篩選條件
                search_scope=SUBTREE,
                attributes=[ALL_ATTRIBUTES]
            )

            # 判斷是否有回傳值
            if res:
                return True, conn
            else:
                return False, 'No Data'
        except Exception as e:
            print(e)
            msg = 'AD connection failed\n' + str(e)
            return False, msg

    def ad_sync_get_user_list(self, conn):
        try:
            ad_user_list = []
            # 取出回傳值
            for entry_1 in conn.response:
                # 取出 attributes
                dict_attr_1 = entry_1['attributes']
                # 取出 member
                for member in dict_attr_1['member']:
                    # 取得 CN
                    user_name = re.findall(r'CN=([^,]+),', str(member))[0]
                    user_name = user_name[:user_name.find('(')].strip()
                    print(user_name)
                    print(member)
                    print(self.SEARCH_BASE)
                    res_2 = conn.search(
                        search_base=self.SEARCH_BASE,
                        # search_filter=f'(&(objectclass=user)(displayName={user_name}))',
                        # search_filter=f'(distinguishedName={member})',
                        search_filter=f'(mailNickname={user_name})',
                        search_scope=SUBTREE,
                        attributes=['sAMAccountName', 'mail', 'userAccountControl'],
                    )
                    print(res_2)
                    if res_2:

                        # 修改
                        for entry_2 in conn.response:
                            dict_attr_2 = entry_2['attributes']
                            ad_user_list.append(dict_attr_2)
                            # Name = dict_attr_2['sAMAccountName']
                            # Mail = dict_attr_2['mail']
                            # userAccountControl = int(dict_attr_2['userAccountControl'])
                            # if not self.ldap_check_user(Name, Mail, userAccountControl, sync_log_data.id):
                            #     return False
                            print(1)
                    else:
                        return False, 'No member in DP_Automation_User'

                return True, ad_user_list

        except Exception as e:
            print(e)
            msg = 'search group member failed\n' + str(e)
            return False, msg

    def get_db_ldap_user(self):
        try:
            db_user_list = []
            user_data = user.objects.filter(ldap=1).values('loginname')
            for user_name in user_data:
                db_user_list.append(str(user_name['loginname']))
            return True, db_user_list
        except Exception as e:
            print(e)
            return False, 'Get db ldap user error'

    def check_user(self, ad_user_list, db_user_list, sync_log_id):
        try:
            for ad_user in ad_user_list:
                # AD user 有在 db_user_list 中
                print('  check:', ad_user['sAMAccountName'])
                if ad_user['sAMAccountName'] in db_user_list:
                    _o = user.objects.get(loginname=ad_user['sAMAccountName'], ldap=1)
                    # loginflag 與 ldap_group 為 True 才移出 db_user_list
                    if _o.loginflag and _o.ldap_group:
                        print('     remove', ad_user['sAMAccountName'])
                        db_user_list.remove(ad_user['sAMAccountName'])
                    elif not (_o.loginflag and _o.ldap_group):
                        print('     enable user:', ad_user)
                        if self.enable_user(ad_user, sync_log_id):
                            db_user_list.remove(ad_user['sAMAccountName'])
                        else:
                            return False, 'Enable user error'
                else:
                    print('     add user:', ad_user)
                    if not self.add_user(ad_user, sync_log_id):
                        return False, 'Add user error'
            if self.cancel_user(db_user_list, sync_log_id):
                return True, 'success',
            else:
                return False, 'Cancel user error'
        except Exception as e:
            print(e)
            return False, 'Check user error'

    def add_user(self, ad_user, sync_log_id):
        try:
            _o = user()
            _o.loginname = ad_user['sAMAccountName']
            _o.email = ad_user['mail']
            _o.ldap = 1
            _o.ldap_group = 1
            _o.loginflag = 1
            _o.save()

            _s = sync_log.objects.get(id=sync_log_id)
            _s.add += 1
            _s.save()

            SYNC_LOG_SERVICE().sync_log_detail(sync_log_id, ad_user['sAMAccountName'], 'add')
            return True
        except Exception as e:
            print(e)
            return False

    def enable_user(self, ad_user, sync_log_id):
        try:
            _o = user.objects.get(ldap=1, loginname=ad_user['sAMAccountName'])
            _o.ldap_group = 1
            _o.loginflag = 1
            _o.save()

            _s = sync_log.objects.get(id=sync_log_id)
            _s.enable += 1
            _s.save()

            SYNC_LOG_SERVICE().sync_log_detail(sync_log_id, ad_user['sAMAccountName'], 'enable')
            return True
        except Exception as e:
            print(e)
            return False

    def cancel_user(self, db_user_list, sync_log_id):
        try:
            print('  cancel_user  list_count:', len(db_user_list), ' db_user_list:', db_user_list)
            if len(db_user_list) == 0:
                return True
            else:
                for db_user in db_user_list:
                    count = user.objects.filter(loginname=db_user).values().count()
                    _o = user.objects.get(loginname=db_user)
                    if count == 0:
                        pass
                    elif _o.ldap_group or _o.loginflag:
                        print('     cancel:', db_user)
                        _o.ldap_group = 0
                        _o.loginflag = 0
                        _o.save()

                        _s = sync_log.objects.get(id=sync_log_id)
                        _s.cancel += 1
                        _s.save()

                        SYNC_LOG_SERVICE().sync_log_detail(sync_log_id, db_user, 'cancel')
                    return True
        except Exception as e:
            print(e)
            return False


class SYNC_LOG_SERVICE(BaseService):

    def sync_log(self, log_id, started, status, remark):
        try:
            print(log_id, started, status, remark)
            finished = float(time.time())
            print("finished =", finished)
            duration = finished - started
            sync_log.objects.filter(id=log_id).update(status=status,
                                                      duration=duration,
                                                      started=started,
                                                      finished=finished,
                                                      remark=remark)
        except Exception as e:
            print(e)

    @transaction.atomic
    def sync_log_detail(self, log_id, name, status):
        try:
            _s = sync_log_detail()
            _s.log_id = log_id
            _s.status = status
            _s.user = name
            _s.save()
        except Exception as e:
            print(e)


class Sync_Service(BaseService):

    # add
    def add_sync(self, sync_config_data):
        data = {}
        try:
            sync_config_data.save()
            data["success"] = True
            data["msg"] = "Success"
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)

    # update
    def upd_sync(self, sync_config_data, sync_id):
        data = {}
        try:
            sync_config_data.save()
            data["success"] = True
            data["msg"] = "Success"
            print('sysc===============')
            SYNC_JOB_SERVICE()
        except Exception as e:
            print(e)
            data["success"] = False
            data["msg"] = "Failed"

        return JsonResponse(data, safe=False)


def SYNC_JOB_SERVICE():
    # 根據ID取得同步資料
    config = sync_config.objects.get(id=1)
    # config = sync_config.objects.get(id=config.id, enable=1)

    # Schedule ID
    sync_schedule_id = 'sync_schedule_' + str(config.id)

    # 獲取jdv.jobs scheduler
    scheduler = get_scheduler()

    # 判斷enable
    if config.enable:
        try:
            scheduler.remove_job(sync_schedule_id)
            time_list = str(config.mode_time).split(':')
            time_sec = int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2])
            print(time_list, time_sec)
            if config.mode == 'interval':
                # Add job
                scheduler.add_job(func=AD_SYNC_SERVICE(config).ad_sync_main,
                                  trigger=config.mode,
                                  seconds=time_sec,
                                  id=sync_schedule_id)
            elif config.mode == 'cron':
                scheduler.add_job(func=AD_SYNC_SERVICE(config).ad_sync_main,
                                  trigger=config.mode,
                                  day_of_week='mon-sun',
                                  hour=int(time_list[0]),
                                  minute=int(time_list[1]),
                                  second=int(time_list[2]),
                                  id=sync_schedule_id)
        except Exception as e:
            print(e)
    else:
        try:
            # Remove job
            scheduler.remove_job(sync_schedule_id)
        except Exception as e:
            print(e)
            pass
