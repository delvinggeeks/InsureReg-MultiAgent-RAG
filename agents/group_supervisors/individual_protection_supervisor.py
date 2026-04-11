"""
InsureReg - Individual Protection Group Supervisor
Manages Life Insurance and Health Insurance department agents.
"""

from agents.group_supervisors.base_supervisor import GroupSupervisor
from agents.department_agents.life_insurance_agent import life_insurance_agent
from agents.department_agents.health_insurance_agent import health_insurance_agent


class IndividualProtectionSupervisor(GroupSupervisor):
    """
    Supervises Life Insurance and Health Insurance agents.
    Routes queries about personal/individual protection to the right department.
    """
    
    def __init__(self):
        super().__init__(
            group_name="Individual Protection",
            department_ids=["life_insurance", "health_insurance"],
            agents={
                "life_insurance": life_insurance_agent,
                "health_insurance": health_insurance_agent,
            },
        )


# Singleton instance
individual_protection_supervisor = IndividualProtectionSupervisor()
