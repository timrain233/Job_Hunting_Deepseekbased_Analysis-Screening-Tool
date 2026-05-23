import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from langchain_functions import read_resumes, build_scoring_prompt
from jd_analyzer import analyze_job_description, format_analysis_result, load_analysis_history


SAMPLE_JD = """岗位：电商运营助理（实习）

【岗位职责】
1. 协助店铺日常运营管理，包括商品上下架、活动报名等
2. 负责店铺数据监控与分析，输出日/周报
3. 协助制定运营策略，优化商品展示和转化率
4. 参与平台活动策划与执行，完成活动复盘报告

【任职要求】
1. 本科及以上学历，专业不限
2. 熟练使用Excel等办公软件，具备基础数据分析能力
3. 良好的沟通协调能力和团队合作精神
4. 有电商实习经验者优先

【加分项】
- 有数据分析工具使用经验（Python/SQL等）
- 了解电商平台规则和运营逻辑"""


def get_user_background():
    return {
        "education": "985本科 + 211硕士（在读）",
        "experience": "数据分析、指标把控、需求落地、预测类项目经验",
        "target": "转行互联网运营，专业不限，希望从事数据驱动型运营岗位",
    }


def interactive_mode(resume_text):
    user_bg = get_user_background()

    print("\n📋 当前简历背景配置（可在 langchain_functions.py 中修改）：")
    print(f"   学历：{user_bg['education']}")
    print(f"   经历：{user_bg['experience']}")
    print(f"   目标：{user_bg['target']}")

    while True:
        print("\n" + "=" * 60)
        print("请选择输入方式：")
        print("1. 手动粘贴职位描述（JD）文本")
        print("2. 使用内置示例JD进行分析")
        print("3. 从文件读取JD文本")
        print("4. 查看历史分析记录")
        print("5. 退出")
        print("=" * 60)

        choice = input("\n请输入选项 (1-5): ").strip()

        if choice == "1":
            print("\n请粘贴职位描述文本（输入完成后，在新行输入 'END' 结束）：")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            jd_text = '\n'.join(lines)

            if not jd_text.strip():
                print("❌ 未输入任何内容")
                continue

        elif choice == "2":
            jd_text = SAMPLE_JD
            print(f"\n📄 使用示例JD：\n{jd_text[:200]}...")

        elif choice == "3":
            file_path = input("请输入JD文件路径: ").strip()
            if not os.path.exists(file_path):
                print(f"❌ 文件不存在: {file_path}")
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    jd_text = f.read()
                print(f"✅ 已读取文件，长度: {len(jd_text)} 字")
            except Exception as e:
                print(f"❌ 读取文件失败: {e}")
                continue

        elif choice == "4":
            history = load_analysis_history()
            records = history.get("records", [])
            summary = history.get("summary", {})
            print(f"\n📊 分析统计：共 {summary.get('total', 0)} 次分析")
            print(f"   高匹配（≥78分）: {summary.get('high_match', 0)} 次")
            print(f"   中匹配（60-77分）: {summary.get('medium_match', 0)} 次")
            print(f"   低匹配（<60分）: {summary.get('low_match', 0)} 次")
            if records:
                print(f"\n最近5条记录：")
                for r in records[-5:]:
                    print(f"   [{r.get('timestamp', '')}] 评分: {r.get('score', 0)} | {r.get('reason', '')[:60]}")
            continue

        elif choice == "5":
            print("\n感谢使用！")
            break

        else:
            print("❌ 无效选项")
            continue

        print("\n🧠 正在分析岗位匹配度...")
        try:
            result = analyze_job_description(jd_text, resume_text, user_bg)
            output = format_analysis_result(result)
            print(output)
        except Exception as e:
            print(f"\n❌ 分析过程出错: {e}")
            import traceback
            traceback.print_exc()

        input("\n按回车继续...")


def main():
    print("=" * 60)
    print("🚀 求职岗位智能分析系统 v2.0（开源学习版）")
    print("📌 本项目仅用于：岗位文本分析 + AI匹配度评估")
    print("📌 不包含任何自动化投递或平台批量操作功能")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
            if not os.getenv("OPENAI_API_KEY"):
                print("\n⚠️  未配置 API Key")
                print("请将 .env.example 复制为 .env 并填入你的 DeepSeek API Key")
                return
        else:
            print("\n⚠️  未找到 .env 配置文件")
            print("请将 .env.example 复制为 .env 并填入你的 DeepSeek API Key")
            return

    print("\n📄 正在读取简历...")
    resume_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume")
    resume_text = read_resumes(resume_dir)

    if not resume_text:
        print("⚠️  resume 目录中未找到 PDF 简历文件")
        print("请将你的 PDF 简历放入 auto_job_analysis/resume/ 目录后重试")
        print("\n继续使用示例模式（无需简历也能演示评分规则）...")
        resume_text = "【示例简历】985本科+211硕士，数据分析、项目实操经验丰富，目标转行互联网运营。"

    print("✅ 就绪！")
    interactive_mode(resume_text)


if __name__ == "__main__":
    main()