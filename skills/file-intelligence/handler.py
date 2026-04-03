#!/usr/bin/env python3
"""file-intelligence - Find, organize, summarize any file."""
import sys
import os
import hashlib
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


def format_size(size):
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f}{u}"
        size /= 1024
    return f"{size:.1f}PB"


# File Finding

def find_files(pattern, search_path="~"):
    """Find files by name pattern."""
    search_path = os.path.expanduser(search_path)
    if not os.path.exists(search_path):
        return f"Path not found: {search_path}"

    cmd = f"find '{search_path}' -name '*{pattern}*' -type f 2>/dev/null | head -100"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    matches = result.stdout.strip().split("\n") if result.stdout.strip() else []

    if not matches or matches == [""]:
        return f"No files matching '{pattern}' in {search_path}"

    lines = [f"Found {len(matches)} file(s) matching '{pattern}':"]
    for m in sorted(matches)[:50]:
        try:
            size = os.path.getsize(m)
            lines.append(f"  {format_size(size):>8}  {m}")
        except:
            lines.append(f"  {'?':>8}  {m}")
    return "\n".join(lines)


def find_ext(extension, search_path="~"):
    """Find files by extension."""
    search_path = os.path.expanduser(search_path)
    if not extension.startswith("."):
        extension = "." + extension

    cmd = f"find '{search_path}' -type f -name '*{extension}' 2>/dev/null | head -100"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    matches = result.stdout.strip().split("\n") if result.stdout.strip() else []

    if not matches or matches == [""]:
        return f"No {extension} files in {search_path}"

    lines = [f"Found {len(matches)} {extension} file(s):"]
    for m in sorted(matches)[:50]:
        try:
            size = os.path.getsize(m)
            lines.append(f"  {format_size(size):>8}  {m}")
        except:
            lines.append(f"  {'?':>8}  {m}")
    return "\n".join(lines)


def find_size(min_mb, search_path="~"):
    """Find files larger than specified size."""
    search_path = os.path.expanduser(search_path)
    min_bytes = int(min_mb * 1024 * 1024)

    cmd = f"find '{search_path}' -type f -size +{min_mb}M 2>/dev/null | head -50"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    matches = result.stdout.strip().split("\n") if result.stdout.strip() else []

    if not matches or matches == [""]:
        return f"No files larger than {min_mb}MB in {search_path}"

    lines = [f"Files larger than {min_mb}MB:"]
    entries = []
    for m in matches[:50]:
        if m:
            try:
                entries.append((os.path.getsize(m), m))
            except:
                pass
    entries.sort(reverse=True)

    for size, path in entries[:30]:
        lines.append(f"  {format_size(size):>10}  {path}")
    return "\n".join(lines)


def find_old(days, search_path="~"):
    """Find files older than specified days."""
    search_path = os.path.expanduser(search_path)
    cutoff = datetime.now() - timedelta(days=days)

    cmd = f"find '{search_path}' -type f -mtime +{days} 2>/dev/null | head -100"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    matches = result.stdout.strip().split("\n") if result.stdout.strip() else []

    if not matches or matches == [""]:
        return f"No files older than {days} days in {search_path}"

    lines = [f"Files older than {days} days:"]
    for m in sorted(matches)[:50]:
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(m))
            age = (datetime.now() - mtime).days
            lines.append(f"  {age:>4}d  {m}")
        except:
            pass
    return "\n".join(lines)


def find_content(text, search_path="~"):
    """Search for text inside files."""
    search_path = os.path.expanduser(search_path)

    cmd = f"grep -rl '{text}' '{search_path}' 2>/dev/null | head -50"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    matches = result.stdout.strip().split("\n") if result.stdout.strip() else []

    if not matches or matches == [""]:
        return f"No files contain '{text}' in {search_path}"

    lines = [f"Found '{text}' in {len(matches)} file(s):"]
    for m in sorted(matches)[:30]:
        # Get matching lines
        try:
            grep = subprocess.run(
                f"grep -n '{text}' '{m}' | head -3",
                shell=True, capture_output=True, text=True, timeout=5
            )
            lines.append(f"\n  {m}:")
            for line in grep.stdout.strip().split("\n")[:3]:
                lines.append(f"    {line}")
        except:
            lines.append(f"  {m}")
    return "\n".join(lines)


# PDF Functions

