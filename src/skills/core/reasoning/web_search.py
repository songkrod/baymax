import requests
from bs4 import BeautifulSoup


def search_web(query: str, top_k: int = 3) -> str:
    """
    Basic web search using DuckDuckGo HTML results (no API key required).
    """
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for a in soup.select("a.result__a")[:top_k]:
            text = a.get_text()
            href = a.get("href")
            results.append(f"- {text} ({href})")
        return "\n".join(results) if results else "ไม่พบข้อมูลที่เกี่ยวข้องครับ"
    except Exception as e:
        return f"ขออภัย ผมหาข้อมูลไม่ได้เนื่องจาก: {e}"