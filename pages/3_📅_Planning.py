# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 19:31:15 2022

@author: damon
"""
import pandas as pd
import matplotlib.pyplot as plt
import datetime 
import numpy as np
from matplotlib.patches import Patch
import streamlit as sl
from PIL import Image

sl.set_page_config(page_title="Planning", page_icon="📅")

#Aangeven dat er data onbreekt
if sl.session_state['noinput'] == True:
    sl.markdown("No schedule has been uploaded. Please return to the frontpage and upload a schedule.")
    noinputimg = Image.open('Geeninput.png')
    sl.image(noinputimg)
    
if sl.session_state['mismatch'] == True and sl.session_state['noinput']==False:
    sl.markdown("The uploaded schedule is not formatted correctly or does not match the uploaded data. Please check if both are correct.")
    badinputimg = Image.open('Fouteinput.png')
    sl.image(badinputimg)
    
if sl.session_state['mismatch'] == False and sl.session_state['noinput'] == False:
    data = sl.session_state['datainput']
    
    #Kleurtjes
    types = data.type.unique()
    #Hier geeft hij een kleur aan elk type rit, tot 30 verschillende ritten.
    kleur = ['#C0392B', '#D98880', '#FFC300', '#F7DC6F', '#D35400', '#E59866','#2ECC71', '#239B56', '#85C1E9', '#2E86C1', '#7D3C98', '#D2B4DE', '#0000FF', '#7DF9FF', '#00A36C', '#CD7F32', '#800020', '#F0E68C', '#808000', '#A52A2A', '#E4D00A', '#7CFC00', '#FA8072', '#9F2B68', '#FF00FF', '#C21E56', '#E0B0FF', '#7F00FF', '#FFDEAD', '#DAA520']
    c_dict = {}
    for i in range(len(types)):
        c_dict[types[i]] = kleur[i]
    
    def color(row):
        return c_dict[row['type']]
    data['color'] = data.apply(color, axis=1)
    
    #plot
    fig, ax = plt.subplots(1, figsize=(16, 6))
    ax.barh(data['omloop nummer'], data.tte, left=data.start_time, color=data.color) 
    
    
    #legenda
    #c_dict = {'materiaalrit garage bus':'#C0392B','m_ag':'#D98880', 'm_gb':'#FFC300', 'm_bg':'#F7DC6F', 'm_ab':'#D35400', 'm_ba':'#E59866', '401ba':'#2ECC71', '401ab':'#239B56', '400ab':'#85C1E9', '400ba':'#2E86C1', 'opl':'#7D3C98', 'idle':'#D2B4DE'}
    legend_elements = [Patch(facecolor=c_dict[i], label=i)  for i in c_dict]
    plt.legend(handles=legend_elements)
    
    #Assen:
    aantalbus = max(data['omloop nummer'])
    yticks = np.arange(1, aantalbus+1, 1)
    yticklabels = np.arange(1, aantalbus+1, 1)
    ax.set_yticks(yticks)
    ax.set_ylabel("Busses")
    
    #De x-as wordt naar uren afgerond
    xticks = np.arange(np.floor(data.start_time.min()/60)*60, np.floor(data.end_time.max()/60)*60 + 60, 60)
    val = np.floor(data.start_time.min()/60)*60
    xticklabels = []
    while val < (np.floor(data.end_time.max()/60)*60 + 60):
        xticklabels.append(str(datetime.timedelta(minutes=val)))
        val = val + 60
    
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, rotation=45)
    
    #plot laten zien
    sl.header("The entire schedule visualized:")
    sl.pyplot(fig)
    
    
    
    planningen = []
    for i in range(aantalbus+1)[1:]:
        busp = data[data['omloop nummer']==i]
        #busp = busp.replace(nan , '', regex=True)
        busp['Activiteit'] = data['activiteit'] +" "+ data['buslijn'].astype(str)
        busp.drop(['omloop nummer', 'type', 'start_time', 'end_time', 'tte', 'color', 'activiteit'], axis=1, inplace=True)
        busp.drop(['buslijn'], axis=1, inplace=True)
        planningen.append(busp)
        
    #Plaatsen als colommen
    sl.header("Each bus' individual schedule:")
    a = 1
    for i in range(int((len(planningen))/2)):
        col1, col2 = sl.columns(2)
        head1 = "Bus " + str(a)
        a = a+1
        head2 = "Bus " + str(a)
        a = a+1
        with col1:
            sl.markdown(head1)
            sl.dataframe(planningen[0])
        with col2:
            sl.markdown(head2)
            sl.dataframe(planningen[1])
        planningen.pop(0)
        planningen.pop(0)
    #In geval van oneven aantal bussen
    if len(planningen)==1:
        head1 = "Bus " + str(a)
        sl.markdown(head1)
        sl.dataframe(planningen[0])
        