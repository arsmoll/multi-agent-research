"""
FastAPI 后端服务 — 多智能体协作研究系统
提供研究主题提交、进度流式推送和结果获取接口
"""
import json
import uuid
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.workflow.graph import run_research
from src.config import settings

app = FastAPI(title="多智能体研究系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 研究任务存储
research_tasks: dict[str, dict] = {}


class ResearchRequest(BaseModel):
    """研究请求"""
    topic: str


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "multi-agent-research"}


@app.post("/api/research")
async def create_research(req: ResearchRequest):
    """创建研究任务，返回任务 ID"""
    task_id = str(uuid.uuid4())[:8]
    research_tasks[task_id] = {
        "topic": req.topic,
        "status": "pending",
        "result": None,
    }

    # 后台启动研究流程
    asyncio.create_task(_run_research_task(task_id, req.topic))

    return {"task_id": task_id, "topic": req.topic, "status": "pending"}


@app.get("/api/research/{task_id}")
async def get_research(task_id: str):
    """获取研究任务结果"""
    task = research_tasks.get(task_id)
    if not task:
        return {"error": "任务不存在", "task_id": task_id}
    return task


@app.get("/api/research/stream/{task_id}")
async def stream_research(task_id: str):
    """SSE 流式推送研究进度"""
    async def event_stream():
        while True:
            task = research_tasks.get(task_id)
            if not task:
                yield f"data: {json.dumps({'error': '任务不存在'})}\n\n"
                break

            if task["status"] == "completed":
                yield f"data: {json.dumps({'status': 'completed', 'result': task['result']})}\n\n"
                break
            elif task["status"] == "failed":
                yield f"data: {json.dumps({'status': 'failed', 'error': task.get('error', '未知错误')})}\n\n"
                break

            yield f"data: {json.dumps({'status': task['status'], 'topic': task['topic']})}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


async def _run_research_task(task_id: str, topic: str):
    """后台执行研究任务"""
    task = research_tasks[task_id]
    try:
        task["status"] = "running"
        result = await run_research(topic)
        task["status"] = "completed"
        task["result"] = result
    except Exception as e:
        task["status"] = "failed"
        task["error"] = str(e)


def start_server():
    """启动服务"""
    import uvicorn
    uvicorn.run(
        app,
        host=settings.service.host,
        port=settings.service.port,
    )
