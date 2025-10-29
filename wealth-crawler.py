"""
Wealth Management Intelligence Crawler
A comprehensive Streamlit application for automated due diligence analysis

Built using techniques from "Web Scraping with Python" by Ryan Mitchell
Designed for MSCI Sales Intelligence & Wealth Management Prospecting
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re
import pandas as pd
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="Wealth Management Crawler",
    page_icon="🕷️",
    layout="wide"
)

# ==================== CONFIGURATION ====================

# Keywords for each category and question
CATEGORIES = {
    "Asset Classes": {
        "MSCI linked ETFs": ["MSCI", "ETF", "exchange traded fund"],
        "Private Equity Funds": ["private equity", "PE fund", "buyout", "venture capital"],
        "Private Debt Funds": ["private debt", "private credit", "direct lending"],
        "Hedge Funds/FoHF": ["hedge fund", "fund of funds", "alternative strategies"],
        "Private Real Estate Funds": ["private real estate", "real estate fund"],
        "Infrastructure Funds": ["infrastructure fund", "infrastructure investment"],
        "Real Estate Assets": ["real estate", "commercial property", "REIT"],
        "Private Companies": ["private company", "private investment"],
        "Structured Products": ["structured products", "structured notes"],
        "MSCI Futures & Options": ["MSCI futures", "MSCI options"],
        "MSCI OTC Derivatives": ["MSCI OTC", "MSCI derivatives"],
        "Carbon Projects": ["carbon", "carbon offset", "carbon credit"]
    },
    "Third Parties & Partnerships": {
        "Investment Consultants": ["investment consultant", "advisory firm"],
        "Custodians": ["custodian", "custody", "safekeeping"],
        "External EQ Managers": ["external manager", "equity manager"],
        "External Indexed EQ Managers": ["indexed manager", "passive manager"],
        "External Private Asset Managers": ["private asset manager", "alternative manager"],
        "Sustainability Regulations": ["SFDR", "Article 8", "Article 9"],
        "IBOR - Privates": ["IBOR", "investment book", "private"],
        "IBOR - Public": ["IBOR", "investment book", "public"],
        "Regulatory Service Providers": ["regulatory service", "compliance"]
    },
    "Internal Capabilities": {
        "Fundamental Active EQ": ["fundamental", "active equity"],
        "Quant EQ": ["quantitative", "quant equity", "systematic"],
        "Indexed EQ": ["indexed equity", "passive"],
        "Fixed Income": ["fixed income", "bond"],
        "Direct Indexing": ["direct indexing", "custom indexing"]
    },
    "Analytics": {
        "Model Portfolio Platform": ["model portfolio", "model management"],
        "Performance Attribution": ["performance attribution"],
        "Risk Platform": ["risk platform", "risk management"],
        "Portfolio Analytics - Equities": ["equity analytics", "portfolio analytics"],
        "Portfolio Analytics - Fixed Income": ["fixed income analytics"],
        "Client Portfolio Management": ["client portal", "wealth platform"],
        "Client Reporting": ["client reporting", "reporting platform"],
        "Fund Universe Data": ["fund data", "fund universe"]
    },
    "Index": {
        "EQ Index Providers": ["MSCI", "S&P", "FTSE", "Russell"],
        "FI Index Providers": ["Bloomberg", "ICE", "bond index"]
    },
    "Sustainability": {
        "Sustainability Integration": ["ESG", "sustainability", "responsible investing"],
        "Climate Integration": ["climate", "carbon", "net zero"],
        "Sustainability Offering": ["ESG fund", "sustainable fund"],
        "Signatory Pledges": ["PRI", "net zero commitment"],
        "Sustainability Competitors": ["Sustainalytics", "MSCI ESG", "ISS ESG"],
        "Climate Competitors": ["Trucost", "carbon data", "CDP"]
    },
    "Private Assets": {
        "Private Assets Analytics": ["private asset analytics", "alternative analytics"],
        "Private Asset Data": ["private asset data", "alternative data"]
    }
}

# ==================== HELPER FUNCTIONS ====================

def fetch_page(url, timeout=10):
    """Fetch a webpage with proper error handling"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"Error fetching {url}: {str(e)}")
        return None

def extract_internal_links(html, base_url):
    """Extract all internal links from HTML"""
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc
    links = set()
    
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        absolute_url = urljoin(base_url, href)
        
        # Check if internal link
        if urlparse(absolute_url).netloc == base_domain:
            # Remove fragments
            absolute_url = absolute_url.split("#")[0]
            links.add(absolute_url)
    
    return list(links)

