# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 14:47:08 2018

@author: ifv-alex.gellner
"""
import pandas as pd
import numpy as np
from pandas import DataFrame


def read(name):
    names = ['date', 'daytime', 'length', 'velocity', 'category', 'timegap', 'direction']
    data = pd.read_csv(name, header=None, names=names, sep='\s+', decimal=',', dtype={'timegap': 'float'})
    
    format = "%Y-%m-%d %H:%M:%S"
    data['time'] = pd.to_datetime(data.date + ' ' + data.daytime, format=format)
    data['length'] *= 10
    data = data.drop(['date', 'daytime'], 1)
    data = data.dropna()
    data = data[data['length'] > 0]
    data.sort_values(by='time', inplace=True)

    return data


def group(track, lengthdelta):
    minL = track['length'].min()
    maxL = track['length'].max()
    length_slices = np.arange(minL, maxL + lengthdelta, lengthdelta)
    cuts = pd.cut(track['length'], length_slices)
    group = track.groupby(cuts, as_index=False)
    return DataFrame({'count': group.count()['length'], 'velocity': group.median()['velocity'], 'length': length_slices[:length_slices.size - 1] + lengthdelta / 2})
