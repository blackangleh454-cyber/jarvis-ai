#!/usr/bin/env python3
"""browser-control - Control browsers via Playwright."""
import sys
import os
from pathlib import Path

PAGE = None
BROWSER = None


def get_browser():
    global BROWSER, PAGE
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, None, "playwright not installed. Run: pip install playwright && playwright install chromium"

    if BROWSER is None:
        pw = sync_playwright().start()
        BROWSER = pw.chromium.launch(headless=True)
        PAGE = BROWSER.new_page()
    return BROWSER, PAGE, None


def close_browser():
    global BROWSER, PAGE
    if BROWSER:
        BROWSER.close()
        BROWSER = None
        PAGE = None
    return "Browser closed"


def open_url(url):
    """Open URL in browser."""
    _, page, err = get_browser()
    if err:
        return err

    page.goto(url, timeout=30000)
    return f"Opened: {url}\nTitle: {page.title()}"


def click_element(selector):
    """Click element by CSS selector."""
    _, page, err = get_browser()
    if err:
        return err

    try:
        page.click(selector, timeout=5000)
        return f"Clicked: {selector}"
    except Exception as e:
        return f"Click failed: {e}"


def type_text(selector, text):
    """Type text into element."""
    _, page, err = get_browser()
    if err:
        return err

    try:
        page.fill(selector, text)
        return f"Typed into {selector}: {text[:30]}"
    except Exception as e:
        return f"Type failed: {e}"


def goto_url(url):
    """Navigate to URL."""
    return open_url(url)


def take_screenshot(output=None):
    """Take screenshot of current page."""
    _, page, err = get_browser()
    if err:
        return err

    if not output:
        output = os.path.expanduser(f"~/Pictures/jarvis_browser_{int(os.times().elapsed * 1000)}.png")

    page.screenshot(path=output, full_page=True)
    size = os.path.getsize(output)
    return f"Screenshot: {output} ({size} bytes)"


def get_html():
    """Get page HTML."""
    _, page, err = get_browser()
    if err:
        return err

    html = page.content()
    if len(html) > 10000:
        return html[:10000] + "\n... (truncated)"
    return html


def get_text():
    """Get visible page text."""
    _, page, err = get_browser()
    if err:
        return err

    text = page.evaluate("() => document.body.innerText")
    if len(text) > 10000:
        return text[:10000] + "\n... (truncated)"
    return text


def find_text(search_text):
    """Find text on page."""
    _, page, err = get_browser()
    if err:
        return err

    try:
        page.wait_for_selector(f"text={search_text}", timeout=5000)
        return f"Found: {search_text}"
    except:
        return f"Text not found: {search_text}"


def execute_js(js_code):
    """Execute JavaScript."""
    _, page, err = get_browser()
    if err:
        return err

    try:
        result = page.evaluate(js_code)
        return f"Result: {result}"
    except Exception as e:
        return f"JS error: {e}"


def get_cookies():
    """Get page cookies."""
    _, page, err = get_browser()
    if err:
        return err

    cookies = page.context.cookies()
    if not cookies:
        return "No cookies"

    lines = ["Cookies:"]
    for c in cookies:
        lines.append(f"  {c['name']}={c['value'][:30]}...")
    return "\n".join(lines)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "open":
        print(open_url(a[0]) if a else "Usage: open <url>")
    elif cmd == "click":
        print(click_element(a[0]) if a else "Usage: click <selector>")
    elif cmd == "type":
        print(type_text(a[0], a[1]) if len(a) >= 2 else "Usage: type <selector> <text>")
    elif cmd == "goto":
        print(goto_url(a[0]) if a else "Usage: goto <url>")
    elif cmd == "screenshot":
        print(take_screenshot(a[0] if a else None))
    elif cmd == "html":
        print(get_html())
    elif cmd == "text":
        print(get_text())
    elif cmd == "find":
        print(find_text(" ".join(a)) if a else "Usage: find <text>")
    elif cmd == "execute":
        print(execute_js(" ".join(a)) if a else "Usage: execute <js>")
    elif cmd == "cookies":
        print(get_cookies())
    elif cmd == "close":
        print(close_browser())
    else:
        print("Commands: open, click, type, goto, screenshot, html, text, find, execute, cookies, close")
