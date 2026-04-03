# PDF Tools

**Description:** Merge, split, extract text and images from PDF files.

**Commands:**
- `merge <output.pdf> <input1.pdf> <input2.pdf> ...` - Merge PDFs
- `split <input.pdf>` - Split PDF into pages
- `extract <input.pdf> <page>` - Extract single page
- `text <input.pdf>` - Extract text from PDF
- `info <input.pdf>` - Show PDF info
- `compress <input.pdf>` - Compress PDF
- `rotate <input.pdf> <degrees>` - Rotate pages

**Dependencies:**
- poppler-utils (pdftk, pdfinfo)
- python3-pypdf or pypdf2

**Usage:**
```bash
python handler.py merge output.pdf file1.pdf file2.pdf
python handler.py split large.pdf
python handler.py extract input.pdf 5
python handler.py text document.pdf
python handler.py info document.pdf
python handler.py compress input.pdf
```
