#/usr/bin/python
#-*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import smtplib
from email.Header import Header
from email.mime.text import MIMEText

def send_email(eamil,content):
    reload(sys)
    sys.setdefaultencoding('utf-8')

    sender = 'zeromail@zerotech.com'
    subject = '待办事项提醒'
    smtpserver = 'smtp.zerotech.com'
    username = 'zeromail@zerotech.com'
    password = '123456Aa'

    message = MIMEText(content,'plain','utf-8')
    message['From'] = '考勤系统'
    message['To'] = Header(eamil)
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(sender, eamil, message.as_string())
        smtp.quit()
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"