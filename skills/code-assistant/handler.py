#!/usr/bin/env python3
"""code-assistant - Write, debug, explain, and run code."""
import sys
import os
import subprocess
import ast
import re
import tempfile
import json
from pathlib import Path


def run_cmd(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def detect_language(filepath):
    """Detect language from file extension."""
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".sh": "bash", ".bash": "bash", ".rb": "ruby",
        ".go": "go", ".rs": "rust", ".c": "c", ".cpp": "cpp",
        ".java": "java", ".html": "html", ".css": "css",
        ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    }
    return ext_map.get(Path(filepath).suffix.lower(), "unknown")


# Code Writing

def write_code(description, lang="python", output=None):
    """Generate code from description (JARVIS LLM handles generation)."""
    # This returns the description for the LLM to generate code
    # The actual code generation happens in the LLM, not here
    return f"Generate {lang} code for: {description}\n\n(Use JARVIS's reasoning to generate code, then save with write_file)"


# Code Debugging

def debug_file(filepath):
    """Debug a code file and find errors."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = [f"Debug Analysis: {filepath} ({lang})"]
    errors = []
    warnings = []

    if lang == "python":
        # Syntax check
        try:
            ast.parse(content)
            lines.append("✓ Syntax: Valid")
        except SyntaxError as e:
            errors.append(f"Syntax Error at line {e.lineno}: {e.msg}")
            lines.append(f"✗ Syntax Error: line {e.lineno}: {e.msg}")

        # Common issues
        for i, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()

            # Unmatched parentheses/brackets
            if stripped.count("(") != stripped.count(")") and not stripped.startswith("#"):
                if stripped.count("(") - stripped.count(")") > 1:
                    warnings.append(f"Line {i}: Possible unmatched parentheses")
            if stripped.count("[") != stripped.count("]") and not stripped.startswith("#"):
                warnings.append(f"Line {i}: Possible unmatched brackets")

            # Common mistakes
            if "print " in stripped and "(" not in stripped and not stripped.startswith("#"):
                warnings.append(f"Line {i}: Python 3 print needs parentheses")
            if "= None" in stripped and "is None" not in stripped and "==" not in stripped:
                pass  # Normal
            if re.search(r"except\s*:", stripped):
                warnings.append(f"Line {i}: Bare except - consider catching specific exceptions")
            if re.search(r"import \*", stripped):
                warnings.append(f"Line {i}: Star import - use explicit imports")
            if stripped.startswith("def ") and ":" not in stripped:
                errors.append(f"Line {i}: Function missing colon")

        # Run flake8 if available
        flake8_out, _, _ = run_cmd(f"flake8 '{filepath}' --max-line-length=120 2>/dev/null")
        if flake8_out:
            lines.append(f"\nFlake8 findings:")
            for finding in flake8_out.split("\n")[:20]:
                if finding.strip():
                    lines.append(f"  {finding}")

    elif lang in ("javascript", "typescript"):
        # Check for common JS issues
        for i, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            if "var " in stripped:
                warnings.append(f"Line {i}: Use 'let' or 'const' instead of 'var'")
            if "==" in stripped and "===" not in stripped:
                warnings.append(f"Line {i}: Use '===' for strict equality")
            if "console.log" in stripped:
                warnings.append(f"Line {i}: console.log found (remove for production)")

    elif lang in ("bash", "shell"):
        shellcheck_out, _, _ = run_cmd(f"shellcheck '{filepath}' 2>/dev/null")
        if shellcheck_out:
            lines.append(f"\nShellCheck findings:")
            for finding in shellcheck_out.split("\n")[:20]:
                if finding.strip():
                    lines.append(f"  {finding}")

    if errors:
        lines.append(f"\n🔴 Errors ({len(errors)}):")
        for e in errors:
            lines.append(f"  {e}")
    else:
        lines.append(f"\n✓ No errors found")

    if warnings:
        lines.append(f"\n🟡 Warnings ({len(warnings)}):")
        for w in warnings[:10]:
            lines.append(f"  {w}")

    if not errors and not warnings:
        lines.append("\n✅ Code looks good!")

    return "\n".join(lines)


def debug_code(code, lang="python"):
    """Debug a code snippet."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=f".{lang}", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    result = debug_file(tmp_path)
    os.unlink(tmp_path)
    return result


