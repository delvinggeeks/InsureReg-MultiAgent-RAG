"""
InsureReg - Health Insurance Department Agent
Handles queries about mediclaim, critical illness, cashless claims, TPA, and portability.
"""

from agents.department_agents.base_agent import BaseDepartmentAgent


class HealthInsuranceAgent(BaseDepartmentAgent):
    """Specialized agent for Health Insurance regulatory queries."""
    
    def __init__(self):
        super().__init__("health_insurance")


# Singleton instance
health_insurance_agent = HealthInsuranceAgent()
