# Requirements
- ffmpeg
- ffprobe

| Codec        | Encoder               |
|--------------|-----------------------|
| AC-3 (DD)    | Dolby Encoding Engine |
| E-AC-3 (DD+) | Dolby Encoding Engine |
| TrueHD       | Dolby Encoding Engine |
| FLAC         | sox                   |
| Opus         | ffmpeg /w libopus     |

# Installation
```sh
git clone https://github.com/vevv/eat
cd eat
pip install .
```
`pip install -e .` can be used instead for an editable instance (see: https://stackoverflow.com/a/35064498)
* run `eat` with no params to generate an example config in ~/.eat/config.toml.example

# Usage
```
usage: eat [-h] [-v] [-i [INPUT ...]] [-f {dd,ddp,thd,thd+ac3,opus,flac}] [-b BITRATE][-m {1,2,6,8}] [-t THREADS]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         shows version
  -i [INPUT ...], --input [INPUT ...]
                        audio file(s)
  -f {dd,ddp,thd,thd+ac3,opus,flac}, --format {dd,ddp,thd,thd+ac3,opus,flac}
                        output codec
  -b BITRATE, --bitrate BITRATE
                        output bitrate for lossy codecs
  -m {1,2,6,8}, --mix {1,2,6,8}
                        specify down/upmix, support varies by codec (default: none)
```

# Default bitrates
| Channels | AC-3 (DD) | E-AC-3 (DD+) | Opus     |
|----------|-----------|--------------|----------|
| 1        | 128 kbps  | 128 kbps     | 96 kbps  |
| 2        | 224 kbps  | 224 kbps     | 160 kbps |
| 6        | 640       | 1024 kbps    | 384 kbps |
| 8        | N/A       | 1536 kbps    | 512 kbps |

# Remixing support
| Channels   | AC-3 (DD) | E-AC-3 (DD+) | TrueHD | Opus | FLAC |
|------------|-----------|--------------|--------|------|------|
| * -> 1     | yes       | yes          | no     | yes  | no   |
| * -> 2     | yes       | yes          | no     | yes  | no   |
| 8 -> 6     | yes       | yes          | no     | no   | no   |
| 6 -> 8     | N/A       | yes          | no     | no   | no   |
| 1/2 -> 6/8 | no        | no           | no     | no   | no   |

Remixing is handled by the encoder rather than ffmpeg, as AFAIK it doesn't do it very well.

# Examples
* DD+5.1 1024 kbps: `eat -i audio.flac -f ddp -b 1024`
* TrueHD + DD5.1 640 kbps "core": `eat -i audio.dts -f thd+ac3`

# Notes
- The DD5.1 "core" will always use Dolby Surround EX if input is 7.1. Standalone DD5.1 encoding does not enable this option by default.
- Only 1.0, 2.0, 5.1, 7.1 are supported, other layouts should be converted to those by user.
- 7.1 will automatically be downmixed to 5.1 with DEE for DD.
- thd.log/thd.mll files are cleaned after all encoding jobs are finished.

# TODO
- [x] Prevent/add warnings for file overwrites
- [ ] Add support for qaac
- [ ] Add warnings for incompatible sample rate
- [x] Add warnings and/or support for odd channel layouts
- [ ] Add bit depth conversion for FLAC
- [x] Consider using sox for sample rate/bit depth conversions/flac encoding
- [ ] Threading support / multiple simultaneous encodes
- [ ] Test with WSL

# Credits
Thanks to pcroland for his [deew](https://github.com/pcroland/deew) project which was the base for this.
