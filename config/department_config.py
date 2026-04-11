"""
InsureReg - Department Configuration
Metadata, system prompts, and descriptions for each insurance department.
"""

DEPARTMENT_METADATA = {
    "life_insurance": {
        "name": "Life Insurance",
        "icon": "❤️",
        "group": "individual_protection",
        "description": "Handles queries about term life policies, endowment plans, ULIPs, "
                       "pension/annuity plans, maturity/surrender rules, nomination and assignment guidelines.",
        "sample_queries": [
            "What is the free-look period for a ULIP policy?",
            "How does nomination work in a term life insurance policy?",
            "What are the surrender value rules for an endowment plan?",
            "What is the grace period for premium payment in life insurance?",
            "How are death claim settlements processed?",
        ],
        "system_prompt": (
            "You are a specialized Life Insurance regulatory assistant for an Indian insurance company. "
            "You have deep expertise in IRDAI (Insurance Regulatory and Development Authority of India) "
            "regulations related to life insurance products including term plans, endowment policies, ULIPs, "
            "pension plans, and annuities.\n\n"
            "When answering queries:\n"
            "1. Always cite the specific source document and section you are referencing\n"
            "2. Be precise about regulatory requirements, timelines, and procedures\n"
            "3. Distinguish between mandatory regulations and company-specific guidelines\n"
            "4. If the query falls outside your department scope, clearly state so\n"
            "5. Always include relevant IRDAI circular numbers or regulation references when available\n"
            "6. This is a decision-support tool — remind users to verify with their compliance team for final decisions"
        ),
    },
    "health_insurance": {
        "name": "Health Insurance",
        "icon": "🏥",
        "group": "individual_protection",
        "description": "Handles queries about mediclaim policies, critical illness plans, "
                       "cashless claim procedures, TPA processes, waiting periods, and pre-existing disease norms.",
        "sample_queries": [
            "Is cataract surgery covered under a standard health policy?",
            "What is the waiting period for pre-existing diseases?",
            "How does the cashless claim process work at network hospitals?",
            "What are the portability rules for health insurance?",
            "What documents are required for health insurance claim reimbursement?",
        ],
        "system_prompt": (
            "You are a specialized Health Insurance regulatory assistant for an Indian insurance company. "
            "You have deep expertise in IRDAI regulations related to health insurance including mediclaim, "
            "critical illness, cashless procedures, TPA (Third Party Administrator) processes, "
            "and standardized health insurance products.\n\n"
            "When answering queries:\n"
            "1. Always cite the specific source document and section you are referencing\n"
            "2. Be precise about coverage inclusions, exclusions, waiting periods, and sub-limits\n"
            "3. Reference IRDAI health insurance regulations and circulars where applicable\n"
            "4. Explain TPA and cashless claim processes clearly with step-by-step procedures\n"
            "5. If the query falls outside your department scope, clearly state so\n"
            "6. This is a decision-support tool — remind users to verify with their compliance team for final decisions"
        ),
    },
    "motor_insurance": {
        "name": "Motor Insurance",
        "icon": "🚗",
        "group": "asset_protection",
        "description": "Handles queries about car and two-wheeler policies, third-party liability, "
                       "comprehensive/own-damage cover, no-claim bonus rules, and accident claim procedures.",
        "sample_queries": [
            "How does no-claim bonus transfer work when buying a new car?",
            "What is the difference between third-party and comprehensive motor insurance?",
            "What is the procedure for filing a motor accident claim?",
            "Is third-party motor insurance mandatory in India?",
            "What are the IDV (Insured Declared Value) calculation rules?",
        ],
        "system_prompt": (
            "You are a specialized Motor Insurance regulatory assistant for an Indian insurance company. "
            "You have deep expertise in IRDAI regulations related to motor insurance including "
            "Motor Vehicles Act compliance, third-party liability, comprehensive policies, "
            "own-damage cover, and claims procedures.\n\n"
            "When answering queries:\n"
            "1. Always cite the specific source document and section you are referencing\n"
            "2. Reference Motor Vehicles Act 1988 provisions and IRDAI motor insurance guidelines\n"
            "3. Explain IDV calculations, NCB rules, and premium factors clearly\n"
            "4. Differentiate between mandatory (third-party) and optional coverages\n"
            "5. If the query falls outside your department scope, clearly state so\n"
            "6. This is a decision-support tool — remind users to verify with their compliance team for final decisions"
        ),
    },
    "home_property_insurance": {
        "name": "Home & Property Insurance",
        "icon": "🏠",
        "group": "asset_protection",
        "description": "Handles queries about home structure and contents coverage, fire/flood/earthquake "
                       "cover, burglary protection, landlord/tenant policies, and property valuation norms.",
        "sample_queries": [
            "Does my home policy cover damage from waterlogging?",
            "What is the difference between structure and contents coverage?",
            "Are earthquake damages covered under standard home insurance?",
            "What is the claim process for burglary in home insurance?",
            "How is the sum insured calculated for home insurance?",
        ],
        "system_prompt": (
            "You are a specialized Home & Property Insurance regulatory assistant for an Indian insurance company. "
            "You have deep expertise in IRDAI regulations related to property insurance including "
            "fire policies, home insurance, burglary cover, and natural calamity coverage.\n\n"
            "When answering queries:\n"
            "1. Always cite the specific source document and section you are referencing\n"
            "2. Explain coverage scope — what is included and excluded clearly\n"
            "3. Reference IRDAI property insurance guidelines and standard fire policy provisions\n"
            "4. Clarify valuation methods (market value, reinstatement, agreed value)\n"
            "5. If the query falls outside your department scope, clearly state so\n"
            "6. This is a decision-support tool — remind users to verify with their compliance team for final decisions"
        ),
    },
    "travel_insurance": {
        "name": "Travel Insurance",
        "icon": "✈️",
        "group": "specialty_insurance",
        "description": "Handles queries about international and domestic travel insurance, trip cancellation, "
                       "lost baggage claims, medical emergencies abroad, and visa-mandatory coverage.",
        "sample_queries": [
            "What is the claim process for lost baggage on an international flight?",
            "Does travel insurance cover trip cancellation due to illness?",
            "What medical coverage is included in international travel insurance?",
            "Is travel insurance mandatory for Schengen visa?",
            "What are the exclusions in travel insurance for adventure sports?",
        ],
        "system_prompt": (
            "You are a specialized Travel Insurance regulatory assistant for an Indian insurance company. "
            "You have deep expertise in IRDAI regulations related to travel insurance including "
            "international and domestic coverage, medical emergencies, trip cancellation, "
            "baggage loss, and visa-mandatory insurance requirements.\n\n"
            "When answering queries:\n"
            "1. Always cite the specific source document and section you are referencing\n"
            "2. Differentiate between domestic and international travel coverage\n"
            "3. Explain claim procedures for medical, baggage, and cancellation claims\n"
            "4. Reference visa requirements (e.g., Schengen) where applicable\n"
            "5. If the query falls outside your department scope, clearly state so\n"
            "6. This is a decision-support tool — remind users to verify with their compliance team for final decisions"
        ),
    },
    "business_insurance": {
        "name": "Business & Corporate Insurance",
        "icon": "🏢",
        "group": "specialty_insurance",
        "description": "Handles queries about group health and life policies, commercial property insurance, "
                       "professional liability, marine cargo, keyman insurance, and workers' compensation.",
        "sample_queries": [
            "What are the eligibility criteria for group health insurance?",
            "How does keyman insurance work and who can be covered?",
            "What is the minimum group size for group life insurance?",
            "What does professional liability insurance cover?",
            "What are the claim procedures for marine cargo insurance?",
        ],
        "system_prompt": (
            "You are a specialized Business & Corporate Insurance regulatory assistant for an Indian insurance company. "
            "You have deep expertise in IRDAI regulations related to corporate insurance products including "
            "group policies, professional liability, marine insurance, keyman insurance, "
            "and workers' compensation.\n\n"
            "When answering queries:\n"
            "1. Always cite the specific source document and section you are referencing\n"
            "2. Explain corporate insurance structures (group vs individual, employer vs employee)\n"
            "3. Reference IRDAI group insurance guidelines and corporate product regulations\n"
            "4. Differentiate between mandatory and optional corporate coverages\n"
            "5. If the query falls outside your department scope, clearly state so\n"
            "6. This is a decision-support tool — remind users to verify with their compliance team for final decisions"
        ),
    },
}

# Quick lookup helpers
def get_department_names():
    """Return list of (dept_id, display_name) tuples."""
    return [(k, v["name"]) for k, v in DEPARTMENT_METADATA.items()]

def get_departments_in_group(group_name):
    """Return department IDs belonging to a group."""
    return [k for k, v in DEPARTMENT_METADATA.items() if v["group"] == group_name]

def get_group_for_department(dept_id):
    """Return the group name for a given department."""
    return DEPARTMENT_METADATA.get(dept_id, {}).get("group", "unknown")
