from django.db import models
from sqlalchemy import Column,create_engine,Integer,String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import OrderedDict
import time

# Create your models here.

Base = declarative_base()

engine = create_engine('mysql+pymysql://signin:signinsec@10.6.65.106:3306/signin',encoding='utf-8',echo=False)

class arp_log(Base):

    __tablename__ = 'arp_log'
    id = Column(Integer,primary_key=True)
    name = Column(String(50))
    mac = Column(String(50))
    ip = Column(String(50))
    starttime = Column(String(50),default=None)
    stoptime = Column(String(50),default=None)
    downflag = Column(Integer,nullable=True,default=0)
    downtime = Column(String(50),default=None)
    date = Column(String(50),default=None)

class user_info(Base):
    __tablename__ = 'user_info'
    id = Column(Integer,primary_key=True)
    name = Column(String(50))
    schoolnum = Column(String(50))
    classname = Column(String(50))
    mac = Column(String(50))
    wirelessmac = Column(String(50))
    ip1 = Column(String(50))
    ip2 = Column(String(50))
    ip3 = Column(String(50))
    ip4 = Column(String(50))
    current_mac = Column(String(50))
    current_ip = Column(String(50))

class day_statistic_people(Base):
    __tablename__ = 'day_statistic_people'
    id = Column(Integer,primary_key=True)
    date = Column(String(50))
    time = Column(String(50))
    signed_count = Column(Integer,default=0)
    signed_people = Column(String(200))


class day_statistic_person(Base):
    __tablename__ = 'day_statistic_person'
    id = Column(Integer,primary_key=True)
    date = Column(String(50))
    name = Column(String(50))
    time = Column(String(50))
    online_count = Column(Integer,default=0)
    offline_count = Column(Integer,default=0)



Base.metadata.create_all(engine)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
session = DBSession()












