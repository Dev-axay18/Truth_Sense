import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import logging
from typing import List, Dict, Optional
import pandas as pd
from tqdm import tqdm
import time
import random
import re
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsDataCollector:
    def __init__(self, output_dir: str = "training_data"):
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(current_dir, output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # List of trusted news sources with their main sections
        self.trusted_sources = {
            'reuters.com': ['/world/', '/technology/', '/science/', '/business/', '/health/'],
            'apnews.com': ['/world/', '/science/', '/technology/', '/business/', '/health/'],
            'bbc.com': ['/news/world/', '/news/science/', '/news/technology/', '/news/business/', '/news/health/'],
            'nytimes.com': ['/world/', '/science/', '/technology/', '/business/', '/health/'],
            'washingtonpost.com': ['/world/', '/science/', '/technology/', '/business/', '/health/'],
            'theguardian.com': ['/world/', '/science/', '/technology/', '/business/', '/health/'],
            'aljazeera.com': ['/news/', '/science-and-technology/', '/business/', '/health/'],
            'timesofindia.indiatimes.com': ['/world/', '/science/', '/business/', '/health/'],
            'indianexpress.com': ['/world-news/', '/technology/', '/business/', '/health/'],
            'thehindu.com': ['/international/', '/sci-tech/', '/business/', '/health/'],
            'ndtv.com': ['/world-news/', '/science/', '/business/', '/health/'],
            'hindustantimes.com': ['/world-news/', '/science/', '/business/', '/health/'],
            'nature.com': ['/news/', '/articles/'],  # Added scientific journal
            'science.org': ['/news/', '/research/'],  # Added scientific journal
            'scientificamerican.com': ['/articles/', '/news/']  # Added science magazine
        }
        
        # List of unreliable sources
        self.unreliable_sources = [
            'infowars.com',
            'naturalnews.com',
            'beforeitsnews.com',
            'worldtruth.tv',
            'yournewswire.com',
            'conspiracyplanet.com',
            'thetruthwins.com',
            'humansarefree.com',
            'wakingtimes.com',
            'collective-evolution.com',
            'davidwolfe.com',
            'healthimpactnews.com',
            'healthnutnews.com',
            'mercola.com',
            'prisonplanet.com',
            'globalresearch.ca',  # Added more unreliable sources
            'activistpost.com',
            'truthout.org',
            'counterpunch.org',
            'alternet.org',
            'truthdig.com',
            'commondreams.org',
            'rawstory.com',
            'salon.com',
            'huffpost.com'
        ]

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?;:\'\"()-]', '', text)
        # Remove multiple punctuation
        text = re.sub(r'([.,!?;:])\1+', r'\1', text)
        return text.strip()

    def get_article_urls(self, base_url: str, section: str = "") -> List[str]:
        """Get article URLs from a news section."""
        try:
            url = urljoin(base_url, section)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article links
            article_urls = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                
                # Filter for article URLs
                if any(keyword in href.lower() for keyword in ['article', 'news', 'story', 'report', 'analysis']):
                    # Skip non-article URLs
                    if any(skip in href.lower() for skip in ['video', 'gallery', 'photo', 'slideshow', 'login', 'signup']):
                        continue
                    article_urls.append(href)
            
            return list(set(article_urls))  # Remove duplicates
        except Exception as e:
            logger.error(f"Error getting article URLs from {url}: {str(e)}")
            return []

    def collect_article(self, url: str) -> Optional[Dict]:
        """Collect a single article's content and metadata."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract article content
            article_text = ' '.join([p.text for p in soup.find_all('p')])
            article_text = self.clean_text(article_text)
            
            # Extract metadata
            title = soup.find('meta', property='og:title')
            title = title.get('content') if title else None
            if title:
                title = self.clean_text(title)
            
            description = soup.find('meta', property='og:description')
            description = description.get('content') if description else None
            if description:
                description = self.clean_text(description)
            
            author = soup.find('meta', property='article:author')
            author = author.get('content') if author else None
            
            date = soup.find('meta', property='article:published_time')
            date = date.get('content') if date else None
            
            # Determine credibility based on source
            domain = urlparse(url).netloc
            is_credible = domain in self.trusted_sources
            is_unreliable = domain in self.unreliable_sources
            
            # Skip if no content or too short
            if not article_text or len(article_text.split()) < 150:  # Increased minimum length
                return None
            
            # Skip if missing essential metadata
            if not title or not description:
                return None
            
            # Skip if content seems like a list or gallery
            if len(article_text.split()) > 1000 and any(keyword in title.lower() for keyword in ['top', 'list', 'gallery', 'slideshow']):
                return None
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content': article_text,
                'author': author,
                'date': date,
                'domain': domain,
                'is_credible': is_credible,
                'is_unreliable': is_unreliable,
                'word_count': len(article_text.split())
            }
        except Exception as e:
            logger.error(f"Error collecting article from {url}: {str(e)}")
            return None

    def save_articles(self, articles: List[Dict], filename: str):
        """Save collected articles to a JSON file."""
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(articles)} articles to {output_path}")

    def prepare_training_data(self, input_file: str, output_file: str):
        """Prepare collected data for model training."""
        # Read collected articles
        input_path = os.path.join(self.output_dir, input_file)
        with open(input_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(articles)
        
        # Create labels
        df['label'] = df.apply(lambda x: 1 if x['is_credible'] else 0, axis=1)
        
        # Prepare text for training
        df['text'] = df.apply(lambda x: f"Title: {x['title']}\nDescription: {x['description']}\nContent: {x['content']}", axis=1)
        
        # Save prepared data
        output_path = os.path.join(self.output_dir, output_file)
        df[['text', 'label']].to_csv(output_path, index=False)
        logger.info(f"Prepared training data saved to {output_path}")

def main():
    collector = NewsDataCollector()
    articles = []
    
    # Collect from trusted sources
    for domain, sections in collector.trusted_sources.items():
        base_url = f"https://www.{domain}"
        for section in sections:
            logger.info(f"Collecting articles from {base_url}{section}")
            article_urls = collector.get_article_urls(base_url, section)
            
            for url in tqdm(article_urls[:15], desc=f"Processing {domain}"):  # Increased to 15 articles per section
                article = collector.collect_article(url)
                if article:
                    articles.append(article)
                time.sleep(2)  # Increased delay to be nicer to servers
    
    # Collect from unreliable sources
    for domain in collector.unreliable_sources:
        base_url = f"https://www.{domain}"
        logger.info(f"Collecting articles from {base_url}")
        article_urls = collector.get_article_urls(base_url)
        
        for url in tqdm(article_urls[:15], desc=f"Processing {domain}"):  # Increased to 15 articles per source
            article = collector.collect_article(url)
            if article:
                articles.append(article)
            time.sleep(2)  # Increased delay to be nicer to servers
    
    # Save collected articles
    collector.save_articles(articles, "collected_articles.json")
    
    # Prepare training data
    collector.prepare_training_data("collected_articles.json", "training_data.csv")

if __name__ == "__main__":
    main() 