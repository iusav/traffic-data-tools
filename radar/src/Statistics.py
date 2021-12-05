# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 14:24:42 2018

@author: ifv-Alex.Gellner
"""

import pandas as pd
import numpy as np

from pandas import DataFrame


def filterOutliers(track, window=250, sdFactor=2.5, iterations=2):
    outliers = track.drop(track.index)
    for _ in range(iterations):
        track['median'] = track['duration'].rolling(window, center=True).median()
        track['std'] = track['duration'].rolling(window, center=True).std()

        outliers = outliers.append(track[track.duration > track['median'] + sdFactor * track['std']], sort=False)
        track = track[track.duration <= track['median'] + sdFactor * track['std']]
        
        track = track.drop(['median', 'std'], axis=1)
    return (track, outliers)
