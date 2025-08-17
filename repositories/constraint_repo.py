from typing import List
from utils.validators import validate_label

class ConstraintRepository:
    def create_unique_id_constraints(self, session, labels: List[str]):
        for l in {x for x in labels if x}:
            l = validate_label(l)
            session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{l}) REQUIRE n.id IS UNIQUE")
