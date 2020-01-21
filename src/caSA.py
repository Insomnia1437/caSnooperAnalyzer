# -*- coding: utf-8 -*-
# @Time    : 2020-01-17
# @File    : caSA
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@post.kek.jp
import json
import time
import glob
import os
from mymailsender import MyMailSender
import subprocess

"""
define crontab job: run this script every hour
30 * * * * /usr/new/pkg/python/3.7.2_x64/bin/python3 /usr/users/sdcswd/python/caSnooperAnalyzer/src/caSA.py > /usr/users/sdcswd/python/caSnooperAnalyzer/caSA.log 2>1& &
"""
caSnooper_path = "/usr/users/control/bin/caSnooper"
# run n seconds then print report
caSnooper_time = 100
caSnooper_print = 1000
threshold = 1.0
pv_requests = {}
path = "/usr/users/sdcswd/python/caSnooperAnalyzer/data"
error_dir = "/usr/users/sdcswd/python/caSnooperAnalyzer/caSA.log"


def to_error_file(value):
    with open(error_dir, 'a') as ff:
        ff.writelines(["%s\n" % value])


def log_runner(date, hour):
    directory = "%s/%s" % (path, date)
    fname = "%s/%s.log" % (directory, hour)
    if not os.path.exists(directory):
        os.mkdir(directory)
    cmd = "%s -t%s -p%s > %s" % (caSnooper_path, caSnooper_time, caSnooper_print, fname)
    stat = subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, )
    try:
        stat.wait(caSnooper_time + 20)
    except subprocess.TimeoutExpired as e:
        to_error_file(e.__traceback__)


def snooper_log_analyzer(yesterday):
    prefix = "%s/%s" % (path, yesterday)
    fns = glob.glob(prefix + "/*.log", recursive=False)
    for fn in fns:
        if os.path.exists(fn):
            with open(fn, 'r') as fd:
                for line in fd:
                    line = line.strip()
                    if line != "" and line[0].isdigit():
                        seq, host, pv, freq = line.split()
                        if float(freq) >= threshold:
                            pair = "%s %s" % (host, pv)
                            if pair not in pv_requests.keys():
                                pv_requests[pair] = [1, float(freq)]
                            else:
                                pv_requests[pair][0] += 1
                                pv_requests[pair][1] += float(freq)
    if len(pv_requests) != 0:
        js_fn = prefix + "/all.log"
        fd = open(js_fn, 'w')
        json.dump(pv_requests, fd, indent=4)
        result = sorted(pv_requests.items(), key=lambda x: x[1][0], reverse=True)
        return to_str(result[:50])
    return ""


def to_str(pairs):
    rtn = ""
    i = 1
    for pair in pairs:
        rtn += "%d\t%-80s\t\t%s\t\t%s\n" % (i, pair[0], pair[1][0], pair[1][1])
        i += 1
    return [rtn]


def remove_log(date):
    pass


if __name__ == '__main__':
    year, month, day, hour = time.strftime("%Y %m %d %H", time.localtime()).split(" ")
    date = "%s_%s_%s" % (year, month, day)
    log_runner(date, hour)
    context = []
    if hour == "8":
        yesterday = time.strftime("%Y_%m_%d", time.localtime(time.time() - 86400))
        subject = "caSnooperAnalyzer information %s" + yesterday
        requests = snooper_log_analyzer(yesterday)
        if requests == "":
            exit(-1)
        context.append("CaSnooper 2.1.2.3 (7-3-2013)\n")
        context.append("caSnooperAnalyzer by Di WANG (sdcswd@post.kek.jp)\n")
        context.append("data locates at: %s\n\n" % path)
        context.append(
            "this script will run caSnooper once an hour and calculate the pv request times and frequency in one day\n")
        context.append("Noted, max value of 'Counts' is 24\n")
        context.append("%s\t%-80s\t\t%s\t\t%s\n" % ("Num", "Client and PV", "Counts", "frequency"))
        context.append(requests)
        sender = MyMailSender()
        sender.send_by_163(''.join(context), subject)
    if day == "1":
        remove_log(date)
