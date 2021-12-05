from scripts.util.Tracks import group, timeSliceCentric
from scripts.Colors import *
from scripts.Strings import *
from scripts.Plot import Plot

from pandas import DataFrame
import numpy as np
from bokeh.models import Select, Slider, CheckboxGroup, Button, ColumnDataSource, Spacer
from bokeh.layouts import row, layout, column


class CertaintyController:

    def __init__(self, raw_data, track_names, max_track_names):
        self.tracks = raw_data
        self.track_names = track_names

        self.updating = False
        self.widgets = CertaintyWidgets(max_track_names, track_names.keys())
        self.plot = CertaintyPlot()
        self.layout = row(self.widgets.layout, self.plot.plot)
            
        self.createListeners()
    
    def applySection(self):
        self.updating = True
        
        section_name = self.widgets.section_selection.value
        self.widgets.track_boxes.labels = self.track_names[section_name]
        self.widgets.track_boxes.active = list(range(len(self.track_names[section_name])))
        self.updating = False
        self.updateCertainty()
            
    def updateCertainty(self):
        if not self.updating:
            section_name = self.widgets.section_selection.value
            track_names = [self.track_names[section_name][index] for index in self.widgets.track_boxes.active]
            self.section = self.tracks[(self.tracks['section_name'] == section_name) & (self.tracks['track_name'].isin(track_names))]
            if len(self.section):
                self.plot.updatePoints(self.section)
                self.updateLines()
            else:
                self.plot.clear()

    def updateLines(self):
        section = self.section
        if len(section) and section['time'].min() != section['time'].max():
            window = np.timedelta64(self.widgets.group_window_slider.value, 'm')
            g = group(section, window)
            t = timeSliceCentric(section['time'], window)
            lines = DataFrame({'time': t, 'certainty': g.median()['certainty']})
            lines = lines.dropna()
            self.plot.updateLines(lines)
        else:
            self.plot.clear()

    def createListeners(self):
        self.widgets.section_selection.on_change('value', lambda attr, old, new: self.applySection())
        self.widgets.track_boxes.on_click(lambda selection: self.updateCertainty())
        self.widgets.group_window_slider.on_change('value', lambda attr, old, new: self.updateLines())
        self.widgets.section_selection.value = list(self.track_names.keys())[0]
        self.widgets.track_boxes.active = []


class CertaintyPlot(Plot):

    def __init__(self):
        self.points = ColumnDataSource({'time':[], 'certainty':[]})
        self.lines = ColumnDataSource({'time':[], 'median':[]})
        self.initFigure()

    def updatePoints(self, points):
        self.points.data = {'time':points.time, 'certainty': points.certainty}
        
    def updateLines(self, lines):
        self.lines.data = {'time': lines.time, 'median': lines.certainty}

    def initFigure(self):
        super(CertaintyPlot, self).__init__(tools='pan,wheel_zoom,box_zoom,save')
        
        self.plot.circle('time', 'certainty', fill_alpha=0.5, line_alpha=0.5, source=self.points, color=orange, legend=certainty_plot_legend_point)
        self.plot.line('time', 'median', color=black, source=self.lines, line_width=3, legend=certainty_plot_legend_median)
        
        self.plot.title.text = certainty_plot_title
        self.plot.xaxis.axis_label = certainty_plot_xaxis
        self.plot.yaxis.axis_label = certainty_plot_yaxis
    
    def clear(self):
        self.points.data = {'time':[], 'certainty':[]}
        self.lines.data = {'time':[], 'median':[]}


class CertaintyWidgets:

    def __init__(self, max_track_names, section_names):
        self.section_selection = Select(options=list(section_names), width=300)
        self.track_boxes = CheckboxGroup(width=150, active=[])

        self.group_window_slider = Slider(start=5, end=60, step=5, value=10, title=group_window_selection_name)

        self.layout = layout([
            row(self.section_selection),
            [Spacer(width=10), row(self.track_boxes, width=350, height=30 * max_track_names)],
            self.group_window_slider,
        ], width=350)