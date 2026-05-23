import os
import json
import re
from datetime import datetime

LOG_FILE = "analysis_results.json"
ANALYSIS_LOG_FILE = "analysis_history.json"


def load_analysis_history():
    if not os.path.exists(ANALYSIS_LOG_FILE):
        return {
            "records": [],
            "summary": {"total": 0, "high_match": 0, "medium_match": 0, "low_match": 0},
        }

    try:
        with open(ANALYSIS_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "records": [],
            "summary": {"total": 0, "high_match": 0, "medium_match": 0, "low_match": 0},
        }


def save_analysis_record(record):
    history = load_analysis_history()
    history["records"].append(record)
    history["summary"]["total"] += 1

    score = record.get("score", 0)
    if score >= 78:
        history["summary"]["high_match"] += 1
    elif score >= 60:
        history["summary"]["medium_match"] += 1
    else:
        history["summary"]["low_match"] += 1

    with open(ANALYSIS_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return history


def clean_jd_text(raw_text):
    """对提取到的JD文本进行清洗和结构化"""
    if not raw_text:
        return None

    lines = raw_text.split('\n')
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) < 3:
            continue
        cleaned_lines.append(stripped)

    return '\n'.join(cleaned_lines)


def extract_jd_sections(jd_text):
    """从JD文本中提取核心段落（岗位职责、任职要求等）"""
    if not jd_text:
        return None

    keywords = [
        '岗位描述', '职位描述', '岗位职责', '岗位要求',
        '任职要求', '工作职责', '工作内容', '职责描述',
        '岗位介绍', '职位介绍', '我们需要你', '我们希望你',
    ]

    lines = jd_text.split('\n')
    jd_sections = []
    in_jd_section = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if any(kw in stripped for kw in keywords):
            in_jd_section = True
        if in_jd_section:
            jd_sections.append(stripped)

    if jd_sections and len(''.join(jd_sections)) > 50:
        return '\n'.join(jd_sections)

    return jd_text


def analyze_job_description(jd_text, resume_text, user_background=None):
    """分析JD文本：评分匹配度 + 生成求职信"""
    from langchain_functions import should_apply, generate_letter

    cleaned_jd = clean_jd_text(jd_text)
    if not cleaned_jd:
        return {"error": "JD文本为空或无效"}

    structured_jd = extract_jd_sections(cleaned_jd)

    score_result = should_apply(resume_text, structured_jd, user_background)
    if not score_result:
        score_result = {"score": 0, "reason": "分析失败"}

    letter = None
    if score_result.get("score", 0) >= 60:
        letter = generate_letter(resume_text, structured_jd)

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jd_length": len(jd_text),
        "score": score_result.get("score", 0),
        "reason": score_result.get("reason", ""),
        "has_letter": letter is not None,
    }
    save_analysis_record(record)

    return {
        "score": score_result.get("score", 0),
        "reason": score_result.get("reason", ""),
        "letter": letter,
        "jd_cleaned_length": len(cleaned_jd),
    }


def batch_analyze_jds(jd_list, resume_text, user_background=None):
    """批量分析多段JD文本"""
    results = []
    for i, jd in enumerate(jd_list):
        result = analyze_job_description(jd, resume_text, user_background)
        result["index"] = i + 1
        results.append(result)
    return results


def format_analysis_result(result):
    """格式化分析结果为可读文本"""
    score = result.get("score", 0)
    reason = result.get("reason", "无分析理由")
    letter = result.get("letter")

    tier = "未匹配"
    if score >= 90:
        tier = "第一梯队（优先推荐）"
    elif score >= 78:
        tier = "第二梯队（推荐）"
    elif score >= 70:
        tier = "第三梯队（可投）"
    elif score >= 60:
        tier = "第四梯队（酌情）"
    elif score > 0:
        tier = "低匹配度"

    output = []
    output.append("=" * 60)
    output.append(f"📊 匹配度评分: {score}/100")
    output.append(f"📋 匹配梯队: {tier}")
    output.append(f"💭 分析理由: {reason}")
    output.append("=" * 60)

    if letter:
        output.append("\n📝 生成的求职信:")
        output.append("-" * 40)
        output.append(letter)
        output.append("-" * 40)
    else:
        output.append("\n❌ 匹配度不足60分，未生成求职信")

    return '\n'.join(output)