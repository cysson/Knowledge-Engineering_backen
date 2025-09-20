# Knowledge Graph Backend (kg\_backend)

## 项目简介

本项目是一个基于 **FastAPI + Neo4j** 的知识图谱管理信息系统后端，实现了：

* 节点和关系的 **增删查改**（CRUD）接口
* **CSV 批量导入**功能，支持大规模知识图谱数据
* 支持 **分页查询**，可对千万级边进行管理
* 提供 JSON 接口，可直接对接前端 Web 可视化界面

本项目可作为课程作业的后端部分，配合前端可实现知识图谱的查询、管理和更新功能。

---

## 文件树形结构

```
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
```

---

## 环境依赖

使用 Python >= 3.9，依赖包在 `requirements.txt` 中：

```text
fastapi==0.109.1
uvicorn==0.24.0
neo4j==5.10.0
pydantic==2.11.1
```

安装依赖：

```bash
pip install -r requirements.txt
```

同时需要本地安装并运行 **Neo4j**，并在 `db.py` 中配置连接信息：

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test123"
```

---

## 运行后端

启动 FastAPI 服务：

```bash
python -m uvicorn main:app --reload --port 8000
```

访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 查看自动生成的 Swagger 接口文档，可直接测试节点和关系的增删改查接口。

---

## CSV 批量导入

* 将节点 CSV 放在 `data/nodes.csv`，关系 CSV 放在 `data/edges.csv`
* 使用 `db.py` 中函数进行导入：

```python
from db import import_nodes, import_edges

# 导入节点
import_nodes("data/nodes.csv", "Entity")

# 导入关系
import_edges("data/edges.csv", "Entity", "Entity", "RELATION")
```

> 注意：CSV 中节点和关系需包含唯一标识（如 `id`），关系文件需包含 `start_id` 和 `end_id` 对应节点 ID。

---

## API 使用说明

### 节点接口

* 查询节点：`GET /query/node?label=Entity&key=name&value=xxx&limit=50&skip=0`
* 新增节点：`POST /add/node`
* 删除节点：`DELETE /delete/node?label=Entity&key=id&value=xxx`
* 更新节点：`PATCH /update/node`

### 关系接口

* 新增关系：`POST /add/edge`
* 删除关系：`DELETE /delete/edge?start_label=Entity&start_id=1&end_label=Entity&end_id=2&relation=RELATION`
* 更新关系：`PATCH /update/edge`

所有接口返回 JSON 格式数据，可直接供前端可视化使用。

---

## 注意事项

1. 数据量大时建议使用 Neo4j 的原生 **LOAD CSV** 功能进行批量导入，以提高效率。
2. 对查询大量数据时建议使用 **分页参数** `limit` 和 `skip` 避免一次性返回过多数据。
3. 节点和关系必须有唯一标识（如 `id`），否则更新和删除接口无法精确匹配。


