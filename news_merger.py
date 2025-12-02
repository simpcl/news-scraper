#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import glob
import os
import sys
from typing import Dict, List, Any

import utils

class NewsMerger:
    def __init__(self):
        self.data_dir = os.environ.get("DATA_DIR", ".")
        self.output_file = "news_merged.json"

    def merge_news_files(self) -> Dict[str, Any]:
        """
        合并指定目录下的所有 *_news.json 文件

        Args:
            directory (str): 包含JSON文件的目录路径，默认为当前目录

        Returns:
            Dict[str, Any]: 合并后的数据，包含 total_count 和 news_list
        """

        merged_data = {"total_count": 0, "news_list": []}
        json_files = self._glob_news_files()
        if not json_files:
            return merged_data

        # 逐个读取并合并文件
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 累加总数
                merged_data["total_count"] += data.get("total_count", 0)

                # 合并新闻列表
                news_list = data.get("news_list", [])
                merged_data["news_list"].extend(news_list)

                print(f"已合并 {os.path.basename(file_path)}: {len(news_list)} 条新闻")

            except Exception as e:
                print(f"读取文件 {file_path} 时出错: {e}")
                continue

        print(
            f"\n合并完成！总计 {merged_data['total_count']} 条新闻，实际合并 {len(merged_data['news_list'])} 条新闻"
        )

        return merged_data

    def _glob_news_files(self) -> List[str]:
        """
        获取所有 *_news.json 文件的路径

        Returns:
            List[str]: 所有 *_news.json 文件的路径
        """
        # 查找所有匹配的JSON文件
        pattern = os.path.join(self.data_dir, "*_news.json")
        json_files = glob.glob(pattern)

        if not json_files:
            print(f"在目录 {self.data_dir} 中未找到 *_news.json 文件")
            return None

        # 按文件名排序，确保合并顺序一致
        json_files.sort()

        print(f"找到 {len(json_files)} 个文件：")
        for file_path in json_files:
            print(f"  - {os.path.basename(file_path)}")
        return json_files

if __name__ == "__main__":
    print("开始合并 *_news.json 文件...")
    try:
        news_merger = NewsMerger()
        merged_data = news_merger.merge_news_files()
        if merged_data is None or "news_list" not in merged_data:
            print("合并的数据为空")
            sys.exit(1)
        if len(merged_data["news_list"]) == 0:
            print("没有找到可合并的数据")
            sys.exit(1)

        data_dir = os.environ.get("DATA_DIR", ".")
        file_path = utils.save_to_json_file(merged_data, data_dir, "news_merged.json")
        print(f"合并结果已保存到: {file_path}")
    except Exception as e:
        print(f"合并文件时发生错误: {e}")
        sys.exit(1)