# Code Explanation

def explain_file(filepath):
    """Explain what a code file does."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = [f"Code Analysis: {filepath} ({lang})"]
    line_count = len(content.split("\n"))

    lines.append(f"Lines: {line_count}")
    lines.append(f"Characters: {len(content)}")
    lines.append("")

    if lang == "python":
        # Parse AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return f"Cannot parse: Syntax error at line {e.lineno}: {e.msg}"

        # Find imports
        imports = []
        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"{node.module}.{'*' if not node.names else ', '.join(a.name for a in node.names)}")
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                classes.append({"name": node.name, "line": node.lineno, "methods": methods})
            elif isinstance(node, ast.FunctionDef) and not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree)):
                # Top-level functions only
                args = [a.arg for a in node.args.args]
                functions.append({"name": node.name, "line": node.lineno, "args": args})

        if imports:
            lines.append(f"📦 Imports ({len(imports)}):")
            for imp in imports[:15]:
                lines.append(f"  {imp}")
            lines.append("")

        if classes:
            lines.append(f"🏗️ Classes ({len(classes)}):")
            for cls in classes:
                lines.append(f"  {cls['name']} (line {cls['line']}) - {len(cls['methods'])} methods")
                for m in cls["methods"][:5]:
                    lines.append(f"    └─ {m}()")
            lines.append("")

        if functions:
            lines.append(f"⚡ Functions ({len(functions)}):")
            for fn in functions:
                args_str = ", ".join(fn["args"]) if fn["args"] else "no args"
                lines.append(f"  {fn['name']}({args_str}) at line {fn['line']}")
            lines.append("")

        # Docstrings
        if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, (ast.Str, ast.Constant)):
            doc = tree.body[0].value.value if hasattr(tree.body[0].value, 'value') else tree.body[0].value.s
            lines.append(f"📝 Module Docstring:")
            lines.append(f"  {doc[:300]}")
            lines.append("")

        # Complexity hint
        complexity = len(list(ast.walk(tree)))
        if complexity > 500:
            lines.append("⚠️ High complexity - consider refactoring")
        elif complexity > 200:
            lines.append("📊 Medium complexity")

    elif lang in ("javascript", "typescript"):
        # Basic JS analysis
        func_pattern = r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))"
        funcs = re.findall(func_pattern, content)
        all_funcs = [f[0] or f[1] for f in funcs if f[0] or f[1]]

        if all_funcs:
            lines.append(f"⚡ Functions ({len(all_funcs)}):")
            for fn in all_funcs[:15]:
                lines.append(f"  {fn}()")
            lines.append("")

        class_pattern = r"class\s+(\w+)"
        classes = re.findall(class_pattern, content)
        if classes:
            lines.append(f"🏗️ Classes ({len(classes)}):")
            for cls in classes:
                lines.append(f"  {cls}")
            lines.append("")

        import_pattern = r"(?:import\s+.*?from\s+['\"]([^'\"]+)['\"]|require\(['\"]([^'\"]+)['\"]\))"
        imports = re.findall(import_pattern, content)
        all_imports = [i[0] or i[1] for i in imports if i[0] or i[1]]
        if all_imports:
            lines.append(f"📦 Imports ({len(all_imports)}):")
            for imp in all_imports[:15]:
                lines.append(f"  {imp}")
            lines.append("")

    elif lang in ("bash", "shell"):
        func_pattern = r"(\w+)\s*\(\)\s*\{"
        funcs = re.findall(func_pattern, content)
        if funcs:
            lines.append(f"⚡ Functions ({len(funcs)}):")
            for fn in funcs:
                lines.append(f"  {fn}()")
            lines.append("")

    # Return analysis for LLM to explain in detail
    lines.append("💡 (Use JARVIS's reasoning for detailed step-by-step explanation)")
    return "\n".join(lines)


def explain_code(code, lang="python"):
    """Explain a code snippet."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=f".{lang}", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    result = explain_file(tmp_path)
    os.unlink(tmp_path)
    return result


