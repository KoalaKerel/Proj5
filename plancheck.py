# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 11:47:12 2022

@author: danny @tool
"""

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as pld
import streamlit as sl

omloop = sl.session_state['datainput']
x = sl.session_state['dienstdata2']
planning = x.parse('Dienstregeling')
afstand = x.parse('Afstand matrix')

file = omloop
cols = omloop.columns

for i in range(len(afstand)):
    if afstand['buslijn'][i]==afstand['buslijn'][i]:
        globals()['%s_%s'%(afstand['startlocatie'][i],int(afstand['buslijn'][i]))]={}
for i in range(len(planning)):
    globals()['%s_%s'%(planning['startlocatie'][i],planning['buslijn'][i])][planning['vertrektijd'][i]]=[]

class bus:
    def __init__(self,name):
        self.soh = sl.session_state['soc']/100
        self.name = name
        self.capacity = 350
        self.SOH = self.capacity*self.soh #State of Health
        self.SOC = self.SOH #State of Charge
        self.current_location = "ehvgar"
        self.verbruik = sl.session_state['stroomverbruik']
        self.log = []
        self.time = None
        self.error = {}
    
    def __str__(self):
        return 'bus_{}'.format(self.name)
    
    def rit(self,startloc,destination,buslijn,activiteit,start,eind):#start,eind aanpassen
        dist = 0
        t1 = datetime.strptime(start,'%H:%M:%S')
        if not self.current_location == startloc:
            try:
                self.error['The bus is not on location it is planned to depart from'].append(t1.strftime("%H:%M:%S"))
            except:
                self.error['The bus is not on location it is planned to depart from']=[t1.strftime("%H:%M:%S")]
        
        if self.time==None:
            self.time = t1
        
        if not t1>=self.time:   
            if t1 < self.log[0][3]:
                try:
                    self.error["The bus has been idle, which was not included in the planning"].append(t1.strftime("%H:%M:%S"))
                except:
                    self.error["The bus has been idle, which was not included in the planning"]=[t1.strftime("%H:%M:%S")]
            else:
                try: 
                    self.error["The bus is scheduled to depart at a time that it is allready in route"].append(t1.strftime("%H:%M:%S"))
                except:
                        self.error["The bus is scheduled to depart at a time that it is allready in route"]=[t1.strftime("%H:%M:%S")]

        if (t1-self.time).total_seconds() > 60:
            try:
                self.error["The bus has been idle, which was not included in the planning"].append(t1.strftime("%H:%M:%S"))
            except:
                self.error["The bus has been idle, which was not included in the planning"]=[t1.strftime("%H:%M:%S")]

        t2 = datetime.strptime(eind,'%H:%M:%S')
        if buslijn != str():
            try:
                globals()['%s_%s'%(startloc,int(buslijn))][start[:5]].append(self.name)
            except:
                try:
                    self.error['Bus planned not according to schedule'].append(t1.strftime("%H:%M:%S"))
                except:
                    self.error['Bus planned not according to schedule']=[t1.strftime("%H:%M:%S")]
        self.time = t2
        if buslijn != str():
            begin = 4
        else:
            begin = 0
        for i in range(begin,len(afstand['startlocatie'])):
            if afstand['startlocatie'][i]==self.current_location and afstand['eindlocatie'][i]==destination:
                dist = afstand['afstand in meters'][i]
                break
        self.SOC -= self.verbruik *dist 
        self.log.append((self.current_location,destination,activiteit,t1,t2,self.SOC))
        self.current_location = destination
        #self time moet iets aan gedaan worden

    def opladen(self,start,eind):
        t1 = datetime.strptime(start,'%H:%M:%S')
        t2 = datetime.strptime(eind,'%H:%M:%S')
        a=(t2-t1).total_seconds()/3600
        if 0.9*self.SOH-self.SOC >= a*250:
            self.SOC+=a*250
        else:
            b=(0.9*self.SOH-self.SOC)/250
            self.SOC += 250*b+60*(a-b)
        if self.SOC>self.SOH:
            self.SOC = self.SOH
        self.time = datetime.strptime(eind,'%H:%M:%S')
        self.log.append((self.current_location,'ehvgar','opladen',t1,t2,self.SOC))
    def plot(self):
        y=[]
        x=[]
        for i in self.log:
            y.append(i[5])
            x.append(i[4])
        formatter = pld.DateFormatter('%H:%M')
        dates = pld.date2num(x)
        figure = plt.figure()
        axes = figure.add_subplot(1,1,1)
        axes.xaxis.set_major_formatter(formatter)
        axes.xaxis.set_major_locator(pld.HourLocator(interval=2))
        axes.plot(dates,y,'.')
        plt.title('State of charge of bus %s over time'%self.name)
        plt.ylabel('State of charge(kWh)')
        plt.xlabel('Time')
        plt.gcf().autofmt_xdate()
        return figure

if not (file.columns == cols).all():#check format van gegeven omloopplanning
    print("ERROR, niet juiste format")
buzin =sorted([j for j in set(i for i in file['omloop nummer'])])#oplopende lijst met busnummers
bussen = [0] #initialisser met 1 element, zodat omloopnummer overeenkomt met index in de list
for i in buzin:
    globals()['bus_%s'%i]=bus(i)
    bussen.append(globals()['bus_%s'%i])#lijst met bus objecten
for i in range(len(file)):
    if file['activiteit'][i]=='opladen':
        bussen[file['omloop nummer'][i]].opladen(file['starttijd'][i],file['eindtijd'][i])
    elif file['activiteit'][i]=='idle':
        bussen[file['omloop nummer'][i]].time = datetime.strptime(file['eindtijd'][i],'%H:%M:%S')
    else:
        bussen[file['omloop nummer'][i]].rit(file['startlocatie'][i],file['eindlocatie'][i],file['buslijn'][i],file['activiteit'][i],file['starttijd'][i],file['eindtijd'][i])
    if bussen[file['omloop nummer'][i]].SOC <0.1*bussen[file['omloop nummer'][i]].SOH:
        try:
            bussen[file['omloop nummer'][i]].error['The battery of the bus is below 10%'].append(bussen[file['omloop nummer'][i]].time.strftime("%H:%M:%S"))
        except:
            bussen[file['omloop nummer'][i]].error['The battery of the bus is below 10%']=[bussen[file['omloop nummer'][i]].time.strftime("%H:%M:%S")]

def assign():
    for i in range(len(afstand)):
        if afstand['buslijn'][i]==afstand['buslijn'][i]:
            for key in globals()['%s_%s'%(afstand['startlocatie'][i],int(afstand['buslijn'][i]))].keys():
                if len(globals()['%s_%s'%(afstand['startlocatie'][i],int(afstand['buslijn'][i]))][key])!=1:
                    print('Error, not all or to many busses assigned')

def update():
    for i in bussen[1:]:
        i.soh = sl.session_state['soc']
        i.capacity = 350
        i.SOH = i.capacity*i.soh #State of Health
        i.SOC = i.SOH #State of Charge
        i.current_location = "ehvgar"
        i.verbruik = sl.session_state['stroomverbruik']
        i.log = []
        i.time = None
        i.error = {}
    for i in range(len(file)):
        if file['activiteit'][i]=='opladen':
            bussen[file['omloop nummer'][i]].opladen(file['starttijd'][i],file['eindtijd'][i])
        elif file['activiteit'][i]=='idle':
            bussen[file['omloop nummer'][i]].time = datetime.strptime(file['eindtijd'][i],'%H:%M:%S')
        else:
            bussen[file['omloop nummer'][i]].rit(file['startlocatie'][i],file['eindlocatie'][i],file['buslijn'][i],file['activiteit'][i],file['starttijd'][i],file['eindtijd'][i])
        if bussen[file['omloop nummer'][i]].SOC <0.1*bussen[file['omloop nummer'][i]].SOH:
            try:
                bussen[file['omloop nummer'][i]].error['The battery of the bus is below 10%'].append(bussen[file['omloop nummer'][i]].time.strftime("%H:%M:%S"))
            except:
                bussen[file['omloop nummer'][i]].error['The battery of the bus is below 10%']=[bussen[file['omloop nummer'][i]].time.strftime("%H:%M:%S")]


def errors():
    lst = []
    for i in bussen[1:]:
        if bool(i.error):
            lst.append(i)
    return lst