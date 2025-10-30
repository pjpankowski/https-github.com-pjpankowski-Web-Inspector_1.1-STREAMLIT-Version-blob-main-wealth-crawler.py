"""
═══════════════════════════════════════════════════════════════════════════════
MSCI WEALTH MANAGEMENT INTELLIGENCE PLATFORM v2.1
═══════════════════════════════════════════════════════════════════════════════

Enterprise-grade web intelligence gathering for wealth management firms
Built using advanced techniques from "Web Scraping with Python" by Ryan Mitchell

NEW in v2.1:
- AUM (Assets Under Management) detection with extraction
- Firm profile intelligence (clients, offices, founding year)
- Refactored code architecture for maintainability
- Bug fixes for variable scoping
- Enhanced error handling
- Improved UI with AUM value display

© 2025 - Built for MSCI Sales Intelligence Team
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import pandas as pd
import logging

# Configure page
st.set_page_config(
    page_title="MSCI Intelligence Platform v2.1",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
# INTELLIGENCE CONFIGURATION
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
            "keywords": ["private debt", "private credit", "direct lending", "mezzanine"],
            "weight": 1.0,
            "priority": "high"
        },
        "Hedge Funds/Fund of Funds": {
            "keywords": ["hedge fund", "fund of funds", "alternative strategies", "absolute return"],
            "weight": 1.0,
            "priority": "medium"
        },
        "Private Real Estate Funds": {
            "keywords": ["private real estate", "real estate fund", "property fund"],
            "weight": 1.0,
            "priority": "medium"
        },
        "Infrastructure Funds": {
            "keywords": ["infrastructure fund", "infrastructure investment"],
            "weight": 1.0,
            "priority": "medium"
        },
        "Real Estate Assets": {
            "keywords": ["real estate", "commercial property", "REIT", "property investment"],
            "weight": 0.8,
            "priority": "low"
        },
        "Private Companies": {
            "keywords": ["private company", "private investment", "direct investment"],
            "weight": 0.9,
            "priority": "medium"
        },
        "Structured Products": {
            "keywords": ["structured products", "structured notes", "equity derivatives"],
            "weight": 0.9,
            "priority": "medium"
        },
        "MSCI Futures & Options": {
            "keywords": ["MSCI futures", "MSCI options", "index derivatives"],
            "weight": 1.1,
            "priority": "high"
        },
        "MSCI OTC Derivatives": {
            "keywords": ["MSCI OTC", "MSCI derivatives", "MSCI swaps"],
            "weight": 1.1,
            "priority": "high"
        },
        "Carbon Projects": {
            "keywords": ["carbon", "carbon offset", "carbon credit", "climate project"],
            "weight": 0.9,
            "priority": "medium"
        }
    },
    
    "Third Parties & Partnerships": {
        "Investment Consultants": {
            "keywords": ["investment consultant", "advisory firm", "consultant"],
            "weight": 1.0,
            "priority": "high"
        },
        "Custodians": {
            "keywords": ["custodian", "custody", "safekeeping", "custodial services"],
            "weight": 1.0,
            "priority": "high"
        },
        "External Equity Managers": {
            "keywords": ["external manager", "third party manager", "equity manager"],
            "weight": 0.9,
            "priority": "medium"
        },
        "External Indexed Equity Managers": {
            "keywords": ["indexed manager", "passive manager", "index fund manager"],
            "weight": 0.9,
            "priority": "medium"
        },
        "External Private Asset Managers": {
            "keywords": ["private asset manager", "alternative manager"],
            "weight": 0.9,
            "priority": "medium"
        },
        "Sustainability Regulations": {
            "keywords": ["SFDR", "Article 8", "Article 9", "ESG regulation"],
            "weight": 1.0,
            "priority": "high"
        },
        "IBOR - Privates": {
            "keywords": ["IBOR", "investment book", "book of records", "private"],
            "weight": 0.8,
            "priority": "low"
        },
        "IBOR - Public": {
            "keywords": ["IBOR", "investment book", "book of records", "public"],
            "weight": 0.8,
            "priority": "low"
        },
        "Regulatory Service Providers": {
            "keywords": ["regulatory service", "compliance provider", "regtech"],
            "weight": 0.8,
            "priority": "medium"
        }
    },
    
    "Internal Capabilities": {
        "Fundamental Active Equity": {
            "keywords": ["fundamental", "active equity", "active management"],
            "weight": 1.0,
            "priority": "high"
        },
        "Quantitative Equity": {
            "keywords": ["quantitative", "quant equity", "systematic", "factor"],
            "weight": 1.0,
            "priority": "high"
        },
        "Indexed Equity": {
            "keywords": ["indexed equity", "passive", "index tracking"],
            "weight": 1.0,
            "priority": "high"
        },
        "Fixed Income": {
            "keywords": ["fixed income", "bond", "credit management"],
            "weight": 1.0,
            "priority": "high"
        },
        "Direct Indexing": {
            "keywords": ["direct indexing", "custom indexing", "SMA"],
            "weight": 1.1,
            "priority": "high"
        }
    },
    
    "Analytics & Technology": {
        "Model Portfolio Platform": {
            "keywords": ["model portfolio", "model management", "portfolio models"],
            "weight": 1.1,
            "priority": "high"
        },
        "Performance Attribution": {
            "keywords": ["performance attribution", "attribution analysis"],
            "weight": 1.0,
            "priority": "high"
        },
        "Risk Platform": {
            "keywords": ["risk platform", "risk management", "risk analytics", "VaR"],
            "weight": 1.2,
            "priority": "high"
        },
        "Portfolio Analytics - Equities": {
            "keywords": ["equity analytics", "portfolio analytics", "equity analysis"],
            "weight": 1.0,
            "priority": "high"
        },
        "Portfolio Analytics - Fixed Income": {
            "keywords": ["fixed income analytics", "bond analytics"],
            "weight": 1.0,
            "priority": "high"
        },
        "Client Portfolio Management": {
            "keywords": ["client portal", "portfolio management system", "wealth platform"],
            "weight": 1.0,
            "priority": "high"
        },
        "Client Reporting": {
            "keywords": ["client reporting", "reporting platform"],
            "weight": 1.0,
            "priority": "high"
        },
        "Fund Universe Data": {
            "keywords": ["fund data", "fund universe", "fund information"],
            "weight": 0.9,
            "priority": "medium"
        }
    },
    
    "Index Providers": {
        "Equity Index Providers": {
            "keywords": ["MSCI", "S&P", "FTSE", "Russell", "index provider"],
            "weight": 1.2,
            "priority": "high"
        },
        "Fixed Income Index Providers": {
            "keywords": ["Bloomberg", "ICE", "bond index", "fixed income benchmark"],
            "weight": 1.0,
            "priority": "high"
        }
    },
    
    "ESG & Sustainability": {
        "Sustainability Integration": {
            "keywords": ["ESG integration", "sustainability", "responsible investing"],
            "weight": 1.2,
            "priority": "high"
        },
        "Climate Integration": {
            "keywords": ["climate", "carbon", "net zero", "decarbonization"],
            "weight": 1.2,
            "priority": "high"
        },
        "Sustainability Offering": {
            "keywords": ["ESG fund", "sustainable fund", "impact fund"],
            "weight": 1.1,
            "priority": "high"
        },
        "Signatory Pledges": {
            "keywords": ["PRI signatory", "net zero commitment", "climate pledge", "TCFD"],
            "weight": 1.0,
            "priority": "medium"
        },
        "ESG Data Providers": {
            "keywords": ["Sustainalytics", "MSCI ESG", "ISS ESG", "Refinitiv"],
            "weight": 1.1,
            "priority": "high"
        },
        "Climate Data Providers": {
            "keywords": ["Trucost", "carbon data", "climate analytics", "CDP"],
            "weight": 1.0,
            "priority": "medium"
        }
    },
    
    "Private Markets": {
        "Private Assets Analytics": {
            "keywords": ["private asset analytics", "alternative analytics"],
            "weight": 1.0,
            "priority": "high"
        },
        "Private Asset Data": {
            "keywords": ["private asset data", "alternative data", "Preqin"],
            "weight": 1.0,
            "priority": "high"
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def fetch_page_robust(url, timeout=10, retries=3):
    """Robust page fetching with retry logic"""
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
    """
    Extract AUM values from text with pattern matching
    Returns: list of found AUM amounts with normalized values
    """
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
                
                # Normalize to billions
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
    """Advanced content analysis with AUM extraction"""
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
    
    # Calculate confidence
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
# STREAMLIT UI
# ═══════════════════════════════════════════════════════════════════════════

st.markdown('<div class="main-header">🎯 MSCI Intelligence Platform v2.1</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Enterprise Intelligence with AUM Detection</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    target_url = st.text_input(
        "Target Firm URL",
        placeholder="https://www.firmname.com",
        help="Homepage of the wealth management firm"
    )
    
    st.markdown("### Crawl Settings")
    max_pages = st.slider("Max Pages", 5, 50, 15)
    max_depth = st.slider("Crawl Depth", 1, 3, 2)
    crawl_delay = st.slider("Delay (sec)", 0.5, 5.0, 1.5, 0.5)
    
    start_intel = st.button("🚀 Start Intelligence Gathering", type="primary", use_container_width=True)
    
    st.markdown("---")
    total_questions = sum(len(q) for q in INTELLIGENCE_CATEGORIES.values())
    st.metric("Intelligence Points", total_questions)
    st.caption("v2.1 - AUM Detection Enabled")

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
        
        status_text.markdown(f"**Analyzing:** `{current_url}`")
        
        html = fetch_page_robust(current_url)
        
        if html:
            visited.add(current_url)
            pages_crawled += 1
            
            # Analyze
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
            
            # Extract links
            if depth < max_depth:
                new_links = extract_internal_links(html, current_url)
                prioritized_links = prioritize_links(new_links)
                
                for link in prioritized_links[:8]:
                    if link not in visited:
                        to_visit.append((link, depth + 1))
            
            # Update metrics
            progress_bar.progress(min(pages_crawled / max_pages, 1.0))
            pages_metric.metric("Pages", pages_crawled)
            
            found_count = sum(1 for cat in intelligence.values() for q in cat.values() if q["status"] == "found")
            partial_count = sum(1 for cat in intelligence.values() for q in cat.values() if q["status"] == "partial")
            not_found_count = sum(1 for cat in intelligence.values() for q in cat.values() if q["status"] == "not found")
            
            found_metric.metric("✓ Found", found_count)
            partial_metric.metric("⚠ Partial", partial_count)
            not_found_metric.metric("✗ Not Found", not_found_count)
            
            time.sleep(crawl_delay)
    
    status_text.markdown(f"**✅ Complete!** Analyzed {pages_crawled} pages.")
    
    # Display results
    st.markdown("## 📊 Intelligence Report")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        st.metric("Found", found_count)
    with summary_col2:
        st.metric("Partial", partial_count)
    with summary_col3:
        coverage = round((found_count + partial_count) / total_questions * 100, 1)
        st.metric("Coverage", f"{coverage}%")
    with summary_col4:
        st.metric("Pages", pages_crawled)
    
    st.markdown("---")
    
    # Results by category
    for category, questions in intelligence.items():
        with st.expander(f"**{category}** ({len(questions)} points)", expanded=False):
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
                        
                        # Keywords
                        if data["matches"]:
                            keywords_found = [m["keyword"] for m in data["matches"]]
                            st.markdown(f"**🎯 Keywords:** {', '.join(keywords_found[:5])}")
                        
                        # Snippets
                        if data["snippets"]:
                            st.markdown("**📄 Evidence:**")
                            for snippet in data["snippets"]:
                                st.markdown(f'<div class="snippet-box">{snippet}</div>', unsafe_allow_html=True)
                        
                        # Sources
                        if data["sources"]:
                            st.markdown(f"**🔗 Found on {len(data['sources'])} page(s)**")
                            for j, source in enumerate(data["sources"][:3], 1):
                                st.caption(f"{j}. {source}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
    
    # Export
    st.markdown("## 📥 Export")
    
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
                "Question": question,
                "Status": data["status"].upper(),
                "Confidence (%)": data["confidence"],
                "Keywords Found": keywords_found,
                "AUM Detected": aum_str,
                "Evidence": data["evidence_count"],
                "Snippets": snippets_combined[:500],
                "Sources": "; ".join(data["sources"]),
                "Priority": data["config"].get("priority", "medium").upper()
            })
    
    df = pd.DataFrame(export_data)
    
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False)
        firm_name = urlparse(target_url).netloc.replace("www.", "")
        st.download_button(
            "📊 Full Report (CSV)",
            csv,
            f"MSCI_Intelligence_{firm_name}_{time.strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        summary_df = df[df["Status"].isin(["FOUND", "PARTIAL"])].copy()
        summary_csv = summary_df.to_csv(index=False)
        st.download_button(
            "📋 Summary (CSV)",
            summary_csv,
            f"MSCI_Summary_{firm_name}_{time.strftime('%Y%m%d')}.csv",
            "text/csv",
            use_container_width=True
        )

else:
    st.info("👈 Configure settings and click 'Start Intelligence Gathering'")
    
    st.markdown("### 🎯 New in v2.1")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💰 AUM Detection")
        st.markdown("""
        - Automatically extracts AUM values
        - Normalizes to billions
        - Shows dollar amounts
        - Multiple detection patterns
        """)
    
    with col2:
        st.markdown("#### 🏢 Firm Profile")
        st.markdown("""
        - Client count tracking
        - Office locations
        - Year founded
        - Geographic presence
        """)
    
    with col3:
        st.markdown("#### 🔧 Improvements")
        st.markdown("""
        - Refactored code
        - Bug fixes
        - Better error handling
        - Enhanced UI
        """)

st.markdown("---")
st.caption("🎯 MSCI Intelligence Platform v2.1 | AUM Detection Enabled")
st.caption("© 2025 - Built for MSCI Sales Team")
