import requests
import pandas as pd
import time

# ============================================================
# TARGETED SEARCH TERMS — ALL PLANTS & COMPOUNDS
# ============================================================

PLANT_COMPOUNDS = {
    "Moringa oleifera": {
        "quercetin"        : "quercetin Moringa anti-inflammatory antioxidant",
        "kaempferol"       : "kaempferol Moringa anticancer cardioprotective",
        "glucosinolate"    : "glucosinolate Moringa antibacterial",
        "chlorogenic acid" : "chlorogenic acid Moringa antidiabetic",
        "beta-sitosterol"  : "beta-sitosterol Moringa cholesterol",
        "zeatin"           : "zeatin Moringa oleifera medicinal",
        "niazimicin"       : "niazimicin Moringa anticancer"
    },
    "Azadirachta indica (Neem)": {
        "azadirachtin"     : "azadirachtin Neem antimicrobial insecticide",
        "nimbin"           : "nimbin Azadirachta anti-inflammatory",
        "nimbidin"         : "nimbidin Neem antibacterial antifungal",
        "gedunin"          : "gedunin Neem antimalarial anticancer"
    },
    "Adansonia digitata (Baobab)": {
        "epicatechin"      : "epicatechin Baobab Adansonia antioxidant Africa",
        "rutin"            : "rutin Baobab flavonoid cardiovascular Africa",
        "procyanidin"      : "procyanidin Adansonia digitata polyphenol"
    },
    "Combretum micranthum (Kinkeliba)": {
        "combretastatin"   : "combretastatin Combretum anticancer",
        "vitexin"          : "vitexin Combretum West Africa medicinal",
        "orientin"         : "orientin Kinkeliba antidiabetic Africa",
        "luteolin"         : "luteolin anti-inflammatory African plant"
    },
    "Curcuma longa (Turmeric)": {
        "curcumin"              : "curcumin Curcuma anti-inflammatory anticancer",
        "bisdemethoxycurcumin"  : "bisdemethoxycurcumin curcuminoid antioxidant",
        "turmerone"             : "turmerone Curcuma longa neuroprotective"
    },
    "Zingiber officinale (Ginger)": {
        "gingerol"         : "gingerol Zingiber anti-inflammatory analgesic",
        "shogaol"          : "shogaol ginger anticancer antioxidant",
        "zingerone"        : "zingerone ginger anti-inflammatory"
    },
    "Aloe vera": {
        "aloin"            : "aloin Aloe vera antimicrobial laxative",
        "aloe-emodin"      : "aloe-emodin Aloe vera anticancer antiviral",
        "acemannan"        : "acemannan Aloe vera immunostimulant healing"
    },
    "Catharanthus roseus (Periwinkle)": {
        "vincristine"      : "vincristine Catharanthus roseus anticancer chemo",
        "vinblastine"      : "vinblastine Catharanthus anticancer leukemia",
        "catharanthine"    : "catharanthine alkaloid Catharanthus medicinal"
    }
}


def fetch_ids(compound, search_term, max_articles=10):
    """Gets PubMed article IDs for a compound"""
    url    = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed", "term": search_term,
        "retmax": max_articles, "retmode": "json", "sort": "relevance"
    }
    try:
        r    = requests.get(url, params=params, timeout=15)
        data = r.json()["esearchresult"]
        print(f"      {data['count']} total → retrieving {len(data['idlist'])}")
        return data["idlist"]
    except Exception as e:
        print(f"      Error: {e}")
        return []


def fetch_abstracts(ids):
    """Gets full abstracts for a list of PubMed IDs"""
    if not ids:
        return ""
    url    = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": ",".join(ids), "rettype": "abstract", "retmode": "text"}
    try:
        return requests.get(url, params=params, timeout=20).text
    except Exception as e:
        print(f"      Fetch error: {e}")
        return ""


def parse_articles(raw_text, ids, compound, plant):
    """Structures raw abstracts into article records"""
    blocks = [b.strip() for b in raw_text.split("\n\n\n") if b.strip()]
    return [
        {
            "Plant"       : plant,
            "Compound"    : compound,
            "PMID"        : pmid,
            "Link"        : f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "Abstract"    : " ".join((blocks[i] if i < len(blocks) else raw_text[:500]).split()),
            "Abstract_len": len(" ".join((blocks[i] if i < len(blocks) else raw_text[:500]).split()))
        }
        for i, pmid in enumerate(ids)
    ]


def retrieve_all(plant_compounds, max_articles=10):
    """Retrieves all articles for all plants and compounds"""

    print("\nRetrieving PubMed articles for all medicinal plants...")
    print(f"Target: {max_articles} articles per compound")
    print("=" * 55)

    all_articles = []
    total_chars  = 0

    for plant, compounds in plant_compounds.items():
        print(f"\n  Plant: {plant}")
        plant_count = 0

        for compound, search_term in compounds.items():
            print(f"    Compound: {compound}")
            ids      = fetch_ids(compound, search_term, max_articles)
            if not ids:
                continue
            raw      = fetch_abstracts(ids)
            articles = parse_articles(raw, ids, compound, plant)
            all_articles.extend(articles)
            plant_count += len(articles)
            total_chars += sum(a["Abstract_len"] for a in articles)
            time.sleep(1)  # Mandatory PubMed pause

        print(f"  Subtotal: {plant_count} articles")

    # Final stats
    print(f"\n{'='*55}")
    print(f"  RETRIEVAL COMPLETE")
    print(f"{'='*55}")
    df = pd.DataFrame(all_articles)
    if not df.empty:
        print(f"  Total articles : {len(df)}")
        print(f"  Total text     : {total_chars:,} characters")
        print(f"  By plant:")
        for plant in df["Plant"].unique():
            n = len(df[df["Plant"] == plant])
            print(f"    {plant:45} {n:3} articles")
    return df


# Main
df = retrieve_all(PLANT_COMPOUNDS, max_articles=10)

if not df.empty:
    df.to_csv("moringa_articles.csv", index=False)
    print(f"\n  Saved in moringa_articles.csv")
    print(f"\n  NEXT STEPS:")
    print(f"  1. python rag_knowledge.py   ← rebuild knowledge base")
    print(f"  2. streamlit run app.py      ← launch interface")
else:
    print("No articles retrieved")