# Code Running

def run_file(filepath):
    """Run a code file and capture output."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    runners = {
        "python": f"python3 '{filepath}'",
        "javascript": f"node '{filepath}'",
        "bash": f"bash '{filepath}'",
        "shell": f"bash '{filepath}'",
        "ruby": f"ruby '{filepath}'",
        "go": f"go run '{filepath}'",
    }

    cmd = runners.get(lang)
    if not cmd:
        return f"No runner for language: {lang}"

    out, err, code = run_cmd(cmd, timeout=60)
    lines = [f"Running {filepath} ({lang}):"]
    lines.append(f"Exit code: {code}")
    if out:
        lines.append(f"\n--- Output ---\n{out}")
    if err:
        lines.append(f"\n--- Error ---\n{err}")
    if not out and not err and code == 0:
        lines.append("(no output)")
    return "\n".join(lines)


def run_code(code, lang="python"):
    """Run a code snippet."""
    extensions = {"python": ".py", "javascript": ".js", "bash": ".sh", "shell": ".sh"}
    ext = extensions.get(lang, ".txt")

    with tempfile.NamedTemporaryFile(mode="w", suffix=ext, delete=False) as f:
        f.write(code)
        tmp_path = f.name

    result = run_file(tmp_path)
    os.unlink(tmp_path)
    return result


# Linting

def lint_file(filepath):
    """Lint a code file."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    lines = [f"Linting {filepath} ({lang}):"]

    if lang == "python":
        # Try flake8 first
        out, _, _ = run_cmd(f"flake8 '{filepath}' --max-line-length=120 --statistics 2>/dev/null")
        if out:
            lines.append(out)
        else:
            # Fallback to basic checks
            with open(filepath) as f:
                content = f.read()
            issues = []
            for i, line in enumerate(content.split("\n"), 1):
                if len(line) > 120:
                    issues.append(f"Line {i}: Too long ({len(line)} chars)")
                if "\t" in line and "    " in line:
                    issues.append(f"Line {i}: Mixed tabs and spaces")
                if line.rstrip() != line:
                    issues.append(f"Line {i}: Trailing whitespace")

            if issues:
                for issue in issues[:20]:
                    lines.append(f"  {issue}")
            else:
                lines.append("✓ No issues found")

    elif lang in ("javascript", "typescript"):
        out, _, _ = run_cmd(f"npx eslint '{filepath}' 2>/dev/null")
        if out:
            lines.append(out)
        else:
            lines.append("✓ No eslint found or no issues")

    elif lang in ("bash", "shell"):
        out, _, _ = run_cmd(f"shellcheck '{filepath}' 2>/dev/null")
        if out:
            lines.append(out)
        else:
            lines.append("✓ No shellcheck found or no issues")

    else:
        lines.append(f"No linter for {lang}")

    return "\n".join(lines)


