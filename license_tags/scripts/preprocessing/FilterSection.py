from scripts.util.Statistics import *
from scripts.util.Tracks import *
from scripts.Colors import *
from scripts.Strings import *
from scripts.Plot import Plot

from bokeh.models import Select, Slider, CheckboxGroup, RadioGroup, Button, Spacer, ColumnDataSource, CustomJS, Dropdown, HoverTool
from bokeh.layouts import row, layout, column
from pandas import DataFrame
import numpy as np

from os.path import join, dirname


class FilterController:

    def __init__(self, raw_data, track_names, max_track_names):
        self.raw_data_source = ColumnDataSource(data={key : raw_data[key] for key in raw_data.keys()})
        routes_dict = {'car':[], 'departure':[], 'arrival':[], 'duration':[], 'section_name_start':[], 'section_name_end':[], 'track_name_start':[], 'track_name_end':[], 'outlier':[]}
        self.routes_source = ColumnDataSource(routes_dict)

        self.track_names = track_names
        self.configurations = {}

        match_list = []
        self.connections = {}
        for (start_name, end_name), route_matches in match(raw_data, raw_data).groupby(['section_name_start', 'section_name_end']):
            if len(route_matches) >= 0.01 * len(raw_data[raw_data['section_name'] == start_name]):
                configuration = Configuration(len(track_names[start_name]), len(track_names[end_name]))
                
                cropped_matches = concat([crop(group) for _, group in route_matches.groupby(['track_name_start', 'track_name_end'])], by='departure');
                
                window = str(configuration.outlier_window * 60) + 's'
                configuration.outlier_filter_method(cropped_matches, window=window, outlier_factor=configuration.outlier_factor, time='departure')
                match_list.append(cropped_matches)

                connection_name = connection_selection_entry.format(start=start_name, end=end_name)
                self.connections[connection_name] = (start_name, end_name)
                self.configurations[connection_name] = configuration

        self.matches = concat(match_list, by='departure')
        self.matches_selection = None

        self.configuration = None
        self.updating = False

        self.times = (start_time, end_time)
        self.outlier_filter_methods = {outlier_filter_method_iqr: filterOutliersByIqr,
                                      outlier_filter_method_std: filterOutliersByStd,
                                      outlier_filter_method_mad: filterOutliersByMad}

        connection_names = self.configurations.keys()
        outlier_method_names = self.outlier_filter_methods.keys()
        download_values = [(download_raw_data_name, 'raw_data'), (download_all_routes_name, 'all_routes'), (download_filtered_routes_name, 'filtered_routes')]

        self.widgets = FilterWidgets(max_track_names, connection_names, outlier_method_names, download_values)
        self.plot = TravelTimePlot()
        self.layout = row(self.widgets.layout, self.plot.plot)

        self.createListeners()
        self.updateRouteSource()

    def getConnections(self):
        return self.connections

    def getRoutes(self, filter_outliers=True):
        connections = {}
        matches = []
        for (start_name, end_name), route_matches in self.matches.groupby(['section_name_start', 'section_name_end']):
            connection_name = connection_selection_entry.format(start=start_name, end=end_name)
            configuration = self.configurations[connection_name]
            start_track_names = [self.track_names[start_name][index] for index in configuration.start_selection]
            end_track_names = [self.track_names[end_name][index] for index in configuration.end_selection]
            filtered = route_matches[route_matches['track_name_start'].isin(start_track_names) & route_matches['track_name_end'].isin(end_track_names)]
            matches.append(filtered)

        routes = concat(matches, by='departure')
        return routes[routes['outlier'] == False] if filter_outliers else routes

    def updateConfiguration(self):
        connection_name = self.widgets.connection_selection.value
        configuration = self.configurations[connection_name]
        (start_name, end_name) = self.connections[connection_name]
        self.configuration = configuration

        self.updating = True
        self.widgets.start_track_boxes.labels = self.track_names[start_name]
        self.widgets.start_track_boxes.active = configuration.start_selection
        self.widgets.end_track_boxes.labels = self.track_names[end_name]
        self.widgets.end_track_boxes.active = configuration.end_selection
        self.widgets.outlier_window_slider.value = configuration.outlier_window
        self.widgets.outlier_factor_slider.value = configuration.outlier_factor
        self.widgets.outlier_method_select.value = configuration.outlier_filter_method_name
        self.updating = False

        self.plot.clear()
        self.updateConnection()
        self.updatePlot()

    def updateTracks(self):
        self.updateConnection()
        self.updateOutliers()

    def updateBase(self):
        time = ('departure', 'arrival')[self.widgets.base_radio_group.active]
        self.matches_selection['time'] = self.matches_selection[time]
        self.updatePlot()
        
    def updateConnection(self):
        if not self.updating:
            connection_name = self.widgets.connection_selection.value
            self.configuration.start_selection = self.widgets.start_track_boxes.active 
            self.configuration.end_selection = self.widgets.end_track_boxes.active
            (start_name, end_name) = self.connections[connection_name]

            matches = self.matches
            
            start_track_names = [self.track_names[start_name][index] for index in self.widgets.start_track_boxes.active]
            end_track_names = [self.track_names[end_name][index] for index in self.widgets.end_track_boxes.active]
            matches = matches.loc[matches['track_name_start'].isin(start_track_names) & matches['track_name_end'].isin(end_track_names)
                                         & (matches['section_name_start'] == start_name) & (matches['section_name_end'] == end_name)
                                         , ('departure', 'arrival', 'duration', 'outlier', 'car')]
            
            time = ('departure', 'arrival')[self.widgets.base_radio_group.active]
            matches['time'] = matches[time]
            self.matches_selection = matches

    def resetZoom(self):
        inliers = self.matches_selection[self.matches_selection['outlier'] == False]
        if len(inliers):
            self.plot.setXAxisRange(min(inliers['time']), max(inliers['time']))
            self.plot.setYAxisRange(min(inliers['duration']), max(inliers['duration']))

    def updateOutliers(self):
        if not self.updating:
            configuration = self.configuration
            configuration.outlier_filter_method = self.outlier_filter_methods[self.widgets.outlier_method_select.value]
            configuration.outlier_window = self.widgets.outlier_window_slider.value
            configuration.outlier_factor = self.widgets.outlier_factor_slider.value
            configuration.outlier_filter_method(self.matches_selection, window=str(self.configuration.outlier_window * 60) + 's', outlier_factor=configuration.outlier_factor)

            matches = self.matches
            matches.loc[self.matches_selection.index, ['outlier']] = self.matches_selection['outlier']
            
            self.updatePlot()
            self.updateRouteSource()
        
    def updatePlot(self):
        if len(self.matches_selection):
            if len(self.widgets.auto_reset_zoom_box.active):
                self.resetZoom()

            time = self.times[self.widgets.base_radio_group.active]
            self.plot.setTitle(travel_time_plot_title.format(time=time, connection=self.widgets.connection_selection.value))
            self.plot.setXLabel(travel_time_plot_xaxis.format(time=time))
            self.plot.updatePoints(self.matches_selection)
            self.updateLines()
        else:
            self.plot.clear()

    def updateLines(self):
        inliers = self.matches_selection[self.matches_selection['outlier'] == False]
        if len(inliers) and inliers['time'].min() != inliers['time'].max():
            window = np.timedelta64(self.widgets.group_window_slider.value, 'm')
            g = group(inliers, window)
            t = timeSliceCentric(inliers['time'], window)
            q = self.widgets.quantile_slider.value
            lines = DataFrame({'time': t, 'median': g.median()['duration'], 'q1': g.quantile(0.5 - q)['duration'], 'q3': g.quantile(0.5 + q)['duration']})
            lines = lines.dropna()
            self.plot.updateLines(lines)
            self.plot.setLegendLabel(2, travel_time_plot_legend_quantile.format(quantile=0.5 + q))
            self.plot.setLegendLabel(4, travel_time_plot_legend_quantile.format(quantile=0.5 - q))
        else:
            self.plot.clear()

    def updateRouteSource(self):
        routes = self.getRoutes(filter_outliers=False)
        self.routes_source.data = {key: routes[key] for key in self.routes_source.data.keys()}

    def createListeners(self):
        self.widgets.connection_selection.on_change('value', lambda attr, old, new: self.updateConfiguration())
        
        self.widgets.start_track_boxes.on_click(lambda selection: self.updateTracks())
        self.widgets.end_track_boxes.on_click(lambda selection: self.updateTracks())

        self.widgets.outlier_method_select.on_change('value', lambda attr, old, new: self.updateOutliers())
        self.widgets.outlier_window_slider.on_change('value', lambda attr, old, new: self.updateOutliers())
        self.widgets.outlier_factor_slider.on_change('value', lambda attr, old, new: self.updateOutliers())

        self.widgets.base_radio_group.on_click(lambda attr: self.updateBase())
        self.widgets.group_window_slider.on_change('value', lambda attr, old, new: self.updateLines())
        self.widgets.quantile_slider.on_change('value', lambda attr, old, new: self.updateLines())

        self.widgets.reset_zoom_button.on_click(self.resetZoom)
        self.widgets.download_dropdown.callback = CustomJS(args=dict(raw_data_source=self.raw_data_source, routes_source=self.routes_source),
                                                           code=open(join(dirname(dirname(dirname(__file__))), "models/preprocessing_download.js")).read())
        
        self.widgets.connection_selection.value = self.configurations.keys()[0]
        self.resetZoom()

        
class TravelTimePlot(Plot):

    def __init__(self):
        super(TravelTimePlot, self).__init__(tools='pan,wheel_zoom,box_zoom,save')
        self.inliers = ColumnDataSource()
        self.outliers = ColumnDataSource()
        self.lines = ColumnDataSource()
        self.initFigure()
        self.clear()
        
        self.setYLabel(travel_time_plot_yaxis)
        
        self.plot.add_tools(HoverTool(tooltips=[('travel time', '@$name{0.0} min')], names=['median','q1','q3'], mode='mouse'))

    def updatePoints(self, points):
        inliers = points[points['outlier'] == False]
        outliers = points[points['outlier'] == True]
        self.inliers.data = {'time' : inliers['time'], 'duration': inliers.duration}
        self.outliers.data = {'time' : outliers['time'], 'duration': outliers.duration}
        
    def updateLines(self, lines):
        self.lines.data = {'time': lines['time'], 'median': lines['median'], 'q1': lines['q1'], 'q3': lines['q3']}
            
    def clear(self):
        self.inliers.data = {'time':[], 'duration':[]}
        self.outliers.data = {'time':[], 'duration':[]}
        self.lines.data = {'time':[], 'median':[], 'q1':[], 'q3':[]}
        
    def initFigure(self):
        self.plot.circle('time', 'duration', color=black , source=self.outliers, legend=travel_time_plot_legend_outlier, fill_alpha=0.2, line_alpha=0.2)
        self.plot.circle('time', 'duration', color=orange, source=self.inliers , legend=travel_time_plot_legend_inlier , fill_alpha=0.5, line_alpha=0.5)
        self.plot.line('time'  , 'q3'      , color=black , source=self.lines   , legend=travel_time_plot_legend_quantile.format(quantile=0.75), name='q3', line_width=2, line_dash='dashed')
        self.plot.line('time'  , 'median'  , color=black , source=self.lines   , legend=travel_time_plot_legend_median                        , name='median', line_width=3)
        self.plot.line('time'  , 'q1'      , color=black , source=self.lines   , legend=travel_time_plot_legend_quantile.format(quantile=0.25), name='q1', line_width=2, line_dash='dashed')
        self.plot.legend.click_policy = 'hide'


