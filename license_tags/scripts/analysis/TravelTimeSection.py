from scripts.util.Tracks import *
from scripts.Plot import Plot
from scripts.Strings import *

from bokeh import events
from bokeh.models import ColumnDataSource, Legend, LegendItem, Slider, HoverTool, BoxSelectTool, ResetTool, CustomJSHover
from bokeh.models.selections import Selection
from bokeh.layouts import row, layout, column


class TravelTimeController:
    column_name_suffixes = ['q1', 'median', 'q3']

    def __init__(self, connection_colors, x_range, box_select_tool, reset_callback):
        self.times = (start_time, end_time)
        self.connection_names = connection_colors.keys()

        self.widgets = TravelTimeWidgets()
        hover_tool = self.createHoverTool()      
        self.plot = TravelTimePlot(x_range, box_select_tool, hover_tool, reset_callback, connection_colors)

        self.createListeners()

    def setData(self, connection_groups, time_slices, base):
        time = self.times[base]
        self.connection_groups = connection_groups
        self.centric_time_slices = time_slices[:-1] + (time_slices[1] - time_slices[0]) / 2
        self.plot.setTitle(travel_times_plot_title.format(time=time))
        self.plot.setXLabel(travel_times_plot_xaxis.format(time=time))
        self.plot.updateLegend(connection_groups.keys())
        self.updateLines()

    def setSelection(self, selected_indices):
        self.plot.updateSelection(selected_indices)

    def resetZoom(self):
        self.plot.resetAxes()

    def getData(self):
        return self.plot.lines

    def updateLines(self):
        empty_values = [0] * len(self.centric_time_slices)
        q = self.widgets.quantile_slider.value
        quantiles = [0.5 - q, 0.5, 0.5 + q]
        active_connections = self.connection_groups.keys()
        
        lines = {connection + suffix : self.connection_groups[connection].quantile(quantile)['duration'] if connection in active_connections else empty_values
                  for quantile, suffix in zip(quantiles, TravelTimeController.column_name_suffixes)
                  for connection in  self.connection_names}       
        lines['time'] = self.centric_time_slices
        self.plot.setYResetAxisRange(min([lines[connection + TravelTimeController.column_name_suffixes[0]].min() for connection in active_connections]),
                                     max([lines[connection + TravelTimeController.column_name_suffixes[2]].max() for connection in active_connections]))

        self.plot.setXResetAxisRange(self.centric_time_slices[0].astype(long) / 1000,
                                     self.centric_time_slices[-1].astype(long) / 1000)
        self.plot.updateLines(lines)
        
    def createListeners(self):
        self.widgets.quantile_slider.on_change('value', lambda attr, old, new: self.updateLines())

    def createHoverTool(self):
        code = """
            var name = special_vars.name;
            return name.substring(0, name.length - {suffix_len}) + ": " + value.toFixed(1) + " min (" + {name} + ")"
        """
        names = ['"q=" + (0.5 - q.value).toFixed(2)', '"median"', '"q=" + (0.5 + q.value).toFixed(2)']
        lens = map(lambda x: len(x), TravelTimeController.column_name_suffixes)
        
        fs = [CustomJSHover(args=dict(q=self.widgets.quantile_slider), code=code.format(name=name, suffix_len=suffix_len)) for name, suffix_len in zip(names, lens)]
        formatters = {connection + suffix: formatter for connection in self.connection_names for formatter, suffix in zip(fs, TravelTimeController.column_name_suffixes)}
        return HoverTool(tooltips='@$name{custom}', formatters=formatters, mode='mouse')


class TravelTimePlot(Plot):

    def __init__(self, x_range, box_select_tool, hover_tool, reset_callback, connection_colors):
        super(TravelTimePlot, self).__init__(tools='pan,wheel_zoom,box_zoom,reset,save')
        self.plot.x_range = x_range
        self.connection_names = connection_colors.keys()
        self.lines = ColumnDataSource()
        self.initFigure(connection_colors)
        self.setTitle(travel_times_plot_title.format(time=start_time))
        self.setXLabel(travel_times_plot_xaxis.format(time=start_time))
        self.setYLabel(travel_times_plot_yaxis)
        self.plot.add_tools(box_select_tool)
        self.plot.add_tools(hover_tool)
        self.plot.js_on_event(events.Reset, reset_callback)

    def updateLines(self, lines):
        self.lines.data = lines

    def updateSelection(self, indices):
        self.lines.selected.indices = indices

    def updateLegend(self, connections):
        for connection in self.connection_names:
            visible = connection in connections
            for renderer in self.legend_items[connection].renderers:
                renderer.visible = visible
        self.plot.legend.items = [self.legend_items[connection] for connection in connections]

    def initFigure(self, connection_colors):
        self.legend_items = {}
        for (connection, color) in connection_colors.items():
            properties = [(connection + TravelTimeController.column_name_suffixes[0], 2, 'dashed'),
                          (connection + TravelTimeController.column_name_suffixes[1], 3, []),
                          (connection + TravelTimeController.column_name_suffixes[2], 2, 'dashed')]
            renderers = [self.plot.line(x='time', y=column, color=color, source=self.lines, line_width=width, name=column, line_dash=dash) for column, width, dash in properties]
            self.legend_items[connection] = LegendItem(label=connection, renderers=renderers)

        self.plot.add_layout(Legend())        


class TravelTimeWidgets:

    def __init__(self):
        self.quantile_slider = Slider(start=0, end=0.5, step=0.05, value=0.25, title=quantile_selection_name, width=320)
        self.layout = layout([
            self.quantile_slider,
        ], width=350)
