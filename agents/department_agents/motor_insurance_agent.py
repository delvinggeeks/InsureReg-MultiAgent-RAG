"""
InsureReg - Motor Insurance Department Agent
Handles queries about car/bike insurance, third-party, comprehensive, NCB, and claims.
"""

from agents.department_agents.base_agent import BaseDepartmentAgent


class MotorInsuranceAgent(BaseDepartmentAgent):
    """Specialized agent for Motor Insurance regulatory queries."""
    
    def __init__(self):
        super().__init__("motor_insurance")


# Singleton instance
motor_insurance_agent = MotorInsuranceAgent()
