import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load API key from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found! Check your .env file.")


def load_vector_store():
    """Loads the knowledge base built in rag_knowledge.py"""
    print("Loading knowledge base...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )
    vector_store = FAISS.load_local(
        "moringa_vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("Knowledge base loaded!")
    return vector_store


def create_agent(vector_store):
    """
    Creates the biomedical AI agent using modern LangChain syntax.
    - LLM    : Llama 3 via Groq (free, fast, no GPU needed)
    - Retriever : FAISS searches the 3 most relevant documents
    - Prompt : instructions that make the LLM behave as a pharmacognosy expert
    """

    # The brain — Llama 3 via Groq
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.1
    )

    # The retriever — finds the 3 most relevant documents for each question
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # The prompt — expert pharmacognosy instructions
    prompt_template = PromptTemplate.from_template("""
You are an expert biomedical agent specialized in pharmacognosy
(the study of medicinal plants and their active compounds).

Use ONLY the scientific context below to answer the question.
Always mention the compound name or PubMed ID as your source.
If the answer is not in the context, say: "I don't have enough data on this."
Never invent information.

--- Scientific context ---
{context}
-------------------------

Question: {question}

Expert answer:""")

    # Helper to format retrieved documents into a single text block
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Modern LangChain chain: retriever → prompt → LLM → text output
    chain = (
        {
            "context" : retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )

    return chain, retriever


def ask_agent(chain, retriever, question):
    """Asks the agent a question and displays the answer with sources"""
    print(f"\n{'='*55}")
    print(f"  Question: {question}")
    print(f"{'='*55}")

    # Get the answer
    answer = chain.invoke(question)
    print(f"\n  Answer:\n  {answer}")

    # Show which documents were used
    source_docs = retriever.invoke(question)
    print(f"\n  Sources used ({len(source_docs)}):")
    for i, doc in enumerate(source_docs, 1):
        print(f"  [{i}] {doc.page_content[:120]}...")


# Main program
vector_store      = load_vector_store()
chain, retriever  = create_agent(vector_store)

print("\nAgent ready! Testing with 3 biomedical questions...\n")

ask_agent(chain, retriever,
          "What are the anti-inflammatory properties of quercetin in Moringa?")

ask_agent(chain, retriever,
          "Which compounds in Moringa help fight cancer?")

ask_agent(chain, retriever,
          "What is the molecular weight of kaempferol and what is it used for?")

print(f"\n{'='*55}")
print("  Agent test complete!")
print("  Next step: build the Streamlit interface!")
print(f"{'='*55}")