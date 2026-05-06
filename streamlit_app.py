import streamlit as st
import requests
import time

# --- CONFIGURATION ---
DEFAULT_API_URL = "https://ai-pass.onrender.com"

st.set_page_config(
    page_title="AI-Pass | Agentic Engine",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- VIBRANT MULTI-COLOR CSS ---
st.markdown("""
<style>
    /* Global Backgrounds */
    .stApp {
        background-color: #0d1117;
    }
    
    /* Vibrant Header */
    .hero-header {
        background: linear-gradient(135deg, #FF007A 0%, #7A00FF 50%, #00E5FF 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(122, 0, 255, 0.3);
        margin-bottom: 2rem;
    }
    .hero-header h1 { margin: 0; font-size: 3rem; font-weight: 900; text-shadow: 2px 2px 4px rgba(0,0,0,0.4); }
    .hero-header p { font-size: 1.2rem; opacity: 0.9; margin-top: 10px; font-weight: 300; }

    /* Verdict Badges */
    .verdict-PASS {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #003300; padding: 20px; border-radius: 15px;
        text-align: center; font-size: 2.5rem; font-weight: 900;
        box-shadow: 0 10px 20px rgba(146, 254, 157, 0.3);
    }
    .verdict-FAIL {
        background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
        color: white; padding: 20px; border-radius: 15px;
        text-align: center; font-size: 2.5rem; font-weight: 900;
        box-shadow: 0 10px 20px rgba(255, 65, 108, 0.3);
    }
    .verdict-NEEDS_INFO {
        background: linear-gradient(90deg, #F7971E 0%, #FFD200 100%);
        color: #4A2B00; padding: 20px; border-radius: 15px;
        text-align: center; font-size: 2.5rem; font-weight: 900;
        box-shadow: 0 10px 20px rgba(247, 151, 30, 0.3);
    }

    /* Multi-color lists */
    .list-item-reason {
        background: rgba(255, 65, 108, 0.1); border-left: 5px solid #FF416C;
        padding: 12px 16px; margin: 8px 0; border-radius: 0 10px 10px 0;
        color: #FFE5EA; font-weight: 400;
    }
    .list-item-evidence {
        background: rgba(0, 201, 255, 0.1); border-left: 5px solid #00C9FF;
        padding: 12px 16px; margin: 8px 0; border-radius: 0 10px 10px 0;
        color: #E5F9FF; font-weight: 400;
    }
    .list-item-step {
        background: rgba(122, 0, 255, 0.1); border-left: 5px solid #7A00FF;
        padding: 12px 16px; margin: 8px 0; border-radius: 0 10px 10px 0;
        color: #F0E5FF; font-family: monospace;
    }

    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="hero-header">
    <h1>🚀 AI-Pass Engine</h1>
    <p>Multi-Agent Policy Evaluation & Structured Decision System</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔌 Connection Settings")
    api_url = st.text_input("API Base URL", value=DEFAULT_API_URL)
    
    st.markdown("### 🔑 Session Management")
    session_id = st.text_input("Session ID (For Memory)", value="demo-session-01")
    
    st.markdown("---")
    st.markdown("### 💓 System Health")
    try:
        health_resp = requests.get(f"{api_url}/health", timeout=5)
        if health_resp.status_code == 200:
            st.success("🟢 Online & Connected")
        else:
            st.error("🔴 API Offline")
    except:
        st.warning("🟡 Cannot reach API")

# --- TABS ---
tab_analyze, tab_memory, tab_how = st.tabs(["⚡ Analyze Document", "🧠 Session Memory", "📖 How It Works"])

# ==========================================
# TAB 1: ANALYZE DOCUMENT
# ==========================================
with tab_analyze:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 1. Provide Document")
        input_type = st.radio("Input Method:", ["✍️ Paste Text", "📂 Upload File"], horizontal=True)
        
        doc_text = ""
        uploaded_file = None
        
        if input_type == "✍️ Paste Text":
            doc_text = st.text_area("Document Content", height=200, placeholder="Paste contract, application, or claim here...")
        else:
            uploaded_file = st.file_uploader("Upload PDF, TXT, or DOCX", type=["pdf", "txt", "docx"])
            if uploaded_file:
                st.success(f"File attached: {uploaded_file.name}")

    with col2:
        st.markdown("### 📜 2. Define Policy Rules")
        policy_text = st.text_area("Policy Rules", height=200, placeholder="Rule 1: Must be over 18.\nRule 2: Income > $40k...")

    st.markdown("---")
    
    # Run Button
    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2:
        run_button = st.button("✨ RUN AGENT PIPELINE ✨", use_container_width=True, type="primary")

    if run_button:
        if not (doc_text or uploaded_file):
            st.error("Please provide a document.")
        elif not policy_text:
            st.error("Please provide policy rules.")
        else:
            with st.spinner("🚀 Agents are waking up and analyzing..."):
                try:
                    # 1. Trigger API
                    if uploaded_file:
                        # USING /run-task-file matching our backend
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"policy_text": policy_text, "session_id": session_id}
                        resp = requests.post(f"{api_url}/run-task-file", files=files, data=data, timeout=30)
                    else:
                        payload = {"document_text": doc_text, "policy_text": policy_text, "session_id": session_id}
                        resp = requests.post(f"{api_url}/run-task", json=payload, timeout=30)
                    
                    if resp.status_code != 200:
                        st.error(f"API Error {resp.status_code}: {resp.text}")
                        st.stop()
                    
                    task_id = resp.json()["task_id"]
                    st.toast(f"Task {task_id} initiated!", icon="✅")
                    
                    # 2. Polling Loop
                    progress_bar = st.progress(0)
                    status_msg = st.empty()
                    final_result = None
                    
                    for i in range(60): # 60 seconds max
                        time.sleep(1)
                        progress_bar.progress((i + 1) / 60)
                        
                        poll = requests.get(f"{api_url}/result/{task_id}", timeout=10)
                        if poll.status_code == 200:
                            data = poll.json()
                            status = data.get("status")
                            status_msg.info(f"Status: **{status.upper()}** - Agents are thinking...")
                            
                            if status in ["completed", "error"]:
                                final_result = data
                                break
                    
                    progress_bar.empty()
                    status_msg.empty()
                    
                    # 3. Display Results
                    if final_result and final_result.get("status") == "completed":
                        decision = final_result.get("decision", "UNKNOWN")
                        
                        st.markdown("---")
                        st.markdown(f'<div class="verdict-{decision}">{decision}</div>', unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Confidence", f"{final_result.get('confidence', 0)*100:.1f}%")
                        m2.metric("Execution Time", f"{final_result.get('latency_ms', 0)} ms")
                        m3.metric("Steps Taken", len(final_result.get("steps_taken", [])))
                        
                        r_col, e_col = st.columns(2)
                        with r_col:
                            st.markdown("#### 🚨 Reasons")
                            for r in final_result.get("reasons", []):
                                st.markdown(f'<div class="list-item-reason">🎯 {r}</div>', unsafe_allow_html=True)
                        with e_col:
                            st.markdown("#### 🔍 Evidence Found")
                            for e in final_result.get("evidence", []):
                                st.markdown(f'<div class="list-item-evidence">📄 "{e}"</div>', unsafe_allow_html=True)
                        
                        st.markdown("#### ⚙️ Agent Pipeline Steps")
                        for s in final_result.get("steps_taken", []):
                            st.markdown(f'<div class="list-item-step">⚡ {s}</div>', unsafe_allow_html=True)
                            
                        with st.expander("🧠 View Full Agent Analysis Summary"):
                            st.write(final_result.get("analysis_summary", "No summary provided."))
                            
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")

# ==========================================
# TAB 2: SESSION MEMORY
# ==========================================
with tab_memory:
    st.markdown("### 🧠 Cross-Task Memory")
    st.write(f"Viewing history for Session ID: **{session_id}**")
    
    if st.button("🔄 Refresh Memory"):
        try:
            mem_resp = requests.get(f"{api_url}/memory/{session_id}", timeout=10)
            if mem_resp.status_code == 200:
                mem_data = mem_resp.json()
                
                # Metrics
                total = mem_data.get("total", 0)
                history = mem_data.get("history", [])
                passes = sum(1 for h in history if h.get("decision") == "PASS")
                fails = sum(1 for h in history if h.get("decision") == "FAIL")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Decisions", total)
                c2.metric("Pass Rate", f"{(passes/total)*100:.0f}%" if total > 0 else "0%")
                c3.metric("Fail Rate", f"{(fails/total)*100:.0f}%" if total > 0 else "0%")
                
                st.markdown("---")
                
                # History List
                for item in reversed(history):
                    dec = item.get("decision")
                    emoji = "✅" if dec == "PASS" else "❌" if dec == "FAIL" else "⚠️"
                    with st.expander(f"{emoji} {dec} | {item.get('document_preview', '')[:60]}..."):
                        st.write(f"**Confidence:** {item.get('confidence', 0)*100:.1f}%")
                        st.write("**Reasons:**")
                        for r in item.get("reasons", []):
                            st.write(f"- {r}")
                        st.caption(f"Task ID: {item.get('task_id')}")
            else:
                # If /memory doesn't exist, we fallback to our old /dashboard/history
                st.warning("Memory endpoint not found. Assuming legacy dashboard fallback.")
        except Exception as e:
            st.error(f"Error fetching memory: {e}")

    st.markdown("---")
    if st.button("🗑️ Clear Session Memory", type="primary"):
        try:
            requests.delete(f"{api_url}/memory/{session_id}")
            st.success("Memory cleared!")
        except:
            st.error("Failed to clear memory.")

# ==========================================
# TAB 3: HOW IT WORKS
# ==========================================
with tab_how:
    st.markdown("""
    ### ⚙️ The Agentic Architecture
    
    AI-Pass uses a **LangGraph StateGraph** to orchestrate specialized AI agents:
    
    1. **📥 Ingestion Agent:** Processes the raw document, creates vector embeddings using `SentenceTransformers`.
    2. **🔍 RAG Agent:** Queries `ChromaDB` using the policy rules as vectors to retrieve strictly relevant context.
    3. **🧠 Analysis Agent:** Consumes the RAG context and document. If confidence is low, it **loops back** to the Retrieval agent for more context.
    4. **⚖️ Decision Agent:** Formats the final output into a deterministic JSON object (`PASS`, `FAIL`, `NEEDS_INFO`).
    
    ### 🛠️ Tech Stack
    * **Frontend:** Streamlit
    * **Backend:** FastAPI
    * **Orchestration:** LangGraph & LangChain
    * **Vector DB:** ChromaDB
    * **LLM:** OpenAI GPT-4o-mini
    """)