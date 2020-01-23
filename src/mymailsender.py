# -*- coding: utf-8 -*-
# @Time    : 2020-01-17
# @File    : mymailsender
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp

import smtplib
from email.mime.text import MIMEText


class MyMailSender:
    # receivers should be a list like ['test@mail.com', 'test2@mail.com']
    def __init__(self, mailhost, mailuser, mailpass, sender, receivers):
        self.mail_host = mailhost
        self.mail_user = mailuser
        self.mail_pass = mailpass
        self.sender = sender
        self.receivers = receivers

    def send_mail(self, context='context', subject='subject'):
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
