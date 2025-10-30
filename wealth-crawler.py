"""
═══════════════════════════════════════════════════════════════════════════════
MSCI WEALTH MANAGEMENT INTELLIGENCE PLATFORM v2.2 ULTIMATE
═══════════════════════════════════════════════════════════════════════════════

The DEFINITIVE enterprise intelligence platform combining the best of v2.0 and v2.1

ULTIMATE FEATURES:
✅ ALL 48 intelligence points (v2.1's expanded coverage)
✅ AUM detection & extraction (v2.1's breakthrough feature)
✅ 3 export options (v2.0's comprehensive exports restored)
✅ Strategic use cases (v2.0's sales enablement content)
✅ Complete documentation (v2.0's "How It Works" section)
✅ Bug fixes (v2.1's variable scoping fixes)
✅ Enhanced error handling (v2.1's improved messages)
✅ Professional UI (v2.0's detailed branding + v2.1's AUM highlights)

This is the COMPLETE, PRODUCTION-READY, FEATURE-COMPLETE version.

© 2025 - Built for MSCI Sales Intelligence Team
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import pandas as pd

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="MSCI Intelligence Platform v2.2",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with AUM highlights + Professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .found-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .partial-badge {
        background-color: #ffc107;
        color: #000;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .not-found-badge {
        background-color: #dc3545;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .finding-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .snippet-box {
        background-color: #fff3cd;
        padding: 0.75rem;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    .aum-highlight {
        background-color: #d4edda;
        padding: 0.5rem;
        border-radius: 4px;
        border-left: 4px solid #28a745;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# INTELLIGENCE CONFIGURATION - COMPLETE 48 POINTS
# ═══════════════════════════════════════════════════════════════════════════

INTELLIGENCE_CATEGORIES = {
    "Firm Profile & Scale": {
        "Assets Under Management (AUM)": {
            "keywords": [
                "AUM", "assets under management", "total assets under management",
                "billion in assets", "million in assets", "trillion in assets",
                "$B in assets", "$M in assets", "$B AUM", "$M AUM",
                "managing $", "oversee $", "advise on $", "responsible for $",
                "client assets", "total client assets", "combined assets",
                "assets totaling", "assets exceeding", "regulatory assets",
                "discretionary assets", "advisory assets"
            ],
            "weight": 1.5,
            "priority": "high"
        },
        "Number of Clients": {
            "keywords": [
                "clients", "client families", "families served",
                "households", "individuals served", "families we serve"
            ],
            "weight": 0.9,
            "priority": "medium"
        },
        "Geographic Presence": {
            "keywords": [
                "offices", "office locations", "locations",
                "countries", "states", "headquarters", "HQ",
                "global presence", "international offices"
            ],
            "weight": 0.8,
            "priority": "medium"
        },
        "Year Founded": {
            "keywords": [
                "founded", "established", "since", "history",
                "years of experience", "decades", "inception"
            ],
            "weight": 0.7,
            "priority": "low"
        }
    },
    
    "Asset Classes & Investment Vehicles": {
        "MSCI Linked ETFs": {
            "keywords": ["MSCI", "ETF", "exchange traded fund", "index fund", "passive investment"],
            "weight": 1.2,
            "priority": "high"
        },
        "Private Equity Funds": {
            "keywords": ["private equity", "PE fund", "buyout", "venture capital", "growth equity"],
            "weight": 1.0,
            "priority": "high"
        },
        "Private Debt Funds": {
            "keywords": ["private debt", "private credit", "direct lending", "mezzanine", "distressed debt"],
            "weight": 1.0,
            "priority": "high"
        },
        "Hedge Funds/Fund of Funds": {
            "keywords": ["hedge fund", "fund of funds", "alternative strategies", "absolute return"],
            "weight": 1.0,
            "priority": "medium"
        },
        "Private Real Estate Funds": {
            "keywords": ["private real estate", "real estate fund", "property fund", "real estate PE"],
            "weight": 1.0,
            "priority": "medium"
        },
        "Infrastructure Funds": {
            "keywords": ["infrastructure fund", "infrastructure investment", "infrastructure equity"],
            "weight": 1.0,
            "priority": "medium"
        },
        "Real Estate Assets (Direct)": {
            "keywords": ["real estate", "commercial property", "REIT", "property investment"],
            "weight": 0.8,
            "priority": "low"
        },
        "Private Companies (Direct Investment)": {
            "keywords": ["private company", "private investment", "direct investment", "co-investment"],
            "weight": 0.9,
            "priority": "medium"
        },
        "Structured Products (Equities)": {
            "keywords": ["structured products", "structured notes", "equity derivatives", "capital protected"],
            "weight": 0.9,
            "priority": "medium"
        },
        "MSCI Futures & Options": {
            "keywords": ["MSCI futures", "MSCI options", "index derivatives", "MSCI contracts"],
            "weight": 1.1,
            "priority": "high"
        },
        "MSCI OTC Derivatives": {
            "keywords": ["MSCI OTC", "MSCI derivatives", "MSCI swaps", "total return swap"],
            "weight": 1.1,
            "priority": "high"
        },
        "Carbon Projects": {
            "keywords": ["carbon", "carbon offset", "carbon credit", "climate project", "carbon neutrality"],
            "weight": 0.9,
            "priority": "medium"
        }
    },
    
    "Third Parties & Partnerships": {
        "Investment Consultants": {
            "keywords": ["investment consultant", "advisory firm", "consultant", "advisor"],
            "weight": 1.0,
            "priority": "high"
        },
        "Custodians": {
            "keywords": ["custodian", "custody", "safekeeping", "custodial services"],
            "weight": 1.0,
            "priority": "high"
        },
        "External Equity Managers": {
            "keywords": ["external manager", "third party manager", "equity manager", "outsourced"],
            "weight": 0.9,
            "priority": "medium"
        },
        "External Indexed Equity Managers": {
            "keywords": ["indexed manager", "passive manager", "index fund manager"],
            "weight": 0.9,
            "priority": "medium"
        },
        "External Private Asset Managers": {
            "keywords": ["private asset manager", "alternative manager", "private markets"],
            "weight": 0.9,
            "priority": "medium"
        },
        "Sustainability Regulations": {
            "keywords": ["SFDR", "Article 8", "Article 9", "ESG regulation", "sustainable finance"],
            "weight": 1.0,
            "priority": "high"
        },
        "IBOR - Privates": {
            "keywords": ["IBOR", "investment book", "book of records", "private assets"],
            "weight": 0.8,
            "priority": "low"
        },
        "IBOR - Public": {
            "keywords": ["IBOR", "investment book", "book of records", "public markets"],
            "weight": 0.8,
            "priority": "low"
        },
        "Regulatory Service Providers": {
            "keywords": ["regulatory service", "compliance provider", "regulatory technology", "regtech"],
            "weight": 0.8,
            "priority": "medium"
        }
    },
    
    "Internal Capabilities": {
        "Fundamental Active Equity": {
            "keywords": ["fundamental", "active equity", "active management", "stock picking"],
            "weight": 1.0,
            "priority": "high"
        },
        "Quantitative Equity": {
            "keywords": ["quantitative", "quant equity", "systematic", "factor investing"],
            "weight": 1.0,
            "priority": "high"
        },
        "Indexed Equity": {
            "keywords": ["indexed equity", "passive", "index tracking", "index replication"],
            "weight": 1.0,
            "priority": "high"
        },
        "Fixed Income Management": {
            "keywords": ["fixed income", "bond", "credit management", "duration management"],
            "weight": 1.0,
            "priority": "high"
        },
        "Direct Indexing": {
            "keywords": ["direct indexing", "custom indexing", "separately managed accounts", "SMA"],
            "weight": 1.1,
            "priority": "high"
        }
    },
    
    "Analytics & Technology Platforms": {
        "Model Portfolio Platform": {
            "keywords": ["model portfolio", "model management", "portfolio models", "model delivery"],
            "weight": 1.1,
            "priority": "high"
        },
        "Performance Attribution": {
            "keywords": ["performance attribution", "attribution analysis", "return decomposition"],
            "weight": 1.0,
            "priority": "high"
        },
        "Risk Platform": {
            "keywords": ["risk platform", "risk management", "risk analytics", "risk system", "VaR"],
            "weight": 1.2,
            "priority": "high"
        },
        "Portfolio Analytics - Equities": {
            "keywords": ["equity analytics", "portfolio analytics", "equity analysis", "stock analysis"],
            "weight": 1.0,
            "priority": "high"
        },
        "Portfolio Analytics - Fixed Income": {
            "keywords": ["fixed income analytics", "bond analytics", "credit analysis"],
            "weight": 1.0,
            "priority": "high"
        },
        "Client Portfolio Management": {
            "keywords": ["client portal", "portfolio management system", "wealth platform"],
            "weight": 1.0,
            "priority": "high"
        },
        "Client Reporting Platform": {
            "keywords": ["client reporting", "reporting platform", "performance reporting"],
            "weight": 1.0,
            "priority": "high"
        },
        "Fund Universe Data": {
            "keywords": ["fund data", "fund universe", "fund information", "fund screening"],
            "weight": 0.9,
            "priority": "medium"
        }
    },
    
    "Index Providers": {
        "Equity Index Providers": {
            "keywords": ["MSCI", "S&P", "FTSE", "Russell", "Dow Jones", "index provider"],
            "weight": 1.2,
            "priority": "high"
        },
        "Fixed Income Index Providers": {
            "keywords": ["Bloomberg Barclays", "ICE BofA", "bond index", "fixed income benchmark"],
            "weight": 1.0,
            "priority": "high"
        }
    },
    
    "ESG & Sustainability": {
        "Sustainability Integration": {
            "keywords": ["ESG integration", "sustainability", "responsible investing", "sustainable investment"],
            "weight": 1.2,
            "priority": "high"
        },
        "Climate Integration": {
            "keywords": ["climate", "carbon footprint", "net zero", "climate change", "decarbonization"],
            "weight": 1.2,
            "priority": "high"
        },
        "Sustainability Product Offering": {
            "keywords": ["ESG fund", "sustainable fund", "impact fund", "green bond"],
            "weight": 1.1,
            "priority": "high"
        },
        "Signatory Status & Pledges": {
            "keywords": ["PRI signatory", "net zero commitment", "climate pledge", "UN PRI", "TCFD"],
            "weight": 1.0,
            "priority": "medium"
        },
        "ESG Data Providers": {
            "keywords": ["Sustainalytics", "MSCI ESG", "ISS ESG", "Refinitiv", "ESG data"],
            "weight": 1.1,
            "priority": "high"
        },
        "Climate Data Providers": {
            "keywords": ["Trucost", "carbon data", "climate analytics", "CDP", "S&P Trucost"],
            "weight": 1.0,
            "priority": "medium"
        }
    },
    
    "Private Markets": {
        "Private Assets Analytics": {
            "keywords": ["private asset analytics", "alternative analytics", "private markets analytics"],
            "weight": 1.0,
            "priority": "high"
        },
        "Private Asset Data": {
            "keywords": ["private asset data", "alternative data", "private markets data", "Preqin"],
            "weight": 1.0,
            "priority": "high"
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# ADVANCED SCRAPING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def fetch_page_robust(url, timeout=10, retries=3):
    """Robust page fetching with retry logic and enhanced error messages"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                st.warning(f"⚠️ Access denied: {url} (403 Forbidden - Site blocks automated access)")
                return None
            elif response.status_code == 404:
                st.warning(f"⚠️ Page not found: {url}")
                return None
            elif attempt == retries - 1:
                st.error(f"❌ HTTP Error on {url}: {str(e)}")
                return None
        except requests.exceptions.Timeout:
            if attempt == retries - 1:
                st.error(f"❌ Timeout on {url}")
                return None
            time.sleep(2 ** attempt)
        except Exception as e:
            if attempt == retries - 1:
                st.error(f"❌ Error fetching {url}: {str(e)}")
                return None
            time.sleep(1)
    
    return None

