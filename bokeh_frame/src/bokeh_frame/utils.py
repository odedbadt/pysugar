from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, CategoricalColorMapper
from bokeh.io import output_notebook
import numpy as np
from pysugar.struct import merge
from functools import partial
from bokeh.palettes import Category20_20, Greys256
from bokeh.layouts import gridplot
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from itertools import islice,cycle
from bokeh.transform import factor_cmap, linear_cmap

_initialized = False
def init_bokeh(force=False):
    global _initialized
    if not _initialized or force:
        output_notebook()
    _initialized = True


default_fig_args = {
    'plot_width': 400,
    'plot_height': 400
}


defaults = {
    'scatter': {
        'line_width':0,
        'size': 3,
    }
}

def property_list_to_tooltip(properties):
    return [(k,f'@{k}') for k in properties]

def _chart(type, x, y=None, fig_args={}, chart_args={}):
    init_bokeh()
    p = figure(tools="wheel_zoom,pan,reset")
    f = figure(**merge(fig_args, default_fig_args))
    # add two scatter series
    method = getattr(f,type)
    p = method(x, y, **merge(chart_args, defaults.get(type)))

    show(f)
    return (f, p)
def _xy(method, x, y, label=None, size=None, axis_labels=['X', 'Y'], data_frame=None, fig=None):
    init_bokeh()
    if fig is None:
        f = figure()
    else:
        f = fig
    a = max([np.nanmax(x), np.nanmax(y)])
    #f.line([0, a], [0,a], line_color='grey', line_alpha=0.5)

    tooltips=[(f"({axis_labels[0]},{axis_labels[1]})", "(@x, @y)")]
    source = ColumnDataSource({'x': x,'y': y})
    if data_frame is not None:
        tooltips += property_list_to_tooltip(data_frame.columns)
        for column in data_frame.columns:
            source.add(data_frame[column], column)

    if label is None:
        p = f.scatter(x='x', y='y', source=source)
    else:
        source.add(label, 'label')
        tooltips.append(("label", "@label"))
        if is_numeric_dtype(label):
            mapper = LinearColorMapper(palette=Greys256)

        else:        
            color_mapper = CategoricalColorMapper(factors=list(set(label)),
                    palette=Category20_20)
            p = getattr(f,method)(
                x='x', y='y', source=source,
                color={'field': 'label', 'transform': color_mapper}, alpha=0.5)
    f.xaxis.axis_label = axis_labels[0]
    f.yaxis.axis_label = axis_labels[1]

    f.add_tools(HoverTool(
        tooltips=tooltips,
        mode="mouse", point_policy="follow_mouse"
    ))

    show(f)
def scatter(x, y, *args, **kwargs):
    _xy('scatter', x, y, *args, **kwargs)

def choose_mapper(fr, col):
    if is_numeric_dtype(label):
        mapper = LinearColorMapper(palette=Greys256)

    else:        
        color_mapper = CategoricalColorMapper(factors=list(set(label)),
                palette=Category20_20)

def _frame_to_labels(fr, f):
    if isinstance(f,str):
        return fr[f].astype(str).values
    elif isinstance(f,list):
        labels = None
        for c in f:
            if labels is None:
                labels = fr[c].astype(str)
            else:
                labels = labels.str.cat(fr[c].astype(str), '|')
        return labels.values

