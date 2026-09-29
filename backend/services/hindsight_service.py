"""
CompetitorIQ Hindsight Memory Service Layer
Official Integration with Hindsight AI Agent Memory Platform (hindsight-client).

Key Responsibilities:
1. RETAIN: Encodes structured competitor telemetry (pricing, hiring, product launches)
   into Hindsight's semantic memory graph.
2. RECALL: Retrieves relevant historical memories from Hindsight to counter recency
   bias during strategic intelligence queries.
3. ISOLATION: Enforces strict competitor memory segregation by allocating dedicated
   Hindsight memory banks per competitor (e.g., competitor-nova-ai, competitor-cloudmind).
"""

import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from hindsight_client import Hindsight
import hindsight_client_api.exceptions as hindsight_exceptions
from config import Config

logger = logging.getLogger("competitoriq.hindsight")


class HindsightServiceError(Exception):
    """Base exception for Hindsight memory operations."""
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class HindsightConfigError(HindsightServiceError):
    """Raised when Hindsight configuration is missing or malformed."""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class HindsightConnectionError(HindsightServiceError):
    """Raised when the Hindsight server/cloud endpoint cannot be reached."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message, status_code=502, details=details)


class HindsightService:
    """
    Production service integrating with Hindsight's official Python SDK.
    Provides isolated competitor memory banks, event retention, and semantic recall.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.base_url = (base_url or Config.HINDSIGHT_BASE_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else Config.HINDSIGHT_API_KEY
        self._local = threading.local()
        self._known_banks: set = set()

    @property
    def client(self) -> Hindsight:
        """
        Lazily initialize and return a thread-local official Hindsight client instance.
        Guarantees thread-safe operation across concurrent Flask worker threads.
        """
        client = getattr(self._local, "client", None)
        if client is None:
            if not self.base_url:
                raise HindsightConfigError("HINDSIGHT_BASE_URL is not configured in .env.")

            # Hindsight client accepts base_url and optional api_key
            api_key_val = self.api_key.strip() if self.api_key else None
            try:
                client = Hindsight(
                    base_url=self.base_url,
                    api_key=api_key_val,
                    timeout=30.0,
                    user_agent="CompetitorIQ-Agent/1.0"
                )
                self._local.client = client
                logger.info(f"Initialized thread-local Hindsight client for thread {threading.get_ident()} connected to {self.base_url}")
            except Exception as e:
                logger.error(f"Failed to instantiate Hindsight client: {e}")
                raise HindsightConfigError(f"Could not initialize Hindsight client: {str(e)}")

        return client

    def is_configured(self) -> bool:
        """Check whether Hindsight endpoint and credentials are configured."""
        return bool(self.base_url and self.api_key and self.api_key.strip())

    def get_bank_id_for_competitor(self, competitor: str) -> str:
        """
        Derive an isolated Hindsight bank_id for a given competitor.
        Guarantees that NovaAI, CloudMind, TechFlow, etc. each possess
        their own separate, unmixed memory partition.

        Examples:
        - 'NovaAI' -> 'competitor-nova-ai'
        - 'CloudMind' -> 'competitor-cloud-mind'
        - 'TechFlow' -> 'competitor-tech-flow'
        """
        if not competitor or not competitor.strip():
            raise ValueError("Competitor name cannot be empty.")

        # Normalize slug
        name = competitor.strip()
        # Insert hyphen between lowercase and uppercase if camelCase (e.g. NovaAI -> Nova-AI)
        s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", s1).lower().strip("-")

        bank_id = f"competitor-{slug}"
        return bank_id

    def ensure_bank_exists(self, competitor: str, bank_id: Optional[str] = None) -> str:
        """
        Ensure the competitor's isolated memory bank exists in Hindsight Cloud.
        Caches known banks in-memory to minimize unnecessary network round trips.
        """
        bid = bank_id or self.get_bank_id_for_competitor(competitor)
        if bid in self._known_banks:
            return bid

        try:
            self.client.create_bank(
                bank_id=bid,
                name=f"{competitor} Memory Bank",
                background=f"Persistent competitive intelligence memory for competitor {competitor}."
            )
            self._known_banks.add(bid)
            logger.info(f"Verified/created Hindsight memory bank '{bid}' for competitor {competitor}")
        except Exception as e:
            err_msg = str(e).lower()
            if "already exists" in err_msg or "conflict" in err_msg or "409" in err_msg:
                self._known_banks.add(bid)
            else:
                logger.warning(f"Note during bank verification for '{bid}': {e}")
        return bid

    def get_status(self) -> Dict[str, Any]:
        """
        Health and configuration status of the Hindsight service.
        """
        configured = self.is_configured()
        return {
            "service": "Hindsight Memory System",
            "configured": configured,
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key and self.api_key.strip()),
            "status": "ready" if configured else "credentials_pending"
        }

    def check_connection(self) -> Dict[str, Any]:
        """
        Actively verify live connectivity and authentication with Hindsight Cloud.
        Returns diagnostic dictionary: {configured: bool, connected: bool, memory_system: 'hindsight', ...}
        """
        if not self.is_configured():
            return {
                "configured": False,
                "connected": False,
                "memory_system": "hindsight",
                "error": "HINDSIGHT_API_KEY or HINDSIGHT_BASE_URL is missing in backend/.env"
            }

        try:
            # Actively test connectivity by ensuring bank exists
            bank_id = self.ensure_bank_exists("NovaAI")
            return {
                "configured": True,
                "connected": True,
                "memory_system": "hindsight",
                "base_url": self.base_url,
                "verified_bank": bank_id,
                "status": "operational"
            }
        except hindsight_exceptions.ApiException as api_err:
            logger.error(f"Hindsight API check failed: {api_err}")
            return {
                "configured": True,
                "connected": False,
                "memory_system": "hindsight",
                "base_url": self.base_url,
                "status_code": api_err.status,
                "error": f"Hindsight API error ({api_err.status}): {api_err.reason}"
            }
        except Exception as e:
            logger.error(f"Hindsight connection check failed: {e}")
            return {
                "configured": True,
                "connected": False,
                "memory_system": "hindsight",
                "base_url": self.base_url,
                "error": str(e)
            }

    def retain_competitor_event(
        self,
        competitor: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Retain a competitor event into its isolated Hindsight memory bank.

        Args:
            competitor: Name or identifier of competitor (e.g. 'NovaAI')
            event_data: Dict with title, event_type, event_date, description, source, etc.

        Returns:
            Dict containing bank_id, operation_id/memory_id, items_count, and retention verification.
        """
        if not competitor or not competitor.strip():
            raise ValueError("Competitor name is required.")

        bank_id = self.get_bank_id_for_competitor(competitor)
        self.ensure_bank_exists(competitor, bank_id)

        title = event_data.get("title", "Untitled Event").strip()
        description = event_data.get("description", "").strip()
        event_type = event_data.get("event_type") or event_data.get("category", "General")
        event_date = event_data.get("event_date", datetime.utcnow().strftime("%Y-%m-%d"))
        source = event_data.get("source") or event_data.get("source_name", "Unknown Source")

        # Parse date to datetime for Hindsight's temporal engine if valid
        parsed_dt = None
        if event_date:
            try:
                date_str = str(event_date).split("T")[0]
                parsed_dt = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                pass

        # Format rich contextual memory text for Hindsight
        memory_content = (
            f"Competitor Event: {title}\n"
            f"Competitor: {competitor}\n"
            f"Date: {event_date}\n"
            f"Category: {event_type}\n"
            f"Details: {description}\n"
            f"Source: {source}"
        )

        metadata = {
            "competitor": str(competitor),
            "category": str(event_type),
            "event_date": str(event_date),
            "source": str(source),
            "title": str(title)
        }

        tags = [
            f"competitor:{competitor.lower().replace(' ', '-')}",
            f"type:{event_type.lower().replace(' ', '-')}"
        ]

        logger.info(f"Retaining event into Hindsight bank '{bank_id}': {title}")

        try:
            # Call official Hindsight client retain method
            response = self.client.retain(
                bank_id=bank_id,
                content=memory_content,
                metadata=metadata,
                tags=tags,
                timestamp=parsed_dt
            )

            # Response is official RetainResponse object
            op_ids = getattr(response, "operation_ids", None)
            operation_id = getattr(response, "operation_id", None) or (op_ids[0] if op_ids else None)

            return {
                "retained": True,
                "bank_id": bank_id,
                "operation_id": operation_id,
                "items_count": getattr(response, "items_count", 1),
                "success": getattr(response, "success", True),
                "content_preview": memory_content[:120] + "..." if len(memory_content) > 120 else memory_content,
                "timestamp": datetime.utcnow().isoformat()
            }

        except hindsight_exceptions.ApiException as api_err:
            logger.error(f"Hindsight API error retaining event: {api_err}")
            raise HindsightServiceError(
                message=f"Hindsight API error ({api_err.status}): {api_err.reason}",
                status_code=502,
                details=str(api_err.body) if hasattr(api_err, "body") else None
            )
        except Exception as e:
            logger.error(f"Failed to connect to Hindsight service: {e}")
            raise HindsightConnectionError(
                message=f"Could not connect to Hindsight service at {self.base_url}: {str(e)}",
                details=str(e)
            )

    def recall_competitor_memory(
        self,
        competitor: str,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Recall relevant historical memories from a specific competitor's isolated bank.

        Args:
            competitor: Name or identifier of competitor (e.g. 'NovaAI')
            query: Natural language search query
            top_k: Max memory units to retrieve

        Returns:
            Dict containing competitor, bank_id, query, and unpacked memories with scores/metadata.
        """
        if not competitor or not competitor.strip():
            raise ValueError("Competitor name is required.")
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")

        bank_id = self.get_bank_id_for_competitor(competitor)
        self.ensure_bank_exists(competitor, bank_id)
        logger.info(f"Recalling memories from Hindsight bank '{bank_id}' for query: '{query}'")

        try:
            # Call official Hindsight client recall method
            response = self.client.recall(
                bank_id=bank_id,
                query=query.strip(),
                max_tokens=4096
            )

            # Unpack RecallResult objects preserving metadata, dates, evidence, and relevance scores
            extracted_memories = []
            results = getattr(response, "results", []) or []

            for item in results:
                # Extract score metrics cleanly
                scores_obj = getattr(item, "scores", None)
                scores_dict = {}
                if scores_obj:
                    if hasattr(scores_obj, "to_dict"):
                        scores_dict = scores_obj.to_dict()
                    else:
                        scores_dict = {
                            "final": getattr(scores_obj, "final", None),
                            "reranker": getattr(scores_obj, "reranker", None),
                            "semantic": getattr(scores_obj, "semantic", None),
                            "keyword": getattr(scores_obj, "keyword", None)
                        }

                mem_dict = {
                    "id": getattr(item, "id", None),
                    "text": getattr(item, "text", ""),
                    "type": getattr(item, "type", "memory"),
                    "occurred_start": getattr(item, "occurred_start", None),
                    "occurred_end": getattr(item, "occurred_end", None),
                    "context": getattr(item, "context", None),
                    "metadata": getattr(item, "metadata", {}) or {},
                    "tags": getattr(item, "tags", []) or [],
                    "scores": scores_dict,
                    "entities": getattr(item, "entities", []) or []
                }
                extracted_memories.append(mem_dict)

            # Limit to top_k if requested
            if top_k and len(extracted_memories) > top_k:
                extracted_memories = extracted_memories[:top_k]

            return {
                "competitor": competitor,
                "bank_id": bank_id,
                "query": query,
                "memories": extracted_memories,
                "count": len(extracted_memories),
                "memory_source": "hindsight"
            }

        except hindsight_exceptions.NotFoundException:
            # Bank is newly initialized or empty
            logger.info(f"Bank '{bank_id}' contains no indexed memories yet.")
            return {
                "competitor": competitor,
                "bank_id": bank_id,
                "query": query,
                "memories": [],
                "count": 0,
                "memory_source": "hindsight"
            }
        except hindsight_exceptions.ApiException as api_err:
            logger.error(f"Hindsight API error recalling memories: {api_err}")
            raise HindsightServiceError(
                message=f"Hindsight API error ({api_err.status}): {api_err.reason}",
                status_code=502,
                details=str(api_err.body) if hasattr(api_err, "body") else None
            )
        except Exception as e:
            logger.error(f"Failed to connect to Hindsight service: {e}")
            raise HindsightConnectionError(
                message=f"Could not connect to Hindsight service at {self.base_url}: {str(e)}",
                details=str(e)
            )

    def get_competitor_memory_context(
        self,
        competitor: str,
        focus: str = "strategic moves, pricing shifts, product launches, and executive hires"
    ) -> Dict[str, Any]:
        """
        Synthesize broad historical memory context for a competitor
        to feed downstream analysis.
        """
        query = f"Overview of {competitor} {focus}"
        return self.recall_competitor_memory(competitor=competitor, query=query, top_k=10)
