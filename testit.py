#!/usr/bin/env python3
#
# Draw image from our font data using Pillow.
#
import os, sys, click
from pdb import pm, set_trace
from PIL import Image
import importlib.machinery


@click.command()
@click.option('--py-code', default='gen/fonts.py', help='Python source to test')
@click.option('--msg', default='Hello, world.', help='Message to show, can include \\n etc')
@click.option('--width', '-w', default=128, help='Screen size: width')
@click.option('--height', '-h', default=64, help='Screen size: height')
@click.option('--font-name', '-f', default='small', help='Name of specific font to demo')
def doit(msg, py_code, width, height, font_name):

    out = Image.new('1', (width, height))

    mod = importlib.machinery.SourceFileLoader('mod', py_code).load_module()
    py = getattr(mod, 'Font'+font_name.title())

    #msg = msg.replace(r'\n', '\n')
    msg = eval('"' + msg + '"')     # risky python un-escape

    x,y = 0,0
    for m in msg:
        if m == '\n':
            x = 0
            y += py.height
            continue

        gl = py.lookup(ord(m))
        if not gl:
            raise ValueError("Character (%d=%c) is not in font" % (ord(m), m))

        assert gl.w

        # for "rotated" case, the height==number of words to be used==scan lines
        rw = ((gl.w+7)//8)          # number of bytes per row
        cw = rw * 8                 # pixels per row
        ch = len(gl.bits) // rw     # number of scan lines
        
        if cw and ch:
            img = Image.frombytes('1', (cw, ch), gl.bits, decoder_name='raw')

            #img.show()
            #img = img.transpose(Image.FLIP_LEFT_RIGHT)
            #img = img.transpose(Image.FLIP_TOP_BOTTOM)

            # NOTE: real code doesn't use gl.x or gl.y!

            out.paste(img, box=(x,y))
        x += gl.w

    #out = out.rotate(90, expand=1)
    out.show()

if __name__ == '__main__':
    doit()
