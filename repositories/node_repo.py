from typing import Dict
from utils.validators import validate_label

class NodeRepository:
    def add_or_update(self, session_or_tx, node_id: str, label: str, properties: Dict):
        label = validate_label(label)
        q = f"MERGE (n:{label} {{id: $id}}) SET n += $props"
        session_or_tx.run(q, id=node_id, props=properties or {})

    def ensure_exists_by_id(self, session, node_id: str):
        session.run("MERGE (n {id: $id})", id=node_id)
