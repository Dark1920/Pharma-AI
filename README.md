# 🌿 Pharma-AI — Biomedical Pharmacognosy Agent

> An AI-powered biomedical agent specialized in pharmacognosy, optimized for AMD GPU acceleration.
> Built for the **AMD Hackathon** — African Medicinal Plants · RAG + Llama 3 · ROCm/HIP

---

## What is Pharma-AI?

Pharma-AI is an intelligent biomedical assistant that helps researchers, pharmacists, and healthcare professionals explore medicinal plants, their active compounds, and potential drug interactions. It combines retrieval-augmented generation (RAG) with a specialized LLM to provide evidence-based answers grounded in real scientific literature.

**Core use case:** Type the name of a medicinal plant → get its active compounds, mechanisms of action, scientific references, and drug interaction warnings — all in seconds.

---

## Live Demo

Try Pharma-AI online: [Pharma-AI Web App](https://pharma-ai-9k4pqn6ymtkamdzhmpz6so.streamlit.app/)

Explore medicinal plants, active compounds, drug interactions, and scientific insights in real time.

## Features

- **AI Agent (RAG + Llama 3)** — answers biomedical questions using PubChem and PubMed data
- **Drug Interaction Checker** — detects plant-drug and plant-plant interactions with risk levels (HIGH / MODERATE / LOW)
- **AMD GPU Acceleration** — optimized for ROCm/HIP; automatic CPU fallback for development
- **Real scientific data** — compounds from PubChem, articles from PubMed/NCBI
- **Clean medical UI** — Streamlit interface with benchmark comparison (CPU vs AMD GPU)

---

## Project Structure

```
Pharma-AI/
├── pubchem_data.py        # Fetches active compounds from PubChem API
├── pubmed_data.py         # Fetches scientific articles from PubMed/NCBI
├── rag_knowledge.py       # Builds the FAISS vector knowledge base
├── interactions_db.py     # Database of known plant-drug interactions
├── interactions.py        # Interaction detection engine (rules + RAG)
├── agent.py               # RAG agent — Llama 3 via Groq API
├── app.py                 # Streamlit web interface
├── .env                   # API keys (never committed to git)
├── .gitignore
└── requirements.txt
```

---

## Quick Start

### 1 — Clone the repository

```bash
git clone https://github.com/your-username/Pharma-AI.git
cd Pharma-AI
```

### 2 — Create virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Set up API key

Create a `.env` file at the root of the project:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free API key at [console.groq.com](https://console.groq.com).

### 5 — Build the knowledge base

Run these scripts in order:

```bash
python pubchem_data.py      # Fetch compounds from PubChem
python pubmed_data.py       # Fetch articles from PubMed
python rag_knowledge.py     # Build FAISS vector store
```

### 6 — Launch the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## AMD GPU Setup (ROCm)

This project is optimized for AMD GPU acceleration using ROCm.

### Install PyTorch with ROCm support

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.0
```

### Verify GPU is detected

```python
import torch
print(torch.cuda.is_available())        # True
print(torch.cuda.get_device_name(0))    # Your AMD GPU name
```

The app automatically detects AMD GPUs and switches to GPU mode. The Benchmark tab shows real-time CPU vs AMD GPU performance comparison.

---

## Requirements

```
langchain
langchain-community
langchain-groq
langchain-huggingface
langchain-text-splitters
faiss-cpu
sentence-transformers
streamlit
requests
pandas
biopython
python-dotenv
groq
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## Data Sources

| Source | Content | Access |
|--------|---------|--------|
| [PubChem](https://pubchem.ncbi.nlm.nih.gov/) | Molecular compounds, formulas, weights | Free REST API |
| [PubMed / NCBI](https://pubmed.ncbi.nlm.nih.gov/) | Scientific abstracts and articles | Free Entrez API |
| [Groq / Llama 3.1](https://console.groq.com/) | LLM inference | Free API key |

---

## Medicinal Plants Covered

The current knowledge base includes compounds from:

- **Moringa oleifera** (Moringa) — quercetin, kaempferol, niazimicin, beta-sitosterol
- **Azadirachta indica** (Neem) — nimbin, azadirachtin
- **Curcuma longa** (Turmeric) — curcumin
- **Zingiber officinale** (Ginger) — gingerol
- **Combretum micranthum** (Kinkeliba) — luteolin, orientin
- **Aloe vera** — aloin, acemannan
- **Catharanthus roseus** (Periwinkle) — vincristine

---

## Architecture

```
User question
      │
      ▼
 FAISS Retriever ──── Vector Store (sentence-transformers)
      │                      │
      │               PubChem + PubMed data
      ▼
 PromptTemplate (pharmacognosy expert)
      │
      ▼
 Llama 3.1 8B (Groq API)
      │
      ▼
 Structured answer + cited sources
      │
      ▼
 Streamlit UI ── Benchmark AMD GPU vs CPU
```

---

## Security

- **Never commit your `.env` file** — it is listed in `.gitignore`
- If a key is accidentally exposed, revoke it immediately at [console.groq.com/keys](https://console.groq.com/keys)
- The app uses `python-dotenv` to load keys safely from the local environment

---

## Built With

- [LangChain](https://langchain.com/) — agent orchestration and RAG pipeline
- [FAISS](https://github.com/facebookresearch/faiss) — vector similarity search
- [Groq](https://groq.com/) — ultra-fast LLM inference
- [Llama 3.1](https://ai.meta.com/llama/) — open-source LLM by Meta
- [HuggingFace](https://huggingface.co/) — sentence embeddings
- [Streamlit](https://streamlit.io/) — web interface
- [AMD ROCm](https://rocm.docs.amd.com/) — GPU acceleration

---

## License

MIT License — free to use, modify, and distribute.

---

*Made with 🌿 for the AMD Hackathon*
