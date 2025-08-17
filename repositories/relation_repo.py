from typing import List
from utils.validators import validate_rel

class RelationRepository:
    def get_targets(self, session_or_tx, src_id: str, rel_type: str) -> List[str]:
        rel_type = validate_rel(rel_type)
        q = f"MATCH (a {{id: $src}})-[r:{rel_type}]->(b) RETURN b.id AS target_id"
        res = session_or_tx.run(q, src=src_id)
        return [r["target_id"] for r in res]

    def add(self, session_or_tx, src_id: str, rel_type: str, tgt_id: str):
        rel_type = validate_rel(rel_type)
        q = f"MATCH (a {{id: $src}}), (b {{id: $tgt}}) MERGE (a)-[r:{rel_type}]->(b)"
        session_or_tx.run(q, src=src_id, tgt=tgt_id)

    def delete(self, session_or_tx, src_id: str, rel_type: str, tgt_id: str):
        rel_type = validate_rel(rel_type)
        q = f"MATCH (a {{id: $src}})-[r:{rel_type}]->(b {{id: $tgt}}) DELETE r"
        session_or_tx.run(q, src=src_id, tgt=tgt_id)
