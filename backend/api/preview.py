from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging
import traceback
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class URLPreviewResponse(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    domain: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None

@router.get("/preview-url", response_model=URLPreviewResponse)
async def preview_url(url: str):
    try:
        logger.info(f"Received preview request for URL: {url}")
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            logger.info(f"Added https:// prefix to URL: {url}")

        # Parse URL to validate
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            logger.error(f"Invalid URL format: {url}")
            raise HTTPException(status_code=400, detail="Invalid URL format")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        # Create a session with custom SSL context
        session = requests.Session()
        session.verify = False  # Disable SSL verification
        session.trust_env = False  # Don't use environment variables for proxy settings
        
        logger.info(f"Fetching preview for URL: {url}")
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        logger.info(f"Successfully fetched URL content, status code: {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract metadata
        title = None
        description = None
        image = None
        author = None

        # Try to get title from meta tags first
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content")
            logger.info(f"Found og:title: {title}")
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text
                logger.info(f"Found title tag: {title}")

        # Get description
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            description = og_desc.get("content")
            logger.info("Found og:description")
        if not description:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                description = meta_desc.get("content")
                logger.info("Found meta description")

        # Get image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            image = og_image.get("content")
            # Convert relative image URL to absolute
            if image and not image.startswith(('http://', 'https://')):
                image = urljoin(url, image)
            logger.info(f"Found og:image: {image}")

        # Get author
        author_tag = soup.find("meta", attrs={"name": "author"})
        if author_tag:
            author = author_tag.get("content")
            logger.info(f"Found author: {author}")

        # If no title found, try to get it from the first h1 tag
        if not title:
            h1_tag = soup.find("h1")
            if h1_tag:
                title = h1_tag.text.strip()
                logger.info(f"Found h1 title: {title}")

        # If still no title, use the domain
        if not title:
            title = parsed_url.netloc
            logger.info(f"Using domain as title: {title}")

        result = {
            "title": title or "No Title",
            "description": description,
            "image": image,
            "domain": parsed_url.netloc,
            "author": author,
            "date": None
        }
        
        logger.info(f"Successfully generated preview for {url}")
        logger.debug(f"Preview data: {result}")
        return result

    except requests.exceptions.SSLError as e:
        logger.error(f"SSL Error for URL {url}: {str(e)}")
        raise HTTPException(status_code=400, detail="SSL certificate verification failed")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error for URL {url}: {str(e)}")
        raise HTTPException(status_code=400, detail="Could not connect to the URL")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout Error for URL {url}: {str(e)}")
        raise HTTPException(status_code=400, detail="Request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error for URL {url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error for URL {url}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing URL preview: {str(e)}")
    finally:
        # Suppress only the single warning from urllib3 needed.
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
