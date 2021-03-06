# -*- coding: utf-8 -*-
# @Time    : 2020-01-17
# @File    : caSA
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp
import configparser
import json
import re
import time
import glob
import os
import sys
import subprocess
sys.path.append(sys.path[0])
from mymailsender import MyMailSender
from esConnector import ESConnector


class caSA:
    def __init__(self, proj_path, conf_path):
        self.proj_path = proj_path
        self.cfg = configparser.ConfigParser()
        self.cfg.read(conf_path)
        # for casnooper
        self.caSnooper_path = self.cfg.get('casnooper', 'casnooper')
        self.caSnooper_time = int(self.cfg.get('casnooper', 'castime'))
        self.caSnooper_print = int(self.cfg.get('casnooper', 'casprint'))
        self.casthreshold = float(self.cfg.get('casnooper', 'casthreshold'))
        # for mail
        self.mail_host = self.cfg.get('mail', 'smtp')
        self.mail_user = self.cfg.get("mail", 'user')
        self.mail_pass = self.cfg.get("mail", 'pass')
        self.sender = self.cfg.get("mail", 'from')
        self.casanum = int(self.cfg.get("mail", 'casanum'))

        self.es_host = self.cfg.get('elasticsearch', 'host')

        to = self.cfg.get("mail", 'to')
        maillist = re.split(r'[ ]+', to)
        self.receivers = maillist

        self.es = ESConnector(self.es_host)
        self.pv_requests = {}

    def cas_log_runner(self, _date, _hour):
        log_path = os.path.join(self.proj_path, 'log')
        error_log = os.path.join(log_path, 'caSA.log')
        directory = log_path
        for d in _date.split("_"):
            directory = os.path.join(directory, d)
            if not os.path.exists(directory):
                os.makedirs(directory)

        f_name = os.path.join(directory, "%s.log" % _hour)
        cmd = "%s -t%s -p%s > %s" % (self.caSnooper_path, self.caSnooper_time, self.caSnooper_print, f_name)
        stat = subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, )
        try:
            stat.wait(self.caSnooper_time + 20)
        except subprocess.TimeoutExpired as e:
            self.to_error_file(error_log, e)

    @staticmethod
    def to_error_file(error_dir, value):
        with open(error_dir, 'a') as ff:
            ff.writelines(["%s\n" % value])

    @staticmethod
    def to_str(pairs):
        rtn = ""
        i = 1
        for pair in pairs:
            rtn += "%d\t%-80s\t\t%d\t\t%.3f\n" % (i, pair[0], pair[1][0], pair[1][1] / pair[1][0])
            i += 1
        return rtn

    def snooper_log_analyzer(self, _yesterday):
        log_path = os.path.join(self.proj_path, 'log')
        for d in _yesterday.split("-"):
            log_path = os.path.join(log_path, d)
        prefix = log_path
        fns = glob.glob(prefix + "/*.log", recursive=False)
        for fn in fns:
            if os.path.exists(fn):
                with open(fn, 'r') as fd:
                    for line in fd:
                        line = line.strip()
                        if line != "" and line[0].isdigit():
                            seq, host, *pv, freq = re.split(r'[ ]+', line)
                            if float(freq) > self.casthreshold:
                                pair = "%s %s" % (host, ' '.join(pv))
                                if pair not in self.pv_requests.keys():
                                    self.pv_requests[pair] = [1, float(freq)]
                                else:
                                    self.pv_requests[pair][0] += 1
                                    self.pv_requests[pair][1] += float(freq)
        if len(self.pv_requests) != 0:
            js_fn = os.path.join(log_path, "caSA.json")
            fd = open(js_fn, 'w')
            json.dump(self.pv_requests, fd, indent=4)
            result = sorted(self.pv_requests.items(), key=lambda x: x[1][1], reverse=True)
            result = sorted(result, key=lambda x: x[1][0], reverse=True)
            return self.to_str(result[:self.casanum])
        return ""

    def es_log_analyzer(self, _yesterday):
        log_path = os.path.join(self.proj_path, 'log')
        directory = log_path
        for d in _yesterday.split("-"):
            directory = os.path.join(directory, d)
            if not os.path.exists(directory):
                os.makedirs(directory)
        for d in _yesterday.split("-"):
            log_path = os.path.join(log_path, d)
        index_name = "linac-casnooper-"+_yesterday.replace('-', '.')
        response = self.es.index_search(index_name)
        print("total doc: %s" % len(response))
        for doc in response:
            freq = doc['_source']['Hz']
            host = doc['_source']['host']
            pv = doc['_source']['pv']
            pair = "%s %s" % (host, pv)
            if pair not in self.pv_requests.keys():
                self.pv_requests[pair] = [1, float(freq)]
            else:
                self.pv_requests[pair][0] += 1
                self.pv_requests[pair][1] += float(freq)
        if len(self.pv_requests) != 0:
            js_fn = os.path.join(log_path, "caSA.json")
            fd = open(js_fn, 'w')
            json.dump(self.pv_requests, fd, indent=4)
            result = sorted(self.pv_requests.items(), key=lambda x: x[1][1], reverse=True)
            result = sorted(result, key=lambda x: x[1][0], reverse=True)
            return self.to_str(result[:self.casanum])
        return ""