def pdf_info(filepath):
    """Get PDF metadata."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    try:
        import fitz
        doc = fitz.open(filepath)

        meta = doc.metadata
        lines = [
            f"PDF: {filepath}",
            f"Pages: {doc.page_count}",
            f"Title: {meta.get('title', 'N/A')}",
            f"Author: {meta.get('author', 'N/A')}",
            f"Subject: {meta.get('subject', 'N/A')}",
            f"Creator: {meta.get('creator', 'N/A')}",
            f"Producer: {meta.get('producer', 'N/A')}",
            f"Created: {meta.get('creationDate', 'N/A')}",
            f"Modified: {meta.get('modDate', 'N/A')}",
            f"Encrypted: {doc.is_encrypted}",
            f"Size: {format_size(os.path.getsize(filepath))}",
        ]

        # TOC
        toc = doc.get_toc()
        if toc:
            lines.append(f"\nTable of Contents ({len(toc)} entries):")
            for entry in toc[:20]:
                indent = "  " * (entry[0] - 1)
                lines.append(f"  {indent}{entry[1]} (p.{entry[2]})")

        doc.close()
        return "\n".join(lines)

    except ImportError:
        return "PyMuPDF not installed. Run: pip install PyMuPDF"
    except Exception as e:
        return f"PDF read error: {e}"


def pdf_text(filepath, start_page=0, end_page=None):
    """Extract text from PDF."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    try:
        import fitz
        doc = fitz.open(filepath)

        if end_page is None:
            end_page = doc.page_count

        lines = []
        for i in range(start_page, min(end_page, doc.page_count)):
            page = doc[i]
            text = page.get_text()
            if text.strip():
                lines.append(f"--- Page {i + 1} ---")
                lines.append(text.strip())

        doc.close()

        full_text = "\n".join(lines)
        if len(full_text) > 20000:
            return full_text[:20000] + f"\n\n... (truncated, total {len(full_text)} chars)"
        return full_text if full_text else "No text found in PDF"

    except ImportError:
        return "PyMuPDF not installed"
    except Exception as e:
        return f"PDF text extraction error: {e}"


def pdf_pages(filepath, start=0, end=None):
    """Extract specific page range."""
    return pdf_text(filepath, start, end)


def pdf_images(filepath, output_dir=None):
    """Extract images from PDF."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    try:
        import fitz
        doc = fitz.open(filepath)

        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(filepath), "pdf_images")
        os.makedirs(output_dir, exist_ok=True)

        image_count = 0
        for page_num in range(doc.page_count):
            page = doc[page_num]
            images = page.get_images(full=True)

            for img_idx, img in enumerate(images):
                xref = img[0]
                base_image = doc.extract_image(xref)
                if base_image:
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]
                    img_path = os.path.join(output_dir, f"page{page_num+1}_img{img_idx+1}.{ext}")
                    with open(img_path, "wb") as f:
                        f.write(image_bytes)
                    image_count += 1

        doc.close()
        return f"Extracted {image_count} image(s) to {output_dir}"

    except Exception as e:
        return f"Image extraction error: {e}"


def pdf_summary(filepath):
    """PDF overview + text preview."""
    filepath = os.path.expanduser(filepath)
    info = pdf_info(filepath)
    text_preview = pdf_text(filepath, 0, 3)  # First 3 pages
    return f"{info}\n\n--- Text Preview (first 3 pages) ---\n{text_preview[:3000]}"


# File Operations

def summarize_file(filepath):
    """Summarize any file."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    stat = os.stat(filepath)
    ext = Path(filepath).suffix.lower()

    lines = [
        f"File: {filepath}",
        f"Type: {ext or 'unknown'}",
        f"Size: {format_size(stat.st_size)}",
        f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}",
        f"Permissions: {oct(stat.st_mode)[-3:]}",
    ]

    # Content preview based on type
    if ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(filepath)
            lines.append(f"Pages: {doc.page_count}")
            first_text = doc[0].get_text()[:500] if doc.page_count > 0 else ""
            doc.close()
            if first_text:
                lines.append(f"\nPreview:\n{first_text}")
        except:
            pass

    elif ext in (".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml",
                 ".sh", ".bash", ".cfg", ".conf", ".ini", ".log", ".csv", ".xml"):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(2000)
            line_count = content.count("\n") + 1
            lines.append(f"Lines: {line_count}")
            lines.append(f"\nPreview:\n{content[:500]}")
        except:
            pass

    elif ext in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"):
        try:
            from PIL import Image
            img = Image.open(filepath)
            lines.append(f"Dimensions: {img.width}x{img.height}")
            lines.append(f"Mode: {img.mode}")
            lines.append(f"Format: {img.format}")
        except:
            pass

    elif ext in (".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar"):
        if ext == ".zip":
            import zipfile
            try:
                with zipfile.ZipFile(filepath) as z:
                    lines.append(f"Contains: {len(z.namelist())} file(s)")
                    for name in z.namelist()[:10]:
                        lines.append(f"  {name}")
            except:
                pass

    elif ext in (".mp3", ".wav", ".ogg", ".flac", ".aac"):
        lines.append("Type: Audio file")

    elif ext in (".mp4", ".avi", ".mkv", ".mov", ".webm"):
        lines.append("Type: Video file")

    elif ext in (".deb", ".rpm", ".AppImage"):
        lines.append("Type: Package/Executable")

    return "\n".join(lines)


