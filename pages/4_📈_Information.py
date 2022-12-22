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

sl.set_page_config(page_title="Informatie", page_icon="📈")
#Aangeven dat er data onbreekt
if sl.session_state['noinput'] == True:
    sl.markdown("Er is geen omloopplanning geupload. Ga terug naar de startpagina.")

basedata = {'activiteit':['ehvaptehvbst400', 'ehvbstehvapt400', 'ehvaptehvbst401', 'ehvbstehvapt401', 'ehvbstehvaptm', 'ehvaptehvbstm', 'ehvbstehvgarm', 'ehvgarehvbstm', 'ehvaptehvgarm', 'ehvgarehvaptm'],
            'mint':[22, 22, 22, 22, 20, 20, 4, 4, 20, 20],
            'maxt':[24, 24, 25, 24, 20, 20, 4, 4, 20, 20],
            'afstand':[10250, 10708, 9050, 9003, 8600, 8600, 1650, 1650, 9000, 9000]
            }
idata = pd.DataFrame(data=basedata)
data = sl.session_state['datainput']
#sl.dataframe(idata)

totdist = 0
for ind in range(len(data)):
    totdist = totdist + idata.afstand[idata.activiteit==data.type[ind]]
toturen = sum(data.tte)
totdienst = sum(data.tte[data.activiteit=="dienst rit"])
totdd = toturen/totdienst#alle uren gedeeld door diensturen    
totusage = totdist * 1.5
inp = {'Statistiek': ['Totale afstand', 'Totaal aantal gereden uren', 'Totaal aantal gereden diensturen', 'DD'], 'Waarde':[totdist, datetime.timedelta(minutes=toturen), datetime.timedelta(minutes=totdienst), totdd]}
totdf = pd.DataFrame(data=inp)  
sl.dataframe(totdf)  
    
bussen = max(data['omloop nummer'])
businfo = []
for i in range(bussen+1)[1:]:
    tempdata = data[data['omloop nummer']==i]
    tempdist = 0
    for ind in list(tempdata.index.values):
        tempdist = tempdist + idata.afstand[idata.activiteit==tempdata.type[ind]]
    tempuren = sum(tempdata.tte)
    tempdienst = sum(tempdata.tte[tempdata.activiteit=="dienst rit"])
    tempdd = tempuren/tempdienst #alle uren gedeeld door diensturen    
    tempusage = tempdist * 1.5
    tempinp = {'Statistiek': ['Totale afstand', 'Totaal aantal gereden uren', 'Totaal aantal gereden diensturen', 'DD'], 'Waarde':[tempdist, datetime.timedelta(minutes=tempuren), datetime.timedelta(minutes=tempdienst), tempdd]}
    tempdf = pd.DataFrame(data=tempinp)    
    businfo.append(tempdf)
    
#Plaatsen als colommen
sl.header("Informatie van individuele bussen:")
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
