#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  4 11:42:46 2018

@author: Yuchong
"""
from bs4 import BeautifulSoup
import requests
import gc
import datetime

point_value={}
source=requests.get('https://thepointsguy.com/guide/monthly-valuations/').text
soup=BeautifulSoup(source,'lxml')
value_table=soup.find('section',class_='table').tbody
for value_program in value_table.find_all('tr'):
    a=[]
    for i in value_program.find_all('td'):
        a.append(i.text)
    try:
        point_value[a[0]]=float(a[3])
    except ValueError:
        pass

date_format = "%m/%d/%Y"


class account:
    email='YOUR_EMAIL'
    phone='YOUR_PHONE'
    username='YOUR_USERNAME'

    def __init__(self,program,account_number,balance,expiration_date):
        self.program=program
        self.account_number=account_number
        self.balance=balance
        self.value_per_point=point_value[program]
        if expiration_date=='':
            self.expiration_date='never'
        else:
            self.expiration_date=expiration_date
        
    def total_value(self):
        return self.balance*self.value_per_point*0.01
    
    def points_change(self,change_amount):
        self.balance=self.balance+change_amount
        
    def expiration_in(self):
        if self.expiration_date=='never':
            return 'never'
        else:
            a = datetime.datetime.strptime(self.expiration_date, date_format)
            b = datetime.datetime.now()
            return (a-b).days

    def expiration_soon(self):
        if self.expiration_date!='never' and self.expiration_in()<=720:
            print ("Attention! {} expires in {} days".format(self.program,self.expiration_in()))

    

class hotel(account):
    pass

class airline(account):
    pass

class bank(account):
    pass

#example
UA=airline('United MileagePlus','SH489204',8000,'')
AA=airline('American AAdvantage','4G33HK0',10000,'9/1/2021')
print(AA.expiration_date)
print(UA.expiration_in())


sum_total_value=0
for obj in gc.get_objects():
    if isinstance(obj, account):
        sum_total_value=sum_total_value+obj.total_value()
        obj.expiration_soon()
        
print(f'Your total points/miles are worth ${sum_total_value}')
#print(Chase.expiration_in())
