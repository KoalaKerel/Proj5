# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 19:31:54 2022

@author: damon
"""

import pandas as pd
import numpy as np 
import streamlit as sl
import matplotlib.pyplot as plt
import datetime 
from PIL import Image

sl.set_page_config(page_title="Information", page_icon="📈")
if sl.session_state['noinput'] == True:
    sl.markdown("No schedule has been uploaded. Please return to the frontpage and upload a schedule.")
    noinputimg = Image.open('Geeninput.png')
    sl.image(noinputimg)
    
if sl.session_state['mismatch'] == True and sl.session_state['noinput']==False:
    sl.markdown("The uploaded schedule is not formatted correctly or does not match the uploaded data. Please check if both are correct.")
    badinputimg = Image.open('Fouteinput.png')
    sl.image(badinputimg)
    
if sl.session_state['mismatch'] == False and sl.session_state['noinput']==False and sl.session_state['wrongdata']==True:
    sl.markdown("The uploaded shedule does not match the current data. Please check if both are correct.")
    sl.image(Image.open('Fouteinput.png'))
    
    
if sl.session_state['mismatch'] == False and sl.session_state['noinput'] == False and sl.session_state['wrongdata']==False:

    #basedata = {'activiteit':['ehvaptehvbst400', 'ehvbstehvapt400', 'ehvaptehvbst401', 'ehvbstehvapt401', 'ehvbstehvaptm', 'ehvaptehvbstm', 'ehvbstehvgarm', 'ehvgarehvbstm', 'ehvaptehvgarm', 'ehvgarehvaptm', 'charge', 'idle'],
    #            'mint':[22, 22, 22, 22, 20, 20, 4, 4, 20, 20, 0, 0],
    #            'maxt':[24, 24, 25, 24, 20, 20, 4, 4, 20, 20, 0, 0],
    #            'afstand':[10250, 10708, 9050, 9003, 8600, 8600, 1650, 1650, 9000, 9000, 0, 0]
    #            }
    #idata = pd.DataFrame(data=basedata)
    idata = sl.session_state['dienstdata']
    data = sl.session_state['datainput']
    #sl.dataframe(idata)
    
    totdist = 0
    for ind in range(len(data)):
        totdist = totdist + idata.loc[idata['activiteit']==data.type[ind], 'afstand in meters'].iloc[0]
    toturen = sum(data.tte)
    totdienst = sum(data.tte[data.activiteit=="dienst rit"])
    totdd = toturen/totdienst#alle uren gedeeld door diensturen    
    totusage = totdist * 1.5
    totidle = sum(data.tte[data.activiteit=="idle"]) #Totale idletijd
    totcharge = sum(data.tte[data.type=="charge"])
    inp = {'Statistic': ['DD', 'Totale distance (m)', 'Total time of activity', 'Total time with passengers', 'Total time spent idling', 'Total time spent charging'], 'Value':[totdd, int(totdist), datetime.timedelta(minutes=toturen), datetime.timedelta(minutes=totdienst), datetime.timedelta(minutes=totidle), datetime.timedelta(minutes=totcharge)]}
    totdf = pd.DataFrame(data=inp)  
    sl.header("Totals of all busses:")
    sl.dataframe(totdf)  
        
    bussen = max(data['omloop nummer'])
    businfo = []
    timespan = max(data['end_time']) - min(data['start_time'])
    
    dists = []
    uren = []
    diensts = []
    idles = []
    charges =[]
    percs = []
    dds = []
    
    for i in range(bussen+1)[1:]:
        tempdata = data[data['omloop nummer']==i]
        
        tempdist = 0
        for ind in list(tempdata.index.values):
            tempdist = tempdist + idata.loc[idata['activiteit']==tempdata.type[ind], 'afstand in meters'].iloc[0]
        dists.append(tempdist)
        
        tempuren = sum(tempdata.tte)
        uren.append(tempuren)
        
        tempdienst = sum(tempdata.tte[tempdata.activiteit=="dienst rit"])
        diensts.append(tempdienst)
        
        if tempdienst > 0:
            tempdd = tempuren/tempdienst #alle uren gedeeld door diensturen    
        else:
            tempdd = 0
        dds.append(tempdd)
        
        tempusage = tempdist * 1.5
        
        tempidle = sum(tempdata.tte[tempdata.activiteit=="idle"]) #Totale idletijd
        idles.append(tempidle)
        
        tempcharge = sum(tempdata.tte[tempdata.type=="charge"])
        charges.append(tempcharge)
        
        tempperc = 100 * tempuren / timespan
        percs.append(tempperc)
        tempinp = {'Statistic': ['DD', 'Total distance (m)', 'Percentage of time active', 'Amount of time active', 'Time with passengers', 'Time spent idling', 'Time spent charging'], 'Value':[ tempdd, tempdist, tempperc, datetime.timedelta(minutes=tempuren), datetime.timedelta(minutes=tempdienst), datetime.timedelta(minutes=tempidle), datetime.timedelta(minutes=tempcharge)]}
        tempdf = pd.DataFrame(data=tempinp)    
        businfo.append(tempdf)
     
    sl.header("Average Statistics of all busses:")   
    avginp = {'Statistic': ['Average DD', 'Average distance (m)', 'Average percentage of time active', 'Average amount of time active', 'Average time with passengers', 'Average time spent idling', 'Average time spent charging'], 'Value':[ sum(dds)/len(dds), sum(dists)/len(dists), sum(percs)/len(percs), datetime.timedelta(minutes=sum(uren)/len(uren)), datetime.timedelta(minutes=sum(diensts)/len(diensts)), datetime.timedelta(minutes=sum(idles)/len(idles)), datetime.timedelta(minutes=sum(charges)/len(charges))]} 
    avgdf = pd.DataFrame(data=avginp)  
    sl.dataframe(avgdf) 
    
    from plancheck import *
    selected = sl.multiselect('select:',bussen[1:])
    for i in selected:
        sl.pyplot(i.plot())
        plt.title('State of charge of busses over time')
        plt.ylabel('State of charge(kWh)')
        plt.xlabel('Time') 
        
    #Plaatsen als colommen
    sl.header("Statistics of individual busses:")
    a = 1
    for i in range(int((len(businfo))/2)):
        col1, col2 = sl.columns(2)
        head1 = "Bus " + str(a)
        a = a+1
        head2 = "Bus " + str(a)
        a = a+1
        with col1:
            sl.markdown(head1)
            sl.dataframe(businfo[0])
        with col2:
            sl.markdown(head2)
            sl.dataframe(businfo[1])
        businfo.pop(0)
        businfo.pop(0)
    #In geval van oneven aantal bussen
    if len(businfo)==1:
        head1 = "Bus " + str(a)
        sl.markdown(head1)
        sl.dataframe(businfo[0])
