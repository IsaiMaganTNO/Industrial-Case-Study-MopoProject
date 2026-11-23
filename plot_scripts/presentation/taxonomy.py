"""Scenario taxonomy: maps raw unit / node names onto the groups used in the deck.

Everything is pattern-based and auditable - `build_deck.py` prints anything that
falls through to a catch-all so the lists can be extended.
"""
from __future__ import annotations

import re

import theme as T

# ----------------------------------------------------------- emission sources
# ordered: first match wins
EMISSION_GROUPS = [
    (r"^CO2-injection", "CO\u2082 stored underground"),
    (r"^LNG-terminal", "Natural gas supply"),
    (r"^REF-SMR", "Refining & grey hydrogen"),
    (r"^BF-BOF|^DRI|DRI-EAF", "Iron & steel"),
    (r"^SCPC|^CCGT|^OCGT|^GT-|^CHP", "Power generation"),
    (r"^EU-mix", "Imported electricity"),
    (r"^CEM|^LC3", "Cement & lime"),
    (r"_gco$|_gfi$|_gfl$|^\(EL\)|^\(H2\)", "Glass"),
    (r"\(NG\)|\(LN\)|\(COEL\)|^Diaphragm|^Membrane|^Mercury", "Chemicals & ammonia"),
    (r"^bio-|^BECCS|^biomass", "Bioenergy"),
    (r"^DAC", "Direct air capture"),
    (r"-production-reference$", "Other manufacturing"),
    (r"^boiler|^burner|^furnace", "Industrial heat"),
]

EMISSION_COLOR = {
    "Natural gas supply": T.SAND,
    "Iron & steel": T.INK,
    "Refining & grey hydrogen": T.VIOLET,
    "Chemicals & ammonia": T.TEAL,
    "Power generation": T.CORAL,
    "Cement & lime": T.SLATE,
    "Glass": T.BLUE,
    "Imported electricity": T.PLUM,
    "Other manufacturing": T.AMBER,
    "Industrial heat": T.MINT,
    "Bioenergy": T.GREEN,
    "Direct air capture": T.BLUE,
    "CO\u2082 stored underground": T.GREEN,
    "Other": T.FAINT,
}

# ------------------------------------------------------------ industry sectors
SECTORS = {
    "steel-primary": "Steel \u2014 primary",
    "steel-secondary": "Steel \u2014 secondary",
    "cement": "Cement",
    "chemical-olefins": "Olefins",
    "chemical-PEA": "Ethylene oxide / PEA",
    "chemical-PE": "Polyethylene",
    "chemical-chlorine": "Chlorine",
    "other-chemicals": "Other chemicals",
    "fertiliser-ammonia-NH3": "Ammonia",
    "glass-float": "Glass \u2014 float",
    "glass-container": "Glass \u2014 container",
    "glass-fibre": "Glass \u2014 fibre",
    "paper": "Paper",
    "pulp": "Pulp",
    "aluminium-primary": "Aluminium",
    "other-non-ferrous-metals": "Other non-ferrous",
    "ceramics-and-other-non-metalic-minerals": "Ceramics & minerals",
    "food-beverages-tobacco": "Food & beverages",
    "machinery-equipment": "Machinery",
    "transport-equipment": "Transport equipment",
    "wood-and-wood-products": "Wood products",
    "leather-and-textile": "Leather & textile",
    "printing-and-media": "Printing & media",
    "pharmaceuticals": "Pharmaceuticals",
    "other-industrial-sectors": "Other industry",
}

HEAVY_INDUSTRY = ["Steel \u2014 primary", "Cement", "Olefins", "Ammonia",
                  "Ethylene oxide / PEA", "Polyethylene", "Chlorine",
                  "Glass \u2014 float", "Paper", "Other chemicals"]

# ------------------------------------------------------------- capture sources
CAPTURE_LABEL = [
    (r"^DAC", "Direct air capture"),
    (r"^bio-diges", "Biomethane upgrading"),
    (r"^CEM|^LC3", "Cement"),
    (r"^REF-SMR|^SMR", "Hydrogen (SMR)"),
    (r"^\(NG\)NH3", "Ammonia"),
    (r"^\(LN\)O|^\(COEL\)", "Olefins & e-fuels"),
    (r"^CCGT", "Gas power"),
]

CAPTURE_COLOR = {
    "Direct air capture": T.BLUE,
    "Biomethane upgrading": T.GREEN,
    "Cement": T.SLATE,
    "Hydrogen (SMR)": T.VIOLET,
    "Ammonia": T.TEAL,
    "Olefins & e-fuels": T.AMBER,
    "Gas power": T.CORAL,
}

