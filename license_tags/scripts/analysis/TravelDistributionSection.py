from scripts.util.Tracks import *
from scripts.util.Statistics import *
from scripts.Plot import Plot
from scripts.Strings import *

from bokeh import events
from bokeh.models import Select, ColumnDataSource, Legend, LegendItem, HoverTool, BoxSelectTool, ResetTool
from bokeh.layouts import row, layout, column
from bokeh.transform import stack


class TravelDistributionController:
    
    def __init__(self, raw_data, connections, connection_colors, x_range, box_select_tool, reset_callback):
        self.diagram_mode_names = [travel_distribution_mode_absolute, travel_distribution_mode_section_relative, travel_distribution_mode_relative_percent]
        self.diagram_modes = {travel_distribution_mode_absolute: AbsoluteMode(),
                              travel_distribution_mode_section_relative: RelativeMode(raw_data, connections),
                              travel_distribution_mode_relative_percent: PercentMode()}
        self.widgets = TravelDistributionWidgets(self.diagram_modes.keys())
        
        self.connection_names = connections.keys()
        self.plot = TravelDistributionPlot(x_range, box_select_tool, reset_callback, connection_colors)
        self.createListeners()        
        self.times = (start_time, end_time)
        
        self.data = {mode : ColumnDataSource() for mode in self.diagram_mode_names}

    def setData(self, connection_groups, time_slices, base):
        time = self.times[base]

        self.connection_groups = connection_groups
        self.time_slices = time_slices
        self.base = base

        self.plot.setTitle(travel_distribution_plot_title.format(time=time))
        self.plot.setXLabel(travel_distribution_plot_xaxis.format(time=time))
        self.plot.updateLegend(connection_groups.keys())
        self.updateBars(False)
        
        for mode in self.data.keys():
            diagram_mode = self.diagram_modes[mode]
            diagram_mode.precalculate(self.connection_groups, self.time_slices, self.base)
            self.data[mode].data = self.calculateBarsDict(diagram_mode)

    def setSelection(self, selected_indices):
        self.plot.updateSelection(selected_indices)
        
    def resetZoom(self):
        self.plot.resetAxes()

    def getData(self):
        return self.data  

    def getModeNames(self):
        return self.diagram_mode_names

    def updateBars(self, updateYAxis):
        diagram_mode = self.diagram_modes[self.widgets.diagram_mode_select.value]
        diagram_mode.precalculate(self.connection_groups, self.time_slices, self.base)

        self.plot.setYLabel(diagram_mode.plotTitle())
        self.plot.updateHover(diagram_mode.format())
        self.plot.setXResetAxisRange(self.time_slices[0].astype(long) / 1000,
                                     self.time_slices[-1].astype(long) / 1000)
        self.plot.setYResetAxisRange(0, diagram_mode.maxY())
        
        self.plot.updateBarWidths(self.time_slices[1] - self.time_slices[0])
        self.plot.updateBarValues(self.calculateBarsDict(diagram_mode))
        if updateYAxis:
            self.plot.setYAxisRange(0, diagram_mode.maxY())

    def calculateBarsDict(self, diagram_mode):
        active_connections = self.connection_groups.keys()
        time_points = self.time_slices[:-1] + (self.time_slices[1] - self.time_slices[0]) / 2
        emptyCol = [0] * len(time_points)
        bars = {connection : diagram_mode.map(self.connection_groups[connection].count()['duration']) if connection in active_connections else emptyCol 
                for connection in self.connection_names}
        bars['time'] = time_points
        return bars;

    def createListeners(self):
        self.widgets.diagram_mode_select.on_change('value', lambda attr, old, new: self.updateBars(True))

        
class TravelDistributionPlot(Plot):

    def __init__(self, x_range, box_select_tool, reset_callback, connection_colors):
        super(TravelDistributionPlot, self).__init__(tools='pan,wheel_zoom,box_zoom,reset,save')
        self.plot.x_range = x_range
        self.connection_names = connection_colors.keys()
        self.bars = ColumnDataSource()
        self.initFigure(connection_colors)

        self.bar_width = 0.8
        
        self.setTitle(travel_distribution_plot_title.format(time=start_time))
        self.setXLabel(travel_distribution_plot_xaxis.format(time=start_time))
        self.setYLabel(travel_distribution_plot_yaxis_absolute)
        self.plot.add_tools(box_select_tool)
        self.plot.js_on_event(events.Reset, reset_callback)

    def updateLegend(self, connections):
        for connection in self.connection_names:
            self.legend_items[connection].renderers[0].visible = connection in connections
        self.plot.legend.items = [self.legend_items[connection] for connection in connections]

    def updateHover(self, format):
        self.hoverTool.tooltips = '$name: @$name' + format

    def updateBarValues(self, bars):
        self.bars.data = bars
            
    def updateBarWidths(self, window):
        width = 0.8 * window / np.timedelta64(1, 'ms')
        for vbar in self.vbars:
            vbar.glyph.width = width

    def updateSelection(self, indices):
        self.bars.selected.indices = indices

    def initFigure(self, connection_colors):
        bottom_fields = []
        top_fields = []
        self.legend_items = {}

        self.vbars = []
        for connection, color in reversed(connection_colors.items()):
            top_fields.append(connection)
            vbar = self.plot.vbar(bottom=stack(*bottom_fields), top=stack(*top_fields), x='time', width=0.8, source=self.bars, color=color, name=connection)
            self.legend_items[connection] = LegendItem(label=connection, renderers=[vbar])
            bottom_fields.append(connection)
            self.vbars.append(vbar)
        self.plot.add_layout(Legend())

        self.hoverTool = HoverTool(mode='vline')
        self.plot.add_tools(self.hoverTool)


class TravelDistributionWidgets:

    def __init__(self, diagram_method_names):
        self.diagram_mode_select = Select(title=travel_distribution_mode_selection_names, options=diagram_method_names, value=travel_distribution_mode_absolute, width=330)
        
        self.layout = layout([
            self.diagram_mode_select,
        ], width=350)


class AbsoluteMode:

    def precalculate(self, connection_groups, time_slices, base):
        counts = [0] * (len(time_slices) - 1)
        for group in connection_groups.values():
            counts = counts + group.count()['duration']
        self.max_value = max(counts)

    def map(self, values):
        return values
    
    def maxY(self):
        return self.max_value
        
    def plotTitle(self):
        return travel_distribution_plot_yaxis_absolute

    def format(self):
        return ''


class RelativeMode:

    def __init__(self, raw_data, connections={}):
        self.raw_data = raw_data
        self.connections = connections

    def precalculate(self, connection_groups, time_slices, base):
        active_sections = set(self.connections[connection][base] for connection in connection_groups.keys())
        filtered = self.raw_data[self.raw_data['section_name'].isin(active_sections)]
        group = groupBy(filtered, time_slices, by='time')
        self.total = group.count()['car']

    def map(self, values):
        return 100. * values / self.total

    def maxY(self):
        return 100

    def plotTitle(self):
        return travel_distribution_plot_yaxis_relative

    def format(self):
        return '{0.0}%'


class PercentMode:

    def precalculate(self, connection_groups, time_slices, base):
        self.counts = [0] * (len(time_slices) - 1)
        for group in connection_groups.values():
            self.counts = self.counts + group.count()['duration']

    def map(self, values):
        return 100. * values / self.counts
    
    def maxY(self):
        return 100
    
    def plotTitle(self):
        return travel_distribution_plot_yaxis_relative
    
    def format(self):
        return '{0.0}%'