def find_duplicates(search_path="~"):
    """Find duplicate files by hash."""
    search_path = os.path.expanduser(search_path)

    hash_map = defaultdict(list)
    for root, dirs, files in os.walk(search_path):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            fpath = os.path.join(root, fname)
            try:
                size = os.path.getsize(fpath)
                if size == 0:
                    continue
                # Quick hash of first 8KB
                with open(fpath, "rb") as f:
                    chunk = f.read(8192)
                h = hashlib.md5(chunk).hexdigest()
                hash_map[h].append(fpath)
            except:
                continue

    duplicates = {k: v for k, v in hash_map.items() if len(v) > 1}

    if not duplicates:
        return "No duplicates found"

    lines = [f"Found {len(duplicates)} set(s) of duplicates:"]
    total_wasted = 0

    for h, paths in sorted(duplicates.items(), key=lambda x: -len(x[1])):
        try:
            size = os.path.getsize(paths[0])
            wasted = size * (len(paths) - 1)
            total_wasted += wasted
            lines.append(f"\n  Hash: {h[:12]}... ({format_size(size)} each)")
            for p in sorted(paths):
                lines.append(f"    {p}")
        except:
            pass

    lines.append(f"\nTotal wasted space: {format_size(total_wasted)}")
    return "\n".join(lines)


def organize_by_type(source_path):
    """Organize files into folders by type."""
    source_path = os.path.expanduser(source_path)
    if not os.path.isdir(source_path):
        return f"Not a directory: {source_path}"

    type_map = {
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".webm"],
        "Audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
        "Archives": [".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".sh", ".go", ".rs"],
        "Data": [".json", ".csv", ".xml", ".yaml", ".yml", ".sql", ".db"],
        "Executables": [".deb", ".rpm", ".AppImage", ".bin", ".run"],
    }

    moved = defaultdict(int)
    for fname in os.listdir(source_path):
        fpath = os.path.join(source_path, fname)
        if not os.path.isfile(fpath):
            continue

        ext = Path(fname).suffix.lower()
        dest_type = "Other"
        for folder, extensions in type_map.items():
            if ext in extensions:
                dest_type = folder
                break

        dest_dir = os.path.join(source_path, dest_type)
        os.makedirs(dest_dir, exist_ok=True)

        try:
            shutil.move(fpath, os.path.join(dest_dir, fname))
            moved[dest_type] += 1
        except:
            pass

    lines = ["Organized by type:"]
    for folder, count in sorted(moved.items()):
        lines.append(f"  {folder}/: {count} file(s)")
    return "\n".join(lines)


def organize_by_date(source_path):
    """Organize files into folders by date."""
    source_path = os.path.expanduser(source_path)
    if not os.path.isdir(source_path):
        return f"Not a directory: {source_path}"

    moved = defaultdict(int)
    for fname in os.listdir(source_path):
        fpath = os.path.join(source_path, fname)
        if not os.path.isfile(fpath):
            continue

        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            date_folder = mtime.strftime("%Y-%m")
            dest_dir = os.path.join(source_path, date_folder)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(fpath, os.path.join(dest_dir, fname))
            moved[date_folder] += 1
        except:
            pass

    lines = ["Organized by date:"]
    for folder, count in sorted(moved.items(), reverse=True):
        lines.append(f"  {folder}/: {count} file(s)")
    return "\n".join(lines)


def watch_directory(path, pattern="*", command="echo 'Change detected'"):
    """Watch directory for file changes."""
    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        return f"Not a directory: {path}"

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class Handler(FileSystemEventHandler):
            def on_any_event(self, event):
                if not event.is_directory:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {event.event_type}: {event.src_path}")

        observer = Observer()
        observer.schedule(Handler(), path, recursive=True)
        observer.start()

        print(f"Watching {path} for changes... (Ctrl+C to stop)")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        return "Watch stopped"

    except ImportError:
        return "watchdog not installed. Run: pip install watchdog"
    except Exception as e:
        return f"Watch error: {e}"


