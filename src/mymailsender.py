# -*- coding: utf-8 -*-
# @Time    : 2020-01-17
# @File    : mymailsender
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp

import smtplib
from email.mime.text import MIMEText
import configparser


class MyMailSender:
    def __init__(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read("../config/robotmail.ini")
        self.mail_host = self.cfg.get('163', 'host')
        self.mail_user = self.cfg.get("163", 'user')
        self.mail_pass = self.cfg.get("163", 'pass')
        self.sender = self.cfg.get("163", 'sender')
        self.receivers = [self.cfg.get("163", 'receivers')]

    def add_receivers(self, receivers):
        if type(receivers) is list:
            if self.receivers[0] in receivers:
                self.receivers = receivers
            else:
                self.receivers.extend(receivers)
        if type(receivers) is str:
            self.receivers.append(receivers)

    def send_by_163(self, context='context', subject='subject'):
        if len(context) is 0:
            print("mail send Error: no content")
            return -1
        message = MIMEText(context, 'plain', 'utf-8')
        # subject
        message['Subject'] = subject
        message['From'] = self.sender
        message['To'] = ",".join(self.receivers)
        try:
            smtp_obj = smtplib.SMTP()
            smtp_obj.connect(self.mail_host, 25)
            smtp_obj.login(self.mail_user, self.mail_pass)
            smtp_obj.sendmail(
                self.sender, self.receivers, message.as_string())
            smtp_obj.quit()
            print('mail send success')
        except smtplib.SMTPException as e:
            print('error', e)
