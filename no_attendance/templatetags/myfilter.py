# -*- coding: utf-8 -*-
from no_attendance.models import *
from django import template
from no_attendance.commend import AutoVivification
from no_attendance.views import *
register = template.Library()

def oa_select(log_id):
    oa_h = log_id.oahandle_set.all()
    oa_u_list = []
    vlog_dict = AutoVivification()
    index = 0
    for h in oa_h:
        oa_u = OaUser.objects.filter(id=h.uid_id).values('name', 'department')[0]
        oa_u['status']= h.status
        vlog_dict[index]=oa_u
        index += 1
        #a = "%s:%s%s " % (oa_u['department'], oa_u['name'],h.status+"")
        #oa_u_list.append(a)
    #len(oa_u_list[0])
    #print oa_u_list
    print vlog_dict
    return vlog_dict.items()
    # for oa_u in user_id:
    #     oa_h = OaHandle.objects.filter(id=oa_u.id)
    #     for i in oa_h.u:
    #         print i.uid_id
# 定义一个将日期中的月份转换为大写的过滤器，如8转换为八

#过滤步骤表 状态
@register.filter
def user_count(u_id):
    return oa_select(u_id)
    #return 1

        #return  OaUser.objects.filter(id = oa_u.uid_id).values('name')[0]['name']
import json
@register.filter
def leave_t(leave_time):
    leave_time = changeTime(int(leave_time.split('-')[0].replace('.0', '')),int(leave_time.split('-')[1]))
    return "%s天 %s小时 %s分钟" %(leave_time['days'],leave_time['hours'],leave_time['mins'])

@register.filter
def leave_log(leave_id):
    # latest_id = OaLeaveLog.objects.filter(log_id=leave_id).latest('id')
    # return OaLeaveLog.objects.filter(id=latest_id.id)

    return OaLeaveLog.objects.filter(log_id=leave_id)

@register.filter
def leave_log_sp(leave_id):
    return OaLeaveLog.objects.filter(log_id=leave_id)

@register.filter
def username_hq(leave_id):
    return OaUser.objects.get(id=leave_id).cn_name

@register.filter
def enclosure(leave_id):
    return OaEnclosure.objects.filter(log_id=leave_id)

@register.filter
def fanxiang_log(log_id):
    return OaLeave.objects.filter(id=log_id.log_id)

@register.filter
def enclosure_log(log_id):
    return OaEnclosure.objects.filter(log_id=log_id.log_id)

# 注册过滤器
# register.filter('month_to_upper', month_to_upper)