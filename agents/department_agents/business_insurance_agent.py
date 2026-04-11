"""
InsureReg - Business & Corporate Insurance Department Agent
Handles queries about group policies, professional liability, marine cargo, and keyman insurance.
"""

from agents.department_agents.base_agent import BaseDepartmentAgent


class BusinessInsuranceAgent(BaseDepartmentAgent):
    """Specialized agent for Business & Corporate Insurance regulatory queries."""
    
    def __init__(self):
        super().__init__("business_insurance")


# Singleton instance
business_insurance_agent = BusinessInsuranceAgent()
