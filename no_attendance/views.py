# -*- coding: utf-8 -*-
from django.shortcuts import render,render_to_response,HttpResponseRedirect
# from django.utils.datastructures import SortedDict
from collections import OrderedDict as SortedDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.template import Template, Context,RequestContext
from models import *
import datetime
import time
#解决文件编码问题
import sys
import json
import math
import imghdr
import os
import xlwt
import csv,codecs
from sql_server import *
import urllib2
import json
from django.db.models import Q
from sendmail import *

defaultencoding = 'utf-8'

if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

from commend import AutoVivification
img_path = '/home/oa/static/image_enclosure/'

def changeTime(allTime,type_time):
    hour = 60 * 60
    min = 60
    day = type_time * 60 * 60
    days = divmod(allTime, day)
    time_day = int(days[0])
    allTime = days[1]
    hours = divmod(allTime, hour)
    time_hour = int(hours[0])
    if type_time == 24:
        if time_hour >= 8:
            time_day = time_day + 1
            time_hour = time_hour - 8
    allTime = hours[1]
    mins = divmod(allTime, min)
    time_mins = int(mins[0])

    date_time = {}
    date_time["days"] = time_day
    date_time["hours"] = time_hour
    date_time["mins"] = time_mins
    return date_time

#时间转换成时间戳
def time_switch(date):
    gsh_time = date.replace('/', '-')
    timeArray = time.strptime(gsh_time, "%Y-%m-%d %H:%M")
    timestamp = time.mktime(timeArray)
    return timestamp

#时间筛选
def time_filtrate(log_list,date_s,date_x):
    pd_list = []
    for i in log_list:
        for i in log_list:
            if i.examine_status != '2':
                if i.end_time and date_x:
                    if time_switch(i.end_time) >= time_switch(date_s) >= time_switch(i.begin_time) or time_switch(i.end_time) >= time_switch(date_x) >= time_switch(i.begin_time) or time_switch(date_s) <= time_switch(i.end_time) <= time_switch(date_x) or time_switch(date_s) <= time_switch(i.begin_time) <= time_switch(date_x):
                        pd_list.append(time_switch(date_s))
                elif date_x:
                    if time_switch(date_x) >= time_switch(i.begin_time) >= time_switch(date_s):
                        pd_list.append(time_switch(date_s))
                elif i.end_time:
                    if time_switch(i.end_time) >= time_switch(date_s) >= time_switch(i.begin_time):
                        pd_list.append(time_switch(date_s))
                else:
                    if time_switch(i.begin_time) == time_switch(date_s):
                            pd_list.append(time_switch(date_s))

    return pd_list

#时间差计算
def time_difference(date_s,date_x):
    date_s_switch = time_switch(date_s)
    date_x_switch = time_switch(date_x)
    difference = date_x_switch - date_s_switch
    return difference

def user_dengji(user_id):
    oa_u = OaUser.objects.get(id=user_id)
    oa_u_r = oa_u.oauserorg_set.all()
    up_orgid_uid = 0
    up_id = ''
    for i in oa_u_r:
        # 上一级用户id
        up_orgid_uid = i.orgid.uid.id
        up_id = i.orgid.up_id
    if oa_u.id == up_orgid_uid:
        try:
            up_orgid_uid = OaOrg.objects.filter(id=up_id).values('uid')[0]['uid']
        except:
            up_orgid_uid = 0
    # oa_id = OaUser.objects.get(id=up_orgid_uid)
    return up_orgid_uid

def email_name_get(uid):
    oa_m = OaUser.objects.get(id=uid)
    return oa_m.mail

def time_calculation(allTime,qj_type,up_end_time=None,begin_time=None,types=None,leave_time=None):
    log = 0
    n_log = ''
    if qj_type != '事假':
        if qj_type == '婚假':
            if allTime / (60 * 60) % 8 == 0:
                if up_end_time != None and begin_time != None:
                    if time_difference(up_end_time,begin_time) >= 604800:
                        if changeTime(allTime, types)['days'] + changeTime(int(leave_time.split('.')[0]), int(leave_time.split('-')[1]))['days'] == 10:
                            log = 0
                        else:
                            log = 1
                            n_log = '婚假已修完或所提交婚假之和不等于十天，请查询之前婚假的请假记录'
                    else:
                        log = 1
                        n_log = '和上次婚假提交时间间隔需超过七天'
                else:
                    if allTime / (60 * 60) <= 240:
                        log = 0
                    else:
                        log = 1
                        n_log = '婚假最多能请10天'
            else:
                log = 1
                n_log = '婚假只能以天为单位'
        else:
            if allTime / (60 * 60) % 4 == 0:
                log = 0
            else:
                log = 1
                n_log = '只能以半天为单位'
    return log,n_log

