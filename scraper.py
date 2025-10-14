import requests
from bs4 import BeautifulSoup

URL = "https://news.ycombinator.com/"
OUTPUT_FILE = "headlines.txt"

def fetch_html(url):
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        print("⏳ Request timed out.")
    except requests.exceptions.RequestException as e:
        print("⚠️ Request failed:", e)
    return None

def extract_headlines(html):
    soup = BeautifulSoup(html, "html.parser")
    headlines = [a.get_text(strip=True) for a in soup.select(".titleline a")]
    return headlines

def save_to_file(headlines, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for line in headlines:
            f.write(line + "\n")
    print(f"✅ Saved {len(headlines)} headlines to {filename}")

def main():
    html = fetch_html(URL)
    if html:
        headlines = extract_headlines(html)
        if headlines:
            save_to_file(headlines, OUTPUT_FILE)
            print("Some headlines collected:")
            for h in headlines[:5]:
                print("-", h)
        else:
            print("No headlines found.")

if __name__ == "__main__":
    main()
