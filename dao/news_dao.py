#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻数据访问对象 (News Data Access Object)
"""

import psycopg2
import psycopg2.extras
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from db_config import get_connection_string, get_database_config


class NewsDAO:
    """新闻数据访问类"""

    def __init__(self, config=None):
        """初始化数据库连接

        Args:
            config: 可选的自定义数据库配置
        """
        self.config = get_database_config(config)
        self.connection_string = get_connection_string(config)
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """确保数据库存在"""
        try:
            # 尝试连接到数据库
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM news LIMIT 1")
                cursor.fetchone()
        except psycopg2.Error:
            # 数据库不存在或表不存在，运行初始化
            from db_init import init_database

            init_database(self.config)

    def _get_connection(self):
        """获取数据库连接"""
        conn = psycopg2.connect(self.connection_string)
        # 使查询结果可以按列名访问
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return conn

    def insert_news(self, news_data: Dict) -> bool:
        """插入单条新闻，避免重复"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 检查URL是否已存在
                cursor.execute(
                    "SELECT id FROM news WHERE url = %s", (news_data["url"],)
                )
                if cursor.fetchone():
                    print(f"新闻已存在，跳过: {news_data['title']}")
                    return False

                # 插入新闻
                # 如果time不存在，使用当前时间
                news_time = news_data.get("time")
                if not news_time:
                    news_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute(
                    """
                    INSERT INTO news (title, url, source, time, content)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (
                        news_data["title"],
                        news_data["url"],
                        news_data["source"],
                        news_time,
                        news_data["content"],
                    ),
                )

                conn.commit()
                print(f"成功插入新闻: {news_data['title']}")
                return True

        except psycopg2.Error as e:
            print(f"插入新闻失败: {e}")
            return False

    def insert_news_batch(self, news_list: List[Dict]) -> int:
        """批量插入新闻，返回成功插入的数量"""
        success_count = 0

        with self._get_connection() as conn:
            cursor = conn.cursor()

            for news in news_list:
                try:
                    # 检查URL是否已存在
                    cursor.execute("SELECT id FROM news WHERE url = %s", (news["url"],))
                    if cursor.fetchone():
                        continue

                    # 插入新闻
                    # 如果time不存在，使用当前时间
                    news_time = news.get("time")
                    if not news_time:
                        news_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    cursor.execute(
                        """
                        INSERT INTO news (title, url, source, time, content)
                        VALUES (%s, %s, %s, %s, %s)
                    """,
                        (
                            news["title"],
                            news["url"],
                            news["source"],
                            news_time,
                            news["content"],
                        ),
                    )

                    success_count += 1

                except psycopg2.Error as e:
                    print(f"插入新闻失败: {news['title']}, 错误: {e}")

            conn.commit()

        print(f"批量插入完成，成功插入 {success_count} 条新闻")
        return success_count

    def load_from_json_file(self, json_file_path: str) -> int:
        """从JSON文件加载新闻到数据库"""
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            news_list = data.get("news_list", [])
            return self.insert_news_batch(news_list)

        except FileNotFoundError:
            print(f"文件不存在: {json_file_path}")
            return 0
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return 0

    def get_news_by_source(self, source: str, limit: int = 10) -> List[Dict]:
        """根据来源获取新闻"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM news
                    WHERE source = %s
                    ORDER BY time DESC
                    LIMIT %s
                """,
                    (source, limit),
                )

                return [dict(row) for row in cursor.fetchall()]

        except psycopg2.Error as e:
            print(f"查询新闻失败: {e}")
            return []

    def get_news_by_time_range(self, start_time: str, end_time: str) -> List[Dict]:
        """根据时间范围获取新闻

        Args:
            start_time: 开始时间，格式为 'YYYY-MM-DD HH:MM:SS' 或 'YYYY-MM-DD'
            end_time: 结束时间，格式为 'YYYY-MM-DD HH:MM:SS' 或 'YYYY-MM-DD'
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 确保时间格式为 TIMESTAMP
                if len(start_time) == 10:  # 只有日期，没有时间
                    start_time += " 00:00:00"
                if len(end_time) == 10:  # 只有日期，没有时间
                    end_time += " 23:59:59"

                cursor.execute(
                    """
                    SELECT * FROM news
                    WHERE time BETWEEN %s AND %s
                    ORDER BY time DESC
                """,
                    (start_time, end_time),
                )

                return [dict(row) for row in cursor.fetchall()]

        except psycopg2.Error as e:
            print(f"查询新闻失败: {e}")
            return []

    def search_news_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """根据关键词搜索新闻"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM news
                    WHERE title LIKE %s OR content LIKE %s
                    ORDER BY time DESC
                    LIMIT %s
                """,
                    (f"%{keyword}%", f"%{keyword}%", limit),
                )

                return [dict(row) for row in cursor.fetchall()]

        except psycopg2.Error as e:
            print(f"搜索新闻失败: {e}")
            return []

    def get_latest_news(self, limit: int = 10) -> List[Dict]:
        """获取最新新闻"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT * FROM news
                    ORDER BY time DESC
                    LIMIT %s
                """,
                    (limit,),
                )

                return [dict(row) for row in cursor.fetchall()]

        except psycopg2.Error as e:
            print(f"获取最新新闻失败: {e}")
            return []

    def get_news_count_by_source(self) -> List[Dict]:
        """统计各来源的新闻数量"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT source, COUNT(*) as count
                    FROM news
                    GROUP BY source
                    ORDER BY count DESC
                """
                )

                return [dict(row) for row in cursor.fetchall()]

        except psycopg2.Error as e:
            print(f"统计新闻数量失败: {e}")
            return []

    def delete_old_news(self, days: int = 30) -> int:
        """删除指定天数之前的新闻，返回删除的数量"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 使用 PostgreSQL 的 NOW() 和 INTERVAL 函数计算时间
                cursor.execute(
                    """
                    DELETE FROM news
                    WHERE time < NOW() - INTERVAL '%s days'
                """,
                    (days,),
                )

                deleted_count = cursor.rowcount
                conn.commit()

                print(f"删除了 {deleted_count} 条旧新闻")
                return deleted_count

        except psycopg2.Error as e:
            print(f"删除旧新闻失败: {e}")
            return 0

    def get_total_count(self) -> int:
        """获取新闻总数"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) as count FROM news")
                result = cursor.fetchone()

                return result["count"] if result else 0

        except psycopg2.Error as e:
            print(f"获取新闻总数失败: {e}")
            return 0


def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="新闻数据访问对象 (News DAO)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    show_parser = subparsers.add_parser("show", help="Show database information")

    import_parser = subparsers.add_parser("import", help="导入新闻数据")
    import_parser.add_argument(
        "--json", nargs="?", default="", help="导入JSON文件路径 (如: news.json)"
    )

    args = parser.parse_args()

    config = None
    dao = NewsDAO(config)

    if args.command and args.command == "import":
        if not args.json:
            print("请指定JSON文件路径")
            return
        print(f"正在从JSON文件导入数据...")
        # 从JSON文件导入数据
        count = dao.load_from_json_file(args.json)
        print(f"从JSON文件导入了 {count} 条新闻")
    elif args.command and args.command == "show":
        # 显示统计信息
        print(f"\n数据库中共有 {dao.get_total_count()} 条新闻")

        # 显示各来源统计
        print("\n各来源新闻统计:")
        for stat in dao.get_news_count_by_source():
            print(f"  {stat['source']}: {stat['count']} 条")

        # 显示最新新闻
        print("\n最新3条新闻:")
        for news in dao.get_latest_news(3):
            print(f"  {news['time']} - {news['title']} ({news['source']})")
    else:
        print("请选择要执行的命令")


if __name__ == "__main__":
    main()
