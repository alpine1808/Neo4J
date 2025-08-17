# services/search_service.py
from typing import List, Optional
from .base_service import BaseService
from repositories.search_repo import SearchRepository

class SearchService(BaseService):
    def __init__(self, client, logger, dry_run: bool):
        super().__init__(client, logger, dry_run)
        self.repo = SearchRepository()

    # Index management
    def ensure_fulltext_index(self, index_name: str, labels: List[str], properties: List[str]):
        if self.dry_run:
            self.log.log(f"[DRYRUN] Would create FULLTEXT index {index_name} on {labels}/{properties}")
            return
        with self.client.session() as session:
            self.repo.ensure_fulltext_index(session, index_name, labels, properties)
        self.log.log(f"[INDEX] Ensure FULLTEXT {index_name} on {labels}/{properties}")

    def ensure_btree_index(self, label: str, prop: str):
        if self.dry_run:
            self.log.log(f"[DRYRUN] Would create BTREE index :{label}({prop})")
            return
        with self.client.session() as session:
            self.repo.ensure_btree_index(session, label, prop)
        self.log.log(f"[INDEX] Ensure BTREE :{label}({prop})")

    # Queries
    def fulltext(self, index_name: str, query: str, limit: int = 25, min_score: float = 0.0):
        with self.client.session() as session:
            return self.repo.query_fulltext(session, index_name, query, limit, min_score)

    def exact(self, label: str, prop: str, value, limit: int = 100):
        with self.client.session() as session:
            return self.repo.find_by_exact(session, label, prop, value, limit)

    def neighbors(self, node_id: str, rel_type: Optional[str] = None, direction: str = "out", limit: int = 100):
        with self.client.session() as session:
            return self.repo.neighbors(session, node_id, rel_type, direction, limit)
