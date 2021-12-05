from scripts.preprocessing.FilterSection import FilterController
from scripts.preprocessing.CertaintySection import CertaintyController

from bokeh.layouts import layout

class PreprocessingController:
    def __init__(self, raw_data):
        track_names = {}
        max_track_names = 0
        for (section_name), group in raw_data.groupby(['section_name']):
            names = list(group['track_name'].unique())
            track_names[section_name] = names
            max_track_names = max(max_track_names, len(names))

        self.filter_controller = FilterController(raw_data, track_names, max_track_names)
        certainty_controller = CertaintyController(raw_data, track_names, max_track_names)
        
        certainty_controller.plot.plot.x_range = self.filter_controller.plot.plot.x_range 
        self.layout = layout([
            self.filter_controller.layout,
            certainty_controller.layout
        ])

    def getRoutes(self):
        return self.filter_controller.getRoutes()
    
    def getConnections(self):
        return self.filter_controller.getConnections()