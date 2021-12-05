# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 14:47:08 2018

@author: ifv-alex.gellner
"""
import pandas as pd
import numpy as np
from pandas import DataFrame


def read(name):
    cols = [1, 2, 3, 4]
    names = ['car', 'date', 'daytime', 'certainty']
    data = pd.read_csv(name, header=None, names=names, skiprows=1, sep=';', usecols=cols)
    
    format = "%d.%m.%Y %H:%M:%S"
    data['time'] = pd.to_datetime(data.date + ' ' + data.daytime, format=format)

    data = data.drop(['date', 'daytime'], 1)
    data = data.dropna()
    data.sort_values(by='time', inplace=True)

    return data


def match(from_track, to_track):
    from_track = from_track.drop('certainty', 1)
    to_track = to_track.drop('certainty', 1)
    
    f = from_track.rename(columns={'time':'departure'})
    t = to_track.rename(columns={'time':'arrival'})
    result = pd.merge_asof(f, t, by='car', left_on='departure', right_on='arrival', direction='forward', suffixes=['_start', '_end'], allow_exact_matches = False)

    result = result.dropna()
    result['track_name_end'] = result['track_name_end'].astype(to_track['track_name'].dtype)
    result['duration'] = (result['arrival'] - result['departure']) / np.timedelta64(1, 'm')
    result['outlier'] = False
    
    return result


def crop(match):
    first_arrival = match['arrival'].min()
    last_departure = match['departure'].max()
    min_duration = match['duration'].min() * np.timedelta64(1, 'm')

    return match[(match['departure'] >= first_arrival - min_duration) & (match['arrival'] <= last_departure + min_duration)]


def areRelated(from_track, to_track):
    f = from_track.drop_duplicates(subset='car')
    t = to_track.drop_duplicates(subset='car').rename(columns={'time':'arrival'})
    result = pd.merge_asof(f, t, by='car', left_on='time', right_on='arrival', direction='forward')

    return result['arrival'].isnull().sum() <= 0.99 * len(result.index)
    

def concat(tracks, by='time'):
    result = pd.concat(tracks, sort=False)
    result.sort_values(by=by, inplace=True)
    return result


def timeSlice(times, timedelta):
    minT = times.min()
    maxT = times.max()
    return np.arange(minT, maxT + timedelta, timedelta)


def timeSliceCentric(times, timedelta):
    timeslices = timeSlice(times, timedelta)
    return timeslices[:timeslices.size - 1] + timedelta / 2


def groupBy(track, timeslices, by='time'):
    cuts = pd.cut(track[by], timeslices)
    group = track.groupby(cuts, as_index=False)
    return group


def group(track, timedelta, by='time'):
    timeslices = timeSlice(track[by], timedelta)
    cuts = pd.cut(track[by], timeslices)
    group = track.groupby(cuts, as_index=False)
    return group
