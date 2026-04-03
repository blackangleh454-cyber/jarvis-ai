# Image Tools

**Description:** Resize, convert, compress images using ImageMagick and PIL.

**Commands:**
- `resize <image> <width> <height>` - Resize image
- `convert <image> <format>` - Convert to different format
- `compress <image>` - Compress JPEG/PNG
- `thumbnail <image> <size>` - Create thumbnail
- `info <image>` - Show image info
- `crop <image> <w>x<h>+<x>+<y>` - Crop image
- `rotate <image> <degrees>` - Rotate image
- `flip <image>` - Flip horizontal
- `flop <image>` - Flip vertical

**Dependencies:**
- imagemagick
- python3-pil

**Usage:**
```bash
python handler.py resize photo.jpg 800 600
python handler.py convert photo.png jpg
python handler.py compress photo.jpg
python handler.py thumbnail image.jpg 200
python handler.py info image.png
python handler.py crop image.jpg 400x300+100+50
python handler.py rotate image.jpg 90
```
