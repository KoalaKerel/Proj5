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
    sl.markdown("Er is geen omloopplanning geupload. Ga terug naar de startpagina.")
    noinputimg = Image.open('Geeninput.png')
    sl.image(noinputimg)
    
if sl.session_state['mismatch'] == True and sl.session_state['noinput']==False:
    sl.markdown("Er is een foute omloopplanning geupload. Ga terug naar de startpagina.")
    badinputimg = Image.open('Fouteinput.png')
    sl.image(badinputimg)
    
if sl.session_state['mismatch'] == False and sl.session_state['noinput'] == False:
    from plancheck import *
    data = sl.session_state['datainput']
#Aangeven dat er data onbreekt

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
