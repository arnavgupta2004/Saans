"""Load the demo schools into DynamoDB. Usage: python scripts/seed_dynamo.py [table] (from backend/)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from saans.store import SEED_SCHOOLS, DynamoStore  # noqa: E402

store = DynamoStore(sys.argv[1] if len(sys.argv) > 1 else "saans-schools")
for s in SEED_SCHOOLS:
    store.save(s)
    print("seeded", s.id)