def get_week_day(date):
    # tool_dict = {
    #     '0':'工作日',
    #     '1':'周末',
    #     '2':'假日',
    # }
    week_day_dict = {
    0 : '星期一',
    1 : '星期二',
    2 : '星期三',
    3 : '星期四',
    4 : '星期五',
    5 : '星期六',
    6 : '星期日',
    }
    # url_save = 'http://tool.bitefu.net/jiari/?d=%s' %date
    # s_save = urllib2.urlopen(url_save).read()
    day = datetime.datetime.strptime(date,'%Y%m%d').weekday()
    # return week_day_dict[day],tool_dict[s_save]
    return week_day_dict[day],day


#提交请假单
def leave(request):
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    t = time.time()
    title_content = "休假申请单"
    apply_type = OaApplyType.objects.all()
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    log = ''
    oa_u = OaUser.objects.get(name=login_user)
    department = oa_u.department
    position = oa_u.position
    reason = ''
    param = ''
    time_file_name = int(round(t * 1000))
    log_list = OaLeave.objects.filter(uid=oa_u.id)
    hj_log_list = ''
    time_log = ''
    n_log = ''
    worker_time = ''

    if request.method == 'POST':
        img = request.FILES.getlist('fileUpload')
        img_num = 1
        types = 24
        date_s = request.POST['date_s']  # 时间上午
        date_x = request.POST['date_x']  # 时间下午
        outgoing_cause = request.POST['outgoing_cause']
        pd_list = []
        try:
            reason = request.POST['reason']
            param = json.loads(reason)
            if date_s:
                if date_x:
                    if outgoing_cause:
                        sec_s = int(date_s[-2:])
                        sec_x = int(date_x[-2:])
                        if sec_s == 30 or sec_s == 0:
                            if sec_x == 30 or sec_x == 0:
                                if time_switch(date_s) < time_switch(date_x) or time_switch(date_s) == time_switch(date_x):
                                    if time_filtrate(log_list,date_s,date_x) == []:
                                        time_s = date_s[11:]
                                        time_x = date_x[11:]
                                        if '17:30' > time_s >= '08:30' and '08:30' < time_x <= '17:30':
                                            if time_s != '13:00' and time_x != '13:00':
                                                if date_s[0:10] == date_x[0:10]:
                                                    types = 8
                                                    if time_s <= '12:30' and time_x >= '13:30':
                                                        nums = time_difference(date_s, date_x) - 3600
                                                    # elif time_s >= '12:30' and time_x <= '13:30':
                                                    #     nums = time_difference(date_s, date_x) - 57600 + 3600
                                                    else:
                                                        nums = time_difference(date_s, date_x)
                                                else:
                                                    if time_s <= '12:30' and time_x >= '13:30':
                                                        nums = time_difference(date_s, date_x) + 57600 - 3600
                                                    elif time_s >= '12:30' and time_x <= '13:30':
                                                        nums = time_difference(date_s, date_x) + 3600
                                                    else:
                                                        nums = time_difference(date_s, date_x)
                                                if nums != 0:
                                                    data_time = changeTime(nums, types)
                                                    days = data_time['days']
                                                    hours = data_time['hours']
                                                    mins = data_time['mins']
                                                    leave_time = {}
                                                    leave_time['days'] = days
                                                    leave_time['hours'] = hours
                                                    leave_time['mins'] = mins
                                                    if days >= 3:
                                                        number = 4
                                                    elif 2 <= days > 1:
                                                        number = 3
                                                    else:
                                                        number = 1
                                                    time_stamp_s = ''
                                                    time_stamp_x = ''
                                                    if int(param['company']) == 0:
                                                        time_stamp_s = 60 * int(param['min'])
                                                        if param['max'] != 'None':
                                                            time_stamp_x = 60 * int(param['max'])
                                                    elif int(param['company']) == 1:
                                                        time_stamp_s = 60 * 60 * int(param['min'])
                                                        if param['max'] != 'None':
                                                            time_stamp_x = 60 * 60 * int(param['max'])
                                                    else:
                                                        time_stamp_s = 60 * 60 * 24 * int(param['min'])
                                                        if param['max'] != 'None':
                                                            time_stamp_x = 60 * 60 * 24 * int(param['max'])

                                                    if param['type'] == '婚假':
                                                        try:
                                                            worker = request.POST['worker']
                                                            worker_time = request.POST['worker_time']
                                                            if worker == '0':
                                                                if worker_time:
                                                                    if time_s == '08:30':
                                                                        st = datetime.datetime.strptime(worker_time, "%Y-%m-%d")
                                                                        ed = datetime.datetime.strptime(date_s.replace('/', '-'), "%Y-%m-%d %H:%M")
                                                                        if st < ed:
                                                                            rtn = (ed - st).days + 1
                                                                            if rtn >= 90:
                                                                                hj_log_list = log_list.filter(leave_type='婚假')
                                                                            else:
                                                                                log = '入职时间与转正时间不符'
                                                                                return render(request,'no_attendance/leave.html',locals())
                                                                        else:
                                                                            log = '入职时间不能大于请假时间'
                                                                            return render(request,'no_attendance/leave.html',locals())
                                                                    else:
                                                                        log = '婚假起始时间必须为8:30'
                                                                        return render(request,'no_attendance/leave.html',locals())
                                                                else:
                                                                    log = '入职时间不能为空'
                                                                    return render(request, 'no_attendance/leave.html',locals())
                                                            else:
                                                                log = '未转正不能提交婚假'
                                                                return render(request, 'no_attendance/leave.html',locals())
                                                        except:
                                                            log = '请选择是否转正'
                                                            return render(request, 'no_attendance/leave.html', locals())
                                                    else:
                                                        hj_log_list = log_list
                                                    hj_time_list = []
                                                    leave_time_2 = ''

                                                    for i in hj_log_list:
                                                        if i.examine_status != '2':
                                                            hj_time_list.append(i.end_time)
                                                            leave_time_2 = i.leave_time
                                                    sql_superior = user_dengji(oa_u.id)
                                                    dq_time = time_switch(time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time())))
                                                    if sql_superior != 0:
                                                        leave_time_type = '%s-%s' %(nums,types)
                                                        if hj_time_list:
                                                            if param['type'] == '婚假':
                                                                if len(hj_time_list) >= 2:
                                                                    time_log = 1
                                                                    n_log = '婚假最多只能提交两次'
                                                                elif time_switch(date_s) - dq_time <= 259200:
                                                                    time_log = 1
                                                                    n_log = '婚假需提前三天申请'
                                                                elif len(hj_time_list) == 1:
                                                                    time_log,n_log = time_calculation(nums, param['type'],max(hj_time_list), date_s,types,leave_time_2)
                                                                else:
                                                                    time_log,n_log = time_calculation(nums, param['type'],max(hj_time_list),date_s)
                                                            else:
                                                                time_log,n_log = time_calculation(nums, param['type'])
                                                        else:
                                                            if time_switch(date_s) - dq_time <= 259200:
                                                                time_log = 1
                                                                n_log = '婚假需提前三天申请'
                                                            else:
                                                                time_log,n_log = time_calculation(nums, param['type'])

                                                        if time_stamp_x:
                                                            if time_stamp_s <= nums <= time_stamp_x:
                                                                if param['show'] == 0:
                                                                    if img:
                                                                        for f in img:
                                                                            if imghdr.what(f) != None:
                                                                                img_num = img_num + 1
                                                                            else:
                                                                                img_num = 0
                                                                        if img_num != 0:
                                                                            file_name_list = []
                                                                            for f in img:
                                                                                filepath, tempfilename = os.path.split(
                                                                                    f.name)
                                                                                shotname, extension = os.path.splitext(
                                                                                    f.name)
                                                                                file_name = shotname + '-' + str(
                                                                                    time_file_name) + extension
                                                                                file_name_list.append(file_name)
                                                                                destination = open(img_path + file_name, 'wb+')
                                                                                for chunk in f.chunks():
                                                                                    destination.write(chunk)
                                                                                destination.close()
                                                                            if time_log == 0:
                                                                                sql_logs = OaLeave.objects.create(
                                                                                    uid=oa_u.id,
                                                                                    department=department,
                                                                                    position=position,
                                                                                    leave_type=param['type'],
                                                                                    begin_time=date_s,
                                                                                    end_time=date_x,
                                                                                    reason=outgoing_cause,
                                                                                    submit_time=date_time,
                                                                                    leave_time=leave_time_type,
                                                                                    entry_time=worker_time,
                                                                                    examine_status=0,
                                                                                    examine_level=number,
                                                                                    superior=sql_superior,
                                                                                )
                                                                                for enclosure in file_name_list:
                                                                                    OaEnclosure.objects.create(log=sql_logs,
                                                                                                               filename=enclosure)
                                                                                OaLeaveLog.objects.create(log=sql_logs,
                                                                                                          uid=None, status=None,
                                                                                                          datetime=None,
                                                                                                          last_uid=None,
                                                                                                          outgoing_cause='')
                                                                                mail_name = email_name_get(sql_superior)
                                                                                content = '您有一个新的待办事项需要处理，请登录http://192.168.50.226:8080 处理'
                                                                                send_email('dongzhi.li@zerotech.com',content)
                                                                                param = ''
                                                                                date_s = ''
                                                                                date_x = ''
                                                                                outgoing_cause = ''
                                                                                log = "提交成功"
                                                                            else:
                                                                                log = n_log
                                                                        else:
                                                                            log = "上传文件类型错误，请选择图片格式上传"
                                                                    else:
                                                                        log = "请选择附件"
                                                                else:
                                                                    if time_log == 0:
                                                                        sql_logs = OaLeave.objects.create(
                                                                            uid=oa_u.id,
                                                                            department=department,
                                                                            position=position,
                                                                            leave_type=param['type'],
                                                                            begin_time=date_s,
                                                                            end_time=date_x,
                                                                            reason=outgoing_cause,
                                                                            submit_time=date_time,
                                                                            leave_time=leave_time_type,
                                                                            entry_time=worker_time,
                                                                            examine_status=0,
                                                                            examine_level=number,
                                                                            superior=sql_superior,
                                                                        )
                                                                        OaLeaveLog.objects.create(log=sql_logs, uid=None, status=None,
                                                                                                  datetime=None, last_uid=None,
                                                                                                  outgoing_cause='')
                                                                        mail_name = email_name_get(sql_superior)
                                                                        content = '您有一个新的待办事项需要处理，请登录http://192.168.50.226:8080处理'
                                                                        send_email('dongzhi.li@zerotech.com', content)
                                                                        param = ''
                                                                        date_s = ''
                                                                        date_x = ''
                                                                        outgoing_cause = ''
                                                                        log = "提交成功"
                                                                    else:
                                                                        log = n_log
                                                            else:
                                                                log = "请假时间大于或小于申请单位"
                                                        else:
                                                            if time_stamp_s <= nums:
                                                                if param['show'] != 1:
                                                                    if img:
                                                                        for f in img:
                                                                            if imghdr.what(f) != None:
                                                                                img_num = img_num + 1
                                                                            else:
                                                                                img_num = 0
                                                                        if img_num != 0:
                                                                            file_name_list = []
                                                                            for f in img:
                                                                                filepath, tempfilename = os.path.split(
                                                                                    f.name)
                                                                                shotname, extension = os.path.splitext(
                                                                                    f.name)
                                                                                file_name = shotname + '-' + str(
                                                                                    time_file_name) + extension
                                                                                file_name_list.append(file_name)
                                                                                destination = open(img_path + file_name, 'wb+')
                                                                                for chunk in f.chunks():
                                                                                    destination.write(chunk)
                                                                                destination.close()
                                                                            if time_log == 0:
                                                                                sql_logs = OaLeave.objects.create(
                                                                                    uid=oa_u.id,
                                                                                    department=department,
                                                                                    position=position,
                                                                                    leave_type=param['type'],
                                                                                    begin_time=date_s,
                                                                                    end_time=date_x,
                                                                                    reason=outgoing_cause,
                                                                                    submit_time=date_time,
                                                                                    leave_time=leave_time_type,
                                                                                    entry_time=worker_time,
                                                                                    examine_status=0,
                                                                                    examine_level=number,
                                                                                    superior=sql_superior,
                                                                                )
                                                                                for enclosure in file_name_list:
                                                                                    OaEnclosure.objects.create(log=sql_logs,
                                                                                                               filename=enclosure)
                                                                                OaLeaveLog.objects.create(log=sql_logs,
                                                                                                          uid=None, status=None,
                                                                                                          datetime=None,
                                                                                                          last_uid=None,
                                                                                                          outgoing_cause='')
                                                                                mail_name = email_name_get(sql_superior)
                                                                                content = '您有一个新的待办事项需要处理，请登录http://192.168.50.226:8080处理'
                                                                                send_email('dongzhi.li@zerotech.com',
                                                                                           content)
                                                                                param = ''
                                                                                date_s = ''
                                                                                date_x = ''
                                                                                outgoing_cause = ''
                                                                                log = "提交成功"
                                                                            else:
                                                                                log = n_log
                                                                        else:
                                                                            log = "上传文件类型错误，请选择图片格式上传"
                                                                    else:
                                                                        log = "请选择附件"
                                                                else:
                                                                    if time_log == 0:
                                                                        sql_logs = OaLeave.objects.create(
                                                                            uid=oa_u.id,
                                                                            department=department,
                                                                            position=position,
                                                                            leave_type=param['type'],
                                                                            begin_time=date_s,
                                                                            end_time=date_x,
                                                                            reason=outgoing_cause,
                                                                            submit_time=date_time,
                                                                            leave_time=leave_time_type,
                                                                            examine_status=0,
                                                                            examine_level=number,
                                                                            superior=sql_superior,
                                                                        )
                                                                        OaLeaveLog.objects.create(log=sql_logs, uid=None, status=None,
                                                                                                  datetime=None, last_uid=None,
                                                                                                  outgoing_cause='')
                                                                        mail_name = email_name_get(sql_superior)
                                                                        content = '您有一个新的待办事项需要处理，请登录http://192.168.50.226:8080处理'
                                                                        send_email('dongzhi.li@zerotech.com', content)
                                                                        param = ''
                                                                        date_s = ''
                                                                        date_x = ''
                                                                        outgoing_cause = ''
                                                                        log = "提交成功"
                                                                    else:
                                                                        log = n_log
                                                            else:
                                                                log = "请假时间小于申请最小单位"
                                                    else:
                                                        log = "用户没有上一级领导，请联系管理员添加"
                                                else:
                                                    log = "时间选择错误，请从新选择"
                                            else:
                                                log = "选择时间非上班时间"
                                        else:
                                            log = "起始时间或结束时间超出上班时间范围"
                                    else:
                                        log = "同时间段不能重复提交"
                                else:
                                    log = "起始时间大于结束时间或两个日期时间相同，请重新选择"
                            else:
                                log = "请选择整点时间"
                        else:
                            log = "请选择整点时间"
                    else:
                        log = "请填写请假事由"
                else:
                    log = "请选择结束时间"
            else:
                log = "请选择起始时间"
        except KeyError:
            log = "请选择申请类别"
    # log = json.dumps(log, encoding='utf-8', ensure_ascii=False)
    return render(request,'no_attendance/leave.html',locals())


