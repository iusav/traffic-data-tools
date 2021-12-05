# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 14:24:42 2018

@author: ifv-Alex.Gellner
"""

import pandas as pd
import numpy as np

from pandas import DataFrame


def filterOutliersByStd(track, window='600s', outlier_factor=1.5, min_periods=1, time='time'):
    index = track.index
    track.index = track[time]

    rolled = track['duration'].rolling(window, min_periods=min_periods)
    mean = rolled.mean()
    std = rolled.std()
    
    track.outlier = (track['duration'] > mean + outlier_factor * std) | mean.isnull()
    track.index = index

def filterOutliersByIqr(track, window='600s', outlier_factor=1.5, min_periods=1, time='time'):
    index = track.index
    track.index = track[time]

    rolled = track['duration'].rolling(window, min_periods=min_periods)
    median = rolled.median()
    q3 = rolled.quantile(0.75)
    iqr = q3 - rolled.quantile(0.25)

    track.outlier = track['duration'] > q3 + outlier_factor * iqr
    track.index = index

def filterOutliersByMad(track, window='600s', outlier_factor=3.5, min_periods=1, time='time'):
    index = track.index
    track.index = track[time]

    rolled = track['duration'].rolling(window, min_periods=min_periods)
    
    def madf(data, axis=None):
        return np.median(np.absolute(data - np.median(data, axis)), axis)

    mad = rolled.apply(madf, raw=True)
    median = rolled.mean()

    track.outlier = 0.6745 * (track['duration'] - median) > outlier_factor * mad
    track.index = index