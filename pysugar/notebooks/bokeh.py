# ---
# jupyter:
#   jupytext:
#     formats: py,ipynb
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.7.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from bokeh.io import output_notebook
output_notebook()

from pysugar.struct import AttributeDict

# +
bokeh_idx = AttributDict(
    
)        

# +
from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook
output_notebook()
# prepare some data
x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]

# output to static HTML file

# create a new plot with a title and axis labels
p = figure(title="simple line example", x_axis_label='x', y_axis_label='y')

# add a line renderer with legend and line thickness
p.line(x, y, line_cap='round', line_width=10)
show(p)
# -

show(p)


