# backend/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict

# 自作コアモジュールのインポート
from core.pipeline import ContextSynthesizer
from core.ollama import OllamaManager

app = FastAPI(title="NovelAgent Core Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ollama_manager = OllamaManager()

# 起動時に自動でGGUFの配置とインポートを走らせる
@app.on_event("startup")
def startup_event():
    if os.path.exists("/content"):  # Colab環境でのみ実行
        ollama_manager.check_and_setup()

class NovelState(BaseModel):
    global_goal: str
    current_chapter: str
    immediate_instruction: str
    current_text: str
    selected_assets: List[str]
    assets: Dict[str, str]

@app.post("/api/generate")
async def generate_next_text(state: NovelState):
    # 1. パイプラインを走らせてXMLプロンプトを成形
    prompt = ContextSynthesizer.synthesize(
        global_goal=state.global_goal,
        current_chapter=state.current_chapter,
        immediate_instruction=state.immediate_instruction,
        current_text=state.current_text,
        selected_assets=state.selected_assets,
        assets_master=state.assets
    )

    # 2. Ollamaで推論実行
    try:
        ai_output = ollama_manager.generate(prompt)
        return {"generated_text": ai_output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成エラー: {str(e)}")

# フロントの成果物（HTML等）を配信する設定
if os.path.exists("./static"):
    app.mount("/", StaticFiles(directory="./static", html=True), name="static")