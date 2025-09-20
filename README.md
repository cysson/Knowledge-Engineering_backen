# Knowledge Graph Backend (kg\_backend)

## 项目简介

本项目是一个 **基于 FastAPI + Neo4j 的知识图谱管理系统后端**，支持：

* 节点和关系的增删改查（CRUD）
* CSV 批量导入节点和关系数据
* 全文索引模糊搜索
* 获取实体的一度邻居关系（支持动态过滤关系类型和节点标签）
* 查找两实体间的最短路径
* 按时间属性生成事件时间线

可直接与前端 Web 界面对接，实现知识图谱可视化管理与探索。

---

## 文件树形结构

```
kg_backend/
│
├─ main.py                # FastAPI 主程序，包含所有接口
├─ db.py                  # Neo4j 数据库连接与批量导入函数
├─ models.py              # Pydantic 数据模型（节点/关系）
├─ requirements.txt       # Python 依赖
├─ data/
│   ├─ nodes.csv          # 节点 CSV
│   └─ edges.csv          # 关系 CSV
└─ README.md
```

---

## 环境依赖

* Python >= 3.9
* Neo4j 数据库（本地或远程）

安装依赖：

```bash
pip install -r requirements.txt
```

配置 Neo4j 连接信息（在 `db.py`）：

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test123"
```

---

## 启动后端

```bash
python -m uvicorn main:app --reload --port 8000
```

浏览器访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 查看 **Swagger UI**，可直接测试接口。

---

## CSV 批量导入

将节点 CSV 放在 `data/nodes.csv`，关系 CSV 放在 `data/edges.csv`。

导入示例：

```python
from db import import_nodes, import_edges

# 导入节点
import_nodes("data/nodes.csv", "Person")

# 导入关系
import_edges("data/edges.csv", "Person", "Organisation", "WORKED_AT")
```

> 节点 CSV 需包含 `id` 唯一标识
> 关系 CSV 需包含 `start_id` 和 `end_id`

---

## API 使用说明

### 节点操作

| 接口                 | 方法     | 参数                             | 功能     |
| ------------------ | ------ | ------------------------------ | ------ |
| `/api/query/node`  | GET    | label, key, value, limit, skip | 查询节点   |
| `/api/add/node`    | POST   | Node                           | 新增节点   |
| `/api/delete/node` | DELETE | label, key, value              | 删除节点   |
| `/api/update/node` | PATCH  | label, key, value, updates     | 更新节点属性 |

### 关系操作

| 接口                 | 方法     | 参数                                                              | 功能     |
| ------------------ | ------ | --------------------------------------------------------------- | ------ |
| `/api/add/edge`    | POST   | Edge                                                            | 新增关系   |
| `/api/delete/edge` | DELETE | start\_label, start\_id, end\_label, end\_id, relation          | 删除关系   |
| `/api/update/edge` | PATCH  | start\_label, start\_id, end\_label, end\_id, relation, updates | 更新关系属性 |

### 高级查询

| 接口                                  | 方法  | 参数                                            | 功能            |
| ----------------------------------- | --- | --------------------------------------------- | ------------- |
| `/api/search`                       | GET | q, limit                                      | 全文索引模糊搜索      |
| `/api/entity/{entity_id}/neighbors` | GET | entity\_id, relationType (可选), nodeLabel (可选) | 获取一度邻居，支持动态过滤 |
| `/api/path`                         | GET | start, end, max\_hops                         | 查找两实体最短路径     |
| `/api/timeline/{entity_id}`         | GET | entity\_id                                    | 按时间属性生成事件时间线  |

---

## 示例

### 模糊搜索

```http
GET /api/search?q=Albert Einstein&limit=5
```

### 获取一度邻居（动态过滤）

```http
GET /api/entity/Albert_Einstein/neighbors?relationType=BORN_IN&nodeLabel=Place
```

### 查找最短路径

```http
GET /api/path?start=Albert_Einstein&end=Princeton_University&max_hops=5
```

### 时间线

```http
GET /api/timeline/Albert_Einstein
```

---

## 注意事项

1. 数据量大时，可使用 Neo4j **LOAD CSV** 提升导入性能
2. 查询大数据量时建议使用 `limit` 和 `skip` 分页
3. 所有节点和关系需有唯一标识，否则更新/删除无法精确匹配
4. 启动时会自动创建全文索引和唯一约束，用于模糊搜索和保证数据唯一性

