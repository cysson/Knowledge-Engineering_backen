## 文件树形结构 
kg_backend/
│
├─ main.py                # FastAPI 主程序
├─ db.py                  # Neo4j 数据库连接与批量导入函数
├─ models.py              # Pydantic 数据模型
├─ requirements.txt       # Python 依赖
├─ data/
│   ├─ nodes.csv          # 节点 CSV
│   └─ edges.csv          # 关系 CSV
└─ README.md
## 运行后端
python -m uvicorn main:app --reload --port 8000