from typing import Dict
from .base_service import BaseService
from repositories.node_repo import NodeRepository
from utils.validators import validate_label

class NodeService(BaseService):
    def __init__(self, client, logger, dry_run: bool):
        super().__init__(client, logger, dry_run)
        self.repo = NodeRepository()

    def upsert(self, node_id: str, label: str, props: Dict, tx=None):
        label = validate_label(label)
        if self.dry_run:
            self.log.log(f"[DRYRUN][NODE] would upsert {node_id} :{label}")
            return
        if tx is not None:
            self.repo.add_or_update(tx, node_id, label, props or {})
        else:
            with self.client.session() as session:
                self.repo.add_or_update(session, node_id, label, props or {})
        self.log.log(f"[NODE] Upserted node {node_id} :{label} props={list((props or {}).keys())}")

    def ensure_exists(self, node_id: str):
        with self.client.session() as session:
            self.repo.ensure_exists_by_id(session, node_id)
