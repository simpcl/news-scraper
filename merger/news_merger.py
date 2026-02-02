#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import glob
import os
import sys
from typing import Dict, List, Any
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import utils

class NewsMerger:
    def __init__(self):
        self.data_dir = os.environ.get("DATA_DIR", ".")
        self.output_file = "news_merged.json"

    def _merge_news_files(self, json_files) -> Dict[str, Any]:
        merged_data = {"total_count": 0, "news_list": []}

        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                merged_data["total_count"] += data.get("total_count", 0)

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

    def _glob_news_files(self, data_dir) -> List[str]:
        pattern = os.path.join(data_dir, "*_news.json")
        json_files = glob.glob(pattern)

        if not json_files:
            return None

        json_files.sort()
        return json_files

    def run(self, data_dir, output_filepath = None) -> str:   
        try:
            print(f"开始合并目录 {data_dir} 中的文件...")
            json_files = self._glob_news_files(data_dir)
            if not json_files:
                print(f"在目录 {data_dir} 中未找到 *_news.json 文件")
                return False
            print(f"找到 {len(json_files)} 个文件：")
            for file_path in json_files:
                print(f"  - {os.path.basename(file_path)}")
            merged_data = news_merger._merge_news_files(json_files)
            if merged_data is None or "news_list" not in merged_data:
                print("合并的数据为空")
                return False
            if len(merged_data["news_list"]) == 0:
                print("没有找到可合并的数据")
                return False

            if not output_filepath:
                output_filepath = os.path.join(self.data_dir, self.output_file)
            utils.save_to_json_file(merged_data, output_filepath)
            print(f"合并结果已保存到: {output_filepath}")
        except Exception as e:
            print(f"合并文件时发生错误: {e}")
            return False
        return True

if __name__ == "__main__":
    load_dotenv()
    data_dir = os.environ.get("DATA_DIR", ".")
    news_merger = NewsMerger()
    news_merger.run(data_dir)

