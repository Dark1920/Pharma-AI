
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from interactions_db import (
    search_plant_drug,
    search_plant_plant,
    get_risk_color,
)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# LLM EXPLANATION ENGINE

def load_llm():
    """Loads the Groq LLM for interaction explanations"""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.1
    )


def load_rag_retriever():
    """Loads the FAISS knowledge base built in rag_knowledge.py"""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    vector_store = FAISS.load_local(
        "moringa_vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_store.as_retriever(search_kwargs={"k": 3})


def explain_interaction_with_llm(interaction: dict) -> str:
    """
    Uses the LLM + RAG to generate a detailed biomedical explanation
    of a known interaction.

    interaction : one dict from interactions_db
    returns     : explanation string
    """
    llm       = load_llm()
    retriever = load_rag_retriever()

    prompt = PromptTemplate.from_template("""
You are a clinical pharmacognosy expert.

A known interaction has been detected:
- Plant    : {plant}
- Compound : {compound}
- Drug     : {drug}
- Effect   : {effect}
- Mechanism: {mechanism}
- Risk     : {risk}

Use the scientific context below AND your expert knowledge
to explain this interaction in simple terms a patient can understand.
Then give a clear clinical recommendation.

Scientific context:
{context}

Detailed explanation:""")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "context"  : retriever | format_docs,
            "plant"    : lambda _: interaction.get("plant", ""),
            "compound" : lambda _: interaction.get("compound", ""),
            "drug"     : lambda _: interaction.get("drug", ""),
            "effect"   : lambda _: interaction.get("effect", ""),
            "mechanism": lambda _: interaction.get("mechanism", ""),
            "risk"     : lambda _: interaction.get("risk", ""),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke("")


# DISPLAY HELPERS

def print_interaction(interaction: dict, detailed: bool = False):
    """Prints a formatted interaction report in the terminal"""
    icon = get_risk_color(interaction.get("risk", ""))
    separator = "=" * 55

    print(f"\n{separator}")
    print(f"  {icon} {interaction.get('risk', '')} RISK")

    if "drug" in interaction:
        print(f"  Plant : {interaction['plant']}")
        print(f"  Drug  : {interaction['drug']} ({interaction['drug_class']})")
    else:
        print(f"  Plant 1 : {interaction['plant_1']}")
        print(f"  Plant 2 : {interaction['plant_2']}")

    print(f"\n  Effect    : {interaction.get('effect', '')}")
    print(f"  Mechanism : {interaction.get('mechanism', '')}")
    print(f"  ⚕️  Action  : {interaction.get('action', '')}")

    if detailed:
        print(f"\n  Generating detailed LLM explanation...")
        explanation = explain_interaction_with_llm(interaction)
        print(f"\n  Detailed explanation:\n  {explanation}")

    print(separator)


# MAIN TEST

if __name__ == "__main__":

    print("\n🌿 PHARMA-AI — Interaction Detection Engine")
    print("=" * 55)

    # Test 1 — Plant + Drug
    print("\n📋 TEST 1: Moringa + Warfarin")
    results = search_plant_drug("Moringa", "Warfarin")
    for r in results:
        print_interaction(r, detailed=False)

    # Test 2 — Plant + Drug
    print("\n📋 TEST 2: Turmeric + Aspirin")
    results = search_plant_drug("Turmeric", "Aspirin")
    for r in results:
        print_interaction(r, detailed=False)

    # Test 3 — Plant + Plant
    print("\n📋 TEST 3: Moringa + Kinkeliba (plant-plant)")
    results = search_plant_plant("Moringa", "Kinkeliba")
    for r in results:
        print_interaction(r, detailed=False)

    # Test 4 — LLM detailed explanation (uses Groq API)
    print("\n📋 TEST 4: Detailed LLM explanation — Aloe + Digoxin")
    results = search_plant_drug("Aloe", "Digoxin")
    for r in results:
        print_interaction(r, detailed=True)

    print("\n✅ Interaction engine test complete!")
    print("   Next step: launch the full Streamlit app with: streamlit run app.py")