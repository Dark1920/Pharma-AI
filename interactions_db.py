# ============================================================
# KNOWN INTERACTIONS DATABASE
# Sources: DrugBank, PubMed, WHO monographs
# ============================================================

# Risk levels
LOW      = "LOW"
MODERATE = "MODERATE"
HIGH     = "HIGH"

# PLANT-DRUG INTERACTIONS
PLANT_DRUG_INTERACTIONS = [
    {
        "plant"      : "Moringa oleifera",
        "compound"   : "beta-sitosterol",
        "drug"       : "Metformin",
        "drug_class" : "Antidiabetic",
        "effect"     : "Additive hypoglycemic effect — may lower blood sugar excessively",
        "mechanism"  : "Both reduce glucose absorption and improve insulin sensitivity",
        "risk"       : HIGH,
        "action"     : "Monitor blood glucose closely. Dose adjustment may be needed."
    },
    {
        "plant"      : "Moringa oleifera",
        "compound"   : "quercetin",
        "drug"       : "Warfarin",
        "drug_class" : "Anticoagulant",
        "effect"     : "Quercetin inhibits CYP2C9 enzyme, increasing warfarin blood levels",
        "mechanism"  : "CYP2C9 inhibition reduces warfarin metabolism → bleeding risk",
        "risk"       : HIGH,
        "action"     : "Avoid combination. Consult physician before use."
    },
    {
        "plant"      : "Moringa oleifera",
        "compound"   : "kaempferol",
        "drug"       : "Atorvastatin",
        "drug_class" : "Statin (cholesterol)",
        "effect"     : "Kaempferol may enhance statin effect on cholesterol reduction",
        "mechanism"  : "HMG-CoA reductase pathway synergy",
        "risk"       : MODERATE,
        "action"     : "Monitor cholesterol levels. Potentially beneficial combination."
    },
    {
        "plant"      : "Azadirachta indica (Neem)",
        "compound"   : "nimbin",
        "drug"       : "Cyclosporine",
        "drug_class" : "Immunosuppressant",
        "effect"     : "Neem may reduce immunosuppressant efficacy",
        "mechanism"  : "Immunostimulant properties of Neem oppose immunosuppression",
        "risk"       : HIGH,
        "action"     : "Avoid in transplant patients. Serious rejection risk."
    },
    {
        "plant"      : "Azadirachta indica (Neem)",
        "compound"   : "azadirachtin",
        "drug"       : "Insulin",
        "drug_class" : "Antidiabetic",
        "effect"     : "Additive blood glucose lowering effect",
        "mechanism"  : "Neem has documented hypoglycemic activity",
        "risk"       : MODERATE,
        "action"     : "Monitor blood glucose. May need insulin dose reduction."
    },
    {
        "plant"      : "Curcuma longa (Turmeric)",
        "compound"   : "curcumin",
        "drug"       : "Aspirin",
        "drug_class" : "Antiplatelet / NSAID",
        "effect"     : "Enhanced antiplatelet effect — increased bleeding risk",
        "mechanism"  : "Both inhibit thromboxane synthesis and platelet aggregation",
        "risk"       : MODERATE,
        "action"     : "Use caution. Avoid before surgery."
    },
    {
        "plant"      : "Curcuma longa (Turmeric)",
        "compound"   : "curcumin",
        "drug"       : "Docetaxel",
        "drug_class" : "Chemotherapy",
        "effect"     : "Curcumin may enhance anticancer efficacy of docetaxel",
        "mechanism"  : "NF-kB pathway inhibition synergy",
        "risk"       : LOW,
        "action"     : "Potentially beneficial. Discuss with oncologist."
    },
    {
        "plant"      : "Zingiber officinale (Ginger)",
        "compound"   : "gingerol",
        "drug"       : "Warfarin",
        "drug_class" : "Anticoagulant",
        "effect"     : "Gingerol inhibits platelet aggregation — enhanced anticoagulation",
        "mechanism"  : "Thromboxane synthetase inhibition",
        "risk"       : HIGH,
        "action"     : "Avoid combination. Serious bleeding risk."
    },
    {
        "plant"      : "Zingiber officinale (Ginger)",
        "compound"   : "gingerol",
        "drug"       : "Metformin",
        "drug_class" : "Antidiabetic",
        "effect"     : "Additive antidiabetic effect",
        "mechanism"  : "Gingerol improves insulin sensitivity independently",
        "risk"       : LOW,
        "action"     : "Generally safe. Monitor blood glucose."
    },
    {
        "plant"      : "Aloe vera",
        "compound"   : "aloin",
        "drug"       : "Digoxin",
        "drug_class" : "Cardiac glycoside",
        "effect"     : "Aloin causes potassium loss → increases digoxin toxicity",
        "mechanism"  : "Laxative effect → hypokalemia → digoxin toxicity",
        "risk"       : HIGH,
        "action"     : "Contraindicated. Serious cardiac arrhythmia risk."
    },
    {
        "plant"      : "Catharanthus roseus (Periwinkle)",
        "compound"   : "vincristine",
        "drug"       : "Itraconazole",
        "drug_class" : "Antifungal",
        "effect"     : "Itraconazole increases vincristine blood levels → neurotoxicity",
        "mechanism"  : "CYP3A4 inhibition reduces vincristine metabolism",
        "risk"       : HIGH,
        "action"     : "Avoid combination in chemotherapy protocols."
    },
    {
        "plant"      : "Combretum micranthum (Kinkeliba)",
        "compound"   : "luteolin",
        "drug"       : "Metformin",
        "drug_class" : "Antidiabetic",
        "effect"     : "Luteolin enhances antidiabetic effect of metformin",
        "mechanism"  : "AMPK pathway activation — additive glucose lowering",
        "risk"       : MODERATE,
        "action"     : "Monitor blood glucose carefully."
    }
]

