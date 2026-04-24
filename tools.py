from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
import os
from rich import print
import requests
from bs4 import BeautifulSoup

load_dotenv()

tavily = TavilyClient(os.getenv("TAVILY_API_KEY"))

@tool
def search_query(query : str) -> str:
    """Search the web for a given query, takes str as input and ouputs str as result"""

    results = tavily.search(query=query, max_results=20)
    
    rs = []

    for result in results["results"]:
        title = result["title"]
        content = result["content"][:100]
        url = result["url"]

        rs.append(f"Title: {title}\nContent: {content}\nURL: {url}")
    return "\n\n--------------------\n\n".join(rs)


@tool
def page_fetch(url: str) -> str:
    """Fetch a web page and return the content, takes str (url) as input and ouputs str as result"""

    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove undesired tags
        for tag in soup(['script', 'style', 'nav', 'footer']):
                tag.decompose()

        text = soup.get_text(separator=" ", strip=True)[:3000]
        return text
    except Exception as err:
        return f"Could not fetch the url err : {err}"

print(page_fetch.invoke('https://en.wikipedia.org/wiki/List_of_ongoing_armed_conflicts'))