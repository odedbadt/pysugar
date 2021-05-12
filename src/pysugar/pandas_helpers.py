def flatten_colums(fr):
    def flatten(col):
        if isinstance(col, str):
            return col
        if isinstance(col, tuple):
            return '_'.join(col).rstrip('_')
    ofr = fr.copy()
    ofr.columns = [flatten(col) for col in fr.columns.values]
    return ofr
