"""
智能Agent接口 - DeepSeek API调用
优化版本：支持流式输出、更好的上下文管理
"""

from __future__ import annotations

import os
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx


router = APIRouter()


def load_config():
    """从.env加载配置"""
    from dotenv import load_dotenv

    load_dotenv()
    return {
        "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
        "api_url": os.getenv(
            "DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions"
        ),
    }


# 专家提示词
EEG_EXPERT_PROMPT = """你是一位**资深的脑机接口（BCI）研究专家**，专门从事运动想象脑电信号处理研究。

## 你的专业领域
1. **脑电信号采集与预处理**
   - 陷波滤波（50Hz去除工频干扰）
   - 带通滤波（8-30Hz提取Mu/Beta节律）
   - 基线校正、伪影去除、Z-score标准化

2. **特征提取与降维**
   - PCA主成分分析
   - CSP共空间模式
   - 线性判别分析LDA

3. **分类器设计**
   - Hopfield神经网络（联想记忆）
   - 支持向量机SVM
   - 卷积神经网络CNN
   - 深度学习模型

4. **运动想象生理学**
   - Mu节律（8-13Hz）与运动皮层激活
   - Beta节律（13-30Hz）与运动准备
   - ERD事件相关去同步
   - ERS事件相关同步

## 回答要求
- 使用**专业但易懂**的语言
- 适当引用脑电生理学概念
- 使用**Markdown格式**，关键术语加粗
- 结构清晰，分点说明
- 如果用户问代码问题，给出Python实现示例
- 结合**数学公式**解释算法原理"""


# 训练相关提示词
TRAINING_CONTEXT = """
当前训练状态：
- 被试: {subject}
- PCA维度: {pca_dims}
- 准确率: {accuracy}%
- 迭代次数: {iterations}
- 能量收敛值: {energy}

请基于以上训练结果进行分析和解释。
"""


class QARequest(BaseModel):
    question: str
    context: str | None = None
    stream: bool = False


class QAResponse(BaseModel):
    answer: str


async def generate_response(messages: list, config: dict):
    """流式生成响应 - SSE格式"""

    url = config["api_url"]

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            url,
            headers={
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "stream": True,
            },
        ) as response:
            async for chunk in response.aiter_lines():
                if chunk.startswith("data: "):
                    data = chunk[6:]
                    if data == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    try:
                        json_data = json.loads(data)
                        content = (
                            json_data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if content:
                            # 发送JSON格式，与OpenAI格式兼容
                            yield f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"
                    except:
                        pass


@router.post("/qa")
async def ask_question(request: QARequest):
    """问答接口 - 支持流式输出"""
    config = load_config()

    if not config["api_key"] or config["api_key"] == "sk-your-api-key-here":
        return {
            "answer": "请在 backend/.env 文件中配置 DEEPSEEK_API_KEY\n\n格式：DEEPSEEK_API_KEY=你的API密钥"
        }

    messages = [
        {"role": "system", "content": EEG_EXPERT_PROMPT},
    ]

    # 添加上下文
    if request.context:
        messages.append(
            {
                "role": "user",
                "content": f"参考当前训练数据：{request.context}\n\n请结合以上数据回答：{request.question}",
            }
        )
    else:
        messages.append({"role": "user", "content": request.question})

    # 流式响应 - 默认启用
    return StreamingResponse(
        generate_response(messages, config), media_type="text/event-stream"
    )


@router.post("/analyze")
async def analyze_training(request: QARequest):
    """分析训练结果"""
    config = load_config()

    if not config["api_key"]:
        return {"answer": "请配置API Key"}

    # 构建分析提示词
    analysis_prompt = f"""作为脑电信号处理专家，请分析以下Hopfield神经网络训练结果：

{request.context or "无训练数据"}

请从以下角度分析：
1. **分类准确率**是否合理？影响因素有哪些？
2. **能量收敛值**反映什么？
3. 如何**优化网络性能**？
4. 与其他方法（SVM、CNN）对比有什么优势？

使用Markdown格式，结构化输出。"""

    messages = [
        {"role": "system", "content": EEG_EXPERT_PROMPT},
        {"role": "user", "content": analysis_prompt},
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                config["api_url"],
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.5,
                },
            )

            result = response.json()
            return {"answer": result["choices"][0]["message"]["content"]}

    except Exception as e:
        return {"answer": f"分析出错: {str(e)}"}


@router.post("/explain-algorithm")
async def explain_algorithm(request: QARequest):
    """解释特定算法"""
    config = load_config()

    algorithm_explainer = """你是一位善于教学的AI教授，请用通俗易懂的方式解释以下概念：

要求：
1. 先用一句话概括
2. 逐步深入细节
3. 结合实际例子
4. 如有数学公式，用LaTeX格式
5. 最后总结关键点"""

    messages = [
        {"role": "system", "content": algorithm_explainer},
        {"role": "user", "content": request.question},
    ]

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                config["api_url"],
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                },
            )

            result = response.json()
            return {"answer": result["choices"][0]["message"]["content"]}

    except Exception as e:
        return {"answer": f"解释出错: {str(e)}"}
