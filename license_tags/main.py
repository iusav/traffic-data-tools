# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 11:28:43 2018

@author: ifv-alex.gellner
"""
from scripts.preprocessing.PreprocessingSection import PreprocessingController
from scripts.analysis.AnalysisSection import AnalysisController
from scripts.util.Tracks import read, concat, match, crop
from scripts.Logo import createLogo
from scripts.Strings import *
from scripts.Colors import *
from bokeh.plotting import figure

from bokeh.io import curdoc
from bokeh.server.server import Server
from bokeh.models.widgets import Panel, Tabs
from bokeh.layouts import row, layout, column

import os
from os.path import join, dirname
from collections import namedtuple

from pandas import DataFrame

import itertools

def readRawData(input):
    raw_data_list = []
    for file in os.listdir(input):
        path = os.path.join(input, file)
        if os.path.isdir(path):
            section_name = file
            data = readFolder(path)
            data['section_name'] = section_name
            raw_data_list.append(data)
        elif file.endswith(".csv"):
            name = os.path.splitext(file)[0]
            data = read(path)
            data['track_name'] = default_track_name
            data['section_name'] = name
            raw_data_list.append(data)
    return concat(raw_data_list)


def readFolder(directory):
    raw_data = []
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            data = read(os.path.join(directory, file))
            track_name = os.path.splitext(file)[0]
            data['track_name'] = track_name
            raw_data.append(data)

    return concat(raw_data)


def make_document(doc):
    input = join(dirname(__file__), "data")
    
    print('reading input...')
    raw_data = readRawData(input)
    
    print('evaluating input...')

    preprocessing_controller = PreprocessingController(raw_data)
    propressing_tab = Panel(child=preprocessing_controller.layout, title=preprocessing_tab_title)
    
    routes = preprocessing_controller.getRoutes()
    connections = preprocessing_controller.getConnections()
    connection_colors = {connection : color for connection, color in zip(connections.keys(), desaturate(green, len(connections)))}
    analysis_controller = AnalysisController(raw_data, routes, connections, connection_colors)
    analysis_tab = Panel(child=analysis_controller.layout, title=analysis_tab_title)

    tabs = Tabs(tabs=[ propressing_tab, analysis_tab ])
    
    content = layout([
        createLogo(),
        tabs
    ])

    def onTabChange(tab):
        if tab == 1:
            routes = preprocessing_controller.getRoutes()
            analysis_controller.setRoutes(routes)

    tabs.on_change('active', lambda attr, old, new: onTabChange(new))
    doc.title = tab_title
    doc.add_root(content)

if not curdoc().session_context:
    server = Server({'/license_tags': make_document})
    server.start()
    server.io_loop.add_callback(server.show, "/license_tags")
    server.io_loop.start()
else:
    make_document(curdoc())
