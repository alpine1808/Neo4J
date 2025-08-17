from typing import List
from .base_service import BaseService
from repositories.constraint_repo import ConstraintRepository
from utils.validators import validate_label

class ConstraintService(BaseService):
    def __init__(self, client, logger, dry_run: bool):
        super().__init__(client, logger, dry_run)
        self.repo = ConstraintRepository()

    def ensure_unique_id(self, labels: List[str]):
        labels = list({l for l in labels if l})
        if self.dry_run:
            for l in labels:
                try:
                    validate_label(l)
                    self.log.log(f"[DRYRUN] Would create UNIQUE constraint for :{l}(id)")
                except Exception as e:
                    self.log.log(f"[DRYRUN][SKIP] label invalid {l}: {e}")
            return
        with self.client.session() as session:
            self.repo.create_unique_id_constraints(session, labels)
        for l in labels:
            self.log.log(f"[CONSTRAINT] Ensure UNIQUE constraint for :{l}(id)")
