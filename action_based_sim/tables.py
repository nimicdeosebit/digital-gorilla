"""Paper table data, the single source of truth. There are no simulation logic here, this is only data."""

ACTORS = ["People", "State", "Enterprises", "AI"]

MODALITIES = ["Economic", "Epistemic", "Narrative", "Authoritative", "Physical"]


# Table 4-derived initial shares. Each modality's four values sum to 1.0
# (zero-sum). Our own numeric reading of Table 4's low/med/high cells.
INITIAL_POWER = {
    "Economic":      {"People": 0.20, "State": 0.25, "Enterprises": 0.50, "AI": 0.05},
    "Epistemic":     {"People": 0.20, "State": 0.25, "Enterprises": 0.40, "AI": 0.15},
    "Narrative":     {"People": 0.25, "State": 0.25, "Enterprises": 0.35, "AI": 0.15},
    "Authoritative": {"People": 0.10, "State": 0.60, "Enterprises": 0.27, "AI": 0.03},
    "Physical":      {"People": 0.20, "State": 0.55, "Enterprises": 0.23, "AI": 0.02},
}


# Table 5-derived initial legitimacy. State/People high, Enterprises medium,
# AI low (delegated procedural legitimacy).
INITIAL_LEGITIMACY = {
    "People": 0.65,
    "State": 0.70,
    "Enterprises": 0.55,
    "AI": 0.35,
}


# Table 6: legality reduces to "not the same actor" (every off-diagonal
# pair has a real mechanism listed in the paper).
def is_check_legal(frm: str, to: str) -> bool:
    return frm != to and frm in ACTORS and to in ACTORS


# Table 6 mechanisms, per (from, to). `weight` multiplies effect_magnitude
# when that mechanism resolves a CHECK. Kept at 1.0 for now.
CHECK_MECHANISMS = {
    ("People", "State"): [
        {"name": "Voting", "weight": 1.0},
        {"name": "Protest", "weight": 1.0},
        {"name": "Civil Disobedience", "weight": 1.0},
        {"name": "Jury Nullification", "weight": 1.0},
        {"name": "Public Opinion", "weight": 1.0},
    ],
    ("People", "Enterprises"): [
        {"name": "Consumer Choice", "weight": 1.0},
        {"name": "Labor Strikes", "weight": 1.0},
        {"name": "Reputational Pressure", "weight": 1.0},
        {"name": "Litigation", "weight": 1.0},
    ],
    ("People", "AI"): [
        {"name": "Refusal to Adopt", "weight": 1.0},
        {"name": "Prompt Steering", "weight": 1.0},
        {"name": "Adversarial Use", "weight": 1.0},
        {"name": "Sectoral/Unionized Action", "weight": 1.0},
    ],
    ("State", "People"): [
        {"name": "Law Enforcement", "weight": 1.0},
        {"name": "Surveillance", "weight": 1.0},
        {"name": "Coercion", "weight": 1.0},
    ],
    ("State", "Enterprises"): [
        {"name": "Regulation", "weight": 1.0},
        {"name": "Antitrust Enforcement", "weight": 1.0},
        {"name": "Taxation", "weight": 1.0},
        {"name": "Procurement Control", "weight": 1.0},
    ],
    ("State", "AI"): [
        {"name": "Legislation", "weight": 1.0},
        {"name": "Bans", "weight": 1.0},
        {"name": "Export Controls", "weight": 1.0},
        {"name": "Nationalization", "weight": 1.0},
        {"name": "Kill Switches", "weight": 1.0},
    ],
    ("Enterprises", "People"): [
        {"name": "Product Design", "weight": 1.0},
        {"name": "Pricing", "weight": 1.0},
        {"name": "Availability", "weight": 1.0},
        {"name": "Targeted Marketing", "weight": 1.0},
    ],
    ("Enterprises", "State"): [
        {"name": "Lobbying", "weight": 1.0},
        {"name": "Regulatory Capture", "weight": 1.0},
        {"name": "Privatized Infrastructure", "weight": 1.0},
        {"name": "Political Donations", "weight": 1.0},
    ],
    ("Enterprises", "AI"): [
        {"name": "AI Development", "weight": 1.0},
        {"name": "Ownership", "weight": 1.0},
        {"name": "Training Data Control", "weight": 1.0},
        {"name": "Capability Throttling", "weight": 1.0},
    ],
    ("AI", "People"): [
        {"name": "Fostering Monoculture", "weight": 1.0},
        {"name": "Manipulating Choices", "weight": 1.0},
        {"name": "Eroding Attention", "weight": 1.0},
        {"name": "Polarizing Norms", "weight": 1.0},
    ],
    ("AI", "State"): [
        {"name": "Outpacing Regulation", "weight": 1.0},
        {"name": "Undermining Legitimacy via Misinformation", "weight": 1.0},
        {"name": "Systems Gaming", "weight": 1.0},
    ],
    ("AI", "Enterprises"): [
        {"name": "Automating Decisions", "weight": 1.0},
        {"name": "Price Manipulation", "weight": 1.0},
        {"name": "Labor Displacement", "weight": 1.0},
        {"name": "Market Disruption", "weight": 1.0},
    ],
}


# Table 7: shock library. Each entry favors one actor in a modality; the
# intervention field is kept for traceability, not yet wired into effects.
SHOCKS = [
    {
        "id": 1,
        "conflict_pair": ("Enterprises", "People"),
        "modality": "Economic",
        "favored_actor": "Enterprises",
        "disfavored_actor": "People",
        "description": "Market shocks and automation crises concentrate resource "
                        "control in corporate actors.",
        "intervention": "Call for redistributive policy and labor safeguards.",
    },
    {
        "id": 2,
        "conflict_pair": ("AI", "State"),
        "modality": "Epistemic",
        "favored_actor": "AI",
        "disfavored_actor": "State",
        "description": "AI systems outperform bureaucratic capacity for data analysis.",
        "intervention": "Establish epistemic oversight councils to prevent information monopoly.",
    },
    {
        "id": 3,
        "conflict_pair": ("AI", "People"),
        "modality": "Narrative",
        "favored_actor": "AI",
        "disfavored_actor": "People",
        "description": "Algorithmic virality and synthetic media outpace civic "
                        "narrative formation.",
        "intervention": "Strengthen public media literacy and disclosure norms.",
    },
    {
        "id": 4,
        "conflict_pair": ("State", "People"),
        "modality": "Authoritative",
        "favored_actor": "State",
        "disfavored_actor": "People",
        "description": "Emergency powers expand during crises.",
        "intervention": "Integrate sunset clauses and independent review to prevent "
                         "normalization of exceptional authority.",
    },
    {
        "id": 5,
        "conflict_pair": ("State", "Enterprises"),
        "modality": "Physical",
        "favored_actor": "State",
        "disfavored_actor": "Enterprises",
        "description": "Infrastructure and coercive capacity remain state-dominant.",
        "intervention": "Partnership frameworks should clarify boundaries on "
                         "surveillance and cyber enforcement.",
    },
]
