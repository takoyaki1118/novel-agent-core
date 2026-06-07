# backend/core/pipeline.py （完全上書き用）
from typing import List, Dict

class NovelPipeline:
    def __init__(self):
        pass

    def build_prompt(
        self,
        global_goal: str,
        current_chapter: str,
        immediate_instruction: str,
        current_text: str,
        selected_assets: List[str],
        assets: Dict[str, str]
    ) -> str:
        """フロントエンドから受け取った情報を元に、Ollama(Gemma4)向けのプロンプトを構築する"""
        
        # 選択された設定（アセット）のテキストを抽出
        asset_context = ""
        if selected_assets:
            asset_context = "\n【採用する設定・世界観】\n"
            for asset_name in selected_assets:
                if asset_name in assets:
                    asset_context += f"- {asset_name}: {assets[asset_name]}\n"

        # プロンプト（指示書）の組み立て
        prompt = f"""以下の設定および執筆指示に従い、小説の続き、または指定された描写の肉付けを執筆してください。

【作品の全体目標・着地点】
{global_goal}

【現在の章の目標・あらすじ】
{current_chapter}
{asset_context}
【現在の本文（この続きを執筆、または修正してください）】
\"\"\"
{current_text}
\"\"\"

【今すぐ行う執筆指示】
{immediate_instruction}

それでは、上記の指示を完全に反映し、前後の文脈やキャラクターの設定を崩さないよう、臨場感のある地の文とセリフで小説を書き進めてください。"""
        
        return prompt