# PLANT-PLANT INTERACTIONS
PLANT_PLANT_INTERACTIONS = [
    {
        "plant_1"   : "Moringa oleifera",
        "plant_2"   : "Azadirachta indica (Neem)",
        "compounds" : "beta-sitosterol + azadirachtin",
        "effect"    : "Enhanced antibacterial and anti-inflammatory effect",
        "mechanism" : "Synergistic membrane disruption of bacterial cells",
        "risk"      : LOW,
        "action"    : "Safe combination. Traditional use documented in West Africa."
    },
    {
        "plant_1"   : "Curcuma longa (Turmeric)",
        "plant_2"   : "Zingiber officinale (Ginger)",
        "compounds" : "curcumin + gingerol",
        "effect"    : "Synergistic anti-inflammatory and antioxidant effect",
        "mechanism" : "Complementary NF-kB and COX-2 inhibition pathways",
        "risk"      : LOW,
        "action"    : "Beneficial combination. Widely used in traditional medicine."
    },
    {
        "plant_1"   : "Moringa oleifera",
        "plant_2"   : "Curcuma longa (Turmeric)",
        "compounds" : "quercetin + curcumin",
        "effect"    : "Additive antioxidant and anti-inflammatory properties",
        "mechanism" : "Different antioxidant pathways act complementarily",
        "risk"      : LOW,
        "action"    : "Safe. Potentially very beneficial combination."
    },
    {
        "plant_1"   : "Aloe vera",
        "plant_2"   : "Azadirachta indica (Neem)",
        "compounds" : "acemannan + nimbidin",
        "effect"    : "Enhanced wound healing and antimicrobial activity",
        "mechanism" : "Acemannan promotes tissue repair; nimbidin prevents infection",
        "risk"      : LOW,
        "action"    : "Safe topical combination. Common in traditional remedies."
    },
    {
        "plant_1"   : "Combretum micranthum (Kinkeliba)",
        "plant_2"   : "Moringa oleifera",
        "compounds" : "orientin + chlorogenic acid",
        "effect"    : "Synergistic antidiabetic effect",
        "mechanism" : "Both inhibit alpha-glucosidase reducing glucose absorption",
        "risk"      : MODERATE,
        "action"    : "Monitor blood glucose. May enhance antidiabetic medication."
    },
    {
        "plant_1"   : "Catharanthus roseus (Periwinkle)",
        "plant_2"   : "Aloe vera",
        "compounds" : "vincristine + aloin",
        "effect"    : "Aloin-induced hypokalemia may increase vincristine neurotoxicity",
        "mechanism" : "Electrolyte imbalance amplifies vincristine side effects",
        "risk"      : HIGH,
        "action"    : "Avoid combination during chemotherapy."
    }
]


def search_plant_drug(plant_query, drug_query):
    """Searches for interactions between a plant and a drug"""
    plant_q = plant_query.lower()
    drug_q  = drug_query.lower()
    results = []
    for inter in PLANT_DRUG_INTERACTIONS:
        plant_match = plant_q in inter["plant"].lower() or plant_q in inter["compound"].lower()
        drug_match  = drug_q  in inter["drug"].lower()  or drug_q  in inter["drug_class"].lower()
        if plant_match and drug_match:
            results.append(inter)
        elif plant_match and not drug_query:
            results.append(inter)
        elif drug_match and not plant_query:
            results.append(inter)
    return results


def search_plant_plant(plant1_query, plant2_query=""):
    """Searches for interactions between two plants"""
    p1 = plant1_query.lower()
    p2 = plant2_query.lower()
    results = []
    for inter in PLANT_PLANT_INTERACTIONS:
        p1_match = p1 in inter["plant_1"].lower() or p1 in inter["plant_2"].lower()
        p2_match = (p2 in inter["plant_1"].lower() or p2 in inter["plant_2"].lower()) if p2 else True
        if p1_match and p2_match:
            results.append(inter)
    return results


def get_risk_color(risk):
    return {"HIGH": "🔴", "MODERATE": "🟡", "LOW": "🟢"}.get(risk, "⚪")


if __name__ == "__main__":
    print("=== TEST: Moringa + Warfarin ===")
    results = search_plant_drug("Moringa", "Warfarin")
    for r in results:
        print(f"{get_risk_color(r['risk'])} {r['risk']} — {r['effect']}")
        print(f"   Action: {r['action']}\n")

    print("=== TEST: Turmeric + Ginger ===")
    results = search_plant_plant("Turmeric", "Ginger")
    for r in results:
        print(f"{get_risk_color(r['risk'])} {r['risk']} — {r['effect']}")
        print(f"   Action: {r['action']}\n")