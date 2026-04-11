"""
InsureReg - Orchestrator Agent
Top-level LangGraph agent that routes user queries to the appropriate group supervisor.
Implements the Orchestrator → Group Supervisor → Department Agent hierarchy.
"""

from typing import TypedDict, Annotated, Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from config.settings import LLM_MODEL, OPENAI_API_KEY
from config.department_config import DEPARTMENT_METADATA, get_group_for_department
from utils.logger import get_logger, log_routing_decision
from utils.audit import audit_trail

logger = get_logger("Orchestrator")


# ─── Routing Schema ────────────────────────────────────────
class RoutingDecision(BaseModel):
    """Structured output for the orchestrator's routing decision."""
    group: Literal["individual_protection", "asset_protection", "specialty_insurance"] = Field(
        description="The group to route the query to"
    )
    department: Literal[
        "life_insurance", "health_insurance",
        "motor_insurance", "home_property_insurance",
        "travel_insurance", "business_insurance"
    ] = Field(
        description="The specific department best suited to answer this query"
    )
    reasoning: str = Field(
        description="Brief explanation of why this routing was chosen"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score for this routing decision (0.0 to 1.0)"
    )


class Orchestrator:
    """
    Top-level orchestrator that analyzes user queries and routes them
    to the appropriate group supervisor → department agent.
    """
    
    def __init__(self):
        # Lazy initialization — agents are created when first query arrives
        self._supervisors = None
        
        # Build the routing LLM with structured output
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0,
            openai_api_key=OPENAI_API_KEY,
        )
        self.structured_llm = self.llm.with_structured_output(RoutingDecision)
        
        # Build department descriptions for routing context
        dept_info = []
        for dept_id, meta in DEPARTMENT_METADATA.items():
            dept_info.append(
                f"- {dept_id} (Group: {meta['group']}) | {meta['name']}: {meta['description']}"
            )
        self.dept_info_text = "\n".join(dept_info)
        
        # Routing prompt
        self.routing_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are the InsureReg Orchestrator — the top-level routing agent for an insurance "
             "regulatory AI assistant system.\n\n"
             "Your ONLY job is to analyze the user's query and determine which department "
             "should handle it.\n\n"
             "AVAILABLE DEPARTMENTS:\n"
             f"{self.dept_info_text}\n\n"
             "GROUP MAPPING:\n"
             "- individual_protection: life_insurance, health_insurance\n"
             "- asset_protection: motor_insurance, home_property_insurance\n"
             "- specialty_insurance: travel_insurance, business_insurance\n\n"
             "ROUTING RULES:\n"
             "1. Analyze the query carefully for keywords and context\n"
             "2. Route to the most specific department that matches\n"
             "3. If the query spans multiple departments, choose the PRIMARY one\n"
             "4. Provide brief reasoning for your routing decision\n\n"
             "CONFIDENCE CALIBRATION — be precise, not generous:\n"
             "  1.0  — Query uses exact domain terms (e.g. 'ULIP', 'NCB', 'TPA', 'Schengen visa')\n"
             "  0.85 — Query clearly belongs to one dept but uses general language\n"
             "  0.70 — Query could fit 2 departments; you picked the most likely one\n"
             "  0.50 — Query is ambiguous or spans multiple departments equally\n"
             "  0.30 — Query is vague or only loosely related to insurance\n"
             "  Never default to 0.9. Vary confidence based on actual query clarity."),
            ("human", "{query}"),
        ])
        
        self.routing_chain = self.routing_prompt | self.structured_llm
        
        logger.info("Orchestrator initialized with structured routing")
    
    @property
    def supervisors(self):
        """Lazy-load group supervisors to avoid circular imports."""
        if self._supervisors is None:
            from agents.group_supervisors.individual_protection_supervisor import individual_protection_supervisor
            from agents.group_supervisors.asset_protection_supervisor import asset_protection_supervisor
            from agents.group_supervisors.specialty_insurance_supervisor import specialty_insurance_supervisor
            
            self._supervisors = {
                "individual_protection": individual_protection_supervisor,
                "asset_protection": asset_protection_supervisor,
                "specialty_insurance": specialty_insurance_supervisor,
            }
            logger.info("All group supervisors loaded")
        return self._supervisors
    
    def route(self, query: str) -> RoutingDecision:
        """
        Analyze the query and determine routing.
        
        Returns:
            RoutingDecision with group, department, reasoning, and confidence
        """
        try:
            decision = self.routing_chain.invoke({"query": query})
            
            # Validate group-department consistency
            expected_group = get_group_for_department(decision.department)
            if decision.group != expected_group:
                logger.warning(
                    f"Group mismatch: LLM said {decision.group} but {decision.department} "
                    f"belongs to {expected_group}. Correcting."
                )
                decision.group = expected_group
            
            log_routing_decision(
                logger, query, decision.group, decision.department, decision.confidence
            )
            return decision
            
        except Exception as e:
            logger.error(f"Routing error: {e}. Defaulting to life_insurance.")
            return RoutingDecision(
                group="individual_protection",
                department="life_insurance",
                reasoning=f"Default routing due to error: {str(e)}",
                confidence=0.1,
            )
    
    def process_query(self, query: str) -> dict:
        """
        Full pipeline: Route → Group Supervisor → Department Agent → Response.
        
        Args:
            query: User's question
        
        Returns:
            Dict with complete response, sources, routing info, and audit trail
        """
        logger.info(f"Processing query: {query[:100]}...")
        
        # Step 1: Route the query
        routing = self.route(query)
        
        # Step 2: Get the appropriate supervisor
        supervisor = self.supervisors[routing.group]
        
        # Step 3: Process through supervisor → department agent
        result = supervisor.process_query(query, target_department=routing.department)
        
        # Step 4: Add orchestrator metadata
        result["routing"] = {
            "group": routing.group,
            "department": routing.department,
            "reasoning": routing.reasoning,
            "confidence": routing.confidence,
        }
        
        # Step 5: Log to audit trail
        try:
            audit_trail.log_query(
                query=query,
                group=routing.group,
                department=routing.department,
                confidence=routing.confidence,
                response=result.get("response", ""),
                sources=result.get("sources", []),
                routing_reasoning=routing.reasoning,
            )
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")
        
        logger.info(
            f"Query processed: {routing.department} "
            f"(confidence: {routing.confidence:.2f})"
        )
        
        return result


# Singleton instance
orchestrator = Orchestrator()
