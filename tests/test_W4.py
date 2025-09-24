# -*- coding: utf-8 -*-
import pytest
import pandas as pd
import importlib.util
from pathlib import Path
import os
import re

# -------------------------
# 取得學生提交程式
# -------------------------
SUBMIT_DIR = Path(__file__).parent / "submit"
student_files = list(SUBMIT_DIR.glob("*.py"))
if not student_files:
    raise FileNotFoundError(f"{SUBMIT_DIR} 沒有學生提交檔案")

student_file = student_files[0]
spec = importlib.util.spec_from_file_location("student_submission", student_file)
student_submission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(student_submission)

# -------------------------
# 測資 DataFrame
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
# 工具函式：記錄測試結果
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
    "summary 含數學欄位": 5,
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
    
    alice = df[df["姓名"] == "Alice"].iloc[0] if "Alice" in df["姓名"].values else None
    david = df[df["姓名"] == "David"].iloc[0] if "David" in df["姓名"].values else None

    # 總分、平均、及格檢查
    expected_total = 95+88+78+90+85
    check("總分正確", df is not None and "總分" in df.columns and alice is not None and alice["總分"] == expected_total,
          msg=f"Alice 總分預期 {expected_total}, 得到 {alice['總分'] if alice is not None else 'None'}")
    check("平均正確", df is not None and "平均" in df.columns and alice is not None and pytest.approx(alice["平均"]) == expected_total/5,
          msg=f"Alice 平均預期 {expected_total/5}, 得到 {alice['平均'] if alice is not None else 'None'}")
    check("David 是否不及格", df is not None and "是否及格" in df.columns and david is not None and david["是否及格"] is False)
    check("Alice 是否及格", df is not None and "是否及格" in df.columns and alice is not None and alice["是否及格"] is True)

def test_filter_and_analyze_data(sample_df):
    df = student_submission.feature_engineering(sample_df.copy())
    result = student_submission.filter_and_analyze_data(df)

    # 確保回傳 dict
    assert isinstance(result, dict), "filter_and_analyze_data 必須回傳 dict"

    math_failed = result.get("math_failed")
    check("數學不及格人數", math_failed is not None and len(math_failed) == 2,
          msg=f"預期 2, 得到 {len(math_failed) if math_failed is not None else 'None'}")

    high_A = result.get("high_A")
    check("A班英文>90人數", high_A is not None and len(high_A) == 2,
          msg=f"預期 2, 得到 {len(high_A) if high_A is not None else 'None'}")

    top_student = result.get("top_student")
    name_top = top_student.iloc[0]["姓名"] if top_student is not None and not top_student.empty else None
    check("總分最高學生是 Eva", name_top == "Eva",
          msg=f"預期 Eva, 得到 {name_top}")

    summary = result.get("summary")
    check("summary 含數學欄位", summary is not None and "數學" in summary.columns if summary is not None else False)

def test_save_results(tmp_path, sample_df):
    df = student_submission.feature_engineering(sample_df.copy())
    result = student_submission.filter_and_analyze_data(df)
    output_file = tmp_path / "grades_test.csv"
    student_submission.save_results(result["processed_df"], output_file)

    check("CSV 檔案存在", output_file.exists())
    if output_file.exists():
        df_read = pd.read_csv(output_file, encoding='utf-8-sig')
        for col in ["總分","平均","是否及格"]:
            check(f"CSV 欄位存在: {col}", col in df_read.columns)

def test_generate_md():
    save_results_md("test_results/results.md")
