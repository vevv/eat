# General requirements
- ffmpeg
- ffprobe

### Codec-specific requirements

| Codec        | Encoder               |
|--------------|-----------------------|
| AC-3 (DD)    | Dolby Encoding Engine |
| E-AC-3 (DD+) | Dolby Encoding Engine |
| TrueHD       | Dolby Encoding Engine |
| AAC          | qaac                  |
| FLAC         | ffmpeg                |
| Opus         | ffmpeg /w libopus     |

# Installation
```sh
git clone https://github.com/vevv/eat
cd eat
pip install .
```
`pip install -e .` can be used instead for an editable instance (see: https://stackoverflow.com/a/35064498)
* run `eat` with no params to generate an example config in ~/.eat/config.toml.example

# Configuration
Binary paths in config should only need to be specified if binary is not in PATH,
but they might be necessary if you're using Wine or WSL.

To use with Wine (for DEE/qaac), please ensure `wine-binfmt` is installed, the binaries are set as executable,
and you're launching eat with the correct Wine prefix.

WSL is untested, but I don't anticipate any issues.

# Usage
```
usage: eat [-h] [-v] [-i [INPUT ...]] [-o OUTPUT_DIR] [-f [{dd,ddp,thd,opus,flac,aac} ...]] [-b BITRATE]
           [-m {1,2,6,8}] [--sample-rate {44100,48000,96000}] [--bit-depth {16,24}] [-y] [-d]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         shows version
  -i [INPUT ...], --input [INPUT ...]
                        audio file(s)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        output directory (default: cwd)
  -f [{dd,ddp,thd,opus,flac,aac} ...], --format [{dd,ddp,thd,opus,flac,aac} ...]
                        output codec
  -b BITRATE, -q BITRATE, --bitrate BITRATE
                        output bitrate (quality value for aac) for lossy codecs
  -m {1,2,6,8}, --mix {1,2,6,8}
                        specify down/upmix, support varies by codec (default: none)
  --sample-rate {44100,48000,96000}
                        change output sample rate (FLAC only)
  --bit-depth {16,24}, --bitdepth {16,24}
                        change output bit depth (FLAC only)
  -y, --allow-overwrite
                        allow file overwrite
  -d, --debug           Print debug statements
```

# Default bitrates
| Channels | AC-3 (DD) | E-AC-3 (DD+) | Opus     | AAC   |
|----------|-----------|--------------|----------|-------|
| 1        | 128 kbps  | 128 kbps     | 96 kbps  | -V127 |
| 2        | 224 kbps  | 224 kbps     | 160 kbps | -V127 |
| 6        | 640       | 1024 kbps    | 384 kbps | -V127 |
| 8        | N/A       | 1536 kbps    | 512 kbps | -V127 |

### AAC
AAC is configured to use TVBR mode rather than ABR/CBR. This means the output param is a value between 0 and 127 rather than a bitrate target.
See https://github.com/nu774/qaac/wiki/Encoder-configuration#tvbr-quality-steps for more details.

Like qaac, eat will accept any value, but it'll internally be clamped to one of the following.
| 0 | 9 | 18 | 27 | 36 | 45 | 54 | 63 | 73 | 82 | 91 | 100 | 109 | 118 | 127 |
| - | - | -- | -- | -- | -- | -- | -- | -- | -- | -- | --- | --- | --- | --- |


Default value is 127, which is the maximum quality, depending on the source it can result in different bitrates,
I've seen it go from 192 kbps and under on some lower quality 2.0 sources to ~490 kbps on 7.1.
I'd recommend trying 127 first, and if bitrate is too high, going from 127 to 91 and then moving up.

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
* TrueHD + DD5.1 640 kbps "core": `eat -i audio.dts -f thd dd -b 640`

# Notes
- Files are processed in order; if multiple formats are passed, each file will be encoded to every format before processing the the next one.
- Support for layouts other than 1.0, 2.0, 5.1, 7.1 depends on the encoder (DEE will only accept those), it's recommended that user converts them beforehand.
- 7.1 will automatically be downmixed to 5.1 with DEE for DD.
- Temp files (including thd.log/thd.mll) are cleaned after each encoding job

# TODO
- [ ] Threading support / multiple simultaneous encodes
- [ ] Test with WSL

# Credits
Thanks to pcroland for his [deew](https://github.com/pcroland/deew) project which was the base for this (originally meant as a fork, ended up rewritten from scratch, with only DEE xml config files being reused).
