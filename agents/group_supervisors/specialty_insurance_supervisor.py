"""
InsureReg - Specialty Insurance Group Supervisor
Manages Travel Insurance and Business/Corporate Insurance department agents.
"""

from agents.group_supervisors.base_supervisor import GroupSupervisor
from agents.department_agents.travel_insurance_agent import travel_insurance_agent
from agents.department_agents.business_insurance_agent import business_insurance_agent


class SpecialtyInsuranceSupervisor(GroupSupervisor):
    """
    Supervises Travel Insurance and Business/Corporate Insurance agents.
    Routes queries about specialty/situational insurance to the right department.
    """
    
    def __init__(self):
        super().__init__(
            group_name="Specialty Insurance",
            department_ids=["travel_insurance", "business_insurance"],
            agents={
                "travel_insurance": travel_insurance_agent,
                "business_insurance": business_insurance_agent,
            },
        )


# Singleton instance
specialty_insurance_supervisor = SpecialtyInsuranceSupervisor()
