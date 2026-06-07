# backend/core/pipeline.py
from typing import List, Dict

class ContextSynthesizer:
    @staticmethod
    def synthesize(
        global_goal: str,
        current_chapter: str,
        immediate_instruction: str,
        current_text: str,
        selected_assets: List[str],
        assets_master: Dict[str, str]
    ) -> str:
        """
        ユーザーの設定（アセット）とプロット（パイプライン）を調合し、
        ローカルLLMに最適化されたXML構造のプロンプトを生成する。
        """
        # 1. 有効化されたアセットの選別とテキスト化
        filtered_assets_str = ""
        for key in selected_assets:
            # キャラクターシート、または世界観設定から該当するものを抽出
            if key in assets_master:
                filtered_assets_str += f'<asset name="{key}">\n{assets_master[key]}\n</asset>\n'

        # 2. トップダウン型XMLプロンプトの成形
        prompt = f"""<system_instruction>
あなたはプロの小説家です。提示された[世界観・キャラクター設定]と[展開のノルマ]を絶対に遵守し、登場人物の行動や心理描写に矛盾がないように、次の展開を肉付けして記述してください。
余計な解説や「はい、分かりました」といった挨拶、メタ発言（XMLタグの出力など）は一切含めず、純粋な小説の本文（続きの文章）のみを出力してください。
</system_instruction>

<global_goal>
{global_goal}
</global_goal>

<current_plan>
【今章の目標】 {current_chapter}
【このシーンでのノルマ】 {immediate_instruction}
</current_plan>

<filtered_settings>
{filtered_assets_str}
</filtered_settings>

<current_text>
{current_text}
</current_text>
"""
        return prompt