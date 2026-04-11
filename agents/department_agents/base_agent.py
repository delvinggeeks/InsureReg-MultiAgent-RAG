"""
InsureReg - Base Department Agent
Template class that all 6 department agents inherit from.
Each department agent implements a RAG-powered query pipeline.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config.settings import LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY
from config.department_config import DEPARTMENT_METADATA
from rag.retriever_factory import retriever_factory
from utils.logger import get_logger

logger = get_logger("DepartmentAgent")


class BaseDepartmentAgent:
    """
    Base class for all department-specific agents.
    Implements the RAG pipeline: Retrieve → Augment → Generate.
    """
    
    def __init__(self, department_id: str):
        self.department_id = department_id
        self.metadata = DEPARTMENT_METADATA[department_id]
        self.name = self.metadata["name"]
        self.system_prompt = self.metadata["system_prompt"]
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            openai_api_key=OPENAI_API_KEY,
        )
        
        # Build the RAG prompt — use .replace() not .format() so {context}/{query}
        # LangChain placeholders are preserved untouched
        rag_instructions = (
            "\n\nCONTEXT FROM RETRIEVED DOCUMENTS:\n"
            "─────────────────────────────────\n"
            "{context}\n"
            "─────────────────────────────────\n\n"
            "STRICT RESPONSE RULES — follow these exactly:\n"
            "1. Answer ONLY using the context provided above. Do NOT use any external knowledge.\n"
            "2. If the context is empty or says 'No relevant documents found':\n"
            "   → Say: 'I don't have information on this topic in the DEPT_NAME knowledge base. "
            "Please upload relevant documents or consult the appropriate regulatory authority.'\n"
            "3. If the query is outside the scope of DEPT_NAME:\n"
            "   → Say: 'This query appears to be outside the scope of DEPT_NAME. "
            "Please direct it to the appropriate department.'\n"
            "4. If partial information is available, answer what you can and state what is missing.\n"
            "5. Always cite the source document name (e.g. 'According to [filename]...').\n"
            "6. Use clear headers and bullet points where appropriate.\n"
            "7. End every response with:\n\n"
            "---\n"
            "*⚠️ This response is for informational purposes only and does not constitute "
            "regulatory or compliance advice.*"
        ).replace("DEPT_NAME", self.name)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + rag_instructions),
            ("human", "{query}"),
        ])

        
        # Build the chain
        self.chain = self.prompt | self.llm | StrOutputParser()
        
        logger.info(f"Initialized {self.name} Agent (department: {self.department_id})")
    
    def retrieve_context(self, query: str) -> tuple:
        """
        Retrieve relevant documents from the department's vector store.
        
        Returns:
            Tuple of (formatted_context_string, list_of_source_dicts)
        """
        documents = retriever_factory.retrieve_documents(self.department_id, query)
        
        if not documents:
            return "No relevant documents found in the knowledge base.", []
        
        # Format context for the prompt
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.get("source", "Unknown")
            page = doc.get("page_number", "")
            page_info = f" (Page {page})" if page else ""
            context_parts.append(
                f"[Source {i}: {source}{page_info}] (Relevance: {doc['score']:.1%})\n"
                f"{doc['content']}\n"
            )
        
        formatted_context = "\n".join(context_parts)
        return formatted_context, documents
    
    def process_query(self, query: str) -> dict:
        """
        Full RAG pipeline: Retrieve context → Generate response.
        
        Args:
            query: User's question
        
        Returns:
            Dict with 'response', 'sources', 'department', and 'agent_name'
        """
        logger.info(f"[{self.name}] Processing query: {query[:80]}...")
        
        # Step 1: Retrieve
        context, sources = self.retrieve_context(query)
        
        # Step 2: Generate
        try:
            response = self.chain.invoke({
                "context": context,
                "query": query,
            })
        except Exception as e:
            logger.error(f"[{self.name}] Error generating response: {e}")
            response = (
                f"I apologize, but I encountered an error while processing your query. "
                f"Please try again or contact support. Error: {str(e)}"
            )
        
        result = {
            "response": response,
            "sources": sources,
            "department": self.department_id,
            "agent_name": self.name,
        }
        
        logger.info(f"[{self.name}] Response generated ({len(response)} chars, {len(sources)} sources)")
        return result