def format_file(filepath):
    """Format a code file."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)

    if lang == "python":
        out, err, code = run_cmd(f"black '{filepath}' --line-length=120 2>&1")
        if code == 0:
            return f"Formatted {filepath}"
        return f"Format error: {err or out}"

    elif lang in ("javascript", "typescript"):
        out, err, code = run_cmd(f"npx prettier --write '{filepath}' 2>&1")
        if code == 0:
            return f"Formatted {filepath}"
        return f"Format error: {err or out}"

    else:
        return f"No formatter for {lang}"


# Analysis

def analyze_file(filepath):
    """Analyze code complexity."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    with open(filepath) as f:
        content = f.read()

    lines = [f"Analysis: {filepath}"]
    line_count = len(content.split("\n"))
    char_count = len(content)

    lines.append(f"Lines: {line_count}")
    lines.append(f"Characters: {char_count}")

    if lang == "python":
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return f"Cannot parse: {e}"

        # Count constructs
        func_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
        class_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
        import_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)))
        loop_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
        if_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.If))
        try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))

        lines.append(f"\nConstructs:")
        lines.append(f"  Functions: {func_count}")
        lines.append(f"  Classes: {class_count}")
        lines.append(f"  Imports: {import_count}")
        lines.append(f"  Loops: {loop_count}")
        lines.append(f"  Conditionals: {if_count}")
        lines.append(f"  Try/Except: {try_count}")

        # Complexity score
        complexity = func_count * 2 + loop_count * 3 + if_count * 2 + try_count * 2
        lines.append(f"\nComplexity Score: {complexity}")
        if complexity > 50:
            lines.append("⚠️ High complexity - consider refactoring")
        elif complexity > 20:
            lines.append("📊 Medium complexity")
        else:
            lines.append("✅ Low complexity")

        # Nesting depth
        max_depth = 0
        for node in ast.walk(tree):
            depth = 0
            parent = getattr(node, 'parent', None)
            while parent:
                depth += 1
                parent = getattr(parent, 'parent', None)
            max_depth = max(max_depth, depth)
        lines.append(f"Max nesting depth: ~{min(max_depth, 10)}")

    return "\n".join(lines)


def security_check(filepath):
    """Check for security issues in code."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    with open(filepath) as f:
        content = f.read()

    lines = [f"Security Check: {filepath}"]
    issues = []

    # Common security patterns
    patterns = {
        "Hardcoded password": r"(?:password|passwd|pwd)\s*=\s*['\"][^'\"]+['\"]",
        "Hardcoded API key": r"(?:api_key|apikey|api[_-]secret)\s*=\s*['\"][^'\"]+['\"]",
        "SQL injection risk": r"(?:execute|cursor\.execute)\s*\(\s*[f]?['\"].*?%s",
        "Command injection": r"os\.system\s*\(|subprocess\.call\s*\(|eval\s*\(",
        "Pickle deserialization": r"pickle\.loads?\s*\(",
        "YAML unsafe load": r"yaml\.load\s*\((?!.*Loader)",
        "Debug mode": r"DEBUG\s*=\s*True",
        "Wildcard import": r"from\s+\S+\s+import\s+\*",
        "Insecure HTTP": r"http://(?!localhost)",
        "Disabled SSL verify": r"verify\s*=\s*False",
    }

    for name, pattern in patterns.items():
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for m in matches:
            line_num = content[:m.start()].count("\n") + 1
            issues.append(f"  Line {line_num}: {name}")

    if lang == "python":
        # Python-specific
        dangerous_funcs = ["exec", "eval", "compile", "__import__", "getattr"]
        for func in dangerous_funcs:
            if re.search(rf"\b{func}\s*\(", content):
                line_num = content.index(func + "(")
                line_num = content[:line_num].count("\n") + 1
                issues.append(f"  Line {line_num}: Dangerous function '{func}()'")

    if issues:
        lines.append(f"\n🔴 Found {len(issues)} potential issue(s):")
        for issue in issues[:20]:
            lines.append(issue)
    else:
        lines.append("\n✅ No obvious security issues found")

    return "\n".join(lines)


# Utilities

def function_list(filepath):
    """List all functions in a file."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    with open(filepath) as f:
        content = f.read()

    lines = [f"Functions in {filepath}:"]

    if lang == "python":
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    args = [a.arg for a in node.args.args]
                    docstring = ast.get_docstring(node) or ""
                    lines.append(f"  Line {node.lineno}: {node.name}({', '.join(args)})")
                    if docstring:
                        lines.append(f"    → {docstring[:80]}")
        except:
            pass

    elif lang in ("javascript", "typescript"):
        pattern = r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))"
        for m in re.finditer(pattern, content):
            name = m.group(1) or m.group(2)
            line_num = content[:m.start()].count("\n") + 1
            lines.append(f"  Line {line_num}: {name}()")

    elif lang in ("bash", "shell"):
        pattern = r"(\w+)\s*\(\)\s*\{"
        for m in re.finditer(pattern, content):
            line_num = content[:m.start()].count("\n") + 1
            lines.append(f"  Line {line_num}: {m.group(1)}()")

    return "\n".join(lines)