class FilterWidgets:

    def __init__(self, max_track_names, connection_names, outlier_method_names, download_values):
        self.download_dropdown = Dropdown(label=download_name, button_type="success", menu=download_values, width=290)
        
        self.connection_selection = Select(options=connection_names, width=300)
        
        self.start_track_boxes = CheckboxGroup(width=150)
        self.end_track_boxes = CheckboxGroup(width=150)

        self.base_radio_group = RadioGroup(labels=[start_based_option_name, end_based_option_name], inline=True, active=0)

        self.outlier_method_select = Select(title=outlier_filter_method_selection_name, options=outlier_method_names, value=outlier_filter_method_iqr, width=300)
        self.outlier_window_slider = Slider(start=5, end=60, step=5, value=5, width=140, title=outlier_filter_window_selection_name)
        self.outlier_factor_slider = Slider(start=1.1, end=5, step=0.1, width=130, title=outlier_filter_factor_selection_name)

        self.group_window_slider = Slider(start=5, end=60, step=5, value=10, title=group_window_selection_name, width=140)
        self.quantile_slider = Slider(start=0, end=0.5, step=0.05, value=0.25, title=quantile_selection_name, width=130)
        
        self.reset_zoom_button = Button(label=axes_reset_name, width=140)
        self.auto_reset_zoom_box = CheckboxGroup(labels=[auto_axes_reset_name])
        
        self.layout = layout([
            row(self.connection_selection),
            [Spacer(width=10), row(self.start_track_boxes, self.end_track_boxes, width=350, height=30 * max_track_names)],
            self.outlier_method_select,
            [row(self.outlier_window_slider, width=150), row(self.outlier_factor_slider, width=150)],
            # self.base_radio_group,
            [row(self.group_window_slider, width=150), row(self.quantile_slider, width=150)],
            [row(self.reset_zoom_button, width=150, height=45), row(self.auto_reset_zoom_box, width=150, height=45)],
            row(self.download_dropdown)
        ], width=350)


class Configuration:

    def __init__(self, start_tracks, end_tracks):
        self.start_selection = range(start_tracks)
        self.end_selection = range(end_tracks)

        self.outlier_filter_method_name = outlier_filter_method_iqr
        self.outlier_filter_method = filterOutliersByIqr
        self.outlier_window = 10
        self.outlier_factor = 3