def analyze_content(html, keywords):
    """Analyze HTML content for keyword matches"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    text = soup.get_text().lower()
    
    matches = []
    for keyword in keywords:
        if keyword.lower() in text:
            matches.append(keyword)
            
    confidence = (len(matches) / len(keywords)) * 100 if keywords else 0
    
    # Extract snippet
    snippet = ""
    if matches:
        idx = text.find(matches[0].lower())
        if idx != -1:
            start = max(0, idx - 100)
            end = min(len(text), idx + 200)
            snippet = "..." + text[start:end].strip() + "..."
    
    return {
        "matches": matches,
        "confidence": round(confidence, 1),
        "snippet": snippet
    }

def determine_status(confidence):
    """Determine finding status based on confidence"""
    if confidence >= 70:
        return "found"
    elif confidence >= 40:
        return "partial"
    else:
        return "not found"

# ==================== MAIN APP ====================

# Header
st.title("🕷️ Wealth Management Intelligence Crawler")
st.markdown("### Automated Due Diligence Analysis for Wealth Management Firms")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Crawl Settings")
    
    url = st.text_input("Target URL", placeholder="https://example.com", help="Enter the homepage URL of the wealth management firm")
    
    max_pages = st.slider("Max Pages", min_value=1, max_value=50, value=10, help="Maximum number of pages to crawl")
    max_depth = st.slider("Max Depth", min_value=1, max_value=3, value=2, help="How many levels deep to follow links")
    crawl_delay = st.slider("Delay (seconds)", min_value=0.5, max_value=5.0, value=1.0, step=0.5, help="Delay between page requests")
    
    start_crawl = st.button("🚀 Start Crawling", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("**📊 Question Coverage**")
    total_questions = sum(len(questions) for questions in CATEGORIES.values())
    st.metric("Total Questions", total_questions)
    
    st.markdown("---")
    st.markdown("**About**")
    st.markdown("Comprehensive web crawler using BeautifulSoup for wealth management due diligence.")
    st.markdown("Built for MSCI sales intelligence.")

# Main content area
if start_crawl and url:
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    metrics_cols = st.columns(4)
    
    with metrics_cols[0]:
        pages_metric = st.empty()
    with metrics_cols[1]:
        found_metric = st.empty()
    with metrics_cols[2]:
        partial_metric = st.empty()
    with metrics_cols[3]:
        not_found_metric = st.empty()
    
    st.markdown("---")
    
    # Initialize findings structure
    findings = {}
    for category, questions in CATEGORIES.items():
        findings[category] = {}
        for question, keywords in questions.items():
            findings[category][question] = {
                "status": "not found",
                "confidence": 0,
                "matches": [],
                "snippet": "",
                "sources": []
            }
    
    # Crawling logic
    visited = set()
    to_visit = [(url, 0)]
    pages_crawled = 0
    
    while to_visit and pages_crawled < max_pages:
        current_url, depth = to_visit.pop(0)
        
        if current_url in visited or depth > max_depth:
            continue
        
        status_text.text(f"🔍 Crawling: {current_url}")
        
        html = fetch_page(current_url)
        
        if html:
            visited.add(current_url)
            pages_crawled += 1
            
            # Analyze content for all questions
            for category, questions in CATEGORIES.items():
                for question, keywords in questions.items():
                    result = analyze_content(html, keywords)
                    
                    # Update if better than previous
                    if result["confidence"] > findings[category][question]["confidence"]:
                        findings[category][question]["confidence"] = result["confidence"]
                        findings[category][question]["matches"] = result["matches"]
                        findings[category][question]["snippet"] = result["snippet"]
                        findings[category][question]["status"] = determine_status(result["confidence"])
                    
                    # Add source
                    if result["matches"] and current_url not in findings[category][question]["sources"]:
                        findings[category][question]["sources"].append(current_url)
            
            # Extract links for next depth level
            if depth < max_depth:
                new_links = extract_internal_links(html, current_url)
                for link in new_links[:5]:  # Limit links per page to prevent explosion
                    if link not in visited:
                        to_visit.append((link, depth + 1))
            
            # Update metrics
            progress_bar.progress(min(pages_crawled / max_pages, 1.0))
            pages_metric.metric("Pages Crawled", pages_crawled)
            
            # Calculate stats
            found_count = sum(1 for cat in findings.values() for q in cat.values() if q["status"] == "found")
            partial_count = sum(1 for cat in findings.values() for q in cat.values() if q["status"] == "partial")
            not_found_count = sum(1 for cat in findings.values() for q in cat.values() if q["status"] == "not found")
            
            found_metric.metric("Found", found_count, delta=None)
            partial_metric.metric("Partial", partial_count, delta=None)
            not_found_metric.metric("Not Found", not_found_count, delta=None)
            
            time.sleep(crawl_delay)
    
    status_text.text(f"✅ Crawling complete! Analyzed {pages_crawled} pages.")
    
    # Display results
    st.markdown("## 📊 Detailed Findings")
    
    # Summary stats
    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.metric("✓ Found", found_count)
    with summary_cols[1]:
        st.metric("⚠ Partial", partial_count)
    with summary_cols[2]:
        st.metric("✗ Not Found", not_found_count)
    
    st.markdown("---")
    
    # Results by category
    for category, questions in findings.items():
        with st.expander(f"**{category}** ({len(questions)} items)", expanded=False):
            for question, data in questions.items():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{question}**")
                
                with col2:
                    if data["status"] == "found":
                        st.success("✓ Found")
                    elif data["status"] == "partial":
                        st.warning("⚠ Partial")
                    else:
                        st.error("✗ Not Found")
                
                with col3:
                    st.metric("", f"{data['confidence']}%")
                
                # Show details if found/partial
                if data["status"] in ["found", "partial"]:
                    with st.container():
                        if data["matches"]:
                            st.markdown(f"**🎯 Keywords Found:** {', '.join(data['matches'])}")
                        if data["snippet"]:
                            with st.expander("View Snippet"):
                                st.text_area("", data["snippet"], height=100, key=f"{category}_{question}_snippet", label_visibility="collapsed")
                        if data["sources"]:
                            st.markdown(f"**📄 Found on {len(data['sources'])} page(s):**")
                            for i, source in enumerate(data["sources"][:3], 1):
                                st.markdown(f"{i}. [{source}]({source})")
                            if len(data["sources"]) > 3:
                                st.markdown(f"*...and {len(data['sources']) - 3} more*")
                
                st.markdown("---")
    
    # Export functionality
    st.markdown("## 📥 Export Results")
    
    # Prepare CSV data
    csv_data = []
    for category, questions in findings.items():
        for question, data in questions.items():
            csv_data.append({
                "Category": category,
                "Question": question,
                "Status": data["status"],
                "Confidence (%)": data["confidence"],
                "Keywords Found": ", ".join(data["matches"]),
                "Snippet": data["snippet"][:500] if data["snippet"] else "",
                "Source Count": len(data["sources"]),
                "Sources": "; ".join(data["sources"])
            })
    
    df = pd.DataFrame(csv_data)
    csv = df.to_csv(index=False)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download Detailed CSV Report",
            data=csv,
            file_name=f"wealth_intelligence_{urlparse(url).netloc}_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Summary report
        summary_df = df[["Category", "Question", "Status", "Confidence (%)"]].copy()
        summary_csv = summary_df.to_csv(index=False)
        st.download_button(
            label="📋 Download Summary CSV",
            data=summary_csv,
            file_name=f"wealth_summary_{urlparse(url).netloc}_{time.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    # Welcome screen
    st.info("👈 **Get Started:** Enter a target URL in the sidebar and click 'Start Crawling'")
    
    st.markdown("### 🎯 Key Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🕸️ Multi-Page Crawling**")
        st.markdown("Automatically discovers and analyzes sub-pages recursively")
        st.markdown("")
        st.markdown("**💾 No CORS Restrictions**")
        st.markdown("Python-based scraping bypasses browser limitations")
    
    with col2:
        st.markdown("**🎯 Intelligent Matching**")
        st.markdown("Matches content against 44 due diligence questions")
        st.markdown("")
        st.markdown("**📊 Confidence Scoring**")
        st.markdown("Quantifies match quality with confidence percentages")
    
    with col3:
        st.markdown("**📈 Real-Time Progress**")
        st.markdown("Live updates as pages are crawled and analyzed")
        st.markdown("")
        st.markdown("**📥 Export Reports**")
        st.markdown("Download findings as CSV for further analysis")
    
    st.markdown("---")
    st.markdown("### 📋 Due Diligence Coverage")
    st.markdown("This crawler analyzes wealth management firms across these key areas:")
    
    for category, questions in CATEGORIES.items():
        st.markdown(f"**{category}** - {len(questions)} questions covering topics like:")
        sample_questions = list(questions.keys())[:3]
        for q in sample_questions:
            st.markdown(f"  • {q}")
        st.markdown("")
    
    st.markdown("---")
    st.markdown("### 💡 How It Works")
    st.markdown("""
    1. **Enter Target URL** - Provide the homepage of a wealth management firm
    2. **Configure Settings** - Set max pages, depth, and crawl delay
    3. **Start Crawling** - The crawler automatically discovers and analyzes pages
    4. **View Results** - See findings organized by category with confidence scores
    5. **Export Reports** - Download comprehensive CSV reports for your team
    """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit • Powered by BeautifulSoup • Designed for MSCI Sales Intelligence")
st.caption("Based on 'Web Scraping with Python' by Ryan Mitchell")
