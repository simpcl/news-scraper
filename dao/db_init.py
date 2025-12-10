#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL数据库初始化脚本
"""

import psycopg2
import psycopg2.extras

from db_config import get_connection_string

def init_database(config=None):
    """初始化新闻数据库"""
    # 获取连接字符串
    conn_str = get_connection_string(config)

    try:
        # 连接到PostgreSQL服务器（不指定数据库）
        conn_str_no_db = conn_str.rsplit('/', 1)[0] + '/postgres'
        conn = psycopg2.connect(conn_str_no_db)
        conn.autocommit = True
        cursor = conn.cursor()

        # 创建数据库（如果不存在）
        db_name = get_connection_string(config).rsplit('/')[-1]
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"数据库 {db_name} 创建成功")

        conn.close()

        # 连接到指定数据库
        conn = psycopg2.connect(conn_str)
        cursor = conn.cursor()

        # 创建新闻表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                time TIMESTAMP NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建索引以优化查询
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_news_source ON news(source)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_news_time ON news(time)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_news_url ON news(url)
        ''')

        # 创建更新时间的触发器
        cursor.execute('''
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        ''')

        cursor.execute('''
            CREATE TRIGGER update_news_updated_at
                BEFORE UPDATE ON news
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        ''')

        # 提交更改并关闭连接
        conn.commit()
        conn.close()

        print(f"数据库初始化完成: {db_name}")

    except psycopg2.Error as e:
        print(f"数据库初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_database()