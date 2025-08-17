from .base_service import BaseService
from repositories.relation_repo import RelationRepository
from utils.validators import validate_rel

class RelationService(BaseService):
    def __init__(self, client, logger, dry_run: bool, multi_object: bool):
        super().__init__(client, logger, dry_run)
        self.repo = RelationRepository()
        self.multi_object = multi_object

    def get_targets(self, src_id: str, rel_type: str, tx=None):
        if tx is not None:
            return self.repo.get_targets(tx, src_id, rel_type)
        with self.client.session() as session:
            return self.repo.get_targets(session, src_id, rel_type)

    def add(self, src_id: str, rel_type: str, tgt_id: str, tx=None):
        if self.dry_run:
            self.log.log(f"[DRYRUN] Would MERGE relation ({src_id})-[:{rel_type}]->({tgt_id})")
            return
        if tx is not None:
            self.repo.add(tx, src_id, rel_type, tgt_id)
        else:
            with self.client.session() as session:
                self.repo.add(session, src_id, rel_type, tgt_id)
        self.log.log(f"[ADD] Relation ({src_id})-[:{rel_type}]->({tgt_id}) added")

    def delete(self, src_id: str, rel_type: str, tgt_id: str, tx=None):
        if self.dry_run:
            self.log.log(f"[DRYRUN] Would DELETE relation ({src_id})-[:{rel_type}]->({tgt_id})")
            return
        if tx is not None:
            self.repo.delete(tx, src_id, rel_type, tgt_id)
        else:
            with self.client.session() as session:
                self.repo.delete(session, src_id, rel_type, tgt_id)
        self.log.log(f"[DELETE] Relation ({src_id})-[:{rel_type}]->({tgt_id}) deleted")

    def update_with_policy(self, src_id: str, rel_type: str, tgt_id: str, tx=None):
        current = self.get_targets(src_id, rel_type, tx=tx)
        if tgt_id in current:
            self.log.log(f"[SKIP] ({src_id}, {rel_type}, {tgt_id}) already exists")
            return
        if not self.multi_object and current:
            for old in current:
                self.log.log(f"[PLANNED DELETE] ({src_id}, {rel_type}, {old})")
                if not self.dry_run:
                    self.delete(src_id, rel_type, old, tx=tx)
        self.add(src_id, rel_type, tgt_id, tx=tx)
