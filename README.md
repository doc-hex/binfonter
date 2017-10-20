
# What Is This?

Seems like every embedded project needs a pretty font.

I wanted to use the fine fixed fonts from the X11 days. 

This library can collect the data needed from BDF font files,
and makes a very compact representation of those fonts which
can be compiled into other programs.

It also support micropython (or python3) to acheive the same goals.

# Font Files

We are using the X11 free fonts stuff, updated for Unicode:
<http://www.cl.cam.ac.uk/~mgk25/ucs-fonts.html>

The useful ones (ie. not Asian) have been copied into this project
so they don't disappear on us.

- `ucs-fonts-75dpi100dpi.tar.gz`
- `ucs-fonts-fixed.tar.gz`

# Usage

- Copy the BDF fonts you want into `./assets`.
- Experiment with `tryout.py` until you are happy with your choices.
- Pick the winner and adjust `build.py` so it makes it in `./gen` subdirectory.

# Size Limitations

- max width: 16 pixels
- max height: 32 pixels
- glyphs that are too big are removed, and shown in a list
- in most fonts, that is less useful stuff, like: Ǆ ǅ Ǌ Ǳ ǲ ⁇ ₨ ℀ ℁ ℅ ℆ № ℡ ℻ Ⅶ Ⅷ ⅷ ⑴ ⑵ ⑶ ⑷ ⑸ ⑹ ⑺ ⑻ ⑼ ⑽ ⑾ ⑿ ⒀ ⒁ ⒂ ⒃ ⒄ ⒅ ⒆ ⒇ ⒑ ⒒ ⒓ ⒔ ⒕ ⒖ ⒗ ⒘ ⒙ ⒚ ⒛ ⒜ ⒝ ⒞ ⒟ ⒠ ⒢ ⒣ ⒦ ⒨ ⒩ ⒪ ⒫ ⒬ ⒮ ⒰ ⒱ ⒲ ⒴ ⩴ ⩵ ⩶ 🄐 🄑 🄒 🄓 🄔 🄕 🄖 🄗 🄙 🄚 🄛 🄜 🄝 🄞 🄟 🄠 🄡 🄢 🄣 🄤 🄥 🄦 🄧 🄨 🄩
- total size of all bitmap data must be less than 64k bytes (easy)

# Other BDF Fonts

- [Powerline Terminus](https://github.com/powerline/fonts/tree/master/Terminus/BDF)
- [Creep](https://github.com/romeovs/creep/releases)

- Large collection, with samples: [Tecate](https://github.com/Tecate/bitmap-fonts)
- [Zevv-pepp](http://zevv.nl/play/code/zevv-peep/)
- [plan9 collection](https://github.com/rtrn/plan9fonts)

# TODO

- combine test and tryout code into single exec
- add example drawing code


