from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, CategoricalColorMapper, DataRange1d, LinearAxis
from bokeh.io import output_notebook
import numpy as np
from pysugar.struct import merge
from functools import partial

from bokeh.palettes import Category20_20, Viridis256
from bokeh.layouts import gridplot
import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from itertools import islice,cycle
from bokeh.transform import factor_cmap, linear_cmap
from bokeh_frame.utils import init_bokeh
from bokeh_frame.functional import *
from bokeh.layouts import column, row, gridplot
from bokeh_frame.column import *
COMPOUND_FIELDS = (
    'x_range',
    'y_range',
    'legend')


class Cartesian:
    def __add__(self, other):
        return Layered(self.children + other.children)

    def __or__(self, other):
        return RowLayout(self.children + other.children)

    def __xor__(self, other):
        return ColumnLayout(self.children + other.children)

    DEFAULT_OPTS = {
            'tools':'pan,wheel_zoom,box_zoom,save,reset', 
            'width':400,
            'height':400,
        }
    def __init__(self):
        self._opts = {}
        self._yaxes = {}

    def init_figure(self):
        opts = self.decorated_opts()
        flat_opts = {}
        non_flat_opts = {}
        for k, v in opts.items():            
            if isinstance(v, dict):
                non_flat_opts[k] = v
            else:
                flat_opts[k] = v
        p = figure(**flat_opts)
        for key, compound in non_flat_opts.items():
            for inner_key, inner_value in compound.items():
                setattr(getattr(p, key), inner_key, inner_value)
        return p

    def decorated_opts(self):
        #TODO OB: not optimal at all:
        # for field in COMPOUND_FIELDS:
        #     for k, v in self._opts.items():
        #         if k == field:
        #             self

        return merge({'legend_position': None}, *[self._opts, self.DEFAULT_OPTS])

    def opts(self, *args, **kwargs):
        self._opts = merge(kwargs, self._opts)
        return self

    @property
    def children(self):
        if isinstance(self, Layered):
            return self._children
        else:
            return [self]

    def calculate_properties(self, properties, fr, x, y):
        source = ColumnDataSource(fr)
        output_props = {}
        tooltip_props = []
        for k, v in properties.items():
            if isinstance(v, AbstractColumn):
                column = v
            elif isinstance(v, tuple):
                if (v[0] == '_index_'):
                    column = IndexColumn()
                else:
                    column = FrameColumn(v[0])
            else:               
                column = LiteralColumn(v)
            column_name = column.column_name
            if column_name is not None:
                tooltip_props.append(column_name)
            column.decorate(fr, source, k, output_props)

        return source, output_props, tooltip_props

    def has_legend(self):
        return 'legend_group' in self._opts

    def display(self):
        init_bokeh()
        fig = self.init_figure()
        axis_labels = self.axis_labels()
        fig.xaxis.axis_label = axis_labels[0]
        fig.yaxis.axis_label = axis_labels[1]
        self.plot(fig)
        tooltips = self.tooltips()
        #print(tooltips)
        fig.add_tools(HoverTool(
            tooltips=list(tooltips.items()),
            mode="mouse", point_policy="snap_to_data",
            line_policy='nearest',
        ))
        if self.has_legend():
            fig.legend.location = self._opts.get('legend_location', None)
        show(fig)
        return fig

    def __repr__(self):
        return repr(self.display())

    def tooltips(self):
        return {}
    def tooltip_formatters(self):
        return {}


class Scatter(Cartesian):
    def __init__(self, x=None, y=None, fr=None, axis_labels=None, tooltip_columns=None, 
        legend_location=None, **kwargs):
        if fr is None:
            self._fr = pd.DataFrame({'X': x, 'Y': y})
            self._x = 'X'
            self._y = 'Y'
        else:            
            self._fr = fr.copy()
            self._x = x
            self._y = y
        self._axis_labels = axis_labels or [self._x, self._y]
        self._source, self._properties, tooltip_extra_columns = self.calculate_properties(kwargs, self._fr, self._x, self._y)
        default_tooltip_columns = [self._x, self._y] + tooltip_extra_columns
        self._tooltip_columns = tooltip_columns or default_tooltip_columns
        self._tooltips = {column:f'@{column}' for column in self._fr.columns}
        self._silence_tooltips = False
        self._legend_location = legend_location
        self._tooltip_formatters = {}
        super().__init__()

    def tooltips(self):
        if self._silence_tooltips:
            return {}
        return {column:f'@{column}' for column in self._tooltip_columns}
    @property
    def tooltip_formatters(self):
        return self._tooltip_formatters
    def axis_labels(self):
        if self._silence_tooltips:
            return None
        return self._axis_labels    
    @property
    def x(self):
        return self._fr[self._x]
    
    @property
    def y(self):
        return self._fr[self._y]

    @property
    def properties(self):
        return self._properties

    def with_identity(self):
        mn = min([np.nanmin(self.x), np.nanmin(self.y)])
        mx = max([np.nanmax(self.x), np.nanmax(self.y)])
        l = Line([mn, mx], [mn, mx], line_color='grey', line_alpha=0.5)
        l.silence_tooltips()
        return self + l
    
    def silence_tooltips(self):
        self._silence_tooltips = True
    
    def datetime(self):
        self._opts['x_axis_type'] = 'datetime'
        self._tooltips[self._x] = f'@{self._x}{{%F}}'
        self._tooltip_formatters = {
            f'@{self._x}': 'datetime',
        }
        return self

