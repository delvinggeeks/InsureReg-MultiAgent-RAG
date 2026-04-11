"""
InsureReg - Group Supervisor Base
Base class for group supervisors that route queries between their department agents.
Each group supervisor manages 2 department agents using LLM-based routing.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Literal

from config.settings import LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY
from config.department_config import DEPARTMENT_METADATA
from utils.logger import get_logger

logger = get_logger("GroupSupervisor")


class GroupSupervisor:
    """
    Base group supervisor that routes queries between 2 department agents.
    Uses LLM structured output for deterministic routing.
    """
    
    def __init__(self, group_name: str, department_ids: list, agents: dict):
        """
        Args:
            group_name: Name of this supervision group
            department_ids: List of 2 department IDs managed by this supervisor
            agents: Dict mapping department_id → agent instance
        """
        self.group_name = group_name
        self.department_ids = department_ids
        self.agents = agents
        
        # Build department descriptions for the routing prompt
        dept_descriptions = []
        for dept_id in department_ids:
            meta = DEPARTMENT_METADATA[dept_id]
            dept_descriptions.append(
                f"- **{dept_id}** ({meta['name']}): {meta['description']}"
            )
        self.dept_descriptions_text = "\n".join(dept_descriptions)
        
        # Initialize the routing LLM
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,  # Zero temperature for deterministic routing
            openai_api_key=OPENAI_API_KEY,
        )
        
        logger.info(f"Initialized {group_name} supervisor managing: {department_ids}")
    
    def route_query(self, query: str) -> str:
        """
        Route a query to the appropriate department within this group.
        
        Returns:
            department_id string
        """
        routing_prompt = ChatPromptTemplate.from_messages([
            ("system", 
             f"You are a routing supervisor for the {self.group_name} group.\n"
             f"Your job is to determine which department should handle the user's query.\n\n"
             f"Available departments:\n{self.dept_descriptions_text}\n\n"
             f"Respond with ONLY the department ID (one of: {', '.join(self.department_ids)}).\n"
             f"Do not include any other text or explanation."),
            ("human", "{query}"),
        ])
        
        chain = routing_prompt | self.llm
        
        try:
            result = chain.invoke({"query": query})
            dept_id = result.content.strip().lower().replace(" ", "_")
            
            # Validate the routing result
            if dept_id in self.department_ids:
                logger.info(f"[{self.group_name}] Routed to: {dept_id}")
                return dept_id
            else:
                # Default to first department if routing fails
                logger.warning(
                    f"[{self.group_name}] Invalid routing result: '{dept_id}', "
                    f"defaulting to {self.department_ids[0]}"
                )
                return self.department_ids[0]
        except Exception as e:
            logger.error(f"[{self.group_name}] Routing error: {e}")
            return self.department_ids[0]
    
    def process_query(self, query: str, target_department: str = None) -> dict:
        """
        Process a query by routing to the correct department agent.
        
        Args:
            query: User's question
            target_department: If specified, skip routing and go directly to this dept
        
        Returns:
            Dict with response, sources, department, and routing info
        """
        # Route if no target specified
        if target_department and target_department in self.department_ids:
            dept_id = target_department
        else:
            dept_id = self.route_query(query)
        
        # Process with the selected department agent
        agent = self.agents[dept_id]
        result = agent.process_query(query)
        
        # Add group routing info
        result["group"] = self.group_name
        result["routed_by"] = f"{self.group_name}_supervisor"
        
        return result
