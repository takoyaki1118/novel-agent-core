// backend/static/main.js
const ASSETS_MASTER = {
    "アリス": "平民出身の魔術師。貧血気味、聖職者を激しく嫌悪している。",
    "司教": "大聖堂を統括する初老の男。強欲だが表向きは慈悲古い。",
    "魔法の等価交換": "この世界において、魔法の行使は等価交換であり、術者の血液を媒介とする。",
    "聖職者階級の規律": "聖職者階級に対しては、平民だけでなく貴族も不敬を働いてはならない。"
};

const generateBtn = document.getElementById('generate-btn');
const logOutput = document.getElementById('log-output');

generateBtn.addEventListener('click', async () => {
    generateBtn.disabled = true;
    generateBtn.innerText = "⚡ 思考中（ファーストトークン待機）...";
    
    const checkedCheckboxes = document.querySelectorAll('#asset-manager input[type="checkbox"]:checked');
    const selected_assets = Array.from(checkedCheckboxes).map(cb => cb.value);

    const payload = {
        global_goal: document.getElementById('global-goal').value,
        current_chapter: document.getElementById('current-chapter').value,
        immediate_instruction: document.getElementById('immediate-instruction').value,
        current_text: document.getElementById('current-text').value,
        selected_assets: selected_assets,
        assets: ASSETS_MASTER
    };

    appendLog("[API] パイプライン成形完了。Ollamaへ送信します。");

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(await response.text());

        // ストリーミングデータを逐次処理するためのリーダーを確立
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const textEditor = document.getElementById('current-text');
        
        let buffer = "";
        textEditor.value += "\n"; // 生成テキストの前に改行を入れる
        
        appendLog("[STREAM] 接続確立。執筆をリアルタイムで同期中...");

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            // バッファにデータを追加し、改行コードで1行ずつパース
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop(); // 未完成の最後の1行を退避
            
            for (const line of lines) {
                if (line.trim() === "") continue;
                try {
                    const parsed = JSON.parse(line);
                    if (parsed.error) {
                        appendLog(`[ERROR] AI生成中にエラー: ${parsed.error}`);
                        continue;
                    }
                    // テキストエリアにリアルタイムで追記してスクロール
                    textEditor.value += parsed.text;
                    textEditor.scrollTop = textEditor.scrollHeight;
                    generateBtn.innerText = "✦ カタカタと肉付け中...";
                } catch (e) {
                    console.error("JSONパースエラー:", e);
                }
            }
        }
        appendLog(`[SUCCESS] 肉付け完了。`);
    } catch (error) {
        appendLog(`[ERROR] 生成通信失敗: ${error}`);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerText = "✦ 次の展開を肉付け（生成）";
    }
});

function appendLog(message) {
    const p = document.createElement('p');
    p.innerText = message;
    logOutput.appendChild(p);
    logOutput.scrollTop = logOutput.scrollHeight;
}