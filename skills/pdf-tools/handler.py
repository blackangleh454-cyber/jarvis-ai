#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("pypdf not installed. Install: pip install pypdf")

def merge_pdfs(output_path, input_paths):
    if not output_path:
        return "Output path required"
    
    if not input_paths:
        return "Input PDFs required"
    
    try:
        writer = PdfWriter()
        
        for pdf_path in input_paths:
            if not os.path.exists(pdf_path):
                return f"File not found: {pdf_path}"
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        return f"Merged: {output_path}"
    except Exception as e:
        return f"Error: {e}"

def split_pdf(input_path, output_dir=None):
    if not input_path or not os.path.exists(input_path):
        return f"PDF not found: {input_path}"
    
    try:
        reader = PdfReader(input_path)
        
        if output_dir is None:
            output_dir = Path(input_path).parent
        else:
            output_dir = Path(output_dir)
        
        base_name = Path(input_path).stem
        
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            
            output_path = output_dir / f"{base_name}_page_{i+1}.pdf"
            with open(output_path, "wb") as f:
                writer.write(f)
        
        return f"Split into {len(reader.pages)} pages"
    except Exception as e:
        return f"Error: {e}"

def extract_page(input_path, page_num, output_path=None):
    if not input_path or not os.path.exists(input_path):
        return f"PDF not found: {input_path}"
    
    if page_num is None:
        return "Page number required"
    
    try:
        reader = PdfReader(input_path)
        
        if page_num < 1 or page_num > len(reader.pages):
            return f"Page {page_num} out of range (1-{len(reader.pages)})"
        
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num - 1])
        
        if output_path is None:
            p = Path(input_path)
            output_path = p.parent / f"{p.stem}_page{page_num}.pdf"
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        return f"Extracted page {page_num}: {output_path}"
    except Exception as e:
        return f"Error: {e}"

def extract_text(input_path):
    if not input_path or not os.path.exists(input_path):
        return f"PDF not found: {input_path}"
    
    try:
        reader = PdfReader(input_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        
        if not text.strip():
            return "No text extracted (may be scanned image)"
        
        return text[:5000]
    except Exception as e:
        return f"Error: {e}"

def pdf_info(input_path):
    if not input_path or not os.path.exists(input_path):
        return f"PDF not found: {input_path}"
    
    try:
        result = subprocess.run(
            ["pdfinfo", input_path],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except FileNotFoundError:
        try:
            reader = PdfReader(input_path)
            info = f"Pages: {len(reader.pages)}\n"
            if reader.metadata:
                info += f"Title: {reader.metadata.get('/Title', 'N/A')}\n"
                info += f"Author: {reader.metadata.get('/Author', 'N/A')}\n"
                info += f"Creator: {reader.metadata.get('/Creator', 'N/A')}\n"
            return info
        except Exception as e:
            return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def compress_pdf(input_path, output_path=None):
    if not input_path or not os.path.exists(input_path):
        return f"PDF not found: {input_path}"
    
    try:
        if output_path is None:
            p = Path(input_path)
            output_path = p.parent / f"{p.stem}_compressed.pdf"
        
        result = subprocess.run(
            ["gs", "-sDEVICE=pdfwrite", "-dNOPAUSE", "-dBATCH", "-dSAFER",
             "-sOutputFile=" + output_path, input_path],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return f"Compressed: {output_path}"
        else:
            return f"gs error: {result.stderr}"
    except FileNotFoundError:
        return "Ghostscript not found. Install: sudo apt install ghostscript"
    except Exception as e:
        return f"Error: {e}"

def rotate_pdf(input_path, degrees, output_path=None):
    if not input_path or not os.path.exists(input_path):
        return f"PDF not found: {input_path}"
    
    if degrees is None:
        return "Degrees required (90, 180, 270)"
    
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            page.rotate(int(degrees))
            writer.add_page(page)
        
        if output_path is None:
            p = Path(input_path)
            output_path = p.parent / f"{p.stem}_rotated.pdf"
        
        with open(output_path, "wb") as f:
            writer.write(f)
        
        return f"Rotated: {output_path}"
    except Exception as e:
        return f"Error: {e}"

def main():
    if len(sys.argv) < 2:
        return """Usage: pdf-tools <command> [args]

Commands:
  merge <output.pdf> <input1.pdf> <input2.pdf> ...  - Merge PDFs
  split <input.pdf> [output_dir]                    - Split into pages
  extract <input.pdf> <page> [output.pdf]           - Extract page
  text <input.pdf>                                  - Extract text
  info <input.pdf>                                   - Show PDF info
  compress <input.pdf> [output.pdf]                 - Compress PDF
  rotate <input.pdf> <degrees> [output.pdf]         - Rotate pages"""
    
    command = sys.argv[1]
    
    if command == "merge":
        if len(sys.argv) < 4:
            return "Usage: merge <output.pdf> <input1.pdf> <input2.pdf> ..."
        output = sys.argv[2]
        inputs = sys.argv[3:]
        return merge_pdfs(output, inputs)
    
    elif command == "split":
        if len(sys.argv) < 3:
            return "Usage: split <input.pdf> [output_dir]"
        output_dir = sys.argv[3] if len(sys.argv) > 3 else None
        return split_pdf(sys.argv[2], output_dir)
    
    elif command == "extract":
        if len(sys.argv) < 4:
            return "Usage: extract <input.pdf> <page> [output.pdf]"
        output = sys.argv[4] if len(sys.argv) > 4 else None
        return extract_page(sys.argv[2], int(sys.argv[3]), output)
    
    elif command == "text":
        if len(sys.argv) < 3:
            return "Usage: text <input.pdf>"
        return extract_text(sys.argv[2])
    
    elif command == "info":
        if len(sys.argv) < 3:
            return "Usage: info <input.pdf>"
        return pdf_info(sys.argv[2])
    
    elif command == "compress":
        if len(sys.argv) < 3:
            return "Usage: compress <input.pdf> [output.pdf]"
        output = sys.argv[3] if len(sys.argv) > 3 else None
        return compress_pdf(sys.argv[2], output)
    
    elif command == "rotate":
        if len(sys.argv) < 4:
            return "Usage: rotate <input.pdf> <degrees> [output.pdf]"
        output = sys.argv[4] if len(sys.argv) > 4 else None
        return rotate_pdf(sys.argv[2], int(sys.argv[3]), output)
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