class Dots(Scatter):
    def __init__(self, x=None, y=None, fr=None, *args, **kwargs):
        super().__init__(x, y, fr, *args, **kwargs)
    
    def plot(self, fig):
        fig.scatter(source=self._source, x=self._x, y=self._y, **self._properties)

class Line(Scatter):
    def __init__(self, x=None, y=None, fr=None, *args, **kwargs):
        super().__init__(x, y, fr, *args, **kwargs)

    @staticmethod
    def simple(y):
        return Line(np.arange(len(y)), y, None)
    
    def plot(self, fig):
        fig.line(source=self._source, x=self._x, y=self._y, **self._properties)

class VBar(Scatter):
    def __init__(self, x=None, y=None, fr=None, alpha=0.2, fill_color='blue', line_color='black', *args, **kwargs):
        if x is None:
            x = np.arange(len(y))
        super().__init__(x, y, fr, *args, **kwargs)
        self._axis_labels = [self._x, self._y]
        self._silence_tooltips = False
        self._legend_location = 'top left'
        self._alpha = alpha
        self._fill_color = fill_color
        self._line_color = line_color
        if not is_numeric_dtype(self._fr[self._x]):
            self._opts['x_range'] = self._fr[self._x]
            

    def plot(self, fig):
        if is_numeric_dtype(self._fr[self._x]):
            self._source = ColumnDataSource({
                'top': self._fr[self._y][0:-1], 
                'left': self._fr[self._x][0:-1],
                
                'right': self._fr[self._x][1:]})
            fig.quad(top='top', bottom=0, left='left', right='right', source=self._source,
                   fill_color=self._fill_color, line_color=self._line_color, alpha=self._alpha, legend_label='legend')
        else:
            self._source = ColumnDataSource({
                self._y: self._fr[self._y], 
                self._x: self._fr[self._x]})
            fig.vbar(x=self._x, top=self._y, source=self._source, 
                   fill_color=self._fill_color, line_color=self._line_color, alpha=self._alpha, width=0.9, legend_label='legend')

class Hist(Cartesian):
    def __init__(self, v=None, fr=None, bins='auto', qcount=None, weights=None, density=False, axis_labels=None, tooltip_columns=None, 
        legend_location=None, alpha=0.2, fill_color='blue', line_color='black', **kwargs):
        if fr is None:
            self._fr = pd.DataFrame({'V': v})
            self._v = 'V'
        else:            
            self._fr = fr.copy()
            self._v = v
        data = self._fr[self._v]
        self._density=density
        legal = ~np.isinf(data) & ~np.isnan(data)
        clean_data = np.sort(data[legal])
        if weights is not None:
            clean_weights = weights[legal]
        else:
            clean_weights = weights        
        if isinstance(bins, str) and (bins == 'q' or weights is not None):
            if bins != 'q':
                raise Exception('Only auto is a valid bins string when weights are provided')
            if qcount is None:
                raise Exception('qcount must be provided if weights are provided with bins=quantiles')
            if weights is None:
                clean_weights = np.ones(clean_data.shape)
            bins = weighted_quatiles(clean_data, clean_weights, np.arange(0,1+1/qcount,1/qcount))            
            self._density=True
        hist_as_data = np.histogram(clean_data, weights=clean_weights, bins=bins, density=self._density)
        self._np_hist = hist_as_data
        self._axis_labels = axis_labels or [self._v, 'Frequency']
        self._silence_tooltips = False
        self._legend_location = legend_location
        self._alpha = alpha
        self._fill_color = fill_color
        self._line_color = line_color
        super().__init__()

    def decorated_opts(self):
        return merge({'legend_position': None,
                      'x_range_end': None},
             self._opts,
             self.DEFAULT_OPTS)
    def tooltips(self):
        return dict([("left", "@left"), ("right", "@right"), ("top", "@top"), ("count", "@count")])
    def axis_labels(self):
        if self._silence_tooltips:
            return None
        return self._axis_labels    
    @property
    def x(self):
        return self._fr[self._x]
    
    @property
    def y(self):
        return self._fr[self._y]
    
    def plot(self, fig):
        source = ColumnDataSource({
            'top':self._np_hist[0], 
            'left':self._np_hist[1][:-1],
            'right':self._np_hist[1][1:],
            'count': (self._np_hist[1][1:] - self._np_hist[1][:-1])*self._np_hist[0]})
        fig.quad(top='top', bottom=0, left='left', right='right', source=source,
               fill_color=self._fill_color, line_color=self._line_color, alpha=self._alpha, legend_label='legend')
        fig.legend.visible=False 


        fig.legend.location = "center_right"
        fig.legend.background_fill_color = "#fefefe"
        fig.xaxis.axis_label = 'x'
        fig.yaxis.axis_label = 'Pr(x)' if self._density else '#'
        fig.grid.grid_line_color="white"

    def silence_tooltips(self):
        self._silence_tooltips = True

