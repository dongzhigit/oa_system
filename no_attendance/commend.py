# -*- coding:utf-8 -*-

# 处理多维字典方法
class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return valu


#数据库操作
#传入登录用户名，返回，上级用户名，上一级用户id，组名

