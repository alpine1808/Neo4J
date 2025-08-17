# main.py
import argparse
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, LOG_FILE, BATCH_SIZE
from db.neo4j_client import Neo4jClient
from utils.logger import LogWriter
from services.import_service import ImportService
from services.search_service import SearchService

def main():
    parser = argparse.ArgumentParser(description="Ontology tools (import + indexed search)")
    subparsers = parser.add_subparsers(dest="cmd")

    # Global/common
    parser.add_argument("--uri", default=NEO4J_URI)
    parser.add_argument("--user", default=NEO4J_USER)
    parser.add_argument("--password", default=NEO4J_PASSWORD)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--log-file", default=LOG_FILE)
    parser.add_argument("--multi-object", action="store_true")

    # import
    p_import = subparsers.add_parser("import", help="Import ontology JSON")
    p_import.add_argument("--file", "-f", required=True)

    # ensure fulltext
    p_efts = subparsers.add_parser("ensure-fulltext", help="Create fulltext index if not exists")
    p_efts.add_argument("--name", required=True)
    p_efts.add_argument("--labels", required=True, help="Comma-separated")
    p_efts.add_argument("--props", required=True, help="Comma-separated")

    # fulltext query
    p_qfts = subparsers.add_parser("fulltext", help="Query fulltext index")
    p_qfts.add_argument("--name", required=True)
    p_qfts.add_argument("--q", required=True)
    p_qfts.add_argument("--limit", type=int, default=25)
    p_qfts.add_argument("--min-score", type=float, default=0.0)

    # ensure btree
    p_ebt = subparsers.add_parser("ensure-btree", help="Create btree index if not exists")
    p_ebt.add_argument("--label", required=True)
    p_ebt.add_argument("--prop", required=True)

    # exact query
    p_exact = subparsers.add_parser("exact", help="Exact match on label/prop=value")
    p_exact.add_argument("--label", required=True)
    p_exact.add_argument("--prop", required=True)
    p_exact.add_argument("--value", required=True)
    p_exact.add_argument("--limit", type=int, default=100)

    # neighbors
    p_nb = subparsers.add_parser("neighbors", help="List neighbors of a node")
    p_nb.add_argument("--id", required=True)
    p_nb.add_argument("--rel", default=None)
    p_nb.add_argument("--direction", choices=["out", "in", "both"], default="out")
    p_nb.add_argument("--limit", type=int, default=100)

    args = parser.parse_args()
    client = Neo4jClient(args.uri, args.user, args.password)
    logger = LogWriter(args.log_file)

    importer = ImportService(client, logger, dry_run=args.dry_run, batch_size=args.batch_size, multi_object=args.multi_object)
    search   = SearchService(client, logger, dry_run=args.dry_run)

    try:
        cmd = args.cmd or "import"
        if cmd == "import":
            data = importer.load_json(args.file)
            importer.process(data)

        elif cmd == "ensure-fulltext":
            labels = [x.strip() for x in args.labels.split(",") if x.strip()]
            props  = [x.strip() for x in args.props.split(",") if x.strip()]
            search.ensure_fulltext_index(args.name, labels, props)

        elif cmd == "fulltext":
            rows = search.fulltext(args.name, args.q, limit=args.limit, min_score=args.min_score)
            for r in rows:
                print(r["id"], r["labels"], round(r["score"], 3))

        elif cmd == "ensure-btree":
            search.ensure_btree_index(args.label, args.prop)

        elif cmd == "exact":
            rows = search.exact(args.label, args.prop, args.value, limit=args.limit)
            for r in rows:
                print(r["id"], r["labels"])

        elif cmd == "neighbors":
            rows = search.neighbors(args.id, rel_type=args.rel, direction=args.direction, limit=args.limit)
            for r in rows:
                print(r["rel_type"], "->", r["id"], r["labels"])
        else:
            parser.error(f"Unknown command: {cmd}")

    finally:
        client.close()

if __name__ == "__main__":
    main()