# Legacy use charts!
def scatmultiline(fr, x, y, g, lgs=None):
    init_bokeh()
    if lgs is None:
        lg = [g]
    scat_labels = _frame_to_labels(fr, g)
    line_labels = []
    for lg in lgs:
        line_labels.extend(_frame_to_labels(fr, lg))
    all_labels = set(scat_labels).union(line_labels)
    some_labels = list(islice(cycle(all_labels),len(Category20_20)))
    color_of_some_labels = {l: Category20_20[j] for j,l in enumerate(some_labels)}
    label_mapper = {label: some_labels[j % len(some_labels)]
        for j, label in enumerate(all_labels)}



    f = figure()
    f.xaxis.axis_label = x
    f.yaxis.axis_label = y
    a = max([np.nanmax(fr[x].values), np.nanmax(fr[y].values)])
    f.line([0, a], [0,a], line_color='grey', line_alpha=0.5)
    
    if isinstance(g, str) and is_numeric_dtype(fr[g]):
        color_mapper = LinearColorMapper(palette=Greys256)
        scat_source = ColumnDataSource({
            'x': fr[x].values,
            'y': fr[y].values,
            'label': fr[g].values})
    else:
        color_mapper = CategoricalColorMapper(factors=some_labels,
                            palette=Category20_20)
        scat_source = ColumnDataSource({
            'x': fr[x].values,
            'y': fr[y].values,
            'label': [label_mapper[x] for x in _frame_to_labels(fr, g)]})
    for column in fr.columns:
        scat_source.add(fr[column].values.tolist(), column)
    scat = f.scatter(source=scat_source , x='x', y='y', 
              color={'field': 'label', 'transform': color_mapper}, size=7)

    for lg in lgs:
        for k, v in fr.groupby(lg).groups.items():
            line_fr = fr.loc[v,:].sort_values(x)
            label = str(_frame_to_labels(line_fr, lg)[0])
            source = ColumnDataSource({'x': line_fr[x],
                'y': line_fr[y],
                'label': [label_mapper[x] for x in _frame_to_labels(line_fr,lg)]})
            for column in fr.columns:
                source.add(fr.loc[v,column].values.tolist(), column)
            f.line(source=source, x='x', y='y', 
                     line_color=color_of_some_labels[label_mapper[label]],
                     line_width=2)

    tooltips=[("(x,y)", "(@x, @y)"), ("label", "@label")]
    tooltips += property_list_to_tooltip(fr.columns)
    f.add_tools(HoverTool(
        tooltips=tooltips,
        mode="mouse", point_policy="snap_to_data",
        line_policy='nearest'
    ))
    show(f)

# Legacy use charts!
def multiline(fr, x, ys):
    init_bokeh()
    labels = {l: Category20_20[j % 20] for j, l in enumerate(ys)}
    f = figure()
    f.xaxis.axis_label = x
    f.yaxis.axis_label = ys[0]


    
    for y in ys:
        source = ColumnDataSource(fr)
        source.add([y]*len(fr), 'label')
        f.scatter(source=source, x=x, y=y, 
               line_color=labels[y],
               size=3,
               line_width=0)
        f.line(source=source, x=x, y=y, 
               line_color=labels[y],
               line_width=2)

    tooltips=[("(x,y)", "(@x, @y)"), ("label", "@label")]
    tooltips += property_list_to_tooltip(fr.columns)
    f.add_tools(HoverTool(
        tooltips=tooltips,
        mode="mouse", point_policy="snap_to_data",
        line_policy='nearest'
    ))
    show(f)

# Legacy use charts!
def scatline(x, y, *args, **kwargs):
    _xy('scatter', x, y, *args, **kwargs)


# Legacy use charts!
def line(*args, **kwargs):
    if len(args) == 3:
        frame = args[0]
        _xy('line', np.arange(len(y)), y, *args, **kwargs)
        x_field = args[1]
        y_field = args[2]
    elif len(args) == 1:        
        y = args[1]
        x = np.arange(len(x))

