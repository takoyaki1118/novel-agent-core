import os
from pydantic import BaseModel
from typing import List, Dict
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json

from core.ollama import OllamaManager
from core.pipeline import NovelPipeline

app = FastAPI(title="NovelAgent-Core API")

# CORS設定（手元からのクロスドメイン接続を許容）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_manager = OllamaManager()
pipeline = NovelPipeline()

class NovelRequest(BaseModel):
    global_goal: str
    current_chapter: str
    immediate_instruction: str
    current_text: str
    selected_assets: List[str]
    assets: Dict[str, str]

@app.on_event("startup")
def startup_event():
    print("[SYSTEM] 起動プロセスを開始...")
    ollama_manager.check_and_setup()
    print("[SYSTEM] 起動完了。Ollama準備OK。")

@app.post("/api/generate")
async def generate_novel(request: NovelRequest):
    # パイプラインを介してプロンプト（指示書）をビルド
    prompt = pipeline.build_prompt(
        global_goal=request.global_goal,
        current_chapter=request.current_chapter,
        immediate_instruction=request.immediate_instruction,
        current_text=request.current_text,
        selected_assets=request.selected_assets,
        assets=request.assets
    )

    # 1トークンずつ即座にブラウザへ配信するジェネレータ
    def generate_stream():
        try:
            # stream=True を指定してOllamaのストリーミングを有効化
            response_stream = ollama_manager.generate_stream(prompt)
            for chunk in response_stream:
                # 行単位のJSON（NDJSON形式）で出力
                yield json.dumps({"text": chunk["response"]}, ensure_ascii=False) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}, ensure_ascii=False) + "\n"

    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")

# 静的ファイルの配信（エディタ画面のHTML/CSS/JSを配信）
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")