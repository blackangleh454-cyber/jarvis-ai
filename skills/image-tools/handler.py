#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

def resize_image(image_path, width, height):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    if not width or not height:
        return "Width and height required"
    
    output_path = _get_output_path(image_path, f"_resized_{width}x{height}")
    
    try:
        cmd = ["convert", image_path, "-resize", f"{width}x{height}", output_path]
        subprocess.run(cmd, check=True)
        return f"Resized: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def convert_image(image_path, target_format):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    if not target_format:
        return "Target format required (jpg, png, webp, etc.)"
    
    p = Path(image_path)
    output_path = str(p.parent / f"{p.stem}.{target_format.lower()}")
    
    try:
        cmd = ["convert", image_path, output_path]
        subprocess.run(cmd, check=True)
        return f"Converted: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def compress_image(image_path, quality=85):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    p = Path(image_path)
    output_path = str(p.parent / f"{p.stem}_compressed{p.suffix}")
    
    try:
        cmd = ["convert", image_path, "-quality", str(quality), output_path]
        subprocess.run(cmd, check=True)
        return f"Compressed: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def thumbnail_image(image_path, size=200):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    p = Path(image_path)
    output_path = str(p.parent / f"{p.stem}_thumb{p.suffix}")
    
    try:
        cmd = ["convert", image_path, "-thumbnail", f"{size}x{size}^", 
               "-gravity", "center", "-extent", f"{size}x{size}", output_path]
        subprocess.run(cmd, check=True)
        return f"Thumbnail created: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def image_info(image_path):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    try:
        cmd = ["identify", "-verbose", image_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        lines = []
        for line in result.stdout.split('\n')[:20]:
            lines.append(line)
        return '\n'.join(lines)
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def crop_image(image_path, geometry):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    if not geometry:
        return "Geometry required (WxH+X+Y)"
    
    p = Path(image_path)
    output_path = str(p.parent / f"{p.stem}_cropped{p.suffix}")
    
    try:
        cmd = ["convert", image_path, "-crop", geometry, "+repage", output_path]
        subprocess.run(cmd, check=True)
        return f"Cropped: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def rotate_image(image_path, degrees):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    if degrees is None:
        return "Degrees required (90, 180, 270)"
    
    p = Path(image_path)
    output_path = str(p.parent / f"{p.stem}_rotated{p.suffix}")
    
    try:
        cmd = ["convert", image_path, "-rotate", str(degrees), output_path]
        subprocess.run(cmd, check=True)
        return f"Rotated: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def flip_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    p = Path(image_path)
    output_path = str(p.parent / f"{p.stem}_flipped{p.suffix}")
    
    try:
        cmd = ["convert", image_path, "-flip", output_path]
        subprocess.run(cmd, check=True)
        return f"Flipped: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def flop_image(image_path):
    if not image_path or not os.path.exists(image_path):
        return f"Image not found: {image_path}"
    
    p = Path(image_path)
    output_path = str(p.parent / f"{p.stem}_flopped{p.suffix}")
    
    try:
        cmd = ["convert", image_path, "-flop", output_path]
        subprocess.run(cmd, check=True)
        return f"Flopped: {output_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError:
        return "ImageMagick not found. Install: sudo apt install imagemagick"

def _get_output_path(original, suffix):
    p = Path(original)
    return str(p.parent / f"{p.stem}{suffix}{p.suffix}")

def main():
    if len(sys.argv) < 2:
        return """Usage: image-tools <command> [args]

Commands:
  resize <image> <width> <height>  - Resize image
  convert <image> <format>          - Convert format
  compress <image> [quality]       - Compress image
  thumbnail <image> [size]          - Create thumbnail
  info <image>                      - Show image info
  crop <image> <geometry>           - Crop image (WxH+X+Y)
  rotate <image> <degrees>         - Rotate (90, 180, 270)
  flip <image>                      - Flip horizontal
  flop <image>                      - Flip vertical"""
    
    command = sys.argv[1]
    
    if command == "resize":
        if len(sys.argv) < 5:
            return "Usage: resize <image> <width> <height>"
        return resize_image(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    
    elif command == "convert":
        if len(sys.argv) < 4:
            return "Usage: convert <image> <format>"
        return convert_image(sys.argv[2], sys.argv[3])
    
    elif command == "compress":
        quality = int(sys.argv[3]) if len(sys.argv) > 3 else 85
        return compress_image(sys.argv[2], quality)
    
    elif command == "thumbnail":
        size = int(sys.argv[3]) if len(sys.argv) > 3 else 200
        return thumbnail_image(sys.argv[2], size)
    
    elif command == "info":
        if len(sys.argv) < 3:
            return "Usage: info <image>"
        return image_info(sys.argv[2])
    
    elif command == "crop":
        if len(sys.argv) < 4:
            return "Usage: crop <image> <geometry>"
        return crop_image(sys.argv[2], sys.argv[3])
    
    elif command == "rotate":
        if len(sys.argv) < 4:
            return "Usage: rotate <image> <degrees>"
        return rotate_image(sys.argv[2], int(sys.argv[3]))
    
    elif command == "flip":
        if len(sys.argv) < 3:
            return "Usage: flip <image>"
        return flip_image(sys.argv[2])
    
    elif command == "flop":
        if len(sys.argv) < 3:
            return "Usage: flop <image>"
        return flop_image(sys.argv[2])
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