def tree(path=".", max_depth=3):
    """Show directory tree."""
    path = os.path.expanduser(path)
    if not os.path.isdir(path):
        return f"Not a directory: {path}"

    lines = [f"{os.path.basename(path)}/"]

    def _tree(current_path, prefix="", depth=0):
        if depth >= max_depth:
            return

        try:
            entries = sorted(os.scandir(current_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except:
            return

        entries = [e for e in entries if not e.name.startswith(".")]

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "

            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                _tree(entry.path, new_prefix, depth + 1)
            else:
                try:
                    size = format_size(entry.stat().st_size)
                except:
                    size = "?"
                lines.append(f"{prefix}{connector}{entry.name} ({size})")

    _tree(path)
    return "\n".join(lines)


def file_stats(search_path="~"):
    """File statistics for a directory."""
    search_path = os.path.expanduser(search_path)
    if not os.path.isdir(search_path):
        return f"Not a directory: {search_path}"

    total_files = 0
    total_dirs = 0
    total_size = 0
    ext_count = defaultdict(int)
    ext_size = defaultdict(int)

    for root, dirs, files in os.walk(search_path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        total_dirs += len(dirs)

        for fname in files:
            if fname.startswith("."):
                continue
            total_files += 1
            fpath = os.path.join(root, fname)
            try:
                size = os.path.getsize(fpath)
                total_size += size
                ext = Path(fname).suffix.lower() or "(none)"
                ext_count[ext] += 1
                ext_size[ext] += size
            except:
                pass

    lines = [
        f"Stats for {search_path}:",
        f"Files: {total_files}",
        f"Directories: {total_dirs}",
        f"Total size: {format_size(total_size)}",
        "",
        "By extension (top 15):",
    ]

    sorted_exts = sorted(ext_count.items(), key=lambda x: -ext_size[x[0]])[:15]
    for ext, count in sorted_exts:
        size = format_size(ext_size[ext])
        lines.append(f"  {ext:<10} {count:>6} files  {size:>10}")

    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "find":
        print(find_files(a[0], a[1] if len(a) > 1 else "~") if a else "Usage: find <pattern> [path]")
    elif cmd == "find_ext":
        print(find_ext(a[0], a[1] if len(a) > 1 else "~") if a else "Usage: find_ext <ext> [path]")
    elif cmd == "find_size":
        print(find_size(float(a[0]), a[1] if len(a) > 1 else "~") if a else "Usage: find_size <min_mb> [path]")
    elif cmd == "find_old":
        print(find_old(int(a[0]), a[1] if len(a) > 1 else "~") if a else "Usage: find_old <days> [path]")
    elif cmd == "find_content":
        print(find_content(a[0], a[1] if len(a) > 1 else "~") if a else "Usage: find_content <text> [path]")
    elif cmd == "pdf_info":
        print(pdf_info(a[0]) if a else "Usage: pdf_info <file>")
    elif cmd == "pdf_text":
        print(pdf_text(a[0], int(a[1]) if len(a) > 1 else 0, int(a[2]) if len(a) > 2 else None) if a else "Usage: pdf_text <file> [start] [end]")
    elif cmd == "pdf_pages":
        print(pdf_pages(a[0], int(a[1]) if len(a) > 1 else 0, int(a[2]) if len(a) > 2 else None) if a else "Usage: pdf_pages <file> [start] [end]")
    elif cmd == "pdf_images":
        print(pdf_images(a[0], a[1] if len(a) > 1 else None) if a else "Usage: pdf_images <file> [output_dir]")
    elif cmd == "pdf_summary":
        print(pdf_summary(a[0]) if a else "Usage: pdf_summary <file>")
    elif cmd == "summarize":
        print(summarize_file(a[0]) if a else "Usage: summarize <file>")
    elif cmd == "duplicates":
        print(find_duplicates(a[0] if a else "~"))
    elif cmd == "organize_by_type":
        print(organize_by_type(a[0]) if a else "Usage: organize_by_type <path>")
    elif cmd == "organize_by_date":
        print(organize_by_date(a[0]) if a else "Usage: organize_by_date <path>")
    elif cmd == "watch":
        print(watch_directory(a[0], a[1] if len(a) > 1 else "*", a[2] if len(a) > 2 else "echo 'changed'") if a else "Usage: watch <path> [pattern] [command]")
    elif cmd == "tree":
        print(tree(a[0] if a else ".", int(a[1]) if len(a) > 1 else 3))
    elif cmd == "stats":
        print(file_stats(a[0] if a else "~"))
    else:
        print("Commands: find, find_ext, find_size, find_old, find_content, pdf_info, pdf_text, "
              "pdf_pages, pdf_images, pdf_summary, summarize, duplicates, organize_by_type, "
              "organize_by_date, watch, tree, stats")
