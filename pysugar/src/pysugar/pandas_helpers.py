def flatten_columns(fr):
    def flatten(col):
        if isinstance(col, tuple):
            return '_'.join(map(str, col)).rstrip('_')
        else: 
            return str(col)
    ofr = fr.copy()
    ofr.columns = [flatten(col) for col in fr.columns.values]
    return ofr

def value_list(fr, limit=None):
    if limit is None:
        limit = len(fr) / 100
    def column_summary(c):
        description = ', '.join([f'{k}: {v}' for k, v in fr[c].describe().to_dict().items()])

        vals = fr[c].drop_duplicates().sort_values().values
        if len(vals) < limit:
            return f"{', '.join(map(str, vals) )} {len(vals)}\n{description}"


        return f'Type: {fr[c].dtype}, unique: {len(vals)}\n{description}'
    print('\n\n\n'.join([f'{c}:\n{"="*len(c)}=\n{column_summary(c)}' for c in fr.columns]))