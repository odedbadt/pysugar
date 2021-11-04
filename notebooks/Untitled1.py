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

# +
from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook
output_notebook()
# prepare some data
import numpy as np
x = np.arange(0, 17, 0.3)
y = np.cos(x)
# create a new plot with a title and axis labels
p = figure(title="simple line example", x_axis_label='x', y_axis_label='y')

# add a line renderer with legend and line thickness
p.line(x, y, line_cap='round', line_join='round', line_width=1)
p.scatter(x, y, line_cap='round', line_join='round', line_width=2)
show(p)
show(p)
# -


