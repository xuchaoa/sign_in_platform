#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Archerx
# @time: 2018/9/29 上午 10:09

### 该views使用非前后端分离，适用于使用Django自带模板

from django.shortcuts import render
from django.http import JsonResponse,HttpResponseRedirect,HttpResponse,HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from sign_in_app.models import DBSession,day_statistic_people,arp_log,day_statistic_person
import datetime
import time
from sqlalchemy import or_, and_
# Create your views here.


def index(request):
    return HttpResponse('yes')

@login_required(login_url='/admin/login/')
def admin_index_interface(request):
    if request.user.is_superuser:
        return HttpResponse()
    else:
        return HttpResponseForbidden()

@login_required(login_url='/admin/login/')
def user_index_interface(request):
    return HttpResponse()

@login_required(login_url='/admin/login/')
def index_json(request):
    '''
    json返回格式如下：
    count:6
    date:"2018-09-26"
    signed_people:"{'周鑫东', '张俊杰', '孙良宇', '曲鑫浩', '骆立康', '巴永豪'}"
    time:"108"
    '''
    session = DBSession()
    current_username = request.user.username
    if request.user.is_superuser:
        data_dic = []
        date1 = datetime.datetime.now()
        # date = date1.strftime('%Y-%m-%d')
        for i in range(0,7):
            i = -i
            day_date = date1 + datetime.timedelta(days=i)
            date = day_date.strftime('%Y-%m-%d')
            result = session.query(day_statistic_people).filter(day_statistic_people.date == date).first()
            if result:
                i = -i
                dic = {
                    'data'+str(i):{'date':result.date,'time':result.time,'count':result.signed_count,'signed_people':result.signed_people}
                }
                data_dic.append(dic)
        session.close()
        return JsonResponse(data=data_dic,safe=False)
    else:
        data_dic = []
        date1 = datetime.datetime.now()
        for i in range(0, 7):
            i = -i
            day_date = date1 + datetime.timedelta(days=i)
            date = day_date.strftime('%Y-%m-%d')
            result = session.query(day_statistic_person).filter(and_(day_statistic_person.date == date,day_statistic_person.name == current_username)).first()
            if result:
                i = -i
                dic = {
                    'data' + str(i): {'date': result.date,'name':result.name, 'time': result.time, 'online':result.online_count,
                                      'offline_count': result.offline_count}
                }
                data_dic.append(dic)
        session.close()
        return JsonResponse(data=data_dic, safe=False)

@login_required(login_url='/admin/login/')
def admin_log_interface(request):
    if request.user.is_superuser:
        return HttpResponse()
    else:
        return HttpResponseForbidden()

@login_required(login_url='/admin/login/')
def user_log_interface(request):
    return HttpResponse()

@login_required(login_url='/admin/login/')
def log_json(request):
    session = DBSession()
    current_username = request.user.username
    if request.user.is_superuser:
        log_dic = []
        results = session.query(arp_log).order_by(arp_log.id.desc()).limit(10).all()  # 10条倒序
        for result in results:
            dic = {
                'name': result.name,
                'mac': result.mac,
                'ip': result.starttime,
                'stoptime': result.stoptime,
                'downflag': result.downflag,
                'downtime': result.downtime,
                'date': result.date,
                'online':True if len(result.stoptime) == 0 else False
            }
            log_dic.append(dic)
        session.close()
        return JsonResponse(data=log_dic,safe=False)
    else:
        log_dic = []
        results = session.query(arp_log).filter(arp_log.name == current_username).order_by(arp_log.id.desc()).limit(10).all()  # 10条倒序
        for result in results:
            dic = {
                'name': result.name,
                'mac': result.mac,
                'ip': result.starttime,
                'stoptime': result.stoptime,
                'downflag': result.downflag,
                'downtime': result.downtime,
                'date': result.date,
                'online': True if len(result.stoptime) == 0 else False
            }
            log_dic.append(dic)
        session.close()
        return JsonResponse(data=log_dic, safe=False)


@login_required(login_url='/admin/login/')
def admin_daily_interface(request):  #json同index
    if request.user.is_superuser:
        return HttpResponse()
    else:
        return HttpResponseForbidden()

@login_required(login_url='/admin/login/')
def user_admin_interface(request):
    return HttpResponse()



