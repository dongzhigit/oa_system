
#-*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import ldap

class ldapc:
    def __init__(self,ldap_path,baseDN):
        self.baseDN = baseDN
        self.ldap_error = None
        self.l=ldap.initialize(ldap_path)
        self.l.protocol_version = ldap.VERSION3

    def search_user(self,username): #精确查找，返回值为list，使用search()
        if self.ldap_error is None:
            try:
                searchScope = ldap.SCOPE_SUBTREE
                searchFiltername = "uid" #通过samaccountname查找用户
                retrieveAttributes = None
                searchFilter = '(' + searchFiltername + "=" + username +')'
                ldap_result_id =self.l.search(self.baseDN, searchScope, searchFilter, retrieveAttributes)
                result_type, result_data = self.l.result(ldap_result_id, 0)
                if result_type == ldap.RES_SEARCH_ENTRY:
                    return result_data
                else:
                    return "%s doesn't exist." %username
            except ldap.LDAPError as err:
                return err

    def search_userDN(self,username): #精确查找，最后返回该用户的DN值
        if self.ldap_error is None:
            try:
                searchScope = ldap.SCOPE_SUBTREE
                searchFiltername = "uid" #通过samaccountname查找用户
                retrieveAttributes = None
                searchFilter = '(' + searchFiltername + "=" + username +')'
                ldap_result_id =self.l.search(self.baseDN, searchScope, searchFilter, retrieveAttributes)
                result_type, result_data = self.l.result(ldap_result_id, 0)
                if result_type == ldap.RES_SEARCH_ENTRY:
                    return result_data[0][0] #list第一个值为用户的DN，第二个值是一个dict，包含了用户属性信息
                else:
                    return "%s doesn't exist." %username
            except ldap.LDAPError as err:
                return err

    def valid_user(self,username,userpassword): #验证用户密码是否正确
        if self.ldap_error is None:
            target_user = self.search_userDN(username) #使用前面定义的search_userDN函数获取用户的DN
            if target_user.find("doesn't exist") == -1:
                try:
                    self.l.simple_bind_s(target_user,userpassword)
                    return True
                except ldap.LDAPError as err:
                    return err
            else:
                return self.ldap_error
