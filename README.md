# Neo4j Ontology Tools

CLI tool để import ontology JSON vào Neo4j và thực hiện các thao tác tìm kiếm có chỉ mục (fulltext, btree, exact, neighbors).

## Cài đặt:
```bash
git clone https://github.com/alpine1808/Neo4J.git
cd Neo4J
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
touch .env
```

## Thiết lập .env:
```env
NEO4J_URI=neo4j_uri
NEO4J_USER=neo4j_user
NEO4J_PASSWORD=neo4j_password
LOG_FILE=update.log
BATCH_SIZE=500
```

## Các lệnh chính:
- import — Nạp ontology
- ensure-fulltext — Tạo fulltext index nếu chưa có
- fulltext — Truy vấn fulltext index
- ensure-btree — Tạo btree index nếu chưa có
- exact — Tìm kiếm chính xác theo label/prop=value
- neighbors — Liệt kê hàng xóm của một node

## Chạy để xem cú pháp:
```bash
python main.py --help
```
