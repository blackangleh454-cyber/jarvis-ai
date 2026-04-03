# Archive Manager

**Description:** Create and extract archives in various formats (zip, tar, 7z, rar).

**Commands:**
- `create <archive> <files...>` - Create archive
- `extract <archive>` - Extract archive
- `list <archive>` - List archive contents
- `compress <file>` - Compress file to .tar.gz

**Supported formats:**
- .zip (zip)
- .tar, .tar.gz, .tgz (tar)
- .7z (7z)
- .rar (unrar)

**Usage:**
```bash
python handler.py create archive.zip file1 file2 folder/
python handler.py extract archive.zip
python handler.py list archive.tar.gz
python handler.py compress largefile
```