# --------------------------------------------------------- electricity sources
SUPPLY_GROUPS = [
    (r"^solar-PV", "Solar PV"),
    (r"^wind-off", "Wind offshore"),
    (r"^wind-on", "Wind onshore"),
    (r"^RoR|^hydro", "Hydro"),
    (r"^nuclear", "Nuclear"),
    (r"^wasteST|^waste", "Waste"),
    (r"__(?:car|truck|bus)-DR$|^battery|^storage", "Demand response & storage"),
    (r"^LH2-terminal", "Hydrogen import"),
    (r"^LNG-terminal", "LNG import"),
    (r"^gas-extraction", "Domestic gas"),
    (r"^REF-SMR-MEA|^SMR\+CC", "SMR + CCS"),
    (r"^REF-SMR|^SMR", "SMR"),
    (r"^PEM|^AEC|^SOEC|^electroly|^Alkaline", "Electrolysis"),
    (r"^CCGT\+CC|^SCPC\+CC", "Gas + CCS"),
    (r"^CCGT|^OCGT|^GT-|^gas-boiler|^gas-eng", "Gas"),
    (r"^SCPC|^coal", "Coal"),
    (r"^oil-", "Oil"),
    (r"^bio", "Bioenergy"),
    (r"^EU-mix|^import", "Imports"),
    (r"^electric-heating|^air-heatpump|^heatpump|^HP-", "Electric heat"),
]

SUPPLY_COLOR = {
    "Solar PV": T.AMBER,
    "Wind offshore": T.BLUE,
    "Wind onshore": T.MINT,
    "Hydro": "#3f7fa6",
    "Bioenergy": T.GREEN,
    "Nuclear": T.VIOLET,
    "Waste": T.PLUM,
    "Gas + CCS": T.TEAL,
    "Gas": T.SAND,
    "Coal": T.INK,
    "Oil": "#7a5c3e",
    "Imports": T.PLUM,
    "Demand response & storage": T.SLATE,
    "LNG import": T.SAND,
    "Hydrogen import": T.BLUE,
    "Domestic gas": T.AMBER,
    "SMR + CCS": T.TEAL,
    "SMR": T.VIOLET,
    "Electrolysis": T.CORAL,
    "Electric heat": T.MINT,
    "Other": T.FAINT,
}


def _match(name, table, default="Other"):
    for pattern, label in table:
        if re.search(pattern, str(name)):
            return label
    return default


def emission_group(tech):
    return _match(tech, EMISSION_GROUPS)


def capture_group(tech):
    return _match(tech, CAPTURE_LABEL)


def supply_group(tech):
    return _match(tech, SUPPLY_GROUPS)


def sector_of(node_prefix):
    return SECTORS.get(node_prefix)


# ------------------------------------------------------------- process routes
FOSSIL_IN = ("CH4", "fossil-CH4", "coal", "crude", "HC", "bunker-HC", "U-92",
             "MeOH", "waste", "LNG")
BIO_IN = ("bio", "biomass-stock")

ROUTE_ORDER = ["Fossil, unabated", "Fossil + CCS", "Biomass", "Biomass + hydrogen",
               "Biomass + CCS", "Hydrogen", "Electrified"]

ROUTE_COLOR = {
    "Fossil, unabated": T.CORAL,
    "Fossil + CCS": T.AMBER,
    "Biomass": T.GREEN,
    "Biomass + hydrogen": T.MINT,
    "Biomass + CCS": T.TEAL,
    "Hydrogen": T.VIOLET,
    "Electrified": T.BLUE,
}


def route_category(inputs, has_ccs):
    """Classify a production route from what it actually consumed.

    `inputs` maps carrier -> annual volume. Waste counts as fossil, which is the
    conservative reading for the EU clinker mix.
    """
    fossil = sum(v for k, v in inputs.items() if k in FOSSIL_IN)
    bio = sum(v for k, v in inputs.items() if k in BIO_IN)
    h2 = inputs.get("H2", 0.0)
    if fossil + bio <= 1e-9:
        return "Hydrogen" if h2 > 1e-9 else "Electrified"
    if fossil / (fossil + bio) > 0.5:
        return "Fossil + CCS" if has_ccs else "Fossil, unabated"
    if has_ccs:
        return "Biomass + CCS"
    return "Biomass + hydrogen" if h2 > 1e-9 else "Biomass"


# --------------------------------------------------------------- region layout
# Schematic positions on a unit square, NOT geographic coordinates. The two
# databases carry no `entity_location` rows. Replace the values here with real
# lon/lat if a coordinate source becomes available - nothing else needs to change.
REGION_XY = {
    "NLC1": (0.17, 0.90), "NLC2": (0.33, 0.95), "NLC3": (0.30, 0.78),
    "NLC4": (0.52, 0.93), "NLC5": (0.47, 0.76), "NLC6": (0.64, 0.79),
    "NLC7": (0.63, 0.64), "NLC8": (0.80, 0.90), "NLC9": (0.86, 0.74),
    "BEC1": (0.14, 0.38), "BEC2": (0.28, 0.46), "BEC3": (0.40, 0.33),
    "BEC4": (0.52, 0.45), "BEC5": (0.63, 0.31), "BEC6": (0.74, 0.44),
    "BEC7": (0.85, 0.33), "BEC8": (0.93, 0.47),
}

STORAGE_XY = {
    "CO2-storage-NSNL031": (0.06, 0.70),
    "CO2-storage-NSNL012": (0.06, 0.60),
}

COUNTRY_OF = {r: ("Netherlands" if r.startswith("NL") else "Belgium")
              for r in REGION_XY}
