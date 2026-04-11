"""
InsureReg - Home & Property Insurance Department Agent
Handles queries about home coverage, fire, flood, earthquake, burglary, and property valuation.
"""

from agents.department_agents.base_agent import BaseDepartmentAgent


class HomePropertyAgent(BaseDepartmentAgent):
    """Specialized agent for Home & Property Insurance regulatory queries."""
    
    def __init__(self):
        super().__init__("home_property_insurance")


# Singleton instance
home_property_agent = HomePropertyAgent()
