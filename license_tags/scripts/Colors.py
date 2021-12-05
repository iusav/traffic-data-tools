import string
from bokeh.colors import HSL, RGB
from bokeh.colors.color import Color

green = '#009682'
blue = '#4664aa'
black = '#000000'

yellow = '#FCE500'
orange = '#DF9B1B'
maygreen = '#8CB63C'
red = '#A22223'
purple = '#A3107C'
brown = '#A7822E'
cyan = '#23A1E0'


def desaturate(color, steps):
    # tuple = make_color_tuple(color)
    hsl = RGB(int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)).to_hsl()
    return [HSL(hsl.h, hsl.s * (float(i) / max(steps - 1, 1)), hsl.l).to_rgb().to_hex() for i in range(steps)]
