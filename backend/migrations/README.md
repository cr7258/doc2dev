# UTC 时间迁移指南

## 概述

本迁移将数据库中的所有时间戳从服务器本地时间转换为 UTC 时间，确保时间存储的一致性。

## 迁移内容

### 修改的表和字段：

1. **doc2dev.repositories**
   - `created_at` 
   - `updated_at`

2. **doc2dev_users.users**
   - `created_at`
   - `updated_at`

3. **doc2dev_user_*.repositories** (所有用户数据库)
   - `created_at`
   - `updated_at`

### 代码修改：

1. **后端 SQLAlchemy 模型**：
   - 使用 `func.utc_timestamp()` 替代 `func.now()`
   - 使用 `datetime.utcnow` (User模型已经是UTC)

2. **数据库创建脚本**：
   - 使用 `UTC_TIMESTAMP()` 替代 `CURRENT_TIMESTAMP`

3. **前端时间处理**：
   - 改进UTC时间解析逻辑
   - 保持相对时间计算不变

## 迁移步骤

### 1. 备份数据库
```bash
# 备份主数据库
mysqldump -u username -p doc2dev > doc2dev_backup.sql
mysqldump -u username -p doc2dev_users > doc2dev_users_backup.sql

# 备份用户数据库（如果有）
mysqldump -u username -p --databases $(mysql -u username -p -e "SHOW DATABASES LIKE 'doc2dev_user_%'" | grep doc2dev_user) > user_databases_backup.sql
```

### 2. 运行迁移脚本

#### 选项 A: 使用 Python 脚本（推荐）
```bash
cd backend/migrations
python migrate_to_utc.py
```

#### 选项 B: 手动执行 SQL
```bash
mysql -u username -p < convert_to_utc.sql
```

### 3. 部署更新的代码
```bash
# 部署后端代码更新
# 重启应用服务器
```

### 4. 验证迁移结果

#### 检查新记录使用 UTC 时间：
```sql
-- 创建测试记录
INSERT INTO doc2dev.repositories (name, repo, repo_url, tokens, snippets, repo_status) 
VALUES ('test', '/test/test', 'https://github.com/test/test', 0, 0, 'pending');

-- 检查时间戳（应该是 UTC 时间）
SELECT created_at, updated_at, NOW(), UTC_TIMESTAMP() FROM doc2dev.repositories WHERE name = 'test';

-- 清理测试记录
DELETE FROM doc2dev.repositories WHERE name = 'test';
```

#### 检查前端显示：
1. 访问应用首页
2. 检查相对时间显示是否正确（如"5分钟前"）
3. 鼠标悬停查看完整时间戳

## 注意事项

### ⚠️ 重要提醒：

1. **时区假设**：迁移脚本假设当前数据库使用服务器默认时区
2. **数据一致性**：迁移后所有新数据都将使用 UTC 时间
3. **前端兼容**：前端代码已更新以正确处理 UTC 时间
4. **相对时间**：由于使用相对时间显示，用户不会感知到变化

### 🔍 故障排除：

1. **时间显示异常**：检查服务器时区设置
2. **迁移失败**：检查数据库权限和连接
3. **数据不一致**：使用备份恢复并重新迁移

### 📊 迁移验证：

```sql
-- 检查时区设置
SELECT @@global.time_zone, @@session.time_zone;

-- 比较 UTC 和本地时间
SELECT NOW(), UTC_TIMESTAMP();

-- 检查迁移后的数据
SELECT id, created_at, updated_at FROM repositories ORDER BY id DESC LIMIT 5;
```

## 回滚计划

如果需要回滚：

1. **停止应用服务**
2. **恢复数据库备份**：
   ```bash
   mysql -u username -p doc2dev < doc2dev_backup.sql
   mysql -u username -p doc2dev_users < doc2dev_users_backup.sql
   ```
3. **回滚代码更改**
4. **重启应用服务**
