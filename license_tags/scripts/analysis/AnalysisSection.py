from scripts.util.Tracks import *
from TravelTimeSection import TravelTimeController
from TravelDistributionSection import TravelDistributionController
from scripts.Strings import * 

from bokeh.layouts import layout, row, widgetbox, column
from bokeh.models import ColumnDataSource, Button, MultiSelect, RadioGroup, Slider, CheckboxGroup, Select, Panel, Tabs, TextInput, Dropdown, CustomJS, BoxSelectTool
from bokeh.models.ranges import Range1d, Range

import numpy as np
from datetime import datetime
from math import floor, ceil

from os.path import join, dirname


class AnalysisController:

    def __init__(self, raw_data, routes, connections, connection_colors):        
        self.times = (start_time, end_time)
        self.selected_connections_source = ColumnDataSource({'connections':[]})
        self.selected_connections = []
        self.updating = False
        self.connection_selectors = [ConnectionSelector(), SectionSelector(0), SectionSelector(1)]
        self.x_range = Range1d()
                
        connection_selection_names = [connection_selection_method_connection, connection_selection_method_start, connection_selection_method_end]
        download_values = [(download_selected_lines_name, 'lines'), (download_selected_bars_name, 'bars'), (download_selected_lines_and_bars_name, 'lines_and_bars')]
        self.widgets = AnalysisWidgets(connection_selection_names, download_values)

        app_path = dirname(dirname(dirname(__file__)))
        select_callback = CustomJS(args=dict(from_select=self.widgets.export_selection_from, to_select=self.widgets.export_selection_to),
                                                 code=open(join(app_path, "models/select.js")).read())
        reset_callback = CustomJS(args=dict(from_select=self.widgets.export_selection_from, to_select=self.widgets.export_selection_to),
                                                 code=open(join(app_path, "models/reset.js")).read())
        box_select_tool = BoxSelectTool(dimensions='width', callback=select_callback, names=[], select_every_mousemove=True)

        self.connection_controller = TravelTimeController(connection_colors, self.x_range, box_select_tool, reset_callback)
        self.profile_controller = TravelDistributionController(raw_data, connections, connection_colors, self.x_range, box_select_tool, reset_callback)

        self.layout = row([
            column(self.widgets.layout, self.connection_controller.widgets.layout, self.profile_controller.widgets.layout, width=350),
            column(self.connection_controller.plot.plot, self.profile_controller.plot.plot)
        ])

        self.createListeners()
        self.setRoutes(routes)

    def updateAxisSelectionValue(self, selection, time):
        self.updating = True
        selection.value = pd.Timestamp(time, unit='ms').strftime('%d.%m.%Y %H:%M:%S')
        self.updating = False
        
    def updateAxis(self):
        if not self.updating:
            from_selection = self.widgets.axis_selection_from.value
            to_selection = self.widgets.axis_selection_to.value
            
            from_date_time = pd.to_datetime(from_selection, format='%d.%m.%Y %H:%M:%S', errors='coerce')
            to_date_time = pd.to_datetime(to_selection, format='%d.%m.%Y %H:%M:%S', errors='coerce')
            
            if not pd.isnull(from_date_time) and not pd.isnull(to_date_time):
                self.x_range.start = from_date_time.value / 1000000
                self.x_range.end = to_date_time.value / 1000000

    def setRoutes(self, routes):
        self.routes = {}
        connections = {}
        for (start_name, end_name), matches_tour in routes.groupby(['section_name_start', 'section_name_end']):
            connection_name = connection_selection_entry.format(start=start_name, end=end_name)
            self.routes[connection_name] = matches_tour
            connections[connection_name] = (start_name, end_name)
        self.connections = connections

        self.updating = True

        for i in range(len(self.connection_selectors)):
            select = self.widgets.connection_selections[i]
            selection = select.value
            options = self.connection_selectors[i].options(connections)
            intersection = list(set(selection) & set(options))

            select.options = options
            select.value = intersection if len(intersection) else [options[0]]
        self.updating = False

        intersection_selection = list(set(connections.keys()) & set(self.selected_connections))
        self.updateSelectedConnections()
        if not len(intersection_selection):
            self.resetZoom()

    def updateSelectedConnections(self):
        if not self.updating:
            method_index = self.widgets.connection_selections_tabs.active
            names = self.widgets.connection_selections[method_index].value
            selector = self.connection_selectors[method_index]
            self.selected_connections = selector.select(self.connections, names)
            self.selected_connections_source.data['connections'] = self.selected_connections

            self.updateGroups()

    def updateSelectedIndices(self):
        from_selection = self.widgets.export_selection_from.value
        to_selection = self.widgets.export_selection_to.value
        
        from_date_time = pd.to_datetime(from_selection, format='%d.%m.%Y %H:%M:%S', errors='coerce')
        to_date_time = pd.to_datetime(to_selection, format='%d.%m.%Y %H:%M:%S', errors='coerce')
        
        if pd.isnull(from_date_time) and pd.isnull(to_date_time):
            selection = [] 
        elif not pd.isnull(from_date_time) and not pd.isnull(to_date_time):
            window = np.timedelta64(self.widgets.group_window_slider.value, 'm')
            start_idx = max(0, int(floor((from_date_time - self.time_range[0]) / window)))
            end_idx = min(len(self.time_slices), int(ceil((to_date_time - self.time_range[0]) / window)))
            selection = range(start_idx, end_idx)
        else:
            return
        
        self.connection_controller.setSelection(selection)
        self.profile_controller.setSelection(selection)
        
    def updateGroups(self):
        if not self.updating:            
            w = self.widgets.group_window_slider.value
            time = self.times[self.widgets.base_radio_group.active]

            window = np.timedelta64(w, 'm')
            self.time_range = (min([self.routes[connection][time].min() for connection in self.selected_connections]).floor(freq=str(w) + 'T'),
                               max([self.routes[connection][time].max() for connection in self.selected_connections]).ceil(freq=str(w) + 'T'))
            self.time_slices = np.arange(self.time_range[0], self.time_range[1] + window, window)
    
            self.connection_groups = {}
            for connection in self.selected_connections:
                self.connection_groups[connection] = groupBy(self.routes[connection], self.time_slices, by=time)

            self.update()
            self.updateSelectedIndices()

    def update(self):
        self.connection_controller.setData(self.connection_groups,
                                           self.time_slices,
                                           self.widgets.base_radio_group.active)
        self.profile_controller.setData(self.connection_groups,
                                        self.time_slices,
                                        self.widgets.base_radio_group.active)
        if self.widgets.auto_reset_zoom_box.active:
            self.resetZoom()
        
    def resetZoom(self):
        self.connection_controller.resetZoom()
        self.profile_controller.resetZoom()

    def createListeners(self):
        self.widgets.connection_selections[0].on_change('value', lambda attr, old, new: self.updateSelectedConnections())
        self.widgets.connection_selections[1].on_change('value', lambda attr, old, new: self.updateSelectedConnections())
        self.widgets.connection_selections[2].on_change('value', lambda attr, old, new: self.updateSelectedConnections())

        self.widgets.base_radio_group.on_click(lambda attr: self.updateGroups())
        self.widgets.group_window_slider.on_change('value', lambda attr, old, new: self.updateGroups())

        self.widgets.reset_zoom_button.on_click(self.resetZoom)
        
        self.widgets.connection_selections_tabs.on_change('active', lambda attr, old, new: self.updateSelectedConnections())

        self.widgets.export_selection_from.on_change('value', lambda attr, old, new: self.updateSelectedIndices())
        self.widgets.export_selection_to.on_change('value', lambda attr, old, new: self.updateSelectedIndices())
        
        self.widgets.axis_selection_from.on_change('value', lambda attr, old, new: self.updateAxis())
        self.widgets.axis_selection_to.on_change('value', lambda attr, old, new: self.updateAxis())
        
        self.widgets.download_dropdown.callback = CustomJS(args=dict(connections_source=self.selected_connections_source,
                                                                     lines=self.connection_controller.getData(),
                                                                     line_name_suffixes=TravelTimeController.column_name_suffixes,
                                                                     quantile=self.connection_controller.widgets.quantile_slider,
                                                                     bars=self.profile_controller.getData(),
                                                                     bar_mode_names=self.profile_controller.getModeNames()),
                                                           code=open(join(dirname(dirname(dirname(__file__))), "models/analysis_download.js")).read())
        
        self.x_range.on_change('start', lambda attr, old, new: self.updateAxisSelectionValue(self.widgets.axis_selection_from, self.x_range.start))
        self.x_range.on_change('end', lambda attr, old, new: self.updateAxisSelectionValue(self.widgets.axis_selection_to, self.x_range.end))


