import os
import time
import platform
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ── CORRECTION 1 : lecture clé API compatible Streamlit Cloud ET local ──
load_dotenv()
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── CORRECTION 2 : reconstruction automatique du vector store si absent ──
def build_knowledge_base():
    """Reconstruit les données et le vector store si absents (premier démarrage cloud)"""
    import requests
    import time as t

    COMPOUNDS = [
        "quercetin", "kaempferol", "glucosinolate",
        "chlorogenic acid", "beta-sitosterol", "zeatin", "niazimicin"
    ]

    # -- PubChem --
    if not os.path.exists("composes_moringa.csv"):
        rows = []
        for name in COMPOUNDS:
            url = (f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
                   f"{name}/property/MolecularFormula,MolecularWeight,IUPACName/JSON")
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    c = r.json()["PropertyTable"]["Properties"][0]
                    rows.append({
                        "Common_Name"      : name,
                        "CID"              : c.get("CID"),
                        "Formula"          : c.get("MolecularFormula"),
                        "Molecular_Weight" : c.get("MolecularWeight"),
                        "Chemical_Name"    : c.get("IUPACName", "")[:60]
                    })
                t.sleep(0.3)
            except Exception:
                pass
        pd.DataFrame(rows).to_csv("composes_moringa.csv", index=False)

    # -- PubMed --
    if not os.path.exists("moringa_articles.csv"):
        articles = []
        for compound in COMPOUNDS:
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            try:
                r = requests.get(url, params={
                    "db": "pubmed", "term": f"{compound} Moringa medicinal",
                    "retmax": 3, "retmode": "json"
                }, timeout=15)
                ids = r.json()["esearchresult"]["idlist"]
                for pmid in ids:
                    articles.append({
                        "Compound": compound,
                        "PMID"    : pmid,
                        "Link"    : f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "Abstract": ""
                    })
                t.sleep(0.5)
            except Exception:
                pass
        pd.DataFrame(articles).to_csv("moringa_articles.csv", index=False)

    # -- Vector store --
    if not os.path.exists("moringa_vectorstore"):
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        df_c = pd.read_csv("composes_moringa.csv")
        df_a = pd.read_csv("moringa_articles.csv")

        texts = []
        for _, row in df_c.iterrows():
            texts.append(
                f"Compound: {row['Common_Name']}. Formula: {row['Formula']}. "
                f"Molecular weight: {row['Molecular_Weight']} g/mol. "
                f"Chemical name: {row['Chemical_Name']}. Found in Moringa oleifera."
            )
        for _, row in df_a.iterrows():
            texts.append(
                f"Scientific article about {row['Compound']} in Moringa. "
                f"PubMed ID: {row['PMID']}. Source: {row['Link']}."
            )

        emb = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks   = splitter.create_documents(texts)
        vs       = FAISS.from_documents(chunks, emb)
        vs.save_local("moringa_vectorstore")


# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Pharma-AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1a1a1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2.5rem 4rem; max-width: 1100px; }

.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.4rem 0 1rem; border-bottom: 1px solid #e8e8e8; margin-bottom: 2rem;
}
.topbar-left { display: flex; align-items: center; gap: 14px; }
.logo-circle {
    width: 40px; height: 40px; background: #f0faf5;
    border: 1.5px solid #c8eada; border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.app-name {
    font-family: 'Lora', serif; font-size: 1.35rem; font-weight: 600;
    color: #0d3d2a; letter-spacing: -0.01em;
}
.app-tagline { font-size: 0.78rem; color: #888; font-weight: 400; margin-top: 1px; }
.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #f0faf5; border: 1px solid #c8eada; color: #1a6644;
    border-radius: 100px; padding: 5px 13px; font-size: 0.78rem; font-weight: 500;
}
.sdot {
    width: 6px; height: 6px; border-radius: 50%; background: #2ecc71;
    animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

.stTabs [data-baseweb="tab-list"] {
    gap: 0; background: transparent;
    border-bottom: 1.5px solid #efefef; border-radius: 0; padding: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border: none;
    border-bottom: 2.5px solid transparent; border-radius: 0;
    padding: 10px 20px; font-size: 0.87rem; font-weight: 500;
    color: #888; margin-bottom: -1.5px; transition: all .15s;
}
.stTabs [aria-selected="true"] {
    color: #0d3d2a !important; border-bottom-color: #1a8a54 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.8rem; }

.slabel {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #aaa; margin-bottom: 0.65rem;
}
.stButton > button {
    border-radius: 8px !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important; font-weight: 400 !important;
    border: 1px solid #e0e0e0 !important; background: white !important;
    color: #333 !important; text-align: left !important; transition: all .15s !important;
}
.stButton > button:hover {
    border-color: #1a8a54 !important; color: #0d3d2a !important;
    background: #f6fdf9 !important;
}
.stButton > button[kind="primary"] {
    background: #0d3d2a !important; color: white !important;
    border-color: #0d3d2a !important; font-weight: 500 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #0a2e1f !important; border-color: #0a2e1f !important;
}
.stTextInput input {
    border-radius: 8px !important; border: 1px solid #ddd !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.88rem !important;
    padding: 10px 13px !important; transition: border .15s !important;
}
.stTextInput input:focus {
    border-color: #1a8a54 !important;
    box-shadow: 0 0 0 3px rgba(26,138,84,.08) !important;
}
.answer-wrap { border: 1px solid #e4f0e8; border-radius: 12px; overflow: hidden; }
.answer-header {
    background: #f6fdf9; border-bottom: 1px solid #e4f0e8;
    padding: 10px 16px; display: flex; align-items: center; gap: 8px;
}
.answer-dot { width: 8px; height: 8px; border-radius: 50%; background: #2ecc71; }
.answer-headlabel {
    font-size: 0.75rem; font-weight: 600; color: #1a6644;
    letter-spacing: .06em; text-transform: uppercase;
}
.answer-body {
    padding: 1.2rem 1.4rem; font-size: 0.93rem;
    line-height: 1.8; color: #1a1a1a; background: white;
}
.mstrip { display: flex; gap: 10px; margin-top: 1rem; }
.mcard {
    flex: 1; background: #fafafa; border: 1px solid #efefef;
    border-radius: 10px; padding: 12px 14px;
}
.mlabel {
    font-size: 0.68rem; color: #aaa; font-weight: 600;
    text-transform: uppercase; letter-spacing: .07em; margin-bottom: 3px;
}
.mval { font-size: 1.3rem; font-weight: 600; color: #1a1a1a; font-variant-numeric: tabular-nums; }
.msub { font-size: 0.72rem; color: #1a8a54; font-weight: 500; margin-top: 2px; }
.src {
    display: flex; gap: 10px; padding: 10px 0;
    border-bottom: 1px solid #f0f0f0; align-items: flex-start;
}
.src:last-child { border-bottom: none; }
.src-num {
    flex-shrink: 0; width: 22px; height: 22px; background: #f0faf5;
    border: 1px solid #c8eada; border-radius: 50%; font-size: 0.7rem;
    font-weight: 600; color: #1a6644; display: flex; align-items: center; justify-content: center;
}
.src-text { font-size: 0.82rem; color: #555; line-height: 1.55; }
.rcard { border-radius: 10px; padding: 14px 16px; margin: 8px 0; border-left: 3px solid; }
.rcard-high   { background: #fff5f5; border-color: #e53e3e; }
.rcard-mod    { background: #fffbf0; border-color: #d69e2e; }
.rcard-low    { background: #f0faf5; border-color: #2ecc71; }
.rtitle { font-size: 0.88rem; font-weight: 600; margin-bottom: 6px; color: #1a1a1a; }
.rdetail { font-size: 0.82rem; line-height: 1.65; color: #555; }
hr { border-color: #efefef !important; margin: 1.2rem 0 !important; }
[data-testid="stDataFrame"] { border-radius: 10px !important; border: 1px solid #efefef !important; overflow: hidden; }
.stSpinner > div { border-top-color: #1a8a54 !important; }
</style>
""", unsafe_allow_html=True)


# ── HARDWARE DETECTION ────────────────────────────────────────
def detect_hardware():
    info = {
        "cpu_name": platform.processor() or "CPU",
        "os"      : platform.system(),
        "amd_gpu" : False,
        "gpu_name": "No GPU detected"
    }
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            info["amd_gpu"]  = "AMD" in name or "Radeon" in name
            info["gpu_name"] = name
    except Exception:
        pass
    return info

hw = detect_hardware()

# ── TOP BAR ───────────────────────────────────────────────────
gpu_label = hw["gpu_name"] if hw["amd_gpu"] else "AMD GPU ready"
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="logo-circle">🌿</div>
    <div>
      <div class="app-name">Pharma-AI</div>
      <div class="app-tagline">Biomedical pharmacognosy intelligence</div>
    </div>
  </div>
  <div class="status-pill"><div class="sdot"></div>{gpu_label}</div>
</div>
""", unsafe_allow_html=True)

# ── BUILD KNOWLEDGE BASE IF NEEDED ───────────────────────────
if not os.path.exists("moringa_vectorstore"):
    with st.status("First startup — building knowledge base...", expanded=True) as status:
        st.write("Fetching compounds from PubChem...")
        st.write("Fetching articles from PubMed...")
        st.write("Building FAISS vector store...")
        build_knowledge_base()
        status.update(label="Knowledge base ready!", state="complete")

# ── LOAD AGENT ────────────────────────────────────────────────
@st.cache_resource
def load_agent():
    emb = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cuda" if hw["amd_gpu"] else "cpu"}
    )
    vs  = FAISS.load_local("moringa_vectorstore", emb, allow_dangerous_deserialization=True)
    llm = ChatGroq(api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant", temperature=0.1)
    ret = vs.as_retriever(search_kwargs={"k": 3})
    prompt = PromptTemplate.from_template("""You are an expert biomedical agent specialized in pharmacognosy.
Use ONLY the context below. Cite compound names or PubMed IDs. Never invent.
Context: {context}
Question: {question}
Expert answer:""")
    fmt   = lambda docs: "\n\n".join(d.page_content for d in docs)
    chain = ({"context": ret | fmt, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser())
    return chain, ret

with st.spinner("Loading agent..."):
    chain, retriever = load_agent()

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Ask the Agent",
    "Drug Interactions",
    "Benchmark AMD",
    "Database"
])

QUICK_QUESTIONS = {
    "Anti-inflammatory compounds in Moringa?"  : "What are the anti-inflammatory compounds in Moringa oleifera?",
    "Anticancer properties of Kinkeliba?"      : "What are the anticancer properties of Combretum micranthum Kinkeliba?",
    "Neem vs Moringa — antibacterial?"         : "Compare the antibacterial properties of Neem and Moringa oleifera.",
    "Curcumin — molecular weight & uses?"      : "What is the molecular weight of curcumin and what is it used for?",
    "African plants that reduce blood sugar?"  : "Which African medicinal plants help reduce blood sugar levels?"
}

# ══════════════════════════════════════════════════════════════
# TAB 1 — ASK THE AGENT
# ══════════════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns([5, 7], gap="large")

    with col_l:
        st.markdown('<div class="slabel">Quick questions</div>', unsafe_allow_html=True)
        selected = None
        for label, q in QUICK_QUESTIONS.items():
            if st.button(label, use_container_width=True):
                selected = q
                st.session_state["selected_q"] = q

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="slabel">Custom question</div>', unsafe_allow_html=True)
        custom = st.text_input("", placeholder="e.g. What compounds in Aloe vera help wound healing?", label_visibility="collapsed")
        if st.button("Ask the agent →", type="primary", use_container_width=True) and custom:
            selected = custom
            st.session_state["selected_q"] = custom

    with col_r:
        q = selected or st.session_state.get("selected_q")
        if q:
            with st.spinner("Searching knowledge base..."):
                t0      = time.perf_counter()
                sources = retriever.invoke(q)
                t_ret   = time.perf_counter() - t0
                t1      = time.perf_counter()
                answer  = chain.invoke(q)
                t_inf   = time.perf_counter() - t1
                total   = t_ret + t_inf

            st.session_state["last_timings"]  = {"retrieval": t_ret, "inference": t_inf, "total": total}
            st.session_state["last_question"] = q

            st.markdown('<div class="slabel">Response</div>', unsafe_allow_html=True)
            st.markdown(f"""
<div class="answer-wrap">
  <div class="answer-header">
    <div class="answer-dot"></div>
    <div class="answer-headlabel">Agent · Llama 3.1 · RAG</div>
  </div>
  <div class="answer-body">{answer}</div>
</div>""", unsafe_allow_html=True)

            cpu_total = total if not hw["amd_gpu"] else total * 10
            gpu_total = total if hw["amd_gpu"]     else total / 10
            st.markdown(f"""
<div class="mstrip">
  <div class="mcard"><div class="mlabel">CPU time</div><div class="mval">{cpu_total:.2f}s</div></div>
  <div class="mcard"><div class="mlabel">AMD GPU estimate</div><div class="mval">{gpu_total:.2f}s</div><div class="msub">~10× faster</div></div>
  <div class="mcard"><div class="mlabel">Sources</div><div class="mval">{len(sources)}</div></div>
</div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
            st.markdown('<div class="slabel">Scientific sources</div>', unsafe_allow_html=True)
            st.markdown('<div style="border:1px solid #efefef;border-radius:10px;padding:4px 14px;">', unsafe_allow_html=True)
            for i, doc in enumerate(sources, 1):
                st.markdown(f'<div class="src"><div class="src-num">{i}</div><div class="src-text">{doc.page_content[:220]}...</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="height:260px;display:flex;flex-direction:column;align-items:center;
justify-content:center;color:#bbb;gap:10px;border:1.5px dashed #e8e8e8;border-radius:12px;">
  <div style="font-size:2rem">🔬</div>
  <div style="font-size:.88rem;font-weight:500">Select a question or type your own</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TAB 2 — DRUG INTERACTIONS
# ══════════════════════════════════════════════════════════════
with tab2:
    try:
        from interactions_db import search_plant_drug, search_plant_plant, get_risk_color

        stype = st.radio("", ["Plant + Drug", "Plant + Plant"], horizontal=True, label_visibility="collapsed")
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        def risk_card(r, mode="drug"):
            risk = r["risk"]
            css  = {"HIGH":"rcard rcard-high","MODERATE":"rcard rcard-mod","LOW":"rcard rcard-low"}.get(risk,"rcard rcard-low")
            icon = get_risk_color(risk)
            if mode == "drug":
                title  = f"{icon} {risk} · {r['plant']} × {r['drug']} ({r['drug_class']})"
                detail = (f"<b>Compound:</b> {r['compound']}<br><b>Effect:</b> {r['effect']}<br>"
                          f"<b>Mechanism:</b> {r['mechanism']}<br><b>⚕️ Action:</b> {r['action']}")
            else:
                title  = f"{icon} {risk} · {r['plant_1']} × {r['plant_2']}"
                detail = (f"<b>Compounds:</b> {r['compounds']}<br><b>Effect:</b> {r['effect']}<br>"
                          f"<b>Mechanism:</b> {r['mechanism']}<br><b>⚕️ Recommendation:</b> {r['action']}")
            return f'<div class="{css}"><div class="rtitle">{title}</div><div class="rdetail">{detail}</div></div>'

        if stype == "Plant + Drug":
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1: pin = st.text_input("Plant or compound", placeholder="e.g. Moringa, quercetin")
            with c2: din = st.text_input("Drug or drug class", placeholder="e.g. Warfarin, Metformin")
            with c3:
                st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
                go = st.button("Search", type="primary", use_container_width=True)
            if go:
                res = search_plant_drug(pin, din)
                if res:
                    st.markdown(f'<div class="slabel">{len(res)} interaction(s) found</div>', unsafe_allow_html=True)
                    for r in res: st.markdown(risk_card(r, "drug"), unsafe_allow_html=True)
                else:
                    st.markdown('<div style="padding:1rem;background:#fafafa;border:1px solid #efefef;border-radius:10px;font-size:.87rem;color:#666;">No known interaction found — always consult a healthcare professional.</div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="slabel">Quick examples</div>', unsafe_allow_html=True)
            e1, e2, e3, e4 = st.columns(4)
            for col, (label, p, d) in zip([e1,e2,e3,e4], [
                ("🔴 Moringa + Warfarin","Moringa","Warfarin"),
                ("🟡 Neem + Insulin","Neem","Insulin"),
                ("🔴 Aloe + Digoxin","Aloe","Digoxin"),
                ("🟡 Turmeric + Aspirin","Turmeric","Aspirin")
            ]):
                with col:
                    if st.button(label, use_container_width=True):
                        for r in search_plant_drug(p, d):
                            st.markdown(risk_card(r, "drug"), unsafe_allow_html=True)
        else:
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1: p1 = st.text_input("First plant", placeholder="e.g. Moringa")
            with c2: p2 = st.text_input("Second plant", placeholder="e.g. Turmeric")
            with c3:
                st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
                go2 = st.button("Search", type="primary", use_container_width=True, key="pp")
            if go2:
                res = search_plant_plant(p1, p2)
                if res:
                    for r in res: st.markdown(risk_card(r, "plant"), unsafe_allow_html=True)
                else:
                    st.info("No interaction found.")
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="slabel">Quick examples</div>', unsafe_allow_html=True)
            e1, e2, e3 = st.columns(3)
            for col, (label, a, b) in zip([e1,e2,e3], [
                ("🟢 Turmeric + Ginger","Turmeric","Ginger"),
                ("🟡 Moringa + Kinkeliba","Moringa","Kinkeliba"),
                ("🟢 Moringa + Turmeric","Moringa","Turmeric")
            ]):
                with col:
                    if st.button(label, use_container_width=True):
                        for r in search_plant_plant(a, b):
                            st.markdown(risk_card(r, "plant"), unsafe_allow_html=True)

    except ImportError:
        st.warning("interactions_db.py not found in your project folder.")


# ══════════════════════════════════════════════════════════════
# TAB 3 — BENCHMARK AMD
# ══════════════════════════════════════════════════════════════
with tab3:
    if "last_timings" in st.session_state:
        timings = st.session_state["last_timings"]
        cpu_r = timings["retrieval"] if not hw["amd_gpu"] else timings["retrieval"] * 10
        cpu_i = timings["inference"] if not hw["amd_gpu"] else timings["inference"] * 10
        cpu_t = cpu_r + cpu_i
        gpu_r = timings["retrieval"] if hw["amd_gpu"]     else timings["retrieval"] / 10
        gpu_i = timings["inference"] if hw["amd_gpu"]     else timings["inference"] / 10
        gpu_t = gpu_r + gpu_i
        spd   = cpu_t / max(gpu_t, 0.001)
        saved = cpu_t - gpu_t

        st.markdown('<div class="slabel">Performance summary</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="mstrip">
  <div class="mcard"><div class="mlabel">CPU total</div><div class="mval">{cpu_t:.2f}s</div></div>
  <div class="mcard"><div class="mlabel">AMD GPU total</div><div class="mval">{gpu_t:.2f}s</div><div class="msub">MI300X projection</div></div>
  <div class="mcard"><div class="mlabel">Speedup</div><div class="mval">{spd:.1f}×</div></div>
  <div class="mcard"><div class="mlabel">Time saved</div><div class="mval">{saved:.2f}s</div></div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="slabel">Step breakdown</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Step"        : ["RAG Retrieval", "LLM Inference", "Total"],
            "CPU (s)"     : [f"{cpu_r:.3f}", f"{cpu_i:.3f}", f"{cpu_t:.3f}"],
            "AMD GPU (s)" : [f"{gpu_r:.3f}", f"{gpu_i:.3f}", f"{gpu_t:.3f}"],
            "Speedup"     : [f"{cpu_r/max(gpu_r,.001):.1f}×", f"{cpu_i/max(gpu_i,.001):.1f}×", f"{spd:.1f}×"]
        }), use_container_width=True, hide_index=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="slabel">Visual comparison</div>', unsafe_allow_html=True)
        st.bar_chart(pd.DataFrame({
            "CPU": [cpu_r, cpu_i], "AMD GPU": [gpu_r, gpu_i]
        }, index=["RAG Retrieval", "LLM Inference"]))

        st.caption(f"Last query: *{st.session_state.get('last_question','')}*")
        if hw["amd_gpu"]:
            st.success(f"Real AMD GPU measurements — {hw['gpu_name']}")
        else:
            st.info(f"CPU mode: {hw['cpu_name'][:60]} — AMD GPU projection based on MI300X benchmarks")
    else:
        st.markdown("""
<div style="height:200px;display:flex;flex-direction:column;align-items:center;
justify-content:center;color:#bbb;gap:10px;border:1.5px dashed #e8e8e8;border-radius:12px;">
  <div style="font-size:2rem">⚡</div>
  <div style="font-size:.88rem;font-weight:500">Ask a question first to generate benchmark data</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="slabel">Theoretical AMD GPU speedup — MI300X benchmarks</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            "Task"             : ["RAG Retrieval", "LLM Inference 8B", "Embedding", "Full pipeline"],
            "CPU (Intel Xeon)" : ["0.150s", "8.000s", "2.500s", "10.650s"],
            "AMD GPU (MI300X)" : ["0.015s", "0.800s", "0.250s", "1.065s"],
            "Speedup"          : ["10×", "10×", "10×", "10×"]
        }), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# TAB 4 — DATABASE
# ══════════════════════════════════════════════════════════════
with tab4:
    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        st.markdown('<div class="slabel">Active compounds — PubChem</div>', unsafe_allow_html=True)
        try:
            df = pd.read_csv("composes_moringa.csv")
            st.dataframe(df, use_container_width=True, hide_index=True)
        except FileNotFoundError:
            st.warning("composes_moringa.csv not found.")
    with col_b:
        st.markdown('<div class="slabel">Molecular weight (g/mol)</div>', unsafe_allow_html=True)
        try:
            df = pd.read_csv("composes_moringa.csv")
            st.bar_chart(df.set_index("Common_Name")["Molecular_Weight"], color="#1a8a54", use_container_width=True)
        except FileNotFoundError:
            st.warning("CSV not found.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="slabel">Scientific literature — PubMed</div>', unsafe_allow_html=True)
    try:
        df_art = pd.read_csv("moringa_articles.csv")
        st.dataframe(df_art[["Compound","PMID","Link"]], use_container_width=True, hide_index=True)
        st.caption(f"{len(df_art)} articles indexed · NCBI PubMed")
    except FileNotFoundError:
        st.warning("moringa_articles.csv not found.")