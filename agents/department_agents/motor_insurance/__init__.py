"""Motor Insurance department package.

Re-exports the public API so callers can use either:
    from agents.department_agents.motor_insurance import motor_insurance_agent
    from agents.department_agents.motor_insurance.agent import MotorInsuranceAgent
"""
from agents.department_agents.motor_insurance.agent import (
    MotorInsuranceAgent,
    motor_insurance_agent,
)

__all__ = ["MotorInsuranceAgent", "motor_insurance_agent"]