class AnalysisWidgets:

    def __init__(self, connection_selection_methods, download_name_values):
        self.connection_selections = [MultiSelect(width=330) for index, method in enumerate(connection_selection_methods)]
        panels = [Panel(child=self.connection_selections[index], title=method) for index, method in enumerate(connection_selection_methods)]
        self.connection_selections_tabs = Tabs(tabs=panels, width=330)

        self.base_radio_group = RadioGroup(labels=[start_based_option_name, end_based_option_name], inline=True, active=0)

        self.group_window_slider = Slider(start=5, end=60, step=5, value=10, title=group_window_selection_name, width=320)
        
        self.reset_zoom_button = Button(label=axes_reset_name, width=163)
        self.auto_reset_zoom_box = CheckboxGroup(labels=[auto_axes_reset_name], width=160)

        self.export_selection_from = TextInput(placeholder='TT.MM.JJJJ hh:mm:ss', title=analysis_export_selection_start, width=150)
        self.export_selection_to = TextInput(placeholder='TT.MM.JJJJ hh:mm:ss', title=analysis_export_selection_end, width=150)
        
        self.axis_selection_from = TextInput(placeholder='TT.MM.JJJJ hh:mm:ss', title=analysis_axis_selection_start, width=150)
        self.axis_selection_to = TextInput(placeholder='TT.MM.JJJJ hh:mm:ss', title=analysis_axis_selection_end, width=150)
        
        self.download_dropdown = Dropdown(label=download_name, button_type="success", menu=download_name_values, width=330)
        
        self.layout = layout([
            self.connection_selections_tabs,
            self.base_radio_group,
            self.group_window_slider,
            [row(self.reset_zoom_button, width=170), row(self.auto_reset_zoom_box, width=165)],
            [row(self.axis_selection_from, width=165), row(self.axis_selection_to, width=165)],
            [row(self.export_selection_from, width=165), row(self.export_selection_to, width=165)],
            [row(self.download_dropdown, width=320)]
        ], width=350)

        
class ConnectionSelector:

    def select(self, connections, selection):
        return selection
    
    def options(self, connections):
        return connections.keys()

    
class SectionSelector:

    def __init__(self, base):
        self.base = base
            
    def select(self, connections, selection):
        return [connection_name for connection_name, connection in connections.items() if connection[self.base] in selection]
    
    def options(self, connections):
        return list(set(connection[self.base] for connection_name, connection in connections.items()))
