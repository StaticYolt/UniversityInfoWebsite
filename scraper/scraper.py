import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ---- OPTIONAL Playwright fallback (for JS-rendered iframes) ----
USE_PLAYWRIGHT = True
try:
    from playwright.sync_api import sync_playwright
except Exception:
    USE_PLAYWRIGHT = False

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/125.0.0.0 Safari/537.36"
}

def get_html(url, timeout=20):
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text

def load_html_with_playwright(url, wait_selector=None, timeout_ms=15000):
    if not USE_PLAYWRIGHT:
        return None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        if wait_selector:
            try:
                page.wait_for_selector(wait_selector, timeout=timeout_ms)
            except Exception:
                pass
        html = page.content()
        browser.close()
        return html

def extract_iframe_srcs(page_url):
    """Fetch the main page and return absolute iframe src URLs."""
    html = get_html(page_url)
    soup = BeautifulSoup(html, "html.parser")
    srcs = []
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if src:
            srcs.append(urljoin(page_url, src))
    return srcs

def parse_items_from_soup(soup):
    """
    Extract items from a soup that uses classes like:
      .fw-feed-item, .fw-feed-item-title, .fw-feed-item-description, .fw-feed-item-date
    Returns list of normalized dicts.
    """
    # print(soup)
    items = []
    for div in soup.select(".fw-feed-item"):
        title_el = div.select_one(".fw-feed-item-title")
        desc_el = div.select_one(".fw-feed-item-description")
        date_el = div.select_one(".fw-feed-item-date")
        link = None

        # Some widgets place the URL in a clickable container with onclick="window.open('URL','_blank')"
        clickable = div.select_one(".fw-feed-item-url")
        if clickable:
            onclick = clickable.get("onclick") or clickable.get("onkeypress")
            if onclick:
                # Extract first quoted URL
                m = re.search(r"window\.open\('([^']+)'", onclick)
                if m:
                    link = m.group(1)

        item = {
            "title": title_el.get_text(strip=True) if title_el else "Untitled",
            "description": desc_el.get_text(strip=True) if desc_el else "",
            "date": date_el.get_text(strip=True) if date_el else None,
            "link": link,
            # Infer type from URL if possible; adjust to your rules
            "type": ("event" if (link and "events" in link) else
                     "job" if (link and "jobs" in link) else
                     "resource"),
            "show": True
        }
        items.append(item)
    return items

def scrape_iframe_page(iframe_url):
    """
    Try plain requests first. If we don't find items and Playwright is available,
    try a JS-rendered fetch.
    """
    # 1) Try standard HTTP fetch
    # try:
    #     html = get_html(iframe_url)
    #     print(html) 
    #     soup = BeautifulSoup(html, "html.parser")
    #     items = parse_items_from_soup(soup)
    #     print("standard")
    #     if items:
    #         return items
    # except Exception as e:
    #     print(f"Requests fetch failed for {iframe_url}: {e}")

    # 2) Fallback to Playwright (if enabled)
    if USE_PLAYWRIGHT:
        try:
            # If you know a selector that appears when items are rendered, put it here:
            html = load_html_with_playwright(iframe_url, wait_selector=".fw-feed-item")
            if html:
                soup = BeautifulSoup(html, "html.parser")
                items = parse_items_from_soup(soup)
                if items:
                    return items
        except Exception as e:
            print(f"Playwright fetch failed for {iframe_url}: {e}")

    # Nothing found
    return []

def scrape_main_page_and_iframes(page_url):
    """
    Pull items from the main page AND from any iframes it embeds.
    """
    all_items = []

    # Main page scrape (in case items are also present outside iframes)
    try:
        main_html = get_html(page_url)
        main_soup = BeautifulSoup(main_html, "html.parser")
        all_items.extend(parse_items_from_soup(main_soup))
    except Exception as e:
        print(f"Failed to fetch main page {page_url}: {e}")

    # Iframes
    try:
        iframe_srcs = extract_iframe_srcs(page_url)
        for src in iframe_srcs:
            print(f"→ Scraping iframe: {src}")
            items = scrape_iframe_page(src)
            all_items.extend(items)
    except Exception as e:
        print(f"Failed while processing iframes: {e}")

    # Deduplicate by link (if available)
    seen = set()
    deduped = []
    for it in all_items:
        key = it.get("link") or (it.get("title"), it.get("date"))
        if key not in seen:
            seen.add(key)
            deduped.append(it)

    return deduped

if __name__ == "__main__":
    # Example uses:

    # A) You have the MAIN PAGE URL that contains the iframe(s):
    MAIN_PAGE = "https://asccareersuccess.osu.edu/"
    items = scrape_main_page_and_iframes(MAIN_PAGE)
    print(f"Found {len(items)} items.")
    print(json.dumps(items[:3], indent=2, ensure_ascii=False))
    with open("datatest.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(items, indent=2, ensure_ascii=False))
    # B) Or you already have the iframe src from the page, e.g.:
    #    <iframe src="https://feed.mikle.com/widget/v2/171428/?preloader-text=Loading&"...>
    # Just call scrape_iframe_page directly:
    # iframe_src = "https://feed.mikle.com/widget/v2/171428/?preloader-text=Loading&"
    # items = scrape_iframe_page(iframe_src)
    # print(json.dumps(items[:3], indent=2, ensure_ascii=False))