def _hist(np_hist, title="Histogram", x=None, pdf=None, cdf=None, quarentiles=False):
    init_bokeh()
    #np_hist = np.histogram(v)
    p = figure(title=title, width=2000, tools='pan,wheel_zoom,box_zoom,save', background_fill_color="#fafafa")
    source = ColumnDataSource({
        'top':np_hist[0], 
        'left':np_hist[1][:-1],
        'right':np_hist[1][1:],
        'count': (np_hist[1][1:] - np_hist[1][:-1])*np_hist[0]})
    p.quad(top='top', bottom=0, left='left', right='right', source=source,
           fill_color="pink", line_color="white", alpha=1, legend_label='legend')
    p.legend.visible=False 

    p.add_tools(HoverTool(
        tooltips=[("left", "@left"), ("right", "@right"), ("top", "@top"), ("count", "@count")],
        mode="mouse", point_policy="follow_mouse"
    ))
    if x:
        p.line(x, pdf, line_color="#ff8888", line_width=4, alpha=0.7, legend_label="PDF")
        p.line(x, cdf, line_color="orange", line_width=2, alpha=0.7, legend_label="CDF")

    p.legend.location = "center_right"
    p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = 'x'
    p.yaxis.axis_label = 'Pr(x)'
    p.grid.grid_line_color="white"
    p.y_range.start = 0    
    show(p)

def nphist(np_hist, title="Histogram", x=None, pdf=None, cdf=None):
    _hist(np_hist, title, x, pdf, cdf)

def hist(data, bins='auto', title="Histogram", x=None, pdf=None, cdf=None):
    _hist(np.histogram(data, bins=bins), title, x, pdf, cdf)

def weighted_quatiles(data, weights, quantiles):
    return data[np.searchsorted(weights.cumsum(), 
        sum(weights)*quantiles)]

def qhist(data, qcount=20, title="Histogram", x=None, pdf=None, cdf=None, weights=None):
    legal = ~np.isinf(data) & ~np.isnan(data)
    clean_data = data[legal]
    if weights is not None:
        clean_weights = weights[legal]
        bins = weighted_quatiles(clean_data, weights, np.arange(0,1+1/qcount,1/qcount))
    else:
        bins = np.quantile(clean_data, np.arange(0,1,1/qcount))
    hist_as_data = np.histogram(clean_data,
        bins=bins,
        density=True)

    _hist(hist_as_data)
    return hist_as_data

def hexbin(x, y, bin_size=10):
    init_bokeh()
    from bokeh.models import HoverTool
    p = figure(tools="wheel_zoom,pan,reset", background_fill_color='#440154')
    p.grid.visible = False

    r, bins = p.hexbin(x, y, size=bin_size, hover_color="pink", hover_alpha=0.8)
    from bokeh.models import Range1d
    range = Range1d(min(min(x), min(y)), max(max(x), max(y)))
    p.x_range = range
    p.y_range = range

    p.scatter(x, y, color="white", size=0.5)


    p.add_tools(HoverTool(
        tooltips=[("count", "@c"), ("(q,r)", "(@q, @r)")],
        mode="mouse", point_policy="follow_mouse", renderers=[r]
    ))
    show(p)

def overtime(t, y):
    init_bokeh()
    p = figure(tools="wheel_zoom,pan,reset,save", x_axis_type='datetime')
    p.line(t, y)
    from bokeh.models import HoverTool
    p.add_tools(HoverTool(mode="mouse", point_policy="follow_mouse"))
    show(p)

def scatter_matrix(dataset):
    init_bokeh()
    dataset_source = ColumnDataSource(data=dataset)
    scatter_plots = []
    y_max = len(dataset.columns)-1
    for i, y_col in enumerate(dataset.columns):
        for j, x_col in enumerate(dataset.columns):
            p = figure(plot_width=100, plot_height=100, x_axis_label=x_col, y_axis_label=y_col)
            p.circle(source=dataset_source,
                x=x_col, 
                y=y_col, 
                fill_alpha=0.9, 
                line_alpha=0.3, 
                size=0.5,
                color='#333333')
            if j > 0:
                p.yaxis.axis_label = ""
                p.yaxis.visible = False
                p.y_range = linked_y_range
            else:
                linked_y_range = p.y_range
                p.plot_width=160
            if i < y_max:
                p.xaxis.axis_label = ""
                p.xaxis.visible = False
            else:
                p.plot_height=140
            if i > 0:
                p.x_range = scatter_plots[j].x_range

            scatter_plots.append(p)
    grid = gridplot(scatter_plots, ncols = len(dataset.columns))
    show(grid)