#提交考勤全局变量
time_list = []
for i in range(0, 24):
    if len(str(i)) == 1:
        time_list.append("0%d:00" % (i))
        time_list.append("0%d:30" % (i))
    else:
        time_list.append("%d:00" % (i))
        time_list.append("%d:30" % (i))

# @csrf_protect
def attendance(request):
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    #返回，上级用户名，上一级用户id，组名
    oa_u = OaUser.objects.get(name=login_user)
    department = oa_u.department
    position = oa_u.position
    username = oa_u.name
    oa_u_r = oa_u.oauserorg_set.all()
    log_list = OaLeave.objects.filter(uid=oa_u.id)
    up_orgid_uid = user_dengji(oa_u.id)
    title_content = "未考勤说明单"
    if request.method == 'POST':
        # 未考勤原因
        try:
            reason = request.POST['reason']
        except:
            reason = ''
        #未考勤时间
        try:
            date_s = request.POST['date_s'] #时间上午
        except:
            date_s = ''
        try:
            date_x = request.POST['date_x'] # 时间下午
        except:
            date_x = ''
        try:
            outgoing_cause = request.POST['outgoing_cause']
        except:
            outgoing_cause = ''
        if reason:
            date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            if up_orgid_uid != 0:
                if reason == u'忘打卡':
                    if date_s:
                        if time_switch(date_s) >= time_switch(time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time()))):
                            title_content_log = "忘打卡时间选择不能选择未发生的时间"
                            return render(request, 'no_attendance/attendance.html', locals())
                        else:
                            if time_filtrate(log_list,date_s,date_x) == []:
                                if date_s[11:] == "08:30" or date_s[11:] == "17:30":
                                    time_a = [ date_s if date_s else date_x]
                                    if time_a[0].split(' ')[1] in time_list:
                                        title_content_log = "提交成功"
                                        log_id = OaLeave.objects.create(
                                            uid=oa_u.id,
                                            department=department,
                                            position=position,
                                            leave_type=reason,
                                            begin_time=date_s,
                                            end_time='',
                                            reason='',
                                            submit_time=date_time,
                                            leave_time=None,
                                            examine_status=0,
                                            examine_level=1,
                                            superior=up_orgid_uid,
                                        )
                                        OaLeaveLog.objects.create(log=log_id, uid=None, status=None,
                                                                  datetime=None, last_uid=None,
                                                                  outgoing_cause='')
                                        reason = ''
                                        date_s = ''
                                        date_x = ''
                                        outgoing_cause = ''
                                else:
                                    title_content_log = "忘打卡时间请选择“08:30”或“17:30”，其他时间不存在忘打卡情况"
                                    return render(request, 'no_attendance/attendance.html', locals())
                            else:
                                title_content_log = "同时间段不能重复提交"
                                return render(request, 'no_attendance/attendance.html', locals())
                    else:
                        title_content_log = "时间选择错误  时间选择为半点"
                        return render(request, 'no_attendance/attendance.html', locals())
                    # else:
                    #     title_content_log = "未考勤时间不能为空"
                    #     return render(request, 'no_attendance/attendance.html', locals())

                else:
                    types = 24
                    # if not outgoing_cause:
                    #     title_content_log = "因公外出必须填写外出事由"
                    #     return render(request, 'no_attendance/attendance.html', locals())
                    if date_s and date_x:
                        if time_switch(date_s) < time_switch(date_x) or time_switch(date_s) == time_switch(date_x):
                            if time_filtrate(log_list,date_s,date_x) == []:
                                if date_s.split(' ')[1] in time_list and date_x.split(' ')[1] in time_list:
                                    time_s = date_s[11:]
                                    time_x = date_x[11:]
                                    if date_s[0:10] == date_x[0:10]:
                                        types = 8
                                    if time_s <= '12:30' and time_x >= '13:30':
                                        nums = time_difference(date_s, date_x) - 3600
                                    else:
                                        nums = time_difference(date_s, date_x)
                                    if nums != 0:
                                        leave_time_type = '%s-%s' % (nums, types)
                                        data_time = changeTime(nums, types)
                                        title_content_log = "单提交成功"
                                        log_id = OaLeave.objects.create(
                                            uid=oa_u.id,
                                            department=department,
                                            position=position,
                                            leave_type=reason,
                                            begin_time=date_s,
                                            end_time=date_x,
                                            reason=outgoing_cause,
                                            submit_time=date_time,
                                            leave_time=leave_time_type,
                                            examine_status=0,
                                            examine_level=1,
                                            superior=up_orgid_uid,
                                        )
                                        OaLeaveLog.objects.create(log=log_id, uid=None, status=None,
                                                                  datetime=None, last_uid=None,
                                                                  outgoing_cause='')
                                        reason = ''
                                        date_s = ''
                                        date_x = ''
                                        outgoing_cause = ''
                                    else:
                                        title_content_log = "时间选择错误"
                                        return render(request, 'no_attendance/attendance.html', locals())
                                else:
                                    title_content_log = "因公外出 时间选择错误  时间选择为半点"
                                    return render(request, 'no_attendance/attendance.html', locals())
                            else:
                                title_content_log = "同时间段不能重复提交"
                                return render(request, 'no_attendance/attendance.html', locals())
                        else:
                            title_content_log = "结束时间不能大于起始时间"
                            return render(request, 'no_attendance/attendance.html', locals())
            #         else:
            #             title_content_log = "未考勤时间 因公外出 时间选择错误  请选择两个时间 起始时间与结束时间"
            #             return render(request, 'no_attendance/attendance.html', locals())
            #
            # else:
            #     title_content_log = "未考勤时间 未考勤原因不能为空"
            #     return render(request, 'no_attendance/attendance.html', locals())
            else:
                log = "用户没有上一级领导，请联系管理员添加"
    return render(request,'no_attendance/attendance.html',locals())


