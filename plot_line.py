from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN


def plot_line(prices):

    #prices = '12000 12000 12000 11900 11900 nan 17000 17000 11500 11500 11500'

    y_values = prices.split(' ')
    x_values = range(len(y_values))

    p = figure(plot_width=400, plot_height=400)
    nan = float('nan')
    p.step(x_values, y_values, line_width=3, mode='center')
    p.title.text_font_size = '16px'
    p.title.text = 'Изменение цены'
    p.title.text_font = 'times'
    p.title.text_font_style = 'italic'
    p.toolbar.logo = None
    p.toolbar_location = None
    script, div = components(p)
    cdn_js = CDN.js_files[0]
    return script, div, cdn_js