#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import io, os, sys

# Decoder:
#   timR08 = Times R=regular 08=8 points, which depends on dpi
#   helvR08 = Helvetica R=regular 
#   helvR08 = Helvetica R=regular 
#
#
#    ucs/100dpi/courR08.bdf
#    ucs/100dpi/helvR08.bdf
#    ucs/100dpi/lubR08.bdf
#    ucs/100dpi/ncenR08.bdf
#    ucs/100dpi/timR08.bdf
#    ucs/unnec_100dpi/UTB___10.bdf
#    assets/8x13.bdf     <-- nice, but big
#
#def doit(fn = 'assets/6x10.bdf', screen_size=(128, 32)):
def doit(fn = 'assets/zevv-peep-iso8859-15-10x20.bdf', screen_size=(128, 64)):

    # lifted from pilfont.py helper script
    from PIL import BdfFontFile
    p = BdfFontFile.BdfFontFile(open(fn, 'rb'))

    # interface of PIL font stuff is dumb; no way to avoid a filesystem file here!
    # XXX also not unicode ready!
    p.save("tmp-font.pil")
    font = ImageFont.load('tmp-font.pil')

    tmp = Image.new('L', screen_size, 255)
    dd = ImageDraw.Draw(tmp)
    w, line_h = font.getsize('Wjp')

    y = 0
    for msg in [ 
        "12.business",
        "13.abstract",
        " 13. english",
        '/'.join(fn.split('/')[-2:]),
    ]:
        dd.text( (1,y), msg, font=font, fill=0)
        y += line_h

    tmp = tmp.convert('1')
    tmp.save('example.png')
    print("Wrote:  example.png")
    #tmp.show()

def doit_TTF(fn = 'something.ttf', sz=18):
    font = ImageFont.truetype(font = fn, size=sz)

    tmp = Image.new('L', (128, 128), 255)
    dd = ImageDraw.Draw(tmp)
    w, line_h = font.getsize('Wjp')

    y = 0
    for msg in [ 
        "Test: size=%d" % sz,
        fn,
        "15dmx8pJZhFBNsZhDune6WKJpS7daePn1w",
        "  - split - ",
        "15dmx8pJZhFBNsZh~",
            "~Dune6WKJpS7daePn1w",
    ]:
        dd.text( (0,y), msg, font=font, fill=0)
        y += line_h

    tmp = tmp.convert('1')
    tmp.show()

if __name__ == '__main__':
    doit(sys.argv[1])       # need BDF on cmd line
