"""
InsureReg - Structured Logging Utility
Provides consistent logging across all agents and modules.
"""

import logging
import sys
from datetime import datetime


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a structured logger with consistent formatting.
    
    Args:
        name: Logger name (typically module name)
        level: Logging level
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(f"InsureReg.{name}")
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger


def log_agent_action(logger: logging.Logger, agent_name: str, action: str, details: str = ""):
    """Log a structured agent action for traceability."""
    logger.info(f"[{agent_name}] {action} | {details}")


def log_routing_decision(logger: logging.Logger, query: str, group: str, department: str, confidence: float):
    """Log a routing decision made by the orchestrator."""
    logger.info(
        f"ROUTING | Query: '{query[:80]}...' → Group: {group} → Dept: {department} | Confidence: {confidence:.2f}"
    )
