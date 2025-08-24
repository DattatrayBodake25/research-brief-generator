import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from langchain.tools import Tool
from tavily import TavilyClient
from langchain_community.utilities.serpapi import SerpAPIWrapper
from src.utils.config import settings
from src.utils.logger import logger

class SearchTools:
    """Collection of search tools for research"""

    @staticmethod
    def get_available_tools() -> List[Tool]:
        tools = []

        # Tavily Search
        if settings.tavily_api_key:
            tavily_client = TavilyClient(api_key=settings.tavily_api_key)

            def tavily_search_func(query: str) -> List[Dict[str, Any]]:
                try:
                    result = tavily_client.search(query)
                    normalized_results = []

                    if isinstance(result, dict) and 'results' in result:
                        for item in result['results']:
                            normalized_results.append({
                                "title": item.get("title", query),
                                "url": item.get("url", ""),
                                "snippet": item.get("content", "No content")
                            })
                    else:
                        normalized_results.append({
                            "title": query,
                            "url": "",
                            "snippet": str(result)
                        })
                    return normalized_results

                except Exception as e:
                    logger.error(f"Tavily search error: {e}")
                    return [{"title": f"Error: {e}", "url": "", "snippet": ""}]

            tools.append(Tool(
                name="tavily_search",
                description="Search for information using Tavily",
                func=tavily_search_func
            ))

        # SerpAPI Search
        if settings.serpapi_api_key:
            serpapi_search = SerpAPIWrapper(serpapi_api_key=settings.serpapi_api_key)

            def serpapi_search_func(query: str) -> List[Dict[str, Any]]:
                try:
                    result = serpapi_search.run(query)
                    normalized_results = []

                    if isinstance(result, dict) and 'organic_results' in result:
                        for item in result['organic_results']:
                            normalized_results.append({
                                "title": item.get('title', query),
                                "url": item.get('link', ""),
                                "snippet": item.get('snippet', 'No snippet')
                            })
                    elif isinstance(result, list):
                        for item in result:
                            if isinstance(item, dict):
                                normalized_results.append({
                                    "title": item.get("title", query),
                                    "url": item.get("url", item.get("link", "")),
                                    "snippet": item.get("snippet", item.get("content", "No content"))
                                })
                    else:
                        normalized_results.append({
                            "title": query,
                            "url": "",
                            "snippet": str(result)
                        })
                    return normalized_results
                except Exception as e:
                    logger.error(f"SerpAPI search error: {e}")
                    return [{"title": f"Error: {e}", "url": "", "snippet": ""}]

            tools.append(Tool(
                name="serpapi_search",
                description="Search Google using SerpAPI",
                func=serpapi_search_func
            ))

        # Mock fallback
        if not tools:
            logger.warning("No search tools configured. Using mock search.")
            def mock_search_func(query: str) -> List[Dict[str, Any]]:
                return [
                    {"title": f"Research on {query}", "url": "https://example.com", "snippet": f"Mock content for {query}"}
                ]
            tools.append(Tool(
                name="mock_search",
                description="Mock search for testing",
                func=mock_search_func
            ))

        return tools

    @staticmethod
    async def async_search(query: str, tool_name: str = "tavily_search") -> List[Dict[str, Any]]:
        try:
            tools = SearchTools.get_available_tools()
            tool = next((t for t in tools if t.name == tool_name), None)

            if not tool:
                logger.warning(f"Tool {tool_name} not found, using mock search")
                tool = next((t for t in tools if t.name == "mock_search"), None)
                if not tool:
                    return []

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, tool.func, query)

            # Ensure consistent structure
            normalized_results = []
            for item in result:
                if isinstance(item, dict):
                    normalized_results.append({
                        "title": item.get("title", query),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", item.get("content", "No content"))
                    })
                else:
                    normalized_results.append({
                        "title": str(item),
                        "url": "",
                        "snippet": ""
                    })
            return normalized_results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

# Add this method to the ContentFetcher class in src/core/tools.py

class ContentFetcher:
    """Tool for fetching web content"""

    @staticmethod
    async def fetch_url_content(url: str) -> Optional[str]:
        if not url or not url.startswith(('http://', 'https://')):
            logger.warning(f"Invalid URL provided: {url}")
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30, headers={"User-Agent": "ResearchBriefGenerator/1.0"}, ssl=False) as response:
                    if response.status == 200:
                        content = await response.text()
                        return content[:10000] if len(content) > 10000 else content
                    else:
                        logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Content fetch error for {url}: {e}")
            return None

    # ADD THIS MISSING METHOD
    @staticmethod
    async def fetch_with_fallback(url: str, fallback_snippet: str = "") -> str:
        """Fetch content with multiple fallback strategies"""
        content = await ContentFetcher.fetch_url_content(url)
        
        if content:
            return content
        
        # If direct fetching fails, try to use the snippet or create meaningful content
        if fallback_snippet:
            return f"Original content unavailable. Based on search result: {fallback_snippet}"
        
        # Final fallback - generate content based on URL
        if "research" in url or "study" in url or "academic" in url:
            return "This appears to be a research paper or academic article. The full content could not be retrieved due to access restrictions."
        elif "news" in url or "article" in url or "blog" in url:
            return "This appears to be a news article or blog post. The full content could not be retrieved due to access restrictions."
        else:
            return "Web content unavailable due to access restrictions. Please visit the URL directly for full content."

# Export tools
search_tools = SearchTools()
content_fetcher = ContentFetcher()