#代办事项
def todo(request,date=None):
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    #获取用户id
    oa_u = OaUser.objects.get(name=login_user)
    content_a = OaLeave.objects.filter(superior=oa_u.id)

    log = []
    if request.method == 'POST':
        submit = request.POST['submit'].split(',')
        outgoing_cause = request.POST['outgoing_cause']
        logcon = OaLeave.objects.get(id=submit[1])
        mail_name = ''
        if submit[0] == '1':
            OaLeaveLog.objects.create(log_id=submit[1], uid=oa_u.id, status=submit[0], datetime=date_time,
                                      last_uid=oa_u.id, outgoing_cause=outgoing_cause)
            logcon.examine_level = logcon.examine_level - 1
            if logcon.examine_level == 0:
                rl_uid = OaOrg.objects.get(org_name='人力资源')
                logcon.superior = rl_uid.uid.id
                logcon.examine_status = 1
                mail_name = rl_uid.uid.mail
            elif logcon.examine_level < 0:
                logcon.examine_status = 3
                mail_name = email_name_get(logcon.uid)
            else:
                logcon.superior = user_dengji(oa_u.id)
                if logcon.superior == 0:
                    rl_uid = OaOrg.objects.get(org_name='人力资源')
                    logcon.superior = rl_uid.uid.id
                    logcon.examine_status = 1
                    logcon.examine_level = 0
                    mail_name = rl_uid.uid.mail
                else:
                    logcon.examine_status = 1

            logcon.save()
            content = '您有一个新的待办事项需要处理，请登录http://192.168.50.226:8080 处理'
            send_email('dongzhi.li@zerotech.com', content)
            log.append("审批成功")
        else:
            if outgoing_cause:
                OaLeaveLog.objects.create(log_id=submit[1], uid=oa_u.id, status=submit[0], datetime=date_time,
                                          last_uid=oa_u.id, outgoing_cause=outgoing_cause)
                logcon.examine_status = 2
                logcon.save()
                mail_name = oa_u.mail
                content = '您有一个新的待办事项需要处理，请登录http://192.168.50.226:8080处理'
                send_email('dongzhi.li@zerotech.com', content)
                log.append("审批成功")
            else:
                log.append("不同意请填写反馈信息")
    log = json.dumps(log, encoding='utf-8', ensure_ascii=False)
    return render(request,'no_attendance/todo.html',locals())

