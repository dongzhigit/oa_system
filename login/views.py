# -*- coding: utf-8 -*-
from django.shortcuts import render,render_to_response,HttpResponseRedirect
#引用模板中的方法 防止 Forbidden (403)
from django.views.decorators.csrf import csrf_protect
from django.template import Template, Context,RequestContext
#用户登录
from django.contrib.auth import authenticate, login, logout
from django.contrib import auth
from django.contrib.auth.models import User
#公共全局变量
from django.conf import settings
#导入python-ldap
import ldap
import os
from no_attendance.models import *
#解决文件编码问题
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

#公共全局变量
def global_setting(request):
    """
    index  登录首页变量
    """

    SITE_URL = settings.SITE_URL
    return locals()

import json

#用户登录
# @csrf_protect
# # 认证操作
# def login_index(request):
#     prompt = "ldap用户登录"
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         if username and password:
#             try:
#                 user = OaUser.objects.get(name=username)
#                 if user:
#                     response = HttpResponseRedirect('/no_attendance/attendance/')
#                     # 将username写入浏览器cookie,失效时间为3600
#                     response.set_cookie('username', username, 3600)
#                     request.session['user'] = username
#                     return response
#             except:
#                 prompt = "用户或密码错误"
#         else:
#             prompt = "用户密码不能为空"
#
#     return render(request,'login/login_soft.html',locals())


# #用户退出
# def logout(request):
#     request.session.delete('user')
#     auth.logout(request)
#     return HttpResponseRedirect("/login")

from django.shortcuts import render, render_to_response
from ldaprz import *
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext

def userauth(username,passwd):
    ldappath = 'ldap://myzero.com:389'
    baseDN = 'ou=People,dc=myzero,dc=com'
    p = ldapc(ldappath, baseDN)
    yanzheng = p.valid_user(username, passwd)
    ziliao = ''
    if yanzheng == True:
        ziliao = p.search_user(username)[0][1]
    else:
        ziliao = 1
    return ziliao

def login_index(request):
    cn_name = request.COOKIES.get('username', '')
    if cn_name != '':
        return HttpResponseRedirect("/no_attendance/todo/")
    if request.method == 'POST':
        username = request.POST['username']
        passwd = request.POST['password']
        find = userauth(username,passwd)
        if find == 1:
            # email = find['mail'][0]
            # cn_name = find['cn'][0]
            response = HttpResponseRedirect("/no_attendance/todo/")
            # 将username写入浏览器cookie,失效时间为3600
            response.set_cookie('username', cn_name, 3600)
            response.set_cookie('username_us', username, 3600)
            return response
        else:
            log = '用户名或密码错误'

    return render_to_response('login/login_soft.html', locals(),context_instance=RequestContext(request))


def logout(request):
    response = HttpResponseRedirect('/login')
    #清理cookie里保存username
    response.delete_cookie('username')
    response.delete_cookie('username_us')
    return response
