# NOTE: {xyz} are placeholders - do not change their names

tab_title = 'TrafficDataTools [license tags]'

#########
# times #
#########
start_time = 'departure'
end_time = 'arrival'

preprocessing_tab_title = 'Preprocessing'
analysis_tab_title = 'Analysis'

default_track_name = 'Track 1'

#########
# PLOTS #
#########

#######################
# preprocessing plots #
#######################
travel_time_plot_title = 'Travel time over {time} time ({connection})'
travel_time_plot_xaxis = '{time} time'
travel_time_plot_yaxis = 'travel time [min]'
travel_time_plot_legend_inlier = 'inlier'
travel_time_plot_legend_outlier = 'outlier'
travel_time_plot_legend_quantile = 'travel time (q={quantile})'
travel_time_plot_legend_median = 'travel time (median)'

certainty_plot_title = 'License tag certainties over time'
certainty_plot_xaxis = 'time'
certainty_plot_yaxis = 'certainty in %'
certainty_plot_legend_point = 'data point'
certainty_plot_legend_median = 'certainty (median)'

##################
# analysis plots #
##################
travel_times_plot_title = 'Travel times over {time} time'
travel_times_plot_xaxis = '{time} time'
travel_times_plot_yaxis = 'travel time [min]'

travel_distribution_plot_title = 'Travel distribution over {time} time'
travel_distribution_plot_xaxis = '{time} time'
travel_distribution_plot_yaxis_absolute = 'Number of trips'
travel_distribution_plot_yaxis_relative = 'Relative trip distribution (in %)'

###########
# WIDGETS #
###########

group_window_selection_name = 'Group by N minutes'
quantile_selection_name = 'Quantiles'
axes_reset_name = 'Reset axes'
auto_axes_reset_name = 'Auto reset axes'
download_name = 'Download .csv'

#########################
# preprocessing widgets #
#########################
connection_selection_name = 'Select Route'
connection_selection_entry = '{start} - {end}'

download_raw_data_name = 'Raw Data'
download_filtered_routes_name = 'Filtered Routes'
download_all_routes_name = 'All Routes'

outlier_filter_method_selection_name = 'Outlier filtering method'
outlier_filter_method_iqr = 'median + interquartile range'
outlier_filter_method_std = 'mean + standard deviation'
outlier_filter_method_mad = 'median + median absolute deviation'
outlier_filter_window_selection_name = 'Filter window [min]'
outlier_filter_factor_selection_name = 'Outlier factor'

####################
# analysis widgets #
####################
analysis_export_selection_start = 'Export start time'
analysis_export_selection_end = 'Export end time'
analysis_axis_selection_start = 'Axis start time'
analysis_axis_selection_end = 'Axis end time'

travel_distribution_mode_selection_names = 'Diagram mode'
travel_distribution_mode_absolute = 'Absolute'
travel_distribution_mode_section_relative = 'Section relative'
travel_distribution_mode_relative_percent = '100%'

connection_selection_method_names = 'Connection selection mode'
connection_selection_method_start = 'Start sections'
connection_selection_method_end = 'End sections'
connection_selection_method_connection = 'Routes'

start_based_option_name = 'Start based'
end_based_option_name = 'End based'

download_selected_lines_name = 'Selected Lines'
download_selected_bars_name = 'Selected Bars'
download_selected_lines_and_bars_name = 'Selected Lines + Bars'