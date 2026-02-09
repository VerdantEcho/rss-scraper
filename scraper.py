import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import html

# Configuration
URL = "https://wanderinginn.com/table-of-contents/"
OUTPUT_FILE = "feed.xml"

def get_date_from_url(url):
    """
    Extracts date from URL structure like: 
    https://wanderinginn.com/2018/04/10/4-27-h/
    Returns an RSS-compliant date string or None.
    """
    match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    if match:
        year, month, day = map(int, match.groups())
        try:
            date_obj = datetime(year, month, day)
            # RSS Date Format: Sat, 07 Sep 2002 00:00:01 GMT
            return date_obj.strftime("%a, %d %b %Y 00:00:00 +0000")
        except ValueError:
            return None
    return None

def generate_rss():
    print(f"Fetching {URL}...")
    try:
        response = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Select all anchor tags inside divs with class "chapter-entry"
    links = soup.select('div.chapter-entry a')
    print(f"Found {len(links)} chapters.")

    # Start RSS content
    rss_content = [
        '<?xml version="1.0" encoding="UTF-8" ?>',
        '<rss version="2.0">',
        '<channel>',
        '<title>The Wandering Inn (Full History)</title>',
        f'<link>{URL}</link>',
        '<description>Automated feed of all Wandering Inn chapters.</description>',
        '<language>en-us</language>'
    ]

    # Process links in REVERSE order (RSS readers expect newest items first)
    # The TOC page lists them Oldest -> Newest, so we reverse extraction.
    for link in reversed(links):
        title = link.get_text().strip()
        href = link.get('href')
        
        # Skip empty links or anchors without href
        if not href or not title:
            continue
            
        pub_date = get_date_from_url(href)
        
        # Use a fallback date if URL scraping fails (optional, but good for validation)
        if not pub_date:
            # Fallback to a generic format or skip date tag
            pub_date_tag = ""
        else:
            pub_date_tag = f"<pubDate>{pub_date}</pubDate>"

        # Construct item
        item = f"""
        <item>
            <title>{html.escape(title)}</title>
            <link>{href}</link>
            <guid>{href}</guid>
            {pub_date_tag}
        </item>"""
        rss_content.append(item)

    # Close RSS
    rss_content.append('</channel>')
    rss_content.append('</rss>')

    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rss_content))
    
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_rss()
