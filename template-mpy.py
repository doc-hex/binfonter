from ucollections import namedtuple

GlyphInfo = namedtuple('GlyphInfo', 'x y w h bits')

class FontBase:

    @classmethod
    def lookup(cls, cp):
        # lookup glyph data for a single codepoint, or return None
        for r,d in cls._code_points:
            if cp not in r: continue
            ptr = d[cp-r.start]
            if not ptr: return None
            
            x,y, w,h, dlen = cls._bboxes[cls._bitmaps[ptr]]
            bits = cls._bitmaps[ptr+1:ptr+1+dlen]
            
            return GlyphInfo(x,y, w,h, bits)
            
        return None

