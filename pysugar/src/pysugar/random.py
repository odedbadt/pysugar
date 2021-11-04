import numpy as np
import pandas as pd

def random_int_frame(rows, cols, mx=100):
    return pd.DataFrame(np.random.randint(mx, size=(rows, cols)), columns=[chr(ord('A') + j) for j in range(cols)])


def random_normal_frame(rows, cols, scale=1, precision=2):
    log_scale = pow(10, precision)
    return pd.DataFrame(np.floor(np.random.randn(rows, cols)*scale*log_scale)/log_scale, columns=[chr(ord('A') + j) for j in range(cols)])