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

# 创建测试表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# 插入数据
cursor.execute("INSERT INTO test_users (name) VALUES ('wyj')")
conn.commit()

# 查询
cursor.execute("SELECT * FROM test_users")
rows = cursor.fetchall()
print("查询结果：", rows)

cursor.close()
conn.close()
print("✅ MySQL 连接测试成功！")