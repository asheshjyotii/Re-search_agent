from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
import os
from rich import print

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

print(search_query.invoke("Latest news on the war"))