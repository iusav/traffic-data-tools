from bokeh.plotting import figure


def createLogo():
    logo = figure(plot_width=350, plot_height=100, x_range=(0, 350), y_range=(0, 100))
    logo.image_url(url=['license_tags/static/logo.png'], x=5, y=0, w=200, h=100, anchor="bottom_left")
    logo.toolbar.logo = None
    logo.toolbar_location = None
    logo.xaxis.visible = None
    logo.toolbar.active_drag = None
    logo.yaxis.visible = None
    logo.xgrid.grid_line_color = None
    logo.ygrid.grid_line_color = None
    logo.outline_line_alpha = 0
    return logo
