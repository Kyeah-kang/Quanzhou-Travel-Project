-- 仅空卷首次启动时执行：启用 pgvector，供 M2 向量检索使用
CREATE EXTENSION IF NOT EXISTS vector;
