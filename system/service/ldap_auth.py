from ldap3 import Connection, SUBTREE, ServerPool
from ldap3.core.exceptions import LDAPInvalidCredentialsResult
from Mask_DP.settings import LDAP


class ldap_auth:

    def __init__(self):
        self.LDAP_SERVER_POOL = LDAP['LDAP_SERVER_POOL']  # 域控服务器ip地址
        self.LDAP_SERVER_PORT = LDAP['LDAP_SERVER_PORT']  # 端口
        self.ADMIN_DN = LDAP['ADMIN_DN']  # 拥有查询权限的域账号
        self.ADMIN_PASSWORD = LDAP['ADMIN_PASSWORD']  # 对应的密码
        self.SEARCH_BASE = LDAP['SEARCH_BASE']

    def user_auth(self, username, password):
        ldap_server_pool = ServerPool(self.LDAP_SERVER_POOL)
        conn = Connection(ldap_server_pool,
                          user=self.ADMIN_DN,
                          password=self.ADMIN_PASSWORD,
                          check_names=True,
                          lazy=False,
                          raise_exceptions=False)
        conn.open()
        conn.bind()

        res = conn.search(
            search_base=self.SEARCH_BASE,
            search_filter='(sAMAccountName=%s)' % username,
            search_scope=SUBTREE,
        )
        if res:
            for entry in conn.response:
                dn = entry['dn']  # dn包含了ou與dc,在做域驗證登入時可以做為驗證帳號

                try:
                    # 使用用戶帳密登入
                    conn2 = Connection(ldap_server_pool,
                                       user=dn,
                                       password=password,
                                       check_names=True,
                                       lazy=False,
                                       raise_exceptions=True)
                    conn2.bind()
                    if conn2.result["description"] == "success":
                        return True, u'Success'
                except LDAPInvalidCredentialsResult as e:
                    print(e.message)
                    if '52e' in e.message:
                        return False, u'Account or password incorrect'
                    elif '775' in e.message:
                        return False, u'This account is locked. Please contact your system administrator'
                    elif '533' in e.message:
                        return False, u'This account is disable. Please contact your system administrator'
                    elif '773' in e.message:
                        return False, u'Success. But you should be reset password in other platform'
                    else:
                        return False, u'Authentication Failed'
        else:
            return False, u'This account is not exist'

# # LDAP SERVER
# LDAP = {
#     'LDAP_SERVER_POOL': ['192.168.40.1'],  # 域控服务器ip地址
#     'LDAP_SERVER_PORT': 389,  # 端口
#     'ADMIN_DN': 'swmaster@qxic.net',  # 拥有查询权限的域账号
#     'ADMIN_PASSWORD': 'RU6T/62U04XJ4',  # 对应的密码
#     'SEARCH_BASE': 'ou=OAUser,dc=qxic,dc=net',
# }
#
# account = 'test'
# password = '!qxic666666'
#
# result = ldap_auth(LDAP).user_auth(account, password)
# print(result)
