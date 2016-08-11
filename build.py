#!/usr/bin/env python3
#
# Read BDF files and produce useful data objects that allow us to
# draw a few limited fonts nicely.
#
# Not using PIL/Pillow for this because their BDF support is not Unicode clean.
#
import os, sys
from pdb import pm
from array import array
from bdflib import reader, glyph_combining
from binascii import b2a_hex, b2a_base64

font_files = {
    'fixed': 'assets/6x10.bdf',
    'normal': 'assets/helvR08.bdf',
    'bold': 'assets/helvB08.bdf',
    'title': 'assets/helvB10.bdf'
}

# Based on http://code.activestate.com/recipes/496682
def list2range(lst):
    '''make iterator of ranges of contiguous numbers from a list of integers'''

    members = sorted(lst)
    start = members[0]
    currentrange = range(start, start + 1)

    for item in members[1:]:
        if currentrange.stop == item:
            # contiguous
            currentrange = range(currentrange.start, currentrange.stop + 1)
        else:
            # new range start
            yield currentrange
            currentrange = range(item, item + 1)

    # last range
    yield currentrange

def allow_gaps(ranges):
    """
        Merge ranges provided by an iterator so that smaller ranges are
          grouped together a bit
    """
    min_rng = 16
    while 1:
        try:
            a = ranges.__next__()
        except StopIteration:
            return

        if len(a) > min_rng:
            yield a
            continue
        
        try:
            b = ranges.__next__()
        except StopIteration:
            yield a
            return
            
        if (b.stop - a.start) < min_rng:
            yield range(a.start, b.stop)
        else:
            yield a
            yield b


def wrapped_byte_literal(bits):
    # output lines that can work inside a b' ... '
    
    w = 20
    for i in range(0, len(bits), w):
        h = bits[i:i+w]
        yield ''.join('\\x%02x' % i for i in h) + '\\'


class Mangler:
    def __init__(self, fn = 'ucs/100dpi/helvB08.bdf', limited_range=None):
        self.filename = fn

        font = reader.read_bdf(open(fn).__iter__())

        print("For font: %s" % fn)
        if limited_range:
            print("  Restricted to: %d chars" % len(limited_range))
        print("  Number of codepoints: %d" % len(font.codepoints()))

        decompositions = glyph_combining.build_unicode_decompositions()
        filler = glyph_combining.FontFiller(font, decompositions)
        filler.add_decomposable_glyphs_to_font()

        print("  Number of codepoints, after comopsitions: %d" % len(font.codepoints()))

        too_wide, too_tall = set(), set()
        all_bb = set()
        data = {}

        for cp in font.codepoints():
            if limited_range and cp not in limited_range: continue

            gy = font[cp]
            x,y,w,h = gy.get_bounding_box()
            bits = gy.get_data()
            if w > 16:
                too_wide.add(cp)
                continue
            if h > 32:
                too_tall.add(cp)
                continue

            # trim trailing zeros
            while bits and bits[-1] == '00':
                bits = bits[:-1]

            all_bb.add( (x,y,w,h, len(bits)) )
            data[cp] = (x,y,w,h, bits)

        print('  %s are too wide: %s' % (len(too_wide),
                                                ' '.join(chr(i) for i in sorted(too_wide))))
        if too_tall:
            print('  %s are too tall: %s' % (len(too_tall),
                                                ' '.join(chr(i) for i in sorted(too_tall))))

        print("  %d different shapes" % len(all_bb))
        assert len(all_bb) < 254, "Too many unique sizes/shapes!"

        self.font = font
        self.data = data
        self.all_bb = list(sorted(all_bb))
        self.omit = set.union(too_wide, too_tall)

    def encode(self, fd, prefix, is_python=1):
        #  output 3 arrays:
        # - map of tightly encoded set of possible BBox and data lengths
        # - map codepoint => raw data
        # - raw data, packed, of one byte header (ptr into BBox data) and bitmap bytes
        font = self.font
        bboxes = [None] + self.all_bb

        max_cp = max(self.font.codepoints())
        codept_map = {}
        bitmaps = bytearray([0xAA])       # first value not usable
        
        for cp in range(max_cp):

            x, y = (cp >> 8), (cp & 0xff)
            if cp in self.omit or cp not in self.data:
                # char is undefined / or omitted
                #codept_map.append(0)
                pass
            else:
                x,y,w,h,d = self.data[cp]
                idx = bboxes.index( (x,y,w,h,len(d)) )
                assert idx >= 1
                codept_map[cp] = len(bitmaps)
                bitmaps.append(idx)
                bitmaps += bytes.fromhex(''.join(d))

        assert len(bitmaps) < 65534, "Font too big"
        print("  %d bytes for bitmaps data" % len(bitmaps))

        if is_python:
            rv = []
            rv.append('# Auto-generated. Dont edit')
            rv.append('# PREFIX = %s' % prefix)
            rv.append('')
            rv.append('class info:')
            rv.append('    max_code_point = %d' % max_cp)
            rv.append('')
            rv.append('bboxes = %r' % bboxes)
            rv.append('')
            rv.append('code_points = [\\')
            for rng in allow_gaps(list2range(codept_map.keys())):
                rv.append('(range(%d, %d), [%s]), ' % (rng.start, rng.stop,
                        ', '.join(str(codept_map.get(i, 0)) for i in rng)))
            rv.append(']')
            rv.append('')

            out = wrap_big_lines(rv)

            out.append('bitmaps = b"""\\')
            out.extend(wrapped_byte_literal(bitmaps))
            out.append('"""')

            out.append("""
try:
    from collections import namedtuple
    GlyphInfo = namedtuple('GlyphInfo', 'x y w h bits')
except ImportError:
    # micropython limitation
    GlyphInfo = tuple

def lookup_glyph(cp):
    for r,d in code_points:
        if cp not in r: continue
        ptr = d[cp-r.start]
        if not ptr: return None

        x,y, w,h, dlen = bboxes[bitmaps[ptr]]
        bits = bitmaps[ptr+1:ptr+1+dlen]

        return GlyphInfo(x,y, w,h, bits)

    return None
""")

        if not is_python:
            # output C Code
            from string import Template
            tmpl = Template(open('template.h').read())

            c_boxes = '\n\t'.join('{ %d,%d, %d,%d, %d },' % j for j in bboxes if j)[:-1]

            rv = []

            for rng in allow_gaps(list2range(codept_map.keys())):
                if len(rng) <= 4:       # NOTE: value tuned for "arm-none-eabi-gcc"
                    for i in rng:
                        if i in codept_map:
                            rv.append('case 0x%x: offset=%d; break;' % (i, codept_map[i]))
                else:
                    rv.append('case 0x%x ... 0x%x: {' % (rng.start, rng.stop-1))
                    rv.append('  static const uint16_t here[%d] = {%s};' % (
                                    len(rng),
                                    ', '.join(str(codept_map.get(i, 0)) for i in rng)))
                    rv.append('  offset = here[cp-0x%x]; break; }' % rng.start)

            c_ranges = '\n\t\t'.join(wrap_big_lines(rv))

            c_bits = '\n\t'.join(wrap_big_lines([', '.join(str(i) for i in bitmaps)]))

            out = []
            out.append(tmpl.substitute(BOXES=c_boxes, RANGES=c_ranges, BITS=c_bits, PREFIX=prefix))

    
        print('\n'.join(out), file=fd)

