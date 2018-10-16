# code is far away from bugs with the god animal protecting
"""
I love animals. They taste delicious.
┏┓ ┏┓
┏┛┻━━━┛┻┓
┃ ☃ ┃
┃ ┳┛ ┗┳ ┃
┃ ┻ ┃
┗━┓ ┏━┛
┃ ┗━━━┓
┃ 神兽保佑 ┣┓
┃　永无BUG！ ┏┛
┗┓┓┏━┳┓┏┛
┃┫┫ ┃┫┫
┗┻┛ ┗┻┛
"""


from django.shortcuts import render
from django.http import JsonResponse,HttpResponseRedirect,HttpResponse,HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from sign_in_app.models import DBSession,day_statistic_people,arp_log,day_statistic_person
import datetime
from django.contrib.auth.models import User
import time
from django.contrib.auth import login as dj_login,logout as dj_logout
from django.contrib.auth import authenticate
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from sqlalchemy import or_, and_
# Create your views here.



def session_required(function):  #判断是否登陆
    def check_session(request,*args,**kwargs):
        # sessionid = request.session.get('sessionid')
        # sessionid = request.COOKIES.get('sessionid')
        try:
            session = request.session['_auth_user_id']
            print(session)
        except:
            return JsonResponse({'msg':'not found sessionid','code':201})
        if not session:
            return JsonResponse({'msg':'no sessionid','code':201})  #需要跳转登录
        else:
            user = User.objects.filter(id=session).first()
            if not user:
                return JsonResponse({'msg':'this user is not in database','code':202})  #用户可能在尝试伪造sessionid，或者session过期，跳转登陆
            else:
                username = user.username
                try:
                    stime = request.POST['stime']
                    etime = request.POST['etime']
                except:
                    return function(request, username=username)
                return function(request, username=username, stime=stime, etime=etime)
    return check_session


def login(request,*args):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        return JsonResponse({'msg':'username or password is empty','code':203},safe=False)
    user = authenticate(username=username, password=password)
    if user is not None:
        dj_login(request, user)
        # print(request.session['_auth_user_hash'])
        # print(request.session['_auth_user_id'])
        # print(request.session['_auth_user_backend'])
        '''
        默认request.session字典key&value
        _auth_user_hash b34a1c470b968f12ac0a1b37bf71955c06114741
        _auth_user_id 4  
        _auth_user_backend django.contrib.auth.backends.ModelBackend
        '''
        user = User.objects.filter(id=request.session['_auth_user_id']).first()
        if user.username == 'admin':
            pass
        return JsonResponse({'msg':'login success','code':20,'username':user.username},safe=False)
    else:
        return JsonResponse({'msg':'no this user in database','code':202})


@session_required
def logout(request,*args,**kwargs):
    print(kwargs['username'])
    try:
        del request.session['_auth_user_id']
    except KeyError:
        return JsonResponse({'msg':'logout error','code':204})
    return JsonResponse({'msg':"you have logged out",'code':20},safe=False)


@session_required
def index(request,username): #test
    print('接受到的name: ',username)
    return HttpResponse('yes')


@session_required
def index_json(request,*args,**kwargs):
    '''
    json返回格式如下：
    count:6
    date:"2018-09-26"
    signed_people:"{'周鑫东', '张俊杰', '孙良宇', '曲鑫浩', '骆立康', '巴永豪'}"
    time:"108"

    '''
    session = DBSession()

    current_username = kwargs['username']
    if current_username == 'admin':
        data_dic = []
        date1 = datetime.datetime.now()
        # date = date1.strftime('%Y-%m-%d')
        for i in range(0,7):
            i = (-i) - 1
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
            i = (-i) - 1
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


