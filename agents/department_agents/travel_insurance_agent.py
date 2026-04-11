"""
InsureReg - Travel Insurance Department Agent
Handles queries about international/domestic travel, baggage, medical abroad, and visa insurance.
"""

from agents.department_agents.base_agent import BaseDepartmentAgent


class TravelInsuranceAgent(BaseDepartmentAgent):
    """Specialized agent for Travel Insurance regulatory queries."""
    
    def __init__(self):
        super().__init__("travel_insurance")


# Singleton instance
travel_insurance_agent = TravelInsuranceAgent()
