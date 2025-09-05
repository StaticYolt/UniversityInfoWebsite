import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# ---- OPTIONAL Playwright fallback ----
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

# ---- MongoDB setup ----

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
DB_NAME = "Feeddata"
client = MongoClient(mongo_uri)
db = client[DB_NAME]

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
    """Return absolute iframe src URLs from the main page."""
    html = get_html(page_url)
    soup = BeautifulSoup(html, "html.parser")
    return [urljoin(page_url, iframe.get("src")) for iframe in soup.find_all("iframe") if iframe.get("src")]

def parse_items_from_soup(soup):
    """Parse items into normalized dicts."""
    items = []
    for div in soup.select(".fw-feed-item"):
        title_el = div.select_one(".fw-feed-item-title")
        desc_el = div.select_one(".fw-feed-item-description")
        date_el = div.select_one(".fw-feed-item-date")
        link = None

        clickable = div.select_one(".fw-feed-item-url")
        if clickable:
            onclick = clickable.get("onclick") or clickable.get("onkeypress")
            if onclick:
                m = re.search(r"window\.open\('([^']+)'", onclick)
                if m:
                    link = m.group(1)

        item_type = "resource"
        if link:
            if "events" in link:
                item_type = "event"
            elif "jobs" in link:
                item_type = "job"

        items.append({
            "title": title_el.get_text(strip=True) if title_el else "Untitled",
            "description": desc_el.get_text(strip=True) if desc_el else "",
            "date": date_el.get_text(strip=True) if date_el else None,
            "link": link,
            "type": item_type,
            "show": True
        })
    return items

def scrape_iframe_page(iframe_url):
    """Scrape inside iframe using requests or Playwright."""
    if USE_PLAYWRIGHT:
        try:
            html = load_html_with_playwright(iframe_url, wait_selector=".fw-feed-item")
            if html:
                return parse_items_from_soup(BeautifulSoup(html, "html.parser"))
        except Exception as e:
            print(f"Playwright fetch failed for {iframe_url}: {e}")
    return []

def scrape_main_page_and_iframes(page_url):
    all_items = []

    try:
        main_html = get_html(page_url)
        main_soup = BeautifulSoup(main_html, "html.parser")
        all_items.extend(parse_items_from_soup(main_soup))
    except Exception as e:
        print(f"Failed to fetch main page {page_url}: {e}")

    try:
        for src in extract_iframe_srcs(page_url):
            print(f"→ Scraping iframe: {src}")
            all_items.extend(scrape_iframe_page(src))
    except Exception as e:
        print(f"Failed while processing iframes: {e}")

    # Deduplicate
    seen, deduped = set(), []
    for it in all_items:
        key = it.get("link") or (it.get("title"), it.get("date"))
        if key not in seen:
            seen.add(key)
            deduped.append(it)
    return deduped

def save_to_mongodb(items):
    """Insert items into jobs, events, resources collections."""
    for item in items:
        collection = db[item["type"] + "s"]  # jobs, events, resources
        # upsert by link (or title+date if link missing)
        query = {"link": item["link"]} if item["link"] else {"title": item["title"], "date": item["date"]}
        collection.update_one(query, {"$set": item}, upsert=True)

if __name__ == "__main__":
    MAIN_PAGE = "https://asccareersuccess.osu.edu/"
    items = scrape_main_page_and_iframes(MAIN_PAGE)
    print(f"✅ Found {len(items)} items.")
    save_to_mongodb(items)
    print("✅ Data saved to MongoDB.")
