class XYColumn():
    def __init__(self, name, wrapped):
        self._name = _name
        self._wrapped = wrapped


class AbstractColumn():

    def values(self, fr):        
        raiception('Unimplemented Error')
    def decorate(self, fr, source, prop_name, properties):
        raise Exception('Unimplemented Error')

     
class LiteralColumn(AbstractColumn):

    def __init__(self, value):
        self._value = value
    
    @property
    def column_name(self):
        return None
    
    def values(self, fr):        
        raise Exception('Unimplemented Error')

    def decorate(self, fr, source, prop_name, properties):
        properties[prop_name] = self._value


class FrameColumn(AbstractColumn):
    
    def __init__(self, name, wrapped=None):
        self._name = name
        self._wrapped = wrapped
    
    @property
    def column_name(self):
        return self._name
    
    def values(self, fr):        
        if self._wrapped:
            return self._wrapped.values(fr)
        else:
            return fr[self._name]
    def decorate(self, fr, source, prop_name, properties):
        properties[prop_name] = self._name
        source.add(self.values(fr), self._name)


class SeriesColumn(FrameColumn):

    def __init__(self, values):
        self._values = values
    
    @property
    def column_name(self):
        return None
    
    def values(self, fr):        
        return self._values

class NumericColumn(FrameColumn):
    def __init__(self, name, wrapped=None, palette=None):
        self._palette = palette or Viridis256
        super().__init__(name, wrapped)
    def decorate(self, fr, source, prop_name, properties):
        super().decorate(fr, source, prop_name, properties)
        if prop_name == 'color':
            V = self.values(fr)
            source.add(V, self._name)
            MN = V.min()
            MX = V.max()
            properties['color'] = linear_cmap(self._name, self._palette, MN, MX)

class CategoryColumn(FrameColumn):
    def __init__(self, name, wrapped=None, palette=None):
        self._palette = palette or Category20_20
        super().__init__(name, wrapped)
    def decorate(self, fr, source, prop_name, properties):
        #super().decorate(fr, source, prop_name, properties)
        if prop_name == 'color':
            V = self.values(fr).astype(str)
            UV = np.unique(V)

            L = len(UV)
            LL = len(self._palette)
            P = list(self._palette) * (int(L/LL)+1)
            properties['legend_group'] = self._name
            properties['color'] = factor_cmap(self._name, self._palette, UV)
            if self._name in source.data:
                # Hack to create "strings" in a numpy array: convert to str then to object
                source.data[self._name] = source.data[self._name].astype(str).astype(object)
            else:
                source.data[self._name] = list(map(str,V))

class CalculatedColumn(FrameColumn):
    def __init__(self, f, name=None, wrapped=None, row_based=False):
        self._f = f
        self._row_based = row_based
        super().__init__(name, wrapped)

    def values(self, fr): 
        if self._row_based:
            return fr.apply(self._f, axis=1)
        else:
            return fr[self._name].apply(self._f)

class IndexColumn(FrameColumn):
    def __init__(self):
        super().__init__(None, None)
    def values(self, fr):        
        return fr.index