#考勤请假申请记录
def record(request):
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    oa_u = OaUser.objects.get(name=login_user)
    title_content = "考勤请假申请记录"
    w_bacth = OaLeave.objects.filter(uid=oa_u.id).filter(examine_status=0)
    bacth_z = OaLeave.objects.filter(uid=oa_u.id).filter(examine_status=1)
    y_bacth = OaLeave.objects.filter(uid=oa_u.id).filter(examine_status=2)
    t_bacth = OaLeave.objects.filter(uid=oa_u.id).filter(examine_status=3)
    if request.method == 'POST':
        log_id = request.POST['submit']
        sql_id = OaLeave.objects.filter(id=log_id)
        for i in OaEnclosure.objects.filter(log_id=sql_id):
            os.remove(img_path + i.filename)
        OaLeaveLog.objects.filter(log_id=sql_id).delete()
        OaEnclosure.objects.filter(log_id=sql_id).delete()
        sql_id.delete()

    return render(request,'no_attendance/record.html',locals())

def examination(request):
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    title_content = "审核记录"
    oa_u = OaUser.objects.get(name=login_user)
    log_id = OaLeaveLog.objects.filter(uid=oa_u.id)
    apply_type = OaApplyType.objects.all()

    return render(request, 'no_attendance/examination.html', locals())

def useradd(request):
    admin_list = ['李冬志', '徐亚楠', '张敏', '刘晶晶']
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    group = OaOrg.objects.all()
    user_a = OaUser.objects.all()
    user_org_a = OaUserOrg.objects.all()
    user_list = []
    oa_u = OaUser.objects.get(name=login_user)
    if oa_u.cn_name not in admin_list:
        log = '权限不足'
        return render(request, 'no_attendance/todo.html', locals())
    for i in user_a:
        user_list.append(int(i.id))

    for org in user_org_a:
        user_list.remove(int(org.uid.id))

    userall = []
    for all in user_list:
        userall.append({'uid':all,'username':OaUser.objects.filter(id=all).values('cn_name')[0]['cn_name']})
    if not userall:
        title = "没有新用户"
        return render(request, 'admin/useradd.html', locals())
    userall = json.dumps(userall)
    title = "添加用户到部门/组"
    if request.method == 'POST':
        department = request.POST['department']
        staff = request.POST['user']
        if department != 1 and staff:
            department_id = OaOrg.objects.get(org_name=department)
            for i in staff.split(','):
                if i:
                    OaUserOrg.objects.create(uid=OaUser.objects.get(cn_name=i),orgid=department_id)
            title = "用户添加成功"
            user_list = []
            for i in OaUser.objects.all():
                user_list.append(int(i.id))

            for org in OaUserOrg.objects.all():
                user_list.remove(int(org.uid.id))

            userall = []
            for all in user_list:
                userall.append({'uid': all, 'username': OaUser.objects.filter(id=all).values('cn_name')[0]['cn_name']})
            if not userall:
                title = "用户添加成功，没有新用户"
                return render(request, 'admin/useradd.html', locals())
            userall = json.dumps(userall)

        else:
            title = "选择错误，都不能为空"
    return render(request, 'admin/useradd.html', locals())

def modify(request):
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    group = OaOrg.objects.all()
    # userall = OaUser.objects.all()
    user_org_a = OaUserOrg.objects.all()
    userall_list = []
    oa_u = OaUser.objects.get(name=login_user)
    admin_list = ['李冬志', '徐亚楠', '张敏', '刘晶晶']
    if oa_u.cn_name not in admin_list:
        log = '权限不足'
        return render(request, 'no_attendance/todo.html', locals())
    for all in user_org_a:
        userall_list.append({'uid': all.uid.id, 'username': OaUser.objects.filter(id=all.uid.id).values('cn_name')[0]['cn_name']})
    if not userall_list:
        title = "没有新用户"
        return render(request, 'admin/useradd.html', locals())
    userall = json.dumps(userall_list)

    title = "部门/组用户修改 和 部门/组负责人修改"
    if request.method == 'POST':
        department = request.POST['department']
        staff = request.POST['user']
        department_user = request.POST['department_user']

        if department == u'1':
            title = "修改错误，只能修改部门用户或者修改部门负责人,部门必须选择"
            return render(request, 'admin/modify.html', locals())

        if department and staff:
            for i in staff.split(','):
                if i:
                    OaUserOrg.objects.filter(uid=OaUser.objects.get(cn_name=i)).update(orgid=OaOrg.objects.get(org_name=department))
            title = "部门用户修改成功"

        if department and department_user != u'11':
            OaOrg.objects.filter(org_name=department).update(uid=OaUser.objects.get(cn_name=department_user))
            # department_user_id = OaUser.objects.get(name=department_user)
            title = "部门负责人修改成功"


    return render(request, 'admin/modify.html', locals())

def work_backup(request):
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    oa_u = OaUser.objects.get(name=login_user)
    admin_list = ['李冬志', '徐亚楠', '张敏', '刘晶晶']
    if oa_u.cn_name not in admin_list:
        log = '权限不足'
        return render(request, 'no_attendance/todo.html', locals())
    username = OaUser.objects.all()
    kq_type = OaApplyType.objects.all()
    if request.method == 'POST':
        # kwargs = Q()
        # name_list = {'uid':4, 'leave_type':'事假','examine_status':0}
        # for i in name_list:
        #     kwargs.add(Q(**{i: name_list[i]}), Q.AND)
        kwargs = {}
        name_list = ['uid', 'leave_type', 'examine_status']
        for i in name_list:
            if request.POST.get(i):
                kwargs[i] = request.POST.get(i)

        sj_list = OaLeave.objects.filter(**kwargs)
        log = 0
        examine_status = {
            '0':'未审批',
            '1':'审批中',
            '2':'审批未通过',
            '3':'审批已通过',
        }
        if sj_list:
            file_path = '/home/oa/excel_file/'
            file_name ='%s%s' %(int(round(time.time() * 1000)),'-data.csv')
            f = open(file_path + file_name, 'w')
            f.write(codecs.BOM_UTF8)
            f.write('用户名' + ',类型' + ',起始时间' + ',结束时间' + ',合计天数' + ',审核状态' + '\n')
            for i in sj_list:
                if request.POST.get('begin_time') != '' and request.POST.get('end_time') != '':
                    c_begin_time = time_switch(str(request.POST.get('begin_time'))+' 00:00')
                    c_end_time = time_switch(str(request.POST.get('end_time'))+' 23:59')
                    s_begin_time = time_switch(i.begin_time)
                    s_end_time = time_switch(i.end_time)
                    if c_end_time >= s_begin_time >= c_begin_time or c_end_time >= s_end_time >= c_begin_time:
                        v = ''
                        if s_end_time:
                            leave_time = changeTime(int(i.leave_time.split('-')[0].replace('.0', '')),
                                                    int(i.leave_time.split('-')[1]))
                            v = "%s天 %s小时 %s分钟" % (leave_time['days'], leave_time['hours'], leave_time['mins'])
                        f.write(str(username.get(id=i.uid).cn_name) + ',' + str(i.leave_type) + ',' + str(
                            i.begin_time) + ',' + str(i.end_time) + ',' + str(v) + ',' + examine_status[i.examine_status] + '\n')
                    else:
                        log = 1
                else:
                    log = 1
                    v = ''
                    if i.end_time:
                        leave_time = changeTime(int(i.leave_time.split('-')[0].replace('.0', '')), int(i.leave_time.split('-')[1]))
                        v = "%s天 %s小时 %s分钟" %(leave_time['days'],leave_time['hours'],leave_time['mins'])
                    f.write(str(username.get(id=i.uid).cn_name)+','+str(i.leave_type)+','+str(i.begin_time)+','+str(i.end_time)+','+str(v) + ',' + examine_status[i.examine_status] +'\n')
            f.close()
            if log == 1:
                def file_iterator(file_name, chunk_size=512):
                    with open(file_name, 'rb') as f:
                        while True:
                            c = f.read(chunk_size)
                            if c:
                                yield c
                            else:
                                break
                response = StreamingHttpResponse(file_iterator(file_path + file_name))
                response['Content-Type'] = 'application/vnd.ms-excel'
                response['Content-Disposition'] = 'attachment;filename="%s"' %file_name
                return response

    return render(request, 'no_attendance/test_execl.html', locals())

def check_work(request):
    login_user = request.COOKIES.get('username_us', '')
    if login_user == '':
        return HttpResponseRedirect("/login/")
    oa_u = OaUser.objects.get(name=login_user)
    admin_list = ['李冬志', '徐亚楠', '张敏', '刘晶晶']
    cn_name = oa_u.cn_name
    begintime = (datetime.date.today().replace(day=1) - datetime.timedelta(1)).replace(day=26).__format__('%Y-%m-%d')
    endtime = datetime.date.today().replace(day=25).__format__('%Y-%m-%d')
    present_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    username = cn_name
    check_box_list = ''

    if request.method == 'POST':
        # username = request.POST['username'].encode('unicode-escape').decode('string_escape')
        try:
            username = request.POST['username']
        except KeyError:
            pass
        try:
            check_box_list = request.POST.getlist("vehicle")[0]
        except IndexError:
            pass
        begintime = str(request.POST['begintime'])
        endtime = str(request.POST['endtime'])
        if begintime and endtime:
            if begintime <= endtime:
                format_begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d').date()
                format_endtime = datetime.datetime.strptime(endtime,'%Y-%m-%d').date()
                ms = MSSQL()
                select_sql = "SELECT BADGENUMBER,USERID,NAME FROM USERINFO WHERE NAME='%s'" %username
                select_name_sql = ms.ExecQuery(select_sql)
                select_name_list = []
                for i in select_name_sql:
                    select_name_list.append((int(i[0]),i[1],i[2]))
                try:
                    select_name = max(select_name_list)
                    uid = select_name[1]
                    userid = select_name[0]
                # except IndexError:
                except ValueError:
                    exit()

                sql = "select USERID,CHECKTIME from CHECKINOUT where USERID=%s and CHECKTIME >= '%s' and CHECKTIME <= '%s'" %(uid,begintime,endtime+' 23:59:59')
                resList = ms.ExecQuery(sql)
                timelist = []
                for (id, weibocontent) in resList:
                    timelist.append(str(weibocontent).decode("utf8"))

                time_dic = SortedDict()
                for i in range((format_endtime - format_begintime).days + 1):
                    day = format_begintime + datetime.timedelta(days=i)
                    datename = str(day)
                    day_list = []
                    week,day = get_week_day(datename.replace('-', ''))
                    for y in timelist:
                        if datename in y:
                            day_list.append(y)
                    if day_list:
                        time_dic[datename] = {1:min(day_list)[11:16],2:max(day_list)[11:16],'name':username,'uid':uid,'userid':userid,'week':week,'day':day}
                    else:
                        time_dic[datename] = {'name':username,'uid':uid,'userid':userid,'week':week,'day':day}
            else:
                log = '起始日期不能大于结束日期'
        else:
            log = '请选择日期'
    return render_to_response('no_attendance/check_work.html',locals(),context_instance=RequestContext(request))