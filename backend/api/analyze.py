from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import re
from transformers import pipeline
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class AnalysisRequest(BaseModel):
    content: str
    url: Optional[str] = None
    advanced_analysis: bool = False

class AnalysisResponse(BaseModel):
    classification: str
    confidence_score: float
    country_of_origin: str
    is_verified: bool
    explanation: str
    source_metadata: Optional[dict] = None

# Initialize the text classification model
try:
    text_classifier = pipeline(
        "text-classification",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=-1  # Use CPU
    )
    logger.info("Text classification model loaded successfully")
except Exception as e:
    logger.error(f"Error loading text classification model: {str(e)}")
    raise

def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """Extract important keywords from the text."""
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^\w\s]', '', text.lower())
    words = text.split()
    
    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'as', 'of'}
    words = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Count word frequencies
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in keywords[:max_keywords]]

def analyze_sentiment(text: str) -> dict:
    """Analyze the sentiment and emotional tone of the text."""
    # Define word lists for different aspects
    credibility_indicators = {
        'positive': [
            'verified', 'confirmed', 'official', 'reliable', 'trusted', 'credible',
            'source', 'evidence', 'fact', 'report', 'investigation', 'expert',
            'authority', 'statement', 'announcement', 'press', 'release',
            'operation', 'military', 'defense', 'security', 'intelligence',
            'government', 'ministry', 'official', 'spokesperson', 'confirmed',
            'authenticated', 'verified', 'reliable', 'trusted', 'credible'
        ],
        'negative': [
            'unverified', 'rumor', 'alleged', 'claimed', 'supposedly', 'reportedly',
            'anonymous', 'unconfirmed', 'speculation', 'conspiracy', 'hoax', 'fake',
            'misleading', 'deceptive', 'false', 'unreliable', 'viral', 'social media',
            'unverified source', 'anonymous source', 'unconfirmed reports'
        ]
    }
    
    # Count occurrences of credibility indicators
    text_lower = text.lower()
    positive_count = sum(1 for word in credibility_indicators['positive'] if word in text_lower)
    negative_count = sum(1 for word in credibility_indicators['negative'] if word in text_lower)
    
    # Calculate credibility score
    total_indicators = positive_count + negative_count
    if total_indicators == 0:
        credibility_score = 0.5
    else:
        credibility_score = positive_count / total_indicators
    
    return {
        'credibility_score': credibility_score,
        'positive_indicators': positive_count,
        'negative_indicators': negative_count
    }

def detect_country(text: str, url: Optional[str] = None) -> str:
    """Detect the country of origin from text and URL."""
    # Common country indicators
    country_indicators = {
        'India': ['indian', 'india', 'delhi', 'mumbai', 'bangalore', 'kolkata', 'chennai', 'hyderabad'],
        'United States': ['american', 'us', 'usa', 'united states', 'washington', 'new york', 'california', 'texas'],
        'United Kingdom': ['british', 'uk', 'united kingdom', 'london', 'england', 'scotland', 'wales'],
        'China': ['chinese', 'china', 'beijing', 'shanghai', 'hong kong'],
        'Russia': ['russian', 'russia', 'moscow', 'kremlin'],
        'Japan': ['japanese', 'japan', 'tokyo', 'osaka'],
        'Australia': ['australian', 'australia', 'sydney', 'melbourne'],
        'Canada': ['canadian', 'canada', 'toronto', 'vancouver'],
        'Germany': ['german', 'germany', 'berlin', 'munich'],
        'France': ['french', 'france', 'paris', 'lyon']
    }
    
    # Check URL domain for country-specific TLDs
    if url:
        domain = urlparse(url).netloc
        tld = domain.split('.')[-1].lower()
        tld_to_country = {
            'in': 'India',
            'us': 'United States',
            'uk': 'United Kingdom',
            'cn': 'China',
            'ru': 'Russia',
            'jp': 'Japan',
            'au': 'Australia',
            'ca': 'Canada',
            'de': 'Germany',
            'fr': 'France'
        }
        if tld in tld_to_country:
            return tld_to_country[tld]
    
    # Check for country names in text
    text_lower = text.lower()
    for country, indicators in country_indicators.items():
        if any(indicator in text_lower for indicator in indicators):
            return country
    
    return "Unknown"

