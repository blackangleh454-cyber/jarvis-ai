---
name: file-intelligence
description: >-
  Find, organize, summarize any file. PDF extraction, content search,
  file watching, automatic organization. Uses watchdog and PyMuPDF.
version: 1.0.0
permissions:
  - read
  - write
  - execute
keywords:
  - file
  - find
  - search
  - organize
  - pdf
  - document
  - content
  - watch
  - summarize
---

# file-intelligence

JARVIS finds, organizes, and summarizes any file on your system.

## Capabilities

- Find files by name, extension, size, date, content
- Full-text search inside documents
- PDF text/image extraction (PyMuPDF)
- PDF metadata and page count
- File organization (by type, date, project)
- Duplicate file detection
- File watching (watchdog) - trigger on changes
- File summary (size, type, content preview)
- Batch operations

## Commands

```bash
python3 handler.py find "<pattern>" [path]           # Find files by name
python3 handler.py find_ext <ext> [path]              # Find by extension
python3 handler.py find_size <min_size> [path]        # Find large files
python3 handler.py find_old <days> [path]             # Find old files
python3 handler.py find_content "<text>" [path]       # Search inside files
python3 handler.py pdf_info <file>                    # PDF metadata
python3 handler.py pdf_text <file>                    # Extract PDF text
python3 handler.py pdf_pages <file> [start] [end]     # Extract specific pages
python3 handler.py pdf_images <file> [output_dir]     # Extract images from PDF
python3 handler.py pdf_summary <file>                 # PDF overview + text preview
python3 handler.py summarize <file>                   # Summarize any file
python3 handler.py duplicates [path]                  # Find duplicate files
python3 handler.py organize_by_type <path>            # Organize into folders by type
python3 handler.py organize_by_date <path>            # Organize by date
python3 handler.py watch "<path>" "<pattern>" "<cmd>" # Watch for file changes
python3 handler.py tree [path] [depth]                # Directory tree
python3 handler.py stats [path]                       # File statistics
```
