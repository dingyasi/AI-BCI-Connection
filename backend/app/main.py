"""
EEG脑电信号识别系统 - FastAPI后端
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent import router as agent_router
from app.api.train import router as train_router


# 加载.env配置
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(
    title="EEG Neural Interface",
    version="1.0.0",
    description="基于Hopfield网络的脑电信号识别系统",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(agent_router, prefix="/api/v1/agent", tags=["智能Agent"])
app.include_router(train_router, prefix="/api/v1/train", tags=["训练"])


@app.get("/")
async def root():
    return {
        "code": 200,
        "msg": "EEG Neural Interface Online",
        "data": {"version": "1.0.0"},
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