if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.getcwd()))
    config_path = os.path.join(path, "config/config.ini")
    if not os.path.exists(config_path):
        print("config file not exist")
        exit(-1)
    else:
        year, month, day, hour = time.strftime("%Y %m %d %H", time.localtime()).split(" ")
        date = "%s_%s_%s" % (year, month, day)
        sa = caSA(path, config_path)
        yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        subject = "caSnooperAnalyzer information on %s" % (yesterday)
        context = []
        if len(sa.es_host) > 0:
            requests = sa.es_log_analyzer(yesterday)
            if requests == "":
                print("Error while get data from ES")
                exit(-1)
            context.append("CaSnooper 2.1.2.3 (7-3-2013)\n")
            context.append("caSnooperAnalyzer by Di WANG (sdcswd@post.kek.jp)\n\n")
            context.append("Source Code is hosted at GitHub: https://github.com/Insomnia1437/caSnooperAnalyzer\n")
            context.append("Data is retrieved from ElasticSearch database at %s\n" % sa.es_host)
            # context.append("data locates at: %s\n\n" % path)
            context.append("CaSnooper will run every 10 minutes (144 times per day), this Analyzer will run every day ")
            context.append("and calculate the pv request times and frequency in one day\n")
            context.append("Note, max value of 'Counts' is 144, which means this request happens every 10 minutes.\n\n")
            context.append("%s\t%-80s\t\t%s\t\t%s\n" % ("Num", "Client and PV", "Counts", "Frequency (Mean)"))
            context.append(requests)
            sender = MyMailSender(sa.mail_host, sa.mail_user, sa.mail_pass, sa.sender, sa.receivers)
            sender.send_mail(''.join(context), subject)
        else:
            sa.cas_log_runner(date, hour)
            if hour == "08":
                requests = sa.snooper_log_analyzer(yesterday)
                if requests == "":
                    exit(-1)
                context.append("CaSnooper 2.1.2.3 (7-3-2013)\n")
                context.append("caSnooperAnalyzer by Di WANG (sdcswd@post.kek.jp)\n")
                context.append("cmd is: %s -t%s -p%s\n" % (sa.caSnooper_path, sa.caSnooper_time, sa.caSnooper_print))
                context.append("data locates at: %s\n\n" % path)
                context.append("this script will run caSnooper every hour ")
                context.append("and calculate the pv request times and frequency in one day\n")
                context.append("Note, max value of 'Counts' is 24, which means this request happens every hour.\n\n")
                context.append("%s\t%-80s\t\t%s\t\t%s\n" % ("Num", "Client and PV", "Counts", "Frequency (Mean)"))
                context.append(requests)
                sender = MyMailSender(sa.mail_host, sa.mail_user, sa.mail_pass, sa.sender, sa.receivers)
                sender.send_mail(''.join(context), subject)
