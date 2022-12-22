# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 11:35:22 2022

@author: damon
"""
import streamlit as sl
import numpy as np
import pandas as pd

sl.markdown("Here you can find the which route is being analysed. By default this will be routes 400 and 401. You can change the routes by uploading the necessary data below.")

new_upload = sl.file_uploader('')

if new_upload is None:
    sl.markdown("Nothing uploaded")
    usedata = sl.session_state['dienstdata']
    usedienst = sl.session_state['dienstregeling']
if new_upload is not None:
    sl.markdown("Upload found")
    usedata = pd.read_excel(new_upload, sheet_name=1)
    usedienst = pd.read_excel(new_upload)
    sl.session_state['dienstdata'] = usedata
    sl.session_state['dienstregeling'] = usedienst

activeroutes = usedata.buslijn.unique()
activeroutes = activeroutes[~np.isnan(activeroutes)]

sl.markdown("The following routes are currently active:")
for i in activeroutes:
    sl.markdown(i)
    
if len(usedienst.columns) > 4:
    usedienst.drop(columns=usedienst.columns[[4, 5]],  axis=1, inplace=True)
sl.markdown("These routes are required to make the following trips:")
sl.dataframe(usedienst)
