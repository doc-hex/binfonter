
try:
    from ucollections import namedtuple
except ImportError:
    from collections import namedtuple

GlyphInfo = namedtuple('GlyphInfo', 'x y w h bits')

class FontBase:
    pass