def list_imports(filepath):
    """List all imports in a file."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    with open(filepath) as f:
        content = f.read()

    lines = [f"Imports in {filepath}:"]

    if lang == "python":
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        lines.append(f"  import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    names = ", ".join(a.name for a in node.names)
                    lines.append(f"  from {node.module} import {names}")
        except:
            pass

    elif lang in ("javascript", "typescript"):
        pattern = r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"
        for m in re.finditer(pattern, content):
            lines.append(f"  {m.group(1)}")
        pattern = r"require\(['\"]([^'\"]+)['\"]\)"
        for m in re.finditer(pattern, content):
            lines.append(f"  {m.group(1)} (require)")

    return "\n".join(lines)


def diff_files(file1, file2):
    """Compare two files."""
    file1 = os.path.expanduser(file1)
    file2 = os.path.expanduser(file2)

    if not os.path.exists(file1):
        return f"File not found: {file1}"
    if not os.path.exists(file2):
        return f"File not found: {file2}"

    out, _, _ = run_cmd(f"diff -u '{file1}' '{file2}' | head -100")
    return out if out else "Files are identical"


def run_tests(filepath):
    """Run tests for a file."""
    filepath = os.path.expanduser(filepath)
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    lang = detect_language(filepath)
    dirpath = os.path.dirname(filepath)

    if lang == "python":
        out, err, code = run_cmd(f"cd '{dirpath}' && python3 -m pytest '{filepath}' -v 2>&1", timeout=60)
        if code == 0 or "collected" in out:
            return out + "\n" + err
        # Try unittest
        out, err, code = run_cmd(f"python3 -m unittest '{filepath}' -v 2>&1", timeout=60)
        return out + "\n" + err

    elif lang in ("javascript", "typescript"):
        out, err, code = run_cmd(f"cd '{dirpath}' && npx jest '{filepath}' 2>&1", timeout=60)
        return out + "\n" + err

    return f"No test runner for {lang}"


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "write":
        print(write_code(a[0], a[1] if len(a) > 1 else "python", a[2] if len(a) > 2 else None) if a else "Usage: write <description> [lang] [output]")
    elif cmd == "debug":
        print(debug_file(a[0]) if a else "Usage: debug <file>")
    elif cmd == "debug_code":
        print(debug_code(a[0], a[1] if len(a) > 1 else "python") if a else "Usage: debug_code <code> [lang]")
    elif cmd == "explain":
        print(explain_file(a[0]) if a else "Usage: explain <file>")
    elif cmd == "explain_code":
        print(explain_code(a[0], a[1] if len(a) > 1 else "python") if a else "Usage: explain_code <code> [lang]")
    elif cmd == "run":
        print(run_file(a[0]) if a else "Usage: run <file>")
    elif cmd == "run_code":
        print(run_code(a[0], a[1] if len(a) > 1 else "python") if a else "Usage: run_code <code> [lang]")
    elif cmd == "lint":
        print(lint_file(a[0]) if a else "Usage: lint <file>")
    elif cmd == "format":
        print(format_file(a[0]) if a else "Usage: format <file>")
    elif cmd == "analyze":
        print(analyze_file(a[0]) if a else "Usage: analyze <file>")
    elif cmd == "security":
        print(security_check(a[0]) if a else "Usage: security <file>")
    elif cmd == "function_list":
        print(function_list(a[0]) if a else "Usage: function_list <file>")
    elif cmd == "imports":
        print(list_imports(a[0]) if a else "Usage: imports <file>")
    elif cmd == "diff":
        print(diff_files(a[0], a[1]) if len(a) >= 2 else "Usage: diff <file1> <file2>")
    elif cmd == "test":
        print(run_tests(a[0]) if a else "Usage: test <file>")
    else:
        print("Commands: write, debug, debug_code, explain, explain_code, run, run_code, "
              "lint, format, analyze, security, function_list, imports, diff, test")
