"""
Web Search Tools for ABC AI Agent
Provides web search via headless browser (no API key required)
Uses Playwright to scrape Google search results
"""

import logging
import asyncio
from typing import Dict, List, Optional
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

# Try to import playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("playwright not installed. Web search capability disabled.")


class WebSearchTools:
    """Web search tools using headless browser"""
    
    def __init__(self):
        """Initialize web search tools"""
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("playwright is required for web search")
        
        logger.info("🔍 Web search tools initialized")
    
    async def _search_google(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search Google using headless browser
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Navigate to Google
                search_url = f"https://www.google.com/search?q={quote_plus(query)}"
                await page.goto(search_url, wait_until='networkidle', timeout=30000)
                
                # Wait for search results to load
                await page.wait_for_selector('div#gws-output-pages-elements-homepage', timeout=10000)
                
                # Extract search results
                search_results = await page.query_selector_all('div.g')
                
                for i, result in enumerate(search_results[:num_results]):
                    try:
                        # Extract title
                        title_elem = await result.query_selector('h3')
                        title = await title_elem.inner_text() if title_elem else 'No title'
                        
                        # Extract URL
                        link_elem = await result.query_selector('a')
                        url = await link_elem.get_attribute('href') if link_elem else ''
                        
                        # Extract snippet
                        snippet_elem = await result.query_selector('div.VwiC3b, span.aCOpRe')
                        snippet = await snippet_elem.inner_text() if snippet_elem else ''
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                    except Exception as e:
                        logger.debug(f"Failed to parse result {i}: {e}")
                        continue
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            raise
        
        return results
    
    async def _fetch_page(self, url: str) -> str:
        """
        Fetch and extract text content from a webpage
        
        Args:
            url: URL to fetch
            
        Returns:
            Extracted text content
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Extract main content
                # Try to find main content area
                content_selectors = [
                    'article',
                    'main',
                    '[role="main"]',
                    '.content',
                    '.post-content',
                    '.entry-content',
                    '#content',
                    'body'
                ]
                
                content = ''
                for selector in content_selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            content = await elem.inner_text()
                            if len(content) > 100:
                                break
                    except:
                        continue
                
                await browser.close()
                
                # Clean up content
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                content = '\n'.join(lines[:50])  # Limit to 50 lines
                
                return content
                
        except Exception as e:
            logger.error(f"Page fetch failed: {e}")
            raise
    
    def search(self, query: str, num_results: int = 5) -> Dict:
        """
        Search the web (synchronous wrapper)
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            Dict with search results
        """
        try:
            results = asyncio.run(self._search_google(query, num_results))
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'count': len(results)
            }
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def fetch_page(self, url: str) -> Dict:
        """
        Fetch a webpage (synchronous wrapper)
        
        Args:
            url: URL to fetch
            
        Returns:
            Dict with page content
        """
        try:
            content = asyncio.run(self._fetch_page(url))
            
            return {
                'success': True,
                'url': url,
                'content': content[:3000] + '...' if len(content) > 3000 else content
            }
            
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def detect_and_execute(self, message: str) -> Optional[Dict]:
        """
        Detect web search commands and execute them
        
        Args:
            message: User message
            
        Returns:
            Result dict if a web command was executed
        """
        import re
        msg_lower = message.lower().strip()
        
        # Search web: "search for X" or "google X" or "web search X"
        search_patterns = [
            r'(?:search|google|look\s+up|find)\s+(?:for\s+)?["\']?(.+?)["\']?$',
            r'(?:web\s+search|search\s+web)\s+["\']?(.+?)["\']?$',
            r'what\s+is\s+["\']?(.+?)["\']?\s+(?:on\s+the\s+web|online)',
        ]
        for pattern in search_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                query = match.group(1).strip()
                return self.search(query, num_results=5)
        
        # Fetch page: "fetch URL" or "get page URL" or "read URL"
        fetch_patterns = [
            r'(?:fetch|get|read|scrape)\s+(?:page\s+)?["\']?(https?://[^\s"\']+)["\']?',
            r'(?:what\s+is\s+on|what\s+is\s+at)\s+["\']?(https?://[^\s"\']+)["\']?',
        ]
        for pattern in fetch_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                url = match.group(1).strip()
                return self.fetch_page(url)
        
        return None


# For testing
if __name__ == "__main__":
    print("Testing WebSearchTools...")
    try:
        tools = WebSearchTools()
        
        print("\nTesting search...")
        result = tools.search("python programming", num_results=3)
        if result.get('success'):
            print(f"Found {result['count']} results")
            for r in result['results'][:2]:
                print(f"  - {r['title'][:50]}...")
        else:
            print(f"Error: {result.get('error')}")
        
        print("\n✅ Web search test completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
