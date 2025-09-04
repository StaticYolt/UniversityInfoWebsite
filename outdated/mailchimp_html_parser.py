from bs4 import BeautifulSoup
import uuid
import json

def parse_mailchimp_html(html):
    soup = BeautifulSoup(html, "html.parser")
    sections = []

    # Each section could be separated by <h1>, <h2>, or sometimes big <table> blocks
    # For simplicity, let's treat each <h1>/<h2>/<h3> as the start of a new section
    current_section = {"id": str(uuid.uuid4()), "content": [], "show": True}

    for tag in soup.find_all(["h1", "h2", "h3", "p", "a", "img", "li"]):
        if tag.name in ["h1", "h2", "h3"]:
            # Start new section if current already has content
            if current_section["content"]:
                sections.append(current_section)
                current_section = {"id": str(uuid.uuid4()), "content": [], "show": True}
            current_section["content"].append({"type": tag.name, "text": tag.get_text(strip=True)})

        elif tag.name == "p":
            text = tag.get_text(strip=True)
            if text:
                current_section["content"].append({"type": "p", "text": text})

        elif tag.name == "a":
            href = tag.get("href", "#")
            if href.startswith("https://www.facebook.com/ASCCareerSuccess/"):
                break
            text = tag.get_text(strip=True) or href
            current_section["content"].append({
                "type": "link",
                "text": text,
                "href": href
            })

        elif tag.name == "img":
            src = tag.get("src", "")
            alt = tag.get("alt", "")
            current_section["content"].append({
                "type": "img",
                "src": src,
                "alt": alt
            })

        elif tag.name == "li":
            text = tag.get_text(strip=True)
            if text:
                current_section["content"].append({"type": "li", "text": text})

    # Add last section
    if current_section["content"]:
        sections.append(current_section)
    
    return sections[1:]


# Example usage
if __name__ == "__main__":
    with open("sample_mailchimp.html", "r", encoding="utf-8") as f:
        html = f.read()

    parsed_sections = parse_mailchimp_html(html)

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(parsed_sections, f, indent=2)

    print("✅ Extracted sections saved to sections.json")