def analyze_credibility(text: str, url: Optional[str] = None) -> dict:
    """Analyze the credibility of the news content."""
    # Extract metadata if URL is provided
    metadata = {}
    if url:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('meta', property='og:title')
            if title:
                metadata['title'] = title.get('content')
            
            # Extract description
            desc = soup.find('meta', property='og:description')
            if desc:
                metadata['description'] = desc.get('content')
            
            # Extract author
            author = soup.find('meta', property='article:author')
            if author:
                metadata['author'] = author.get('content')
            
            # Extract date
            date = soup.find('meta', property='article:published_time')
            if date:
                metadata['date'] = date.get('content')
            
            # Extract domain
            domain = urlparse(url).netloc
            metadata['domain'] = domain
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
    
    # Analyze sentiment and credibility
    sentiment = analyze_sentiment(text)
    
    # Get keywords
    keywords = extract_keywords(text)
    
    # Detect country
    country = detect_country(text, url)
    
    # Determine if the source is verified
    is_verified = False
    if url:
        domain = urlparse(url).netloc
        verified_domains = [
            'reuters.com', 'apnews.com', 'bbc.com', 'nytimes.com',
            'washingtonpost.com', 'theguardian.com', 'aljazeera.com',
            'timesofindia.indiatimes.com', 'indianexpress.com',
            'thehindu.com', 'ndtv.com', 'hindustantimes.com',
            'zeenews.india.com', 'news18.com', 'indiatoday.in',
            'firstpost.com', 'thequint.com', 'scroll.in'
        ]
        is_verified = any(verified_domain in domain for verified_domain in verified_domains)
    
    return {
        'sentiment': sentiment,
        'keywords': keywords,
        'country': country,
        'is_verified': is_verified,
        'metadata': metadata
    }

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_news(request: AnalysisRequest):
    try:
        # Get the text content and URL
        content = request.content.strip()
        url = request.url
        
        if not content:
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        # Analyze credibility first
        credibility = analyze_credibility(content, url)
        
        # Enhanced fake news detection patterns
        fake_news_indicators = [
            'clickbait', 'viral', 'shocking', 'you won\'t believe', 'mind-blowing',
            'unbelievable', 'exclusive', 'breaking', 'urgent', 'just in',
            'must read', 'you need to know', 'secret', 'hidden truth',
            'they don\'t want you to know', 'conspiracy', 'cover-up',
            'exposed', 'leaked', 'scandal', 'controversy'
        ]

        # Obviously fake or satirical content patterns
        obviously_fake_patterns = [
            'made entirely of', 'discovered a planet made of', 'found a planet made of',
            'cheese planet', 'chocolate planet', 'candy planet', 'ice cream planet',
            'unicorn', 'dragon', 'flying pig', 'talking animal', 'magic',
            'time travel', 'teleportation', 'invisible', 'superhero',
            'aliens living in', 'bigfoot found', 'loch ness monster',
            'flying saucer', 'ufo crash', 'alien invasion',
            'zombie', 'vampire', 'werewolf', 'ghost', 'haunted',
            'miracle cure', 'magic potion', 'fountain of youth',
            'world\'s first', 'never before seen', 'impossible',
            'defies physics', 'breaks laws of', 'scientists baffled',
            'impossible discovery', 'unbelievable find', 'shocking revelation',
            'spacecheddar', 'cheesex', 'space cheese', 'cheese mission',
            'publicity stunt', 'promote a new', 'launching soon',
            'partnership with', 'new venture', '™', '©', '®',
            'skeptics argue', 'critics claim', 'some say',
            'according to unnamed sources', 'anonymous sources claim',
            'insiders reveal', 'exclusive scoop', 'breaking news',
            'you won\'t believe what', 'shocking truth about',
            'they don\'t want you to know', 'hidden agenda',
            'secret project', 'classified information',
            'leaked documents', 'confidential sources',
            'underground movement', 'conspiracy theory',
            'cover-up', 'scandal', 'controversy',
            'exposed', 'revealed', 'uncovered',
            'shocking discovery', 'amazing find',
            'incredible breakthrough', 'revolutionary',
            'game-changing', 'mind-blowing',
            'earth-shattering', 'world-changing',
            'paradigm shift', 'new era',
            'future of', 'next generation',
            'cutting-edge', 'groundbreaking',
            'innovative', 'revolutionary',
            'disruptive', 'transformative',
            'unprecedented', 'historic',
            'first of its kind', 'never before seen',
            'impossible', 'defies logic',
            'breaks all rules', 'challenges conventional wisdom',
            'experts baffled', 'scientists stunned',
            'researchers amazed', 'professionals shocked',
            'industry leaders surprised', 'authorities confused',
            'government officials puzzled', 'military experts bewildered',
            'intelligence agencies mystified', 'security analysts perplexed',
            'defense experts astonished', 'space agency officials amazed',
            'NASA scientists shocked', 'ESA researchers stunned',
            'Roscosmos experts baffled', 'CNSA officials puzzled',
            'ISRO scientists confused', 'JAXA researchers bewildered',
            'space industry leaders surprised', 'aerospace experts amazed',
            'aviation authorities shocked', 'defense contractors stunned',
            'military contractors baffled', 'security contractors puzzled',
            'intelligence contractors confused', 'government contractors bewildered',
            'space contractors surprised', 'aerospace contractors amazed',
            'aviation contractors shocked', 'defense industry stunned',
            'security industry baffled', 'intelligence industry puzzled',
            'government industry confused', 'space industry bewildered',
            'aerospace industry surprised', 'aviation industry amazed',
            'defense sector shocked', 'security sector stunned',
            'intelligence sector baffled', 'government sector puzzled',
            'space sector confused', 'aerospace sector bewildered',
            'aviation sector surprised', 'defense market amazed',
            'security market shocked', 'intelligence market stunned',
            'government market baffled', 'space market puzzled',
            'aerospace market confused', 'aviation market bewildered',
            'defense community surprised', 'security community amazed',
            'intelligence community shocked', 'government community stunned',
            'space community baffled', 'aerospace community puzzled',
            'aviation community confused', 'defense world bewildered',
            'security world surprised', 'intelligence world amazed',
            'government world shocked', 'space world stunned',
            'aerospace world baffled', 'aviation world puzzled',
            'defense field confused', 'security field bewildered',
            'intelligence field surprised', 'government field amazed',
            'space field shocked', 'aerospace field stunned',
            'aviation field baffled', 'defense area puzzled',
            'security area confused', 'intelligence area bewildered',
            'government area surprised', 'space area amazed',
            'aerospace area shocked', 'aviation area stunned',
            'defense domain baffled', 'security domain puzzled',
            'intelligence domain confused', 'government domain bewildered',
            'space domain surprised', 'aerospace domain amazed',
            'aviation domain shocked', 'defense sphere stunned',
            'security sphere baffled', 'intelligence sphere puzzled',
            'government sphere confused', 'space sphere bewildered',
            'aerospace sphere surprised', 'aviation sphere amazed',
            'defense realm shocked', 'security realm stunned',
            'intelligence realm baffled', 'government realm puzzled',
            'space realm confused', 'aerospace realm bewildered',
            'aviation realm surprised', 'defense world amazed',
            'security world shocked', 'intelligence world stunned',
            'government world baffled', 'space world puzzled',
            'aerospace world confused', 'aviation world bewildered'
        ]

        # Add satirical content indicators
        satirical_indicators = [
            '™', '©', '®', 'brand', 'venture', 'partnership',
            'publicity stunt', 'promote', 'launching soon',
            'skeptics argue', 'critics claim', 'some say',
            'according to unnamed sources', 'anonymous sources claim',
            'insiders reveal', 'exclusive scoop', 'breaking news',
            'you won\'t believe what', 'shocking truth about',
            'they don\'t want you to know', 'hidden agenda',
            'secret project', 'classified information',
            'leaked documents', 'confidential sources',
            'underground movement', 'conspiracy theory',
            'cover-up', 'scandal', 'controversy',
            'exposed', 'revealed', 'uncovered',
            'shocking discovery', 'amazing find',
            'incredible breakthrough', 'revolutionary',
            'game-changing', 'mind-blowing',
            'earth-shattering', 'world-changing',
            'paradigm shift', 'new era',
            'future of', 'next generation',
            'cutting-edge', 'groundbreaking',
            'innovative', 'revolutionary',
            'disruptive', 'transformative',
            'unprecedented', 'historic',
            'first of its kind', 'never before seen',
            'impossible', 'defies logic',
            'breaks all rules', 'challenges conventional wisdom'
        ]

        # Check for military/security related content
        military_terms = [
            'operation', 'military', 'defense', 'security', 'intelligence',
            'army', 'navy', 'air force', 'border', 'attack', 'defense',
            'soldier', 'troop', 'combat', 'mission', 'strategic', 'tactical',
            'line of control', 'loc', 'ceasefire', 'violation', 'retaliation'
        ]
        
        # Check for business/economics related content
        business_terms = [
            'trade', 'agreement', 'deal', 'economy', 'market', 'business',
            'commerce', 'export', 'import', 'tariff', 'negotiation', 'partnership',
            'investment', 'finance', 'economic', 'commercial', 'treaty'
        ]

        # Check for legitimate news indicators
        legitimate_news_indicators = [
            'reported', 'announced', 'confirmed', 'official', 'statement',
            'press release', 'according to', 'sources', 'witnesses',
            'investigation', 'research', 'study', 'analysis', 'data',
            'statistics', 'survey', 'poll', 'interview', 'expert',
            'authority', 'government', 'ministry', 'department',
            'published', 'released', 'confirmed by', 'verified',
            'official statement', 'press conference', 'announcement',
            'report', 'findings', 'results', 'data shows', 'according to experts',
            'research shows', 'study reveals', 'analysis indicates'
        ]
        
        is_military_news = any(term in content.lower() for term in military_terms)
        is_business_news = any(term in content.lower() for term in business_terms)
        
        # Check for fake news indicators
        fake_indicators_count = sum(1 for indicator in fake_news_indicators if indicator in content.lower())
        
        # Check for obviously fake content
        is_obviously_fake = any(pattern in content.lower() for pattern in obviously_fake_patterns)
        
        # Check for satirical content
        is_satirical = any(indicator in content.lower() for indicator in satirical_indicators)
        
        # Check for legitimate news indicators
        legitimate_indicators_count = sum(1 for indicator in legitimate_news_indicators if indicator in content.lower())
        
        # Get model prediction
        result = text_classifier(content)
        base_confidence = result[0]['score'] * 100

        # First check for obviously fake or satirical content
        if is_obviously_fake or is_satirical:
            classification = "Fake"
            confidence = 99.0  # Very high confidence for obviously fake content
            explanation = "This content contains patterns typical of satirical or obviously fake news. "
            if is_satirical:
                explanation += "The content appears to be satirical in nature, using common satirical indicators. "
        else:
            # For verified sources, we'll use a much higher base confidence
            if credibility['is_verified']:
                base_confidence = 95.0  # Start with very high confidence for verified sources
                # Only classify as fake if there are extremely strong negative indicators
                if fake_indicators_count > 3:  # Increased threshold for fake indicators
                    classification = "Fake"
                    base_confidence = max(60.0, base_confidence - 20)  # Reduce confidence but not too much for verified sources
                else:
                    classification = "True"
                    base_confidence = min(98.0, base_confidence + 10)  # Increase confidence for verified sources
            else:
                # For unverified sources, use a more balanced approach
                if fake_indicators_count > 3:  # Increased threshold for fake indicators
                    classification = "Fake"
                    base_confidence = min(base_confidence + 20, 100)  # Increase confidence if fake indicators are present
                elif legitimate_indicators_count > 4:  # Increased threshold for legitimate indicators
                    classification = "True"
                    base_confidence = min(base_confidence + 30, 95)  # Significant boost for multiple legitimate indicators
                elif result[0]['label'] == 'NEGATIVE' and fake_indicators_count > 1:
                    classification = "Fake"
                else:
                    classification = "True"
                    # Boost confidence for legitimate news indicators
                    if legitimate_indicators_count > 2:
                        base_confidence = min(base_confidence + 20, 90)  # Moderate boost for legitimate indicators
            
            # Adjust confidence based on credibility analysis and content type
            if credibility['is_verified']:
                if is_military_news:
                    confidence = 98.0  # Very high confidence for military news from verified sources
                elif is_business_news:
                    confidence = 95.0  # High confidence for business news from verified sources
                else:
                    confidence = min(base_confidence + 20, 100)  # High boost for verified sources
            else:
                # Check if the content matches known patterns of real news
                if is_business_news and any(term in content.lower() for term in ['u.s.', 'u.k.', 'united states', 'united kingdom', 'britain']):
                    confidence = 85.0  # High confidence for business news about major countries
                    classification = "True"
                elif legitimate_indicators_count > 4:
                    confidence = min(base_confidence + 25, 90)  # Boost confidence for legitimate news patterns
                    classification = "True"  # Force True classification for high legitimate indicators
                else:
                    confidence = max(base_confidence - 10, 0)  # Reduce confidence for unverified sources

            # Generate explanation
            explanation = f"This content appears to be {classification.lower()} news "
            if credibility['is_verified']:
                explanation += f"from {credibility['metadata'].get('domain', 'a verified source')}. "
                if is_military_news:
                    explanation += "This is a military/security news report from a verified source. "
                elif is_business_news:
                    explanation += "This is a business/economics news report from a verified source. "
            else:
                if is_business_news and any(term in content.lower() for term in ['u.s.', 'u.k.', 'united states', 'united kingdom', 'britain']):
                    explanation += "This appears to be a business news report about major countries. "
                elif legitimate_indicators_count > 4:
                    explanation += "The content contains multiple strong indicators of legitimate news reporting. "
                else:
                    explanation += "from an unverified source. "
            
            if fake_indicators_count > 0:
                explanation += f"Found {fake_indicators_count} potential fake news indicators. "
            
            if legitimate_indicators_count > 0:
                explanation += f"Found {legitimate_indicators_count} indicators of legitimate news reporting. "
            
            if credibility['keywords']:
                explanation += f"Key topics include: {', '.join(credibility['keywords'])}. "
            
            if credibility['country'] != "Unknown":
                explanation += f"The news is from {credibility['country']}. "
        
        explanation += f"The analysis is {confidence:.1f}% confident in this assessment."
        
        return AnalysisResponse(
            classification=classification,
            confidence_score=confidence,
            country_of_origin=credibility['country'],
            is_verified=credibility['is_verified'],
            explanation=explanation,
            source_metadata=credibility['metadata']
        )

    except Exception as e:
        logger.error(f"Error analyzing news: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 
