import pymysql

# 连接数据库
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="office_agent",
    port=3306
)

cursor = conn.cursor()

# 1. 用户表
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. 对话记录表
cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    role VARCHAR(20),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

# 3. 文档表
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

print("✅ 三张表创建成功！")
print("   - users: 用户表")
print("   - conversations: 对话记录表")
print("   - documents: 文档表")

cursor.close()
conn.close()