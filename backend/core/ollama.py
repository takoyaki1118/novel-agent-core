# backend/core/ollama.py
import os
import subprocess
import time
import requests
import ollama

class OllamaManager:
    def __init__(self, model_name: str = "gemma4-novel"):
        self.model_name = model_name
        self.gguf_url = "https://huggingface.co/HauhauCS/Gemma4-26B-A4B-Uncensored-HauhauCS-Balanced/resolve/main/Gemma4-26B-A4B-Uncensored-HauhauCS-Balanced-Q2_K_P.gguf"
        self.gguf_path = "/content/Gemma4-26B-A4B-Uncensored-HauhauCS-Balanced-Q2_K_P.gguf"

    def check_and_setup(self):
        """Colab環境でOllamaの起動確認とGGUFモデルのセットアップを行う"""
        print("[Ollama] サーバーの応答を確認中...")
        for _ in range(15):
            try:
                requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
                print("[Ollama] サーバーとの接続に成功しました。")
                break
            except:
                time.sleep(2)

        if not os.path.exists(self.gguf_path):
            print(f"[Ollama] GGUFモデルをダウンロード中... (高速URL: {self.gguf_url})")
            subprocess.run(["wget", "-O", self.gguf_path, self.gguf_url], check=True)

        # 最も確実かつ、ライブラリのバージョン変更に強い「コマンドライン経由」でModelfileをインポートします
        modelfile_content = f"""
FROM {self.gguf_path}
TEMPLATE \"\"\"{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
{{..end}}}}<|im_start|>assistant
{{{{ .Response }}}}<|im_end|>\"\"\"
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
"""
        with open("/content/Modelfile_temp", "w") as f:
            f.write(modelfile_content)

        print(f"[Ollama] カスタムモデル '{self.model_name}' を登録中...")
        # ライブラリのバグを回避するため、確実な subprocess 呼び出しに切り替え
        subprocess.run(["ollama", "create", self.model_name, "-f", "/content/Modelfile_temp"], check=True)
        print(f"[Ollama] '{self.model_name}' のインポートが完了しました。")

    def generate(self, prompt: str) -> str:
        try:
            response = ollama.generate(model=self.model_name, prompt=prompt)
            return response['response']
        except Exception as e:
            print(f"[Ollama] 生成エラー: {e}")
            raise e