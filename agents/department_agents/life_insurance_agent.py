"""
InsureReg - Life Insurance Department Agent
Handles queries about term life, endowment, ULIPs, pension, and annuity plans.
"""

from agents.department_agents.base_agent import BaseDepartmentAgent


class LifeInsuranceAgent(BaseDepartmentAgent):
    """Specialized agent for Life Insurance regulatory queries."""
    
    def __init__(self):
        super().__init__("life_insurance")


# Singleton instance
life_insurance_agent = LifeInsuranceAgent()
