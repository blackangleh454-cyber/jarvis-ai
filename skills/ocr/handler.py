#!/usr/bin/env python3
"""ocr - Jarvis reads text from any image/PDF."""
import sys
import os
import subprocess
from pathlib import Path

SCREENSHOT_DIR = os.path.expanduser("~/Pictures/jarvis_screenshots")


def run(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def capture_temp():
    """Capture screenshot to temp file."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    output = os.path.join(SCREENSHOT_DIR, f"ocr_{int(os.times().elapsed * 1000)}.png")
    run(f"scrot '{output}'")
    if not os.path.exists(output):
        run(f"import -window root '{output}'")
    return output if os.path.exists(output) else None


def tesseract_ocr(image_path):
    """OCR using tesseract."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "pytesseract/pillow not installed"

    if not os.path.exists(image_path):
        return f"Image not found: {image_path}"

    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip() if text.strip() else "No text found"
    except Exception as e:
        return f"Tesseract error: {e}"


def easyocr_read(image_path):
    """OCR using easyocr (more accurate for complex images)."""
    try:
        import easyocr
    except ImportError:
        return "easyocr not installed. Run: pip install easyocr"

    if not os.path.exists(image_path):
        return f"Image not found: {image_path}"

    try:
        reader = easyocr.Reader(['en'])
        results = reader.readtext(image_path)
        text = " ".join([r[1] for r in results])
        return text.strip() if text.strip() else "No text found"
    except Exception as e:
        return f"EasyOCR error: {e}"


def read_image(image_path, use_easy=False):
    """Read text from image file."""
    if use_easy:
        return easyocr_read(image_path)
    return tesseract_ocr(image_path)


def read_screen():
    """Capture screen and OCR."""
    img = capture_temp()
    if not img:
        return "Failed to capture screen"
    return tesseract_ocr(img)


def read_region(x, y, w, h):
    """Capture region and OCR."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    output = os.path.join(SCREENSHOT_DIR, f"ocr_region_{int(os.times().elapsed * 1000)}.png")
    run(f"scrot -a {x},{y},{w},{h} '{output}'")

    if not os.path.exists(output):
        return "Failed to capture region"

    return tesseract_ocr(output)


def read_pdf(pdf_path):
    """Extract text from PDF."""
    pdf_path = os.path.expanduser(pdf_path)
    if not os.path.exists(pdf_path):
        return f"PDF not found: {pdf_path}"

    try:
        import fitz
    except ImportError:
        return "PyMuPDF not installed. Run: pip install PyMuPDF"

    try:
        doc = fitz.open(pdf_path)
        lines = [f"PDF: {pdf_path} ({doc.page_count} pages)"]
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                lines.append(f"\n--- Page {i+1} ---")
                lines.append(text[:2000])
        return "\n".join(lines)
    except Exception as e:
        return f"PDF read error: {e}"


def find_text_on_screen(search_text):
    """Find text on screen."""
    if not search_text:
        return "Usage: find_text <text>"

    img = capture_temp()
    if not img:
        return "Failed to capture screen"

    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return "pytesseract not installed"

    try:
        img_obj = Image.open(img)
        data = pytesseract.image_to_data(img_obj, output_type=pytesseract.Output.DICT)
        found = False
        lines = [f"Searching for '{search_text}':"]

        for i, text in enumerate(data["text"]):
            if search_text.lower() in text.lower():
                x, y = data["left"][i], data["top"][i]
                conf = data["conf"][i]
                if float(conf) > 50:
                    lines.append(f"  Found at ({x}, {y}): '{text}' (confidence: {conf:.0f})")
                    found = True

        if found:
            return "\n".join(lines)
        return f"Text '{search_text}' not found on screen"
    except Exception as e:
        return f"Error: {e}"


def capture_and_ocr():
    """Capture screen, OCR, and return text."""
    return read_screen()


def scan_document():
    """Scan document (capture + enhance + OCR)."""
    img = capture_temp()
    if not img:
        return "Failed to capture"

    try:
        from PIL import Image, ImageEnhance
    except ImportError:
        return read_screen()

    try:
        im = Image.open(img)
        enhancer = ImageEnhance.Contrast(im)
        enhanced = enhancer.enhance(2.0)

        temp_enhanced = img.replace(".png", "_enhanced.png")
        enhanced.save(temp_enhanced)

        return tesseract_ocr(temp_enhanced)
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "read_image":
        print(read_image(a[0], use_easy=("--easy" in a)) if a else "Usage: read_image <image_path>")
    elif cmd == "read_screen":
        print(read_screen())
    elif cmd == "read_region":
        print(read_region(int(a[0]), int(a[1]), int(a[2]), int(a[3])) if len(a) >= 4 else "Usage: read_region <x> <y> <w> <h>")
    elif cmd == "read_pdf":
        print(read_pdf(a[0]) if a else "Usage: read_pdf <pdf_path>")
    elif cmd == "find_text":
        print(find_text_on_screen(" ".join(a)) if a else "Usage: find_text <text>")
    elif cmd == "capture_ocr":
        print(capture_and_ocr())
    elif cmd == "scan_document":
        print(scan_document())
    else:
        print("Commands: read_image, read_screen, read_region, read_pdf, find_text, capture_ocr, scan_document")
