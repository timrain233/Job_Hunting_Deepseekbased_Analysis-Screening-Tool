from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_openai import ChatOpenAI
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')


def should_use_langchain():
    return True


def read_resumes(resume_dir="./resume"):
    d_loader = DirectoryLoader(resume_dir, glob="*.pdf", loader_cls=PyPDFLoader)
    pdf_pages = d_loader.load()

    resume_text = ""
    for page in pdf_pages:
        page_text = page.page_content
        resume_text += page_text

    return resume_text


def build_scoring_prompt(resume_text, job_description, user_background=None):
    if user_background is None:
        user_background = {
            "education": "请在此填写您的学历背景（例如：985本科 + 211硕士）",
            "experience": "请在此填写您的核心经历与技能（例如：数据分析、项目管理）",
            "target": "请在此填写您的目标岗位方向（例如：转行运营，专业不限）",
        }

    prompt = f"""
你是一个专业的HR招聘助手，负责判断求职者的简历与岗位是否匹配。

求职者背景：
- 学历：{user_background.get('education', '待填写')}
- 经历：{user_background.get('experience', '待填写')}
- 目标：{user_background.get('target', '待填写')}

## 简历内容：
{resume_text}

## 岗位描述：
{job_description}

## 评分规则（严格执行各梯队分数范围）：

第一梯队 90-100分（优先推荐）：运营助理、电商运营、店铺运营、数据运营、运营数据分析、策略运营、增长运营
第二梯队 78-88分（推荐）：用户运营、内容运营
第三梯队 70-77分（可投）：运营专员、互联网运营、市场运营、活动运营（跨专业友好，适合实习转正）
第四梯队 60-68分（酌情）：新媒体运营
0分（跳过）：岗位要求与求职者专业背景完全不匹配

加分项（每项提升匹配度）：985/211学历背景、数据分析能力、项目实操经验
减分项：岗位明确要求不匹配的专业背景

## 输出要求：
请严格按照以下JSON格式返回，不要添加任何额外内容：
{{
    "score": 0-100之间的整数（严格按评分规则给出的匹配度分数）,
    "reason": "匹配梯队+核心匹配点/不匹配原因"
}}

注意：只输出JSON，不要包含任何其他文字。
"""
    return prompt


def should_apply(resume_text, job_description, user_background=None):
    prompt = build_scoring_prompt(resume_text, job_description, user_background)

    llm = ChatOpenAI(
        temperature=0.3,
        model_name="deepseek-chat",
        openai_api_base=OPENAI_BASE_URL,
        openai_api_key=OPENAI_API_KEY,
    )

    try:
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        return {
            "score": 0,
            "reason": f"API调用失败: {str(e)}",
        }

    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {
                "score": 0,
                "reason": "无法解析判断结果",
            }
    except Exception as e:
        return {
            "score": 0,
            "reason": f"解析错误: {str(e)}",
        }


def generate_letter(resume_text, job_description, character_limit=300):
    prompt = f"""
你将扮演一位求职者的角色，根据简历内容和岗位描述来写一封专业的求职消息。

## 简历内容：
{resume_text}

## 岗位描述：
{job_description}

要求：
1. 字数严格限制在{character_limit}字以内
2. 用专业的语言结合简历中的经历和技能
3. 阐述自己的优势，尽最大可能打动招聘者
4. 始终使用中文
5. 开头写"招聘负责人您好"
6. 结尾附上求职者的联系方式
7. 不要包含求职内容以外的东西，如"根据您上传的求职要求和个人简历，我来帮您起草一封求职邮件"这类内容

直接输出求职消息内容，不要添加任何额外说明。
"""

    llm = ChatOpenAI(
        temperature=0.7,
        model_name="deepseek-chat",
        openai_api_base=OPENAI_BASE_URL,
        openai_api_key=OPENAI_API_KEY,
    )

    try:
        response = llm.invoke(prompt)
        letter = response.content if hasattr(response, 'content') else str(response)
        letter = letter.replace('\n', ' ')
        return letter
    except Exception as e:
        return f"生成求职信失败: {str(e)}"