@session_required
def log_json(request,*args,**kwargs):
    session = DBSession()
    current_username = kwargs['username']
    stime = ''
    etime = ''
    try:
        stime = kwargs['stime']
        etime = kwargs['etime']
    except:
        pass
    if current_username == 'admin':
        log_dic = []
        if (len(stime) != 0 and len(etime) != 0):
            results = session.query(arp_log).filter(arp_log.date.between(stime,etime)).order_by(arp_log.id.desc()).all()  # 倒序
        else:
            results = session.query(arp_log).order_by(arp_log.id.desc()).limit(20).all()  # 倒序
        for result in results:
            dic = {
                'name': result.name,
                'mac': result.mac,
                'ip': result.ip,
                'starttime': result.starttime,
                'stoptime': result.stoptime,
                'downflag': result.downflag,
                'downtime': result.downtime,
                'date': result.date,
                'online':True if result.stoptime is None or len(result.stoptime) == 0 else False
            }
            log_dic.append(dic)
        session.close()
        return JsonResponse(data=log_dic,safe=False)
    else:
        log_dic = []
        if (len(stime) != 0 and len(etime) != 0):
            results = session.query(arp_log).filter(and_(arp_log.name == current_username,arp_log.date.between(stime,etime))).all()
        else:
            results = session.query(arp_log).filter(arp_log.name == current_username).order_by(arp_log.id.desc()).limit(20).all()  # 10条倒序
        for result in results:
            dic = {
                'name': result.name,
                'mac': result.mac,
                'ip': result.ip,
                'starttime': result.starttime,
                'stoptime': result.stoptime,
                'downflag': result.downflag,
                'downtime': result.downtime,
                'date': result.date,
                'online': True if len(result.stoptime) == 0 else False
            }
            log_dic.append(dic)
        session.close()
        return JsonResponse(data=log_dic, safe=False)

@session_required
def day_log_json(request,*args,**kwargs):
    session = DBSession()
    current_username = kwargs['username']
    data_dic = []
    date1 = datetime.datetime.now()
    stime = ''
    etime = ''
    try:
        stime = kwargs['stime']
        etime = kwargs['etime']
    except:
        pass

    if current_username == 'admin':
        if(len(stime) != 0 and len(etime) != 0):
            results = session.query(day_statistic_person).filter(day_statistic_person.date.between(stime,etime)).all()
            for result in results:
                dic = {
                    'name': result.name,
                    'date': result.date,
                    'time': result.time,
                    'online_count': result.online_count,
                    'offline_count': result.offline_count,
                }
                data_dic.append(dic)
            session.close()
            return JsonResponse(data=data_dic, safe=False)
        else:
            for i in range(0, 2):  #默认返回近2天 5kB左右
                i = (-i) - 1
                day_date = date1 + datetime.timedelta(days=i)
                date = day_date.strftime('%Y-%m-%d')
                results = session.query(day_statistic_person).filter(day_statistic_person.date == date).order_by(day_statistic_person.id.desc()).all()  #倒叙返回
                for result in results:
                    i = -i
                    dic = {
                         'name':result.name,
                         'date': result.date,
                         'time': result.time,
                         'online_count': result.online_count,
                         'offline_count': result.offline_count,
                        }
                    data_dic.append(dic)
            session.close()
            return JsonResponse(data=data_dic, safe=False)
    else:
        if (len(stime) != 0 and len(etime) != 0):
            results = session.query(day_statistic_person).filter(and_(day_statistic_person.date.between(stime, etime),day_statistic_person.name == current_username)).all()
            for result in results:
                dic = {
                    'name': result.name,
                    'date': result.date,
                    'time': result.time,
                    'online_count': result.online_count,
                    'offline_count': result.offline_count,
                }
                data_dic.append(dic)
            session.close()
            return JsonResponse(data=data_dic, safe=False)
        else:
            for i in range(0, 20):  # 默认返回近20天
                i = (-i) - 1
                day_date = date1 + datetime.timedelta(days=i)
                date = day_date.strftime('%Y-%m-%d')
                results = session.query(day_statistic_person).filter(and_(day_statistic_person.date == date,day_statistic_person.name == current_username)).order_by(
                    day_statistic_person.id.desc()).all()  # 倒叙返回
                for result in results:
                    i = -i
                    dic = {
                        'name': result.name,
                        'date': result.date,
                        'time': result.time,
                        'online_count': result.online_count,
                        'offline_count': result.offline_count,
                    }
                    data_dic.append(dic)
            session.close()
            return JsonResponse(data=data_dic, safe=False)














