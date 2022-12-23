# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 12:18:00 2022

@author: damon
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime 
import numpy as np
from matplotlib.patches import Patch
import streamlit as sl
from PIL import Image

sl.set_page_config(page_title="Controle", page_icon="🔎")

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
    from plancheck import *
    data = sl.session_state['datainput']

    sl.markdown("Op deze pagina kunt u controleren of de planning voldoet aan alle eisen.")
    if not assign():
        sl.write("De dienstregeling is niet volledig of dubbel ingepland")
    errdisp = errors()
    
    for i in bussen[1:]:
        if i not in errdisp:
            sl.write("Bus %s has no errors."%i.name)
    
    for i in errdisp:
        sl.write("Bus %s has the following errors on departure times:"%i.name)
        sl.write(pd.DataFrame.from_dict(i.error, orient='index'))
