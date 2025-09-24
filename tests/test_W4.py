# -*- coding: utf-8 -*-
import pytest
import pandas as pd
import importlib.util
from pathlib import Path
import os
import re

# -------------------------
# 取得學生 PR 新增檔案
# -------------------------
SUBMIT_DIR = Path(__file__).parent / "submit"
student_files = list(SUBMIT_DIR.glob("W4_*.py"))
if not student_files:
    raise FileNotFoundError(f"{SUBMIT_DIR} ❌ 目錄下沒有學生提交檔案")

student_file = student_files[0]

# 動態 import 學生程式
spec = importlib.util.spec_from_file_location("student_submission", student_file)
student_submission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(student_submission)

# -------------------------
# 測試用 DataFrame
# -------------------------
@pytest.fixture
def sample_df():
    data = {
        "姓名": ["Alice","Bob","Charlie","David","Eva"],
        "性別": ["F","M","M","M","F"],
        "班級": ["A","B","A","C","A"],
        "數學": [95,55,60,45,88],
        "英文": [88,70,92,60,95],
        "國文": [78,82,85,50,90],
        "自然": [90,65,80,40,85],
        "社會": [85,60,70,55,92],
    }
    return pd.DataFrame(data)

# -------------------------
# 工具函式：記錄測試結果與計分
# -------------------------
results = []

POINTS = {
    "總分正確": 10,
    "平均正確": 10,
    "David 是否不及格": 5,
    "Alice 是否及格": 5,
    "數學不及格人數": 10,
    "A班英文>90人數": 5,
    "總分最高學生是 Eva": 10,
    "CSV 檔案存在": 5,
    "CSV 欄位存在: 總分": 5,
    "CSV 欄位存在: 平均": 5,
    "CSV 欄位存在: 是否及格": 5
}

def check(name, condition, msg=""):
    if condition:
        results.append(f"✅ {name} (+{POINTS.get(name,0)})")
    else:
        results.append(f"❌ {name} - {msg} (+0)")

def calculate_score():
    score = 0
    for line in results:
        if line.startswith("✅"):
            m = re.search(r'\+(\d+)', line)
            if m:
                score += int(m.group(1))
    return score

def save_results_md(filename="test_results/results.md"):
    score = calculate_score()
    os.makedirs(Path(filename).parent, exist_ok=True)
    content = f"### 學生作業自動測試結果\n正確性總分: {score}\n\n" + "\n".join(results)

    print("===== results.md 內容 =====")
    print(content)
    print("===========================")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# -------------------------
# 功能測試
# -------------------------
def test_feature_engineering(sample_df):
    df = student_submission.feature_engineering(sample_df.copy())

    check("總分正確", df.loc[0, "總分"] == 95+88+78+90+85,
          msg=f"預期 {95+88+78+90+85}, 但得到 {df.loc[0,'總分']}")

    check("平均正確", pytest.approx(df.loc[0, "平均"]) == (95+88+78+90+85)/5,
          msg=f"預期 {(95+88+78+90+85)/5}, 但得到 {df.loc[0,'平均']}")

    check("David 是否不及格", bool(df.loc[3, "是否及格"]) == False)
    check("Alice 是否及格", bool(df.loc[0, "是否及格"]) == True)

def test_filter_and_analyze_data(sample_df):
    df = student_submission.feature_engineering(sample_df.copy())
    df = student_submission.filter_and_analyze_data(df)

    math_failed = df[df['數學']<60]
    check("數學不及格人數", len(math_failed) == 2,
          msg=f"預期 2, 但得到 {len(math_failed)}")

    high_A = df[(df['班級']=='A') & (df['英文']>90)]
    check("A班英文>90人數", len(high_A) == 2,
          msg=f"預期 2, 但得到 {len(high_A)}")

    top_student = df.loc[df['總分'].idxmax()]
    check("總分最高學生是 Eva", top_student["姓名"] == "Eva",
          msg=f"預期 Eva, 但得到 {top_student['姓名']}")

def test_save_results(tmp_path, sample_df):
    df = student_submission.feature_engineering(sample_df.copy())
    output_file = tmp_path / "grades_test.csv"
    student_submission.save_results(df, output_file)

    check("CSV 檔案存在", output_file.exists())

    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    for col in ["總分","平均","是否及格"]:
        check(f"CSV 欄位存在: {col}", col in df_read.columns)

# -------------------------
# 最後將結果寫入 Markdown
# -------------------------
def test_generate_md():
    save_results_md("test_results/results.md")
