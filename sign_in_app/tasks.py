#! /usr/bin/env python34
# -*- coding: utf-8 -*-
# Author: Archerx
# @time: 2018/9/24 下午 07:55

import time
import celery
from celery.schedules import crontab
from celery.task import periodic_task
from scapy.all import Ether,ARP,srp,arping,conf
from sign_in_app.models import user_info,DBSession,arp_log,day_statistic_person,day_statistic_people  #直接引用类名
from sqlalchemy import or_, and_
from sign_in_app.APIC_Client import APIC
import datetime



@periodic_task(run_every=crontab(minute='*/5',hour='6-22'),name='schedules.sign_in_app')#每天6-23时之间探测
def mac_scan():
    session = DBSession()
    try:
        ipscan = '10.6.65.0/24'
        arp_list = []
        try:
            ans, unans = srp(Ether(dst="FF:FF:FF:FF:FF:FF") / ARP(pdst=ipscan), timeout=10, verbose=False)
        except Exception as e:
            print (str(e))
        else:
            for snd, rcv in ans:
                mac = rcv.sprintf("%Ether.src%")
                ip = rcv.sprintf("%ARP.psrc%")
                arp_dic = {
                    'arp_mac':mac,
                    'arp_ip':ip
                }
                arp_list.append(arp_dic)

        # print('arp mac')
        # for i in arp_list:
        #     print(i.get('arp_mac'),i.get('arp_ip'))

        user_list = []  #当前在线的用户的数据库操作对象  user_info
        for i in arp_list:
            try:
                # tem = session.query(user_info).filter(and_(or_(user_info.mac == '00:0c:29:5c:30:c3',user_info.wirelessmac == i.get('arp_mac', None)),
                #                                 or_(user_info.ip1 == '10.6.65.5',user_info.ip2 == i.get('arp_ip', None)))).first()
                # print(i.get('arp_mac'),i.get('arp_ip'))
                tem = session.query(user_info).filter(or_(user_info.mac == i.get('arp_mac'),user_info.wirelessmac == i.get('arp_mac',None))).first()

                if tem :     #如果数据库中存在该用户
                    # print("refresh mac/ip")
                    user_list.append(tem)
                    tem.current_ip = i.get('arp_ip', None)
                    tem.current_mac = i.get('arp_mac', None)
                    # print(tem.current_mac)
                    # print(i.get('arp_mac', None))
                    session.commit()
            except BaseException as e:
                print(e)


        # [print(_.name) for _ in user_list]
        # print('online users\'s mac')
        # for i in user_list:
        #     print(i.current_mac)

        for res in user_list:
            # print('当前操作的用户名：',res.name,res.mac)
            sql_result = session.query(arp_log).filter(and_(arp_log.mac == res.current_mac,arp_log.stoptime == None)).first()
            # print(sql_result)  #未查到返回为None
            if sql_result is None: #不存在在线用户
                # print('new log')
                new_log = arp_log(name = res.name,mac = res.current_mac,ip=res.current_ip,
                                  starttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),date=time.strftime("%Y-%m-%d", time.localtime(time.time())))
                session.add(new_log)
                session.commit()

            else: #存在在线用户记录
                # print('down flag be zero')
                session.query(arp_log).filter(arp_log.mac == res.current_mac).update({'downflag': 0})
                # session.commit()

        sql_online_result = session.query(arp_log).filter(arp_log.stoptime == None).all()

        for res in sql_online_result:
            # print(res.name)
            flag = 0
            for a in user_list:
                if res.mac == a.current_mac:
                    flag = 1
                    break
            if flag == 0:  #本次掉线
                # print('offline count',res.downflag)
                if res.downflag >= 2:#掉线次数超过五次
                    # print("offline 5 times")
                    res.stoptime = res.downtime
                    session.commit()
                elif res.downflag == 0:
                    # print('first offline')
                    res.downflag += 1
                    res.downtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    session.commit()
                else:
                    # print("offline+1")
                    # result = session.query(arp_log).filter(arp_log.rurrent_mac == res.mac).first()
                    res.downflag = res.downflag + 1
                    session.commit()

            else:
                pass
        session.close()
        print(APIC().send())
    except:
        pass



@periodic_task(run_every=crontab(minute=5,hour=23),name='schedules.all_offline')
def all_offline():
    session = DBSession()
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    current_time = today+' 22:50:00'
    results = session.query(arp_log).filter(and_(arp_log.date == today,arp_log.stoptime == None)).all()
    for result in results:
        result.stoptime = current_time
    session.commit()
    session.close()



@periodic_task(run_every=crontab(minute=10,hour=23),name='schedules.statistic_everyday')
def statistic_everyday():  ##输出格式  0:38:00  小时:分钟:秒  写入数据库（小时，签到人数）
    session = DBSession()
    today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    alltime = datetime.timedelta()
    time_results = session.query(arp_log).filter(arp_log.date == today).all()
    signed_user = set()
    for res in time_results:
        start_time = datetime.datetime.strptime(res.starttime, '%Y-%m-%d %H:%M:%S')
        stop_time = datetime.datetime.strptime(res.stoptime, '%Y-%m-%d %H:%M:%S')
        time_interval = (stop_time - start_time)
        alltime += time_interval
        signed_user.add(res.name)  #签到姓名
    signed_user_count = len(signed_user)  #签到人数
    signed_user_str = str(signed_user)
    day_log = day_statistic_people(date=today,time=alltime,signed_count=signed_user_count,signed_people=signed_user_str)
    session.add(day_log)
    session.commit()
    session.close()



@periodic_task(run_every=crontab(minute=20,hour=23),name='schedules.statistic_everyday_person')
def statistic_person_everyday():
    session = DBSession()
    day_date = datetime.datetime.now()
    date = day_date.strftime('%Y-%m-%d')
    usernames = session.query(user_info).all()
    for name in usernames:
        results = session.query(arp_log).filter(and_(arp_log.name == name.name,arp_log.date == date)).all()
        alltime = datetime.timedelta()
        for result in results:
            start_time = datetime.datetime.strptime(result.starttime, '%Y-%m-%d %H:%M:%S')
            stop_time = datetime.datetime.strptime(result.stoptime, '%Y-%m-%d %H:%M:%S')
            time_interval = (stop_time - start_time)
            alltime += time_interval
            print(alltime)
        new_log = day_statistic_person(date=date,name=name.name,time=alltime,online_count=len(results),offline_count=len(results))
        session.add(new_log)
        session.commit()
    session.close()






broker = 'redis://127.0.0.1:6379/2'   #消息中间件
app = celery.Celery('tasks', broker=broker)
app.conf.update(
    CELERY_RESULT_BACKEND='redis://127.0.0.1:6379/3'
)

#
# if __name__ == '__main__':
#     # mac_scan()
#     #get_all_userinfo()
#     # add()
#     statistic_everyday()