def wrap_big_lines(lines):
    from textwrap import fill
    out = []
    [out.extend(fill(i, subsequent_indent='  ', initial_indent='').split('\n'))
                            for i in lines]
    return out

def test_generated_code(quick=0):
    # This is a exhausitive test, which compares the output from the python
    # generated code with the same data from the C code. Uses ctypes, and needs
    # a working GCC in the path.
    #
    # run with:
    #       python3 -m pytest ./build.py
    #
    import os, ctypes

    if not os.path.isdir('tmp'):
        os.mkdir('tmp')

    # Generate files, C and Python
    if not quick:
        for name, fn in font_files.items():
            m = Mangler(fn)
            m.encode(open('tmp/%s.py' % name, 'w'), 'unused', is_python=1)
            m.encode(open('tmp/fonts.c', 'w'), 'test', is_python=0)
            r = os.system(
                "(cd tmp; gcc -c -D INCL_C_SOURCE fonts.c; gcc -shared -o c_%s.so fonts.o)" % name)
            assert not r

    # Compare them both

    sys.path.insert(0, 'tmp')

    from ctypes import c_ubyte, c_void_p, c_byte, byref, POINTER
    class bboxInfo_t(ctypes.Structure):
        _fields_ = [ 
                ("x", c_byte), ("y", c_byte), 
                ("w", c_byte), ("h", c_byte), 
                ("dlen", c_ubyte), ("bits", POINTER(c_ubyte * 32)) ]

    for name in font_files:
        clib = ctypes.cdll.LoadLibrary('tmp/c_%s.so' % name)
        assert clib
        py = __import__('%s' % name)

        for cp in range(py.info.max_code_point):
            a = py.lookup_glyph(cp)

            bbox = bboxInfo_t()
            rv = clib.test_lookup_glyph(cp, byref(bbox))

            assert (a == None) == (rv == 1)
            if a:
                assert (bbox.x, bbox.y, bbox.w, bbox.h) == a[0:4]
                assert bbox.dlen == len(a[-1])
                assert bytes(bbox.bits.contents[0:bbox.dlen]) == a[-1]
        

if __name__ == '__main__':
    if 0:
        test_generated_code()

    if 0:
        m = Mangler()
        m.encode(open('tmp/fonts.py', 'w'), 'test', is_python=1)
        m.encode(open('tmp/fonts.c', 'w'), 'test', is_python=0)

    if 1:
        for name in font_files:
            m = Mangler(font_files[name])
            m.encode(open('gen/font_%s.py' % name, 'w'), name, is_python=1)
            m.encode(open('gen/font_%s.h' % name, 'w'), name, is_python=0)

    if 0:
        # for deeper-embedded C code.
        name = 'fixed'
        m = Mangler(font_files[name], limited_range=range(0, 256))
        m.encode(open('gen/font_arm_%s.h' % name, 'w'), name, is_python=0)
