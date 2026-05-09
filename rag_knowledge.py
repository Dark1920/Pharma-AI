import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def load_knowledge():
    #Loads compounds and articles

    print("Loading knowledge base...")

    # Load both CSV files
    df_compounds = pd.read_csv("moringa_compounds.csv")
    df_articles  = pd.read_csv("moringa_articles.csv")

    # Convert compounds into readable text
    compound_texts = []
    for _, row in df_compounds.iterrows():
        text = (
            f"Compound: {row['Common_Name']}. "
            f"Molecular formula: {row['Formula']}. "
            f"Molecular weight: {row['Molecular_Weight']} g/mol. "
            f"Chemical name: {row['Chemical_Name']}. "
            f"This compound is found in Moringa oleifera."
        )
        compound_texts.append(text)

    # Convert articles into readable text
    article_texts = []
    for _, row in df_articles.iterrows():
        text = (
            f"Scientific article about {row['Compound']} in Moringa. "
            f"PubMed ID: {row['PMID']}. "
            f"Source: {row['Link']}. "
            f"Abstract excerpt: {row['Abstract']}"
        )
        article_texts.append(text)

    all_texts = compound_texts + article_texts
    print(f"  {len(compound_texts)} compound documents loaded")
    print(f"  {len(article_texts)} article documents loaded")
    print(f"  Total: {len(all_texts)} documents")
    return all_texts


def build_vector_store(texts):
    """
    Converts texts into vectors and stores them in FAISS.
    A vector = a list of numbers that represents the meaning of a text.
    FAISS finds the most similar vectors to a question in milliseconds.
    """

    print("\nBuilding vector store...")
    print("  Loading embedding model (first time may take 2-3 min)...")

    # This model converts text into vectors
    # It runs locally on your CPU — no API key needed
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    # Split long texts into smaller chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.create_documents(texts)
    print(f"  {len(chunks)} text chunks created")

    # Build the FAISS vector store
    print("  Building FAISS index...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    # Save locally so we don't rebuild every time
    vector_store.save_local("moringa_vectorstore")
    print("  Vector store saved in moringa_vectorstore/")

    return vector_store


def test_search(vector_store):
    """Tests a question on the knowledge base"""

    print("\nTesting knowledge base search...")
    print("-" * 45)

    questions = [
        "What are the anti-inflammatory compounds in Moringa?",
        "Which compound helps reduce cholesterol?",
        "What is the molecular formula of quercetin?"
    ]

    for question in questions:
        print(f"\n  Question: {question}")
        results = vector_store.similarity_search(question, k=2)
        print(f"  Best answer found:")
        print(f"  {results[0].page_content[:200]}...")


# --- Main program ---
texts        = load_knowledge()
vector_store = build_vector_store(texts)
test_search(vector_store)

print("\nKnowledge base ready!")
print("Next step: connect the LLM to answer questions intelligently!")