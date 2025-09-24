# -*- coding: utf-8 -*-
"""
Pandas 基礎操作課堂練習：學生期中成績分析
"""

import pandas as pd

def load_and_explore_data(file_path):
    """任務一：讀取 CSV 並初步探索資料"""
    df = pd.read_csv(file_path, encoding='utf-8-sig')

    # TODO 1.1: 顯示前 5 筆資料
    # Hint: 使用 df.head() 來查看前幾筆

    # TODO 1.2: 查看資料結構（欄位、型態、缺失值）
    # Fill here

    return df

def feature_engineering(df):
    """計算總分、平均分數與是否及格"""
    
    # TODO 2.1: 計算總分
    # Fill here

    # TODO 2.2: 計算平均分數
    # Fill here

    # TODO 2.3: 新增是否及格欄位
    # Hint: 可以用比較運算符產生布林值

    return df

def filter_and_analyze_data(df):
    """篩選資料與統計"""
    
    # TODO 3.1: 找出數學成績 < 60 的學生
    # Fill here

    # TODO 3.2: 找出班級為 'A' 且英文 > 90 的學生
    # Fill here

    # TODO 4.1: 顯示統計摘要
    # Fill here

    # TODO 4.2: 找出總分最高的學生
    # Fill here

    return df

def save_results(df, output_file_path):
    """儲存為 CSV"""
    
    # TODO 5.1: 儲存 CSV
    # Fill here

if __name__ == "__main__":
    INPUT_CSV = "grades.csv"
    OUTPUT_CSV = "grades_analyzed.csv"

    df = load_and_explore_data(INPUT_CSV)
    df = feature_engineering(df)
    df = filter_and_analyze_data(df)
    save_results(df, OUTPUT_CSV)

    print("完成所有分析任務")
