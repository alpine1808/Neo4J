import json, chardet
from typing import List
from .base_service import BaseService
from .node_service import NodeService
from .relation_service import RelationService
from .constraint_service import ConstraintService

class ImportService(BaseService):
    def __init__(self, client, logger, dry_run: bool, batch_size: int, multi_object: bool):
        super().__init__(client, logger, dry_run)
        self.batch_size = max(1, int(batch_size))
        self.nodes = NodeService(client, logger, dry_run)
        self.rels = RelationService(client, logger, dry_run, multi_object)
        self.cons = ConstraintService(client, logger, dry_run)

    def load_json(self, file_path: str) -> dict:
        with open(file_path, "rb") as f: raw = f.read()
        enc = chardet.detect(raw).get("encoding") or "utf-8"
        self.log.log(f"[INFO] Detected encoding for {file_path}: {enc}")
        try:
            with open(file_path, "r", encoding=enc, errors="replace") as f:
                return json.load(f)
        except Exception as e:
            self.log.log(f"[WARN] JSON load failed with {enc}: {e}; retrying with utf-8-sig")
            with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
                return json.load(f)

    def process(self, data: dict):
        kg = data.get("knowledge_graph")
        if not kg: raise ValueError("No 'knowledge_graph' key in data")
        nodes = kg.get("nodes", []); edges = kg.get("edges", [])

        labels: List[str] = []
        schema = data.get("ontology_schema", {})
        for ent in schema.get("entity_labels", []) if schema else []:
            if ent.get("label"): labels.append(ent["label"])
        for n in nodes:
            if n.get("label"): labels.append(n["label"])
        self.cons.ensure_unique_id(list({l for l in labels if l}))

        self.log.log(f"[INFO] Starting node upsert: total_nodes={len(nodes)} batch_size={self.batch_size}")
        if self.dry_run:
            for n in nodes:
                self.log.log(f"[DRYRUN][NODE] would upsert {n['id']} :{n['label']}")
        else:
            count = 0
            with self.client.session() as session:
                tx = session.begin_transaction()
                try:
                    for n in nodes:
                        self.nodes.upsert(n["id"], n["label"], n.get("properties", {}), tx=tx)
                        count += 1
                        if count % self.batch_size == 0:
                            tx.commit(); self.log.log(f"[BATCH] committed {count} nodes")
                            tx = session.begin_transaction()
                    tx.commit(); self.log.log(f"[BATCH] final commit nodes total={count}")
                except Exception as e:
                    try: tx.rollback()
                    except Exception: pass
                    self.log.log(f"[ERROR] during node batching: {e}")

        self.log.log(f"[INFO] Starting edges processing: total_edges={len(edges)} batch_size={self.batch_size}")
        if self.dry_run:
            for e in edges:
                self.log.log(f"[DRYRUN][EDGE] would process ({e['source']}, {e['type']}, {e['target']})")
        else:
            count = 0
            with self.client.session() as session:
                tx = session.begin_transaction()
                try:
                    for e in edges:
                        try:
                            # validate ngay trong RelationService qua validators
                            pass
                        except Exception as ex:
                            self.log.log(f"[SKIP EDGE] invalid rel type {e.get('type')}: {ex}")
                            continue
                        self.rels.update_with_policy(e["source"], e["type"], e["target"], tx=tx)
                        count += 1
                        if count % self.batch_size == 0:
                            tx.commit(); self.log.log(f"[BATCH] committed {count} edges")
                            tx = session.begin_transaction()
                    tx.commit(); self.log.log(f"[BATCH] final commit edges total={count}")
                except Exception as e:
                    try: tx.rollback()
                    except Exception: pass
                    self.log.log(f"[ERROR] during edge batching: {e}")

        self.log.log("[DONE] process finished")
