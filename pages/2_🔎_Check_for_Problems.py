# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 12:18:00 2022

@author: damon
"""

import streamlit as sl

sl.set_page_config(page_title="Controle", page_icon="🔎")
#Aangeven dat er data onbreekt
if sl.session_state['noinput'] == True:
    sl.markdown("Er is geen omloopplanning geupload. Ga terug naar de startpagina.")



sl.markdown("Op deze pagina kunt u controleren of de planning voldoet aan alle eisen.")

sl.write(sl.session_state["soc"])