import streamlit as st
import requests
import re
import time


API_URL = "https://sec-filing-research-agent-399390869297.europe-west1.run.app/query"

COMPANY_MAP = {
    "apple": "AAPL", "aapl": "AAPL",
    "microsoft": "MSFT", "msft": "MSFT",
    "amazon": "AMZN", "amzn": "AMZN",
    "alphabet": "GOOGL", "google": "GOOGL", "googl": "GOOGL",
    "nvidia": "NVDA", "nvda": "NVDA",
    "tesla": "TSLA", "tsla": "TSLA",
    "johnson": "JNJ", "jnj": "JNJ", 'J&J'
    "jpmorgan": "JPM", "chase": "JPM", "jpm": "JPM"
}

def extract_params(question: str):
    """Scan the question for a known company and year."""
    q_lower = question.lower()
    
    detected_ticker = None
    for key, ticker in COMPANY_MAP.items():
        if key in q_lower:
            detected_ticker = ticker
            break
            
    detected_year = None
    year_match = re.search(r"\b(202[0-9])\b", question)
    if year_match:
        detected_year = int(year_match.group(1))
        
    return detected_ticker, detected_year


st.set_page_config(page_title="SEC Research Agent", layout="wide")


if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "trigger_search" not in st.session_state:
    st.session_state.trigger_search = False

def set_query(query_text):
    st.session_state.user_query = query_text
    st.session_state.trigger_search = True


with st.sidebar:
    st.header("Try an Example")
    st.caption("Click any question below to test the agent's routing and verification guardrails.")
    st.divider()

    st.subheader("Numeric (SEC API)")
    if st.button("What was Apple's revenue in 2025?", use_container_width=True):
        set_query("What was Apple's revenue in 2025?")
    if st.button("What was Nvidia's net income in 2026?", use_container_width=True):
        set_query("What was Nvidia's net income in 2026?")

    st.divider()    
    st.subheader("Narrative (Vector DB)")
    if st.button("What risks does Microsoft identify related to its business in 2025?", use_container_width=True):
        set_query("What risks does Microsoft identify related to its business in 2025?")
    if st.button("What products and services does Apple offer in 2025?", use_container_width=True):
        set_query("What products and services does Apple offer in 2025?")

    st.divider()    
    st.subheader("Hybrid (Combined)")
    if st.button("What was Johnson's revenue in 2025, and why did it change?", use_container_width=True):
        set_query("What was Johnson's revenue in 2025, and why did it change?")

    st.divider()    
    st.subheader("Guardrails (Unsupported)")
    if st.button("What was Apple's free cash flow in 2025?", use_container_width=True):
        set_query("What was Apple's free cash flow in 2025?")


st.title("SEC Filing Research Agent")
st.divider()
st.text("Ask financial or operational questions about major public companies. The system explicitly routes your question to either structured SEC financial databases (for exact numbers) or an embedded vector database (for narrative text)." \
" Every AI-generated answer is mathematically and lexically verified against the source documents to prevent hallucinations.")


st.text("Currently supports: Apple, Microsoft, Amazon, Alphabet, NVIDIA, Tesla, J&J, JPMorgan for recent fiscal years (2024-2026)")

st.divider()
cont = st.container(border=True)
with cont:
    question = st.text_input(
        "Ask a financial question:", 
        value=st.session_state.user_query,
        placeholder="e.g., What was Apple's revenue in 2025?"
    )


    submit_clicked = st.button("Submit Query", type="primary")

if submit_clicked or st.session_state.trigger_search:

    st.session_state.trigger_search = False
    
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        ticker, fiscal_year = extract_params(question)
        
        if not ticker or not fiscal_year:
            st.error("Please include a supported company name (e.g., Apple) and a year (e.g., 2025) in your question.")
        else:
            with st.spinner(f"Querying {ticker} for FY{fiscal_year}... Routing, retrieving, and verifying..."):
                payload = {
                    "question": question,
                    "ticker": ticker,
                    "fiscal_year": fiscal_year
                }
                
                try:
    
                    start_time = time.perf_counter()
                    response = requests.post(API_URL, json=payload)
                    latency_sec = round(time.perf_counter() - start_time, 1)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                
                        st.subheader("Generated Answer")
                        raw_answer = data.get("answer", "No answer generated.")
                        safe_answer = raw_answer.replace("$", r"\$")
                        st.info(safe_answer)
                        
                        
                        st.divider()
                        
                        
                        st.subheader("Agent Telemetry")
                        
                        route = str(data.get("route")).upper()
                        verdict_raw = str(data.get("verification", {}).get("verdict")).upper()
                        model_str = str(data.get("model", "unknown")).replace("openrouter/", "").replace(":free", "")
                        
                        if verdict_raw == "SUPPORTED":
                            verdict_ui, v_color = "SUPPORTED", "#198754"
                        elif verdict_raw == "PARTIALLY_SUPPORTED":
                            verdict_ui, v_color = "PARTIAL", "#ffc107"
                        else:
                            verdict_ui, v_color = "UNSUPPORTED", "#dc3545"
                            
                    
                        st.markdown(f"""
                        <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px;">
                            <div style="background-color: #1e1e2f; padding: 15px; border-radius: 8px; flex: 1; min-width: 120px; border: 1px solid #333;">
                                <div style="font-size: 12px; color: #888; text-transform: uppercase;">Route</div>
                                <div style="font-size: 18px; font-weight: bold; color: #fff;">{route}</div>
                            </div>
                            <div style="background-color: #1e1e2f; padding: 15px; border-radius: 8px; flex: 1; min-width: 150px; border: 1px solid #333;">
                                <div style="font-size: 12px; color: #888; text-transform: uppercase;">Verification</div>
                                <div style="font-size: 18px; font-weight: bold; color: {v_color};">{verdict_ui}</div>
                            </div>
                            <div style="background-color: #1e1e2f; padding: 15px; border-radius: 8px; flex: 1; min-width: 120px; border: 1px solid #333;">
                                <div style="font-size: 12px; color: #888; text-transform: uppercase;">Latency</div>
                                <div style="font-size: 18px; font-weight: bold; color: #fff;">{latency_sec:,}s</div>
                            </div>
                            <div style="background-color: #1e1e2f; padding: 15px; border-radius: 8px; flex: 2; min-width: 250px; border: 1px solid #333;">
                                <div style="font-size: 12px; color: #888; text-transform: uppercase;">LLM Model</div>
                                <div style="font-size: 18px; font-weight: bold; color: #0dcaf0; word-wrap: break-word;">{model_str}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    
                        col_ev, col_iss = st.columns(2)
                        with col_ev:
                            with st.expander("View Retrieved Evidence"):
                                st.json(data.get("evidence", []))
                                
                        with col_iss:
                            issues = data.get("verification", {}).get("issues", [])
                            if issues:
                                with st.expander("View Verification Issues"):
                                    st.json(issues)
                            else:
                                with st.expander("No Verification Issues"):
                                    st.write("All extracted claims successfully mapped to evidence.")
                                
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                        
                except Exception as e:
                    st.error(f"Failed to connect to the API: {e}")