# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 11:28:43 2018

@author: ifv-alex.gellner
"""

import os
import itertools

from Tracks import read, group
from Plots import Plot

from thread import start_new_thread


def main():
    # input = '//ifv-fs.ifv.kit.edu/User/HiWi/Alexander.Gellner/traffic-data-tools/license tags/data'
    input = 'D:\\Studium\\HiWi\\traffic-data-tools\\radar\\data'
    
    for name in 'kelter_weg_neu', 'lindenplatz_ost_neu', 'lindenplatz_west_neu', 'lommatzscher_str_west_neu', 'stuttgarter_str_neu', 'welzheimer_str_nord_neu', 'welzheimer_str_sued_neu':
        print('reading input...')
        track = read(input + '\\' + name + '.txt')
        result = group(track, 50)
        # print(track)
    
        print('evaluating input...')
        start_new_thread(evaluate, (track, result, name,))
    c = raw_input("Press ENTER to exit.")
    # evaluate(track, result)

    
def readTracks(input):
    tracks = []
    for file in os.listdir(input):
        path = os.path.join(input, file)
        if os.path.isdir(path):
            csvs = getCSVs(path)
            if (len(csvs) != 0):
                tracks.append((appendAll(csvs), file))
        elif file.endswith(".csv"):
            tracks.append((read(file), file))
    
    return tracks


def getCSVs(directory):
    csvs = []
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            csvs.append(os.path.join(directory, file))
    return csvs


def appendAll(csvs):
    track = read(csvs[0])
    for i in range(1, len(csvs)):
        track = append(track, read(csvs[i]))
    return track


def evaluate(track, group, name):
    plot = Plot()
    plot.show(track, group, name)


if __name__ == '__main__':
    main()
    