def extract_internal_links(html, base_url):
    """Extract internal links with URL normalization"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, "lxml")
    base_domain = urlparse(base_url).netloc
    links = set()
    
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        try:
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            
            if parsed.netloc == base_domain:
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
                if parsed.query:
                    normalized += f"?{parsed.query}"
                links.add(normalized)
        except:
            continue
    
    return list(links)

def clean_text(text):
    """Advanced text cleaning"""
    text = re.sub(r'\s+', ' ', text)
    text = ''.join(char for char in text if char.isprintable() or char.isspace())
    return text.strip()

def extract_aum_value(text):
    """Extract AUM values with pattern matching and normalization"""
    aum_patterns = [
        r'\$\s*(\d+(?:\.\d+)?)\s*(billion|trillion|million)\s*(?:in)?\s*(?:assets|AUM)',
        r'(\d+(?:\.\d+)?)\s*(billion|trillion|million)\s*(?:in)?\s*(?:assets|AUM)',
        r'\$(\d+(?:\.\d+)?)\s*([BMT])(?:\s*(?:in)?\s*(?:assets|AUM))?',
        r'(?:managing|oversee|advise)\s*\$?\s*(\d+(?:\.\d+)?)\s*(billion|trillion|million)',
        r'AUM\s*of\s*\$?\s*(\d+(?:\.\d+)?)\s*(billion|trillion|million)',
    ]
    
    found_amounts = []
    text_lower = text.lower()
    
    for pattern in aum_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            try:
                amount = float(match.group(1))
                unit = match.group(2).lower()
                
                if unit in ['b', 'billion']:
                    value_in_billions = amount
                elif unit in ['m', 'million']:
                    value_in_billions = amount / 1000
                elif unit in ['t', 'trillion']:
                    value_in_billions = amount * 1000
                else:
                    continue
                
                found_amounts.append({
                    'raw': match.group(0),
                    'amount': amount,
                    'unit': unit,
                    'billions': round(value_in_billions, 2)
                })
            except:
                continue
    
    return found_amounts

def extract_context_snippet(text, keyword, context_length=150):
    """Extract meaningful context around keywords"""
    text_lower = text.lower()
    keyword_lower = keyword.lower()
    
    idx = text_lower.find(keyword_lower)
    if idx == -1:
        return ""
    
    start = max(0, text_lower.rfind('.', 0, idx) + 1)
    end = text_lower.find('.', idx + len(keyword))
    if end == -1:
        end = min(len(text), idx + context_length)
    else:
        end = min(end + 1, len(text))
    
    snippet = text[start:end].strip()
    return snippet

def analyze_content_advanced(html, question, config):
    """Advanced content analysis with AUM extraction and weighted scoring"""
    if not html:
        return {
            "matches": [],
            "confidence": 0,
            "snippets": [],
            "evidence_count": 0,
            "aum_values": []
        }
    
    soup = BeautifulSoup(html, "lxml")
    
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    
    text = soup.get_text()
    text = clean_text(text)
    text_lower = text.lower()
    
    keywords = config["keywords"]
    weight = config.get("weight", 1.0)
    
    matches = []
    snippets = []
    aum_values = []
    
    # Special AUM extraction
    if "AUM" in question or "Assets Under Management" in question:
        aum_values = extract_aum_value(text)
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        count = text_lower.count(keyword_lower)
        if count > 0:
            matches.append({
                "keyword": keyword,
                "count": count
            })
            snippet = extract_context_snippet(text, keyword)
            if snippet and snippet not in snippets:
                snippets.append(snippet)
    
    # Calculate weighted confidence
    if len(keywords) > 0:
        base_confidence = (len(matches) / len(keywords)) * 100
        total_mentions = sum(m["count"] for m in matches)
        mention_boost = min(20, total_mentions * 2)
        weighted_confidence = (base_confidence + mention_boost) * weight
        confidence = min(100, round(weighted_confidence, 1))
    else:
        confidence = 0
    
    return {
        "matches": matches,
        "confidence": confidence,
        "snippets": snippets[:3],
        "evidence_count": sum(m["count"] for m in matches),
        "aum_values": aum_values
    }

def determine_status_advanced(confidence):
    """Determine status with granular thresholds"""
    if confidence >= 75:
        return "found"
    elif confidence >= 35:
        return "partial"
    else:
        return "not found"

def prioritize_links(links):
    """Prioritize links based on URL patterns"""
    priority_keywords = [
        'about', 'capabilities', 'solutions', 'services', 'products',
        'investment', 'approach', 'strategy', 'team', 'esg',
        'sustainability', 'technology', 'platform'
    ]
    
    prioritized = []
    normal = []
    
    for link in links:
        link_lower = link.lower()
        if any(keyword in link_lower for keyword in priority_keywords):
            prioritized.append(link)
        else:
            normal.append(link)
    
    return prioritized + normal

# ═══════════════════════════════════════════════════════════════════════════
# STREAMLIT UI - ULTIMATE DESIGN
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-header">🎯 MSCI Wealth Management Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">v2.2 ULTIMATE - Automated Due Diligence with AUM Detection</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Intelligence Configuration")
    
    target_url = st.text_input(
        "Target Firm URL",
        placeholder="https://www.firmname.com",
        help="Enter the homepage of the wealth management firm"
    )
    
    st.markdown("### Crawl Parameters")
    max_pages = st.slider("Maximum Pages", 1, 50, 15, help="Number of pages to analyze")
    max_depth = st.slider("Crawl Depth", 1, 3, 2, help="How deep to follow links")
    crawl_delay = st.slider("Request Delay (sec)", 0.5, 5.0, 1.5, 0.5, help="Polite delay between requests")
    
    st.markdown("---")
    
    start_intel = st.button("🚀 Start Intelligence Gathering", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Coverage")
    total_questions = sum(len(q) for q in INTELLIGENCE_CATEGORIES.values())
    st.metric("Total Intelligence Points", total_questions)
    st.metric("Categories", len(INTELLIGENCE_CATEGORIES))
    
    st.markdown("---")
    st.markdown("### 🛡️ About")
    st.caption("**Ultimate Edition v2.2**")
    st.caption("Comprehensive web intelligence using BeautifulSoup for wealth management due diligence")
    st.caption("Built for MSCI Sales Team")

# Main content
if start_intel and target_url:
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pages_metric = st.empty()
    with col2:
        found_metric = st.empty()
    with col3:
        partial_metric = st.empty()
    with col4:
        not_found_metric = st.empty()
    
    st.markdown("---")
    
    # Initialize intelligence
    intelligence = {}
    for category, questions in INTELLIGENCE_CATEGORIES.items():
        intelligence[category] = {}
        for question, config in questions.items():
            intelligence[category][question] = {
                "status": "not found",
                "confidence": 0,
                "matches": [],
                "snippets": [],
                "sources": [],
                "evidence_count": 0,
                "aum_values": [],
                "config": config
            }
    
    # Crawling
    visited = set()
    to_visit = [(target_url, 0)]
    pages_crawled = 0
    
    while to_visit and pages_crawled < max_pages:
        current_url, depth = to_visit.pop(0)
        
        if current_url in visited or depth > max_depth:
            continue
        
        status_text.markdown(f"**🔍 Analyzing:** `{current_url}`")
        
        html = fetch_page_robust(current_url)
        
        if html:
            visited.add(current_url)
            pages_crawled += 1
            
            # Analyze for all intelligence points
            for category, questions in INTELLIGENCE_CATEGORIES.items():
                for question, config in questions.items():
                    result = analyze_content_advanced(html, question, config)
                    
                    current_intel = intelligence[category][question]
                    
                    if result["confidence"] > current_intel["confidence"]:
                        current_intel["confidence"] = result["confidence"]
                        current_intel["matches"] = result["matches"]
                        current_intel["snippets"] = result["snippets"]
                        current_intel["evidence_count"] = result["evidence_count"]
                        current_intel["status"] = determine_status_advanced(result["confidence"])
                        current_intel["aum_values"] = result.get("aum_values", [])
                    
                    if result["matches"] and current_url not in current_intel["sources"]:
                        current_intel["sources"].append(current_url)
            
            # Extract and prioritize links
            if depth < max_depth:
                new_links = extract_internal_links(html, current_url)
                prioritized_links = prioritize_links(new_links)
                
                for link in prioritized_links[:8]:
                    if link not in visited:
                        to_visit.append((link, depth + 1))
            
            # Update metrics
            progress_bar.progress(min(pages_crawled / max_pages, 1.0))
            pages_metric.metric("Pages", pages_crawled)
            
            # Calculate stats
            found_count = sum(1 for cat in intelligence.values() for q in cat.values() if q["status"] == "found")
            partial_count = sum(1 for cat in intelligence.values() for q in cat.values() if q["status"] == "partial")
            not_found_count = sum(1 for cat in intelligence.values() for q in cat.values() if q["status"] == "not found")
            
            found_metric.metric("✓ Found", found_count)
            partial_metric.metric("⚠ Partial", partial_count)
            not_found_metric.metric("✗ Not Found", not_found_count)
            
            time.sleep(crawl_delay)
    
    status_text.markdown(f"**✅ Intelligence Gathering Complete!** Analyzed {pages_crawled} pages.")
    
    # Display results
    st.markdown("## 📊 Intelligence Report")
    
    # Executive summary
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        st.metric("Intelligence Points Found", found_count)
    with summary_col2:
        st.metric("Partial Intelligence", partial_count)
    with summary_col3:
        coverage = round((found_count + partial_count) / total_questions * 100, 1)
        st.metric("Coverage", f"{coverage}%")
    with summary_col4:
        st.metric("Pages Analyzed", pages_crawled)
    
    st.markdown("---")
    
    # Detailed findings by category
    for category, questions in intelligence.items():
        with st.expander(f"**{category}** ({len(questions)} intelligence points)", expanded=False):
            for question, data in questions.items():
                col_q, col_s, col_c = st.columns([3, 1, 1])
                
                with col_q:
                    st.markdown(f"**{question}**")
                
                with col_s:
                    if data["status"] == "found":
                        st.markdown('<span class="found-badge">✓ FOUND</span>', unsafe_allow_html=True)
                    elif data["status"] == "partial":
                        st.markdown('<span class="partial-badge">⚠ PARTIAL</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="not-found-badge">✗ NOT FOUND</span>', unsafe_allow_html=True)
                
                with col_c:
                    st.metric("", f"{data['confidence']}%", label_visibility="collapsed")
                
                if data["status"] in ["found", "partial"]:
                    with st.container():
                        st.markdown('<div class="finding-card">', unsafe_allow_html=True)
                        
                        # AUM values (if present)
                        if data["aum_values"]:
                            st.markdown("**💰 AUM Detected:**")
                            for aum in data["aum_values"][:3]:
                                st.markdown(
                                    f'<div class="aum-highlight">${aum["amount"]} {aum["unit"]} ≈ ${aum["billions"]}B</div>',
                                    unsafe_allow_html=True
                                )
                        
                        # Keywords found
                        if data["matches"]:
                            keywords_found = [m["keyword"] for m in data["matches"]]
                            mentions_total = sum(m["count"] for m in data["matches"])
                            st.markdown(f"**🎯 Keywords Found:** {', '.join(keywords_found[:5])}")
                            st.caption(f"Total mentions: {mentions_total}")
                        
                        # Evidence snippets
                        if data["snippets"]:
                            st.markdown("**📄 Evidence:**")
                            for snippet in data["snippets"]:
                                st.markdown(f'<div class="snippet-box">{snippet}</div>', unsafe_allow_html=True)
                        
                        # Sources
                        if data["sources"]:
                            st.markdown(f"**🔗 Found on {len(data['sources'])} page(s):**")
                            for j, source in enumerate(data["sources"][:3], 1):
                                st.markdown(f"{j}. [{source}]({source})")
                            if len(data["sources"]) > 3:
                                st.caption(f"...and {len(data['sources']) - 3} more pages")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
    
    # Export functionality - ALL 3 OPTIONS RESTORED
    st.markdown("## 📥 Export Intelligence Reports")
    
    # Prepare export data
    export_data = []
    for category, questions in intelligence.items():
        for question, data in questions.items():
            keywords_found = ", ".join([m["keyword"] for m in data["matches"]])
            snippets_combined = " | ".join(data["snippets"][:2])
            aum_str = ""
            if data["aum_values"]:
                aum_str = "; ".join([f"${a['billions']}B" for a in data["aum_values"]])
            
            export_data.append({
                "Category": category,
                "Intelligence Point": question,
                "Status": data["status"].upper(),
                "Confidence (%)": data["confidence"],
                "Keywords Found": keywords_found,
                "AUM Detected": aum_str,
                "Evidence Count": data["evidence_count"],
                "Top Snippets": snippets_combined[:500],
                "Sources": "; ".join(data["sources"]),
                "Number of Sources": len(data["sources"]),
                "Priority": data["config"].get("priority", "medium").upper()
            })
    
    df = pd.DataFrame(export_data)
    firm_name = urlparse(target_url).netloc.replace("www.", "")
    
    # THREE export options
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📊 Download Full Intelligence Report (CSV)",
            data=csv,
            file_name=f"MSCI_Intelligence_{firm_name}_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Complete intelligence report with all findings"
        )
    
    with col_export2:
        summary_df = df[df["Status"].isin(["FOUND", "PARTIAL"])].copy()
        summary_csv = summary_df.to_csv(index=False)
        st.download_button(
            label="📋 Download Summary Report (CSV)",
            data=summary_csv,
            file_name=f"MSCI_Summary_{firm_name}_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Found and Partial findings only"
        )
    
    with col_export3:
        # RESTORED: High priority items export
        priority_df = df[df["Priority"] == "HIGH"].copy()
        priority_csv = priority_df.to_csv(index=False)
        st.download_button(
            label="🎯 Download High Priority Items (CSV)",
            data=priority_csv,
            file_name=f"MSCI_Priority_{firm_name}_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="High-priority intelligence points only"
        )

else:
    # Welcome screen - RESTORED COMPREHENSIVE CONTENT
    st.info("👈 **Get Started:** Configure settings in the sidebar and click 'Start Intelligence Gathering'")
    
    st.markdown("### 🎯 Strategic Intelligence Platform - Ultimate Edition")
    
    col_feature1, col_feature2, col_feature3 = st.columns(3)
    
    with col_feature1:
        st.markdown("#### 🕸️ Advanced Crawling")
        st.markdown("""
        - Multi-page recursive analysis
        - Intelligent link prioritization
        - Robust error handling
        - Production-grade reliability
        - No CORS restrictions
        """)
    
    with col_feature2:
        st.markdown("#### 🎯 Deep Intelligence")
        st.markdown("""
        - 48 intelligence data points
        - Weighted keyword matching
        - Context-aware extraction
        - Evidence-based findings
        - **NEW: AUM detection & extraction**
        """)
    
    with col_feature3:
        st.markdown("#### 📊 Professional Reports")
        st.markdown("""
        - Detailed findings display
        - Source attribution
        - **3 export options restored**
        - Priority-based filtering
        - Export-ready formats
        """)
    
    st.markdown("---")
    st.markdown("### 💼 Perfect for MSCI Sales & Relationship Management")
    st.markdown("""
    **Strategic Use Cases:**
    
    - **Pre-Meeting Intelligence**: Gather comprehensive firm insights before client calls
    - **Competitive Analysis**: Understand technology stacks and capabilities
    - **Opportunity Identification**: Spot gaps where MSCI solutions fit
    - **Account Planning**: Build strategic account plans with data-driven insights
    - **Proposal Development**: Reference actual firm practices in proposals
    - **RFP Responses**: Quick intelligence for RFP questionnaires
    - **AUM Sizing**: Automatically detect and extract Assets Under Management
    - **Prospect Prioritization**: Focus on firms with specific AUM ranges
    """)
    
    st.markdown("---")
    st.markdown("### 📋 Intelligence Coverage Areas")
    
    for i, (category, questions) in enumerate(INTELLIGENCE_CATEGORIES.items(), 1):
        high_priority = sum(1 for q in questions.values() if q.get("priority") == "high")
        st.markdown(f"**{i}. {category}** - {len(questions)} points ({high_priority} high priority)")
        sample_questions = list(questions.keys())[:3]
        for q in sample_questions:
            st.markdown(f"   • {q}")
    
    st.markdown("---")
    st.markdown("### 💡 How It Works")
    st.markdown("""
    1. **Enter Target URL** - Provide the homepage of a wealth management firm
    2. **Configure Settings** - Set max pages, depth, and crawl delay
    3. **Start Crawling** - The system automatically discovers and analyzes pages
    4. **View Results** - See findings organized by category with confidence scores
    5. **Export Reports** - Download comprehensive CSV reports for your team
    
    **The platform uses advanced techniques from "Web Scraping with Python" by Ryan Mitchell
    to ensure robust, reliable, and accurate intelligence gathering.**
    """)

# Footer - RESTORED COMPREHENSIVE CREDITS
st.markdown("---")
st.caption("🎯 MSCI Wealth Management Intelligence Platform v2.2 ULTIMATE | Enterprise Sales Intelligence")
st.caption("Powered by Advanced Web Scraping Techniques • BeautifulSoup • Streamlit")
st.caption("© 2025 - Designed for MSCI Sales & Relationship Management Teams • Built with techniques from 'Web Scraping with Python' by Ryan Mitchell")
