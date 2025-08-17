# repositories/search_repo.py
from typing import List, Dict, Any, Optional
import re
from utils.validators import validate_label, validate_prop, validate_rel

class SearchRepository:
    def ensure_fulltext_index(self, session, index_name: str, labels: List[str], properties: List[str]):
        if not index_name or not re.match(r"^[A-Za-z0-9_]+$", index_name):
            raise ValueError("Invalid index_name")
        labels = [validate_label(l) for l in labels if l]
        properties = [validate_prop(p) for p in properties if p]
        if not labels or not properties:
            raise ValueError("Labels and properties must be non-empty")

        label_union = "|".join(labels)
        props = ", ".join(f"n.{p}" for p in properties)
        cypher = f"CREATE FULLTEXT INDEX {index_name} IF NOT EXISTS FOR (n:{label_union}) ON EACH [{props}]"
        session.run(cypher)

    def query_fulltext(self, session, index_name: str, query: str, limit: int, min_score: float) -> List[Dict[str, Any]]:
        cypher = """
        CALL db.index.fulltext.queryNodes($index_name, $q) YIELD node, score
        WITH node, score WHERE score >= $min_score
        RETURN node.id AS id, labels(node) AS labels, score, node AS props
        LIMIT $limit
        """
        res = session.run(cypher, index_name=index_name, q=query, min_score=float(min_score), limit=int(limit))
        return [{"id": r["id"], "labels": r["labels"], "score": r["score"], "props": dict(r["props"])} for r in res]

    def ensure_btree_index(self, session, label: str, prop: str):
        label = validate_label(label); prop = validate_prop(prop)
        session.run(f"CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.{prop})")

    def find_by_exact(self, session, label: str, prop: str, value, limit: int) -> List[Dict[str, Any]]:
        label = validate_label(label); prop = validate_prop(prop)
        cypher = f"MATCH (n:{label}) WHERE n.{prop} = $val RETURN n.id AS id, labels(n) AS labels, n AS props LIMIT $limit"
        res = session.run(cypher, val=value, limit=int(limit))
        return [{"id": r["id"], "labels": r["labels"], "props": dict(r["props"])} for r in res]

    def neighbors(self, session, node_id: str, rel_type: Optional[str], direction: str, limit: int):
        rseg = f":{validate_rel(rel_type)}" if rel_type else ""
        if direction == "out":
            pattern = f"-[r{rseg}]->(m)"
        elif direction == "in":
            pattern = f"<-[r{rseg}]-(m)"
        else:
            pattern = f"-[r{rseg}]-(m)"
        cypher = f"""
        MATCH (n {{id: $id}}){pattern}
        RETURN DISTINCT m.id AS id, labels(m) AS labels, type(r) AS rel_type, m AS props
        LIMIT $limit
        """
        res = session.run(cypher, id=node_id, limit=int(limit))
        return [{"id": r["id"], "labels": r["labels"], "rel_type": r["rel_type"], "props": dict(r["props"])} for r in res]
