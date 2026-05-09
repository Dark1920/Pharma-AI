import requests
import pandas as pd
import time

# ============================================================
# 8 AFRICAN & TROPICAL MEDICINAL PLANTS
# ============================================================

PLANTS = {
    "Moringa oleifera": [
        "quercetin", "kaempferol", "glucosinolate",
        "chlorogenic acid", "beta-sitosterol", "zeatin", "niazimicin"
    ],
    "Azadirachta indica (Neem)": [
        "azadirachtin", "nimbin", "nimbidin", "gedunin"
    ],
    "Adansonia digitata (Baobab)": [
        "epicatechin", "rutin", "procyanidin"
    ],
    "Combretum micranthum (Kinkeliba)": [
        "combretastatin", "vitexin", "orientin", "luteolin"
    ],
    "Curcuma longa (Turmeric)": [
        "curcumin", "bisdemethoxycurcumin", "turmerone"
    ],
    "Zingiber officinale (Ginger)": [
        "gingerol", "shogaol", "zingerone"
    ],
    "Aloe vera": [
        "aloin", "aloe-emodin", "acemannan"
    ],
    "Catharanthus roseus (Periwinkle)": [
        "vincristine", "vinblastine", "catharanthine"
    ]
}


def fetch_compound(name, plant_name):
    """Fetches one compound from PubChem"""
    url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
        f"{requests.utils.quote(name)}/property/"
        f"MolecularFormula,MolecularWeight,IUPACName/JSON"
    )
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data     = response.json()
            compound = data["PropertyTable"]["Properties"][0]
            return {
                "Plant"           : plant_name,
                "Common_Name"     : name,
                "CID"             : compound.get("CID"),
                "Formula"         : compound.get("MolecularFormula"),
                "Molecular_Weight": compound.get("MolecularWeight"),
                "Chemical_Name"   : compound.get("IUPACName", "")[:80]
            }
        else:
            print(f"      Not found: {name}")
            return None
    except Exception as e:
        print(f"      Error for {name}: {e}")
        return None


def retrieve_all_plants(plants_dict):
    """Retrieves all compounds for all plants"""

    print("\nRetrieving compounds for all medicinal plants...")
    print("=" * 55)

    all_results = []

    for plant_name, compounds in plants_dict.items():
        print(f"\n  Plant: {plant_name}")
        found = 0

        for compound in compounds:
            print(f"    Searching: {compound}...")
            result = fetch_compound(compound, plant_name)
            if result:
                all_results.append(result)
                found += 1
                print(f"    Found: {result['Formula']} | {result['Molecular_Weight']} g/mol")
            time.sleep(0.4)

        print(f"  Result: {found}/{len(compounds)} compounds found")

    return pd.DataFrame(all_results)


def display_summary(df):
    """Displays a summary by plant"""
    print(f"\n{'='*55}")
    print(f"  SUMMARY — ALL MEDICINAL PLANTS")
    print(f"{'='*55}")
    for plant in df["Plant"].unique():
        sub = df[df["Plant"] == plant]
        print(f"\n  {plant}")
        for _, row in sub.iterrows():
            print(f"    • {row['Common_Name']:25} {row['Formula']}")
    print(f"\n  TOTAL: {len(df)} compounds | {df['Plant'].nunique()} plants")


# Main
df_plants = retrieve_all_plants(PLANTS)

if not df_plants.empty:
    display_summary(df_plants)
    df_plants.to_csv("composes_moringa.csv", index=False)
    print(f"\n  Saved in composes_moringa.csv")
    print(f"  Next: run pubmed_data.py")
else:
    print("No compounds retrieved")