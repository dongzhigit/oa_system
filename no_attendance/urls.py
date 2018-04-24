# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

# 引入login中试图函数
from no_attendance.views import *


urlpatterns = patterns('',
                        url(r'^leave/$', leave, name='请假说明单'),
                        url(r'^attendance/$', attendance, name='未考勤说明单'),
                        url(r'^todo/(?P<date>.*?)$', todo, name='待办事项'),
                        url(r'^record/$', record, name='考勤请假申请记录'),
                        url(r'^examination/$',examination,name='审核记录'),
                        url(r'^useradd/$', useradd, name='后台用户添加'),
                        url(r'^modify/$', modify, name='后台用户修改'),
                        url(r'^backup/$', work_backup,name='导出'),
                        url(r'^check_work/$', check_work,name='考勤查询'),

                       # url(r'^in/$', inde, name='登录首页1'),
                       # # url(r'^rollback/(?P<version_name>.*)$', rollback, name='版本回滚'),
                       # url(r'^rollback_version_log/$', rollback_version_log, name='回滚版本数据交互'),
                       # url(r'^service_restart/$', service_restart, name='回滚版本数据交互'),
                       # url(r'^file_log/(?P<cactlog>.*?)/(?P<file>.*?)/(?P<url_file_name>.*?)$', file_log, name='文件日志收集'),
                       # url(r'^file_log_content/$', file_log_content, name='文件日志收集'),

                       )
