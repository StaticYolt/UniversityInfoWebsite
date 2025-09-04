import json

def generate_html(sections, output_file="output.html"):
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <title>University Resources</title>",
        "  <style>",
        "    body { font-family: sans-serif; background: #fdfdfd; margin: 0; padding: 0; }",
        "    .section { padding: 20px; border-bottom: 1px solid #ddd; }",
        "    h1, h2, h3 { margin: 0 0 10px 0; }",
        "    p, li { margin: 5px 0; }",
        "    a { color: #0066cc; text-decoration: none; }",
        "    a:hover { text-decoration: underline; }",
        "    img { max-width: 100%; height: auto; display: block; margin: 10px 0; }",
        "  </style>",
        "</head>",
        "<body>",
    ]

    for section in sections:
        if not section.get("show", True):
            continue  # skip hidden sections
        html_parts.append("<div class='section'>")
        for item in section["content"]:
            if item["type"] in ["h1", "h2", "h3"]:
                html_parts.append(f"<{item['type']}>{item['text']}</{item['type']}>")
            elif item["type"] == "p":
                html_parts.append(f"<p>{item['text']}</p>")
            elif item["type"] == "li":
                html_parts.append(f"<li>{item['text']}</li>")
            elif item["type"] == "link":
                html_parts.append(f"<a href='{item['href']}' target='_blank'>{item['text']}</a>")
            elif item["type"] == "img":
                html_parts.append(f"<img src='{item['src']}' alt='{item['alt']}'>")
        html_parts.append("</div>")

    html_parts.extend(["</body>", "</html>"])

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))

    print(f"✅ HTML generated at {output_file}")


if __name__ == "__main__":
    with open("output.json", "r", encoding="utf-8") as f:
        sections = json.load(f)
    generate_html(sections, "resources.html")
