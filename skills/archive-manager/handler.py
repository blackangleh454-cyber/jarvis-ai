#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

def get_archive_type(archive_path):
    ext = Path(archive_path).suffix.lower()
    if ext in ['.tar', '.gz', '.tgz', '.bz2', '.xz']:
        return 'tar'
    elif ext == '.zip':
        return 'zip'
    elif ext == '.7z':
        return '7z'
    elif ext == '.rar':
        return 'rar'
    return None

def create_archive(archive_path, files):
    if not archive_path:
        return "Archive name required"
    
    if not files:
        return "Files to archive required"
    
    archive_path = os.path.abspath(archive_path)
    archive_type = get_archive_type(archive_path)
    
    if not archive_type:
        return f"Unsupported archive format: {Path(archive_path).suffix}"
    
    try:
        if archive_type == 'tar':
            cmd = ['tar', '-czf', archive_path] + files
        elif archive_type == 'zip':
            cmd = ['zip', '-r', archive_path] + files
        elif archive_type == '7z':
            cmd = ['7z', 'a', archive_path] + files
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Created: {archive_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError as e:
        return f"Command not found: {e.filename}"

def extract_archive(archive_path, destination=None):
    if not archive_path:
        return "Archive path required"
    
    if not os.path.exists(archive_path):
        return f"Archive not found: {archive_path}"
    
    archive_path = os.path.abspath(archive_path)
    archive_type = get_archive_type(archive_path)
    
    if not archive_type:
        return f"Unsupported archive format: {Path(archive_path).suffix}"
    
    try:
        if archive_type == 'tar':
            cmd = ['tar', '-xf', archive_path]
            if destination:
                cmd.extend(['-C', destination])
        elif archive_type == 'zip':
            cmd = ['unzip', archive_path]
            if destination:
                cmd.extend(['-d', destination])
        elif archive_type == '7z':
            cmd = ['7z', 'x', archive_path]
            if destination:
                cmd.extend(['-o' + destination])
        elif archive_type == 'rar':
            cmd = ['unrar', 'x', archive_path]
            if destination:
                cmd.extend(['-d', destination])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return f"Extracted: {archive_path}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError as e:
        return f"Command not found: {e.filename}"

def list_contents(archive_path):
    if not archive_path:
        return "Archive path required"
    
    if not os.path.exists(archive_path):
        return f"Archive not found: {archive_path}"
    
    archive_path = os.path.abspath(archive_path)
    archive_type = get_archive_type(archive_path)
    
    if not archive_type:
        return f"Unsupported archive format: {Path(archive_path).suffix}"
    
    try:
        if archive_type == 'tar':
            cmd = ['tar', '-tzf', archive_path]
        elif archive_type == 'zip':
            cmd = ['unzip', '-l', archive_path]
        elif archive_type == '7z':
            cmd = ['7z', 'l', archive_path]
        elif archive_type == 'rar':
            cmd = ['unrar', 'l', archive_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
    except FileNotFoundError as e:
        return f"Command not found: {e.filename}"

def compress_targz(file_path):
    if not file_path:
        return "File path required"
    
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    file_path = os.path.abspath(file_path)
    output = file_path + ".tar.gz"
    
    try:
        cmd = ['tar', '-czf', output, file_path]
        subprocess.run(cmd, check=True)
        return f"Compressed: {output}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def main():
    if len(sys.argv) < 2:
        return """Usage: archive-manager <command> [args]

Commands:
  create <archive> <files...>  - Create archive
  extract <archive> [dest]      - Extract archive
  list <archive>                - List contents
  compress <file>               - Compress to .tar.gz"""
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 4:
            return "Usage: create <archive> <files...>"
        archive = sys.argv[2]
        files = sys.argv[3:]
        return create_archive(archive, files)
    
    elif command == "extract":
        if len(sys.argv) < 3:
            return "Usage: extract <archive> [destination]"
        archive = sys.argv[2]
        dest = sys.argv[3] if len(sys.argv) > 3 else None
        return extract_archive(archive, dest)
    
    elif command == "list":
        if len(sys.argv) < 3:
            return "Usage: list <archive>"
        return list_contents(sys.argv[2])
    
    elif command == "compress":
        if len(sys.argv) < 3:
            return "Usage: compress <file>"
        return compress_targz(sys.argv[2])
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
