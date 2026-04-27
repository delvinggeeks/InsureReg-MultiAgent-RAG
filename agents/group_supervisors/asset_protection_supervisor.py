"""
InsureReg - Asset Protection Group Supervisor
Manages Motor Insurance and Home & Property Insurance department agents.
"""

from agents.group_supervisors.base_supervisor import GroupSupervisor
from agents.department_agents.motor_insurance import motor_insurance_agent
from agents.department_agents.home_property_agent import home_property_agent


class AssetProtectionSupervisor(GroupSupervisor):
    """
    Supervises Motor Insurance and Home & Property Insurance agents.
    Routes queries about asset/property protection to the right department.
    """
    
    def __init__(self):
        super().__init__(
            group_name="Asset Protection",
            department_ids=["motor_insurance", "home_property_insurance"],
            agents={
                "motor_insurance": motor_insurance_agent,
                "home_property_insurance": home_property_agent,
            },
        )


# Singleton instance
asset_protection_supervisor = AssetProtectionSupervisor()
