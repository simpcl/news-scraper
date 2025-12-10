#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 数据库配置
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# 默认 PostgreSQL 配置
DEFAULT_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'news_scraper'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password'),
}

def get_database_config(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """获取数据库配置

    Args:
        config: 可选的自定义配置，会覆盖默认配置

    Returns:
        合并后的数据库配置字典
    """
    db_config = DEFAULT_CONFIG.copy()

    if config:
        db_config.update(config)

    return db_config

def get_connection_string(config: Dict[str, Any] = None) -> str:
    """获取 PostgreSQL 连接字符串

    Args:
        config: 可选的自定义配置

    Returns:
        PostgreSQL 连接字符串
    """
    db_config = get_database_config(config)

    return (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )