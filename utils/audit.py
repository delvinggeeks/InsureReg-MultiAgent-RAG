"""
InsureReg - Audit Trail System
Records all query routing decisions and responses for regulatory traceability.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import AUDIT_LOG_DIR


class AuditTrail:
    """Maintains an audit log of all queries, routing decisions, and responses."""
    
    def __init__(self):
        self.log_file = AUDIT_LOG_DIR / "audit_log.json"
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Create the audit log file if it doesn't exist."""
        if not self.log_file.exists():
            with open(self.log_file, "w") as f:
                json.dump([], f)
    
    def _load_logs(self) -> list:
        """Load existing audit logs."""
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_logs(self, logs: list):
        """Save audit logs to file."""
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2, default=str)
    
    def log_query(
        self,
        query: str,
        group: str,
        department: str,
        confidence: float,
        response: str,
        sources: list,
        routing_reasoning: str = "",
    ):
        """
        Log a complete query-response cycle.
        
        Args:
            query: The user's original query
            group: The group the query was routed to
            department: The specific department agent
            confidence: Routing confidence score
            response: The generated response
            sources: List of source document references
            routing_reasoning: Orchestrator's reasoning for routing decision
        """
        logs = self._load_logs()
        
        entry = {
            "id": len(logs) + 1,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "routing": {
                "group": group,
                "department": department,
                "confidence": confidence,
                "reasoning": routing_reasoning,
            },
            "response_preview": response[:200] + "..." if len(response) > 200 else response,
            "sources_count": len(sources),
            "sources": [
                {
                    "document": s.get("source", "Unknown"),
                    "relevance_score": s.get("score", 0),
                }
                for s in sources
            ],
        }
        
        logs.append(entry)
        self._save_logs(logs)
        
        return entry
    
    def get_recent_logs(self, n: int = 50) -> list:
        """Get the most recent n audit log entries."""
        logs = self._load_logs()
        return logs[-n:][::-1]  # Most recent first
    
    def get_department_stats(self) -> dict:
        """Get query count statistics per department."""
        logs = self._load_logs()
        stats = {}
        for log in logs:
            dept = log.get("routing", {}).get("department", "unknown")
            stats[dept] = stats.get(dept, 0) + 1
        return stats
    
    def clear_logs(self):
        """Clear all audit logs."""
        self._save_logs([])


# Singleton instance
audit_trail = AuditTrail()