class Layered(Cartesian):
    def __init__(self, children=[], *args, **kwargs):
        self._children = children
        super().__init__(*args, **kwargs)
    
    def plot(self, fig):
        for child in self._children:
            if child.properties.get('y_range_name') is not None:
                name = child.properties['y_range_name']
                side = 'right' if child.properties['y_range_name'].startswith('right') else 'left'
                if fig.extra_y_ranges is None:
                    fig.extra_y_ranges = {}
                fig.extra_y_ranges[name] = DataRange1d()
                fig.add_layout(LinearAxis(y_range_name=child.properties['y_range_name']), side)
            child.plot(fig)

    
    def tooltips(self):
        return merge(*[l.tooltips() for l in self._children])

    def decorated_opts(self):
        children_opts = [l.decorated_opts() for l in self._children]
        return merge({'legend_position': None},
             self._opts,
            *[o for o in children_opts if o is not None],
             self.DEFAULT_OPTS)
    
    def axis_labels(self):
        l = [set(), set()]
        for child in self._children:
            xy = child.axis_labels()
            if xy is None:
                continue
            l[0] = set(map(str, l[0].union({xy[0]})))
            l[1] = set(map(str, l[1].union({xy[1]})))
        return [','.join(l[0]), ','.join(l[1])]


class RowLayout(Cartesian):
    def __init__(self, children=[], *args, **kwargs):
        self._children = children
        self._figures = None
        super().__init__(*args, **kwargs)
    
    def plot(self, fig):
        pass
    
    def display(self):
        init_bokeh()
        fig = self.init_figure()
        self.plot(fig)
        show(fig)
        return fig

    def init_figure(self):
        figure_row = []
        for xy in self._children:
            child_fig = xy.init_figure()
            xy.plot(child_fig)
            figure_row.append(child_fig)
        return row(*figure_row)

    def tooltips(self):
        return merge(*[l.tooltips() for l in self._children])
    def tooltip_formatters(self):
        return merge(*[l.tooltip_formatters() for l in self._children])

    def decorated_opts(self):
        children_opts = [l.decorated_opts() for l in self._children]
        return merge({'legend_position': None},
             self._opts,
            *[o for o in children_opts if o is not None],
             self.DEFAULT_OPTS)

class ColumnLayout(Cartesian):
    def __init__(self, children=[], *args, **kwargs):
        self._children = children
        self._figures = None
        super().__init__(*args, **kwargs)
    
    def plot(self, fig):
        pass
    
    def display(self):
        init_bokeh()
        fig = self.init_figure()
        self.plot(fig)
        show(fig)
        return fig

    def init_figure(self):
        figure_row = []
        for xy in self._children:
            child_fig = xy.init_figure()
            xy.plot(child_fig)
            figure_row.append(child_fig)
        return column(*figure_row)

    def tooltips(self):
        return merge(*[l.tooltips() for l in self._children])

    def decorated_opts(self):
        children_opts = [l.decorated_opts() for l in self._children]
        return merge({'legend_position': None},
             self._opts,
            *[o for o in children_opts if o is not None],
             self.DEFAULT_OPTS)

class Grid(Cartesian):
    def __init__(self, children=[], *args, **kwargs):
        self._children = children
        self._figures = None
        super().__init__(*args, **kwargs)
    
    def plot(self, fig):
        pass
    
    def display(self):
        init_bokeh()
        fig = self.init_figure()
        self.plot(fig)
        show(fig)
        return fig

    def init_figure(self):
        grid_figs = []
        for xy in self._children:
            child_fig = xy.init_figure()
            xy.plot(child_fig)
            grid_figs.append([child_fig])
        return gridplot(grid_figs)

    def tooltips(self):
        return merge(*[l.tooltips() for l in self._children])

    def decorated_opts(self):
        children_opts = [l.decorated_opts() for l in self._children]
        return merge({'legend_position': None},
             self._opts,
            *[o for o in children_opts if o is not None],
             self.DEFAULT_OPTS)
