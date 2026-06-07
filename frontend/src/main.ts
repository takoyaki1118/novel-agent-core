// 設定データのマスター（本来は画面から編集可能にする）
const ASSETS_MASTER: Record<string, string> = {
    "アリス": "平民出身の魔術師。貧血気味、聖職者を激しく嫌悪している。",
    "司教": "大聖堂を統括する初老の男。強欲だが表向きは慈悲深い。",
    "魔法の等価交換": "この世界において、魔法の行使は等価交換であり、術者の血液を媒介とする。",
    "聖職者階級の規律": "聖職者階級に対しては、平民だけでなく貴族も不敬を働いてはならない。"
};

const generateBtn = document.getElementById('generate-btn') as HTMLButtonElement;
const logOutput = document.getElementById('log-output') as HTMLDivElement;

generateBtn.addEventListener('click', async () => {
    generateBtn.disabled = true;
    generateBtn.innerText = "⚡ 肉付け中（ローカルLLM推論中）...";
    
    // 1. 画面から選択されているアセットのキーを取得
    const checkedCheckboxes = document.querySelectorAll('#asset-manager input[type="checkbox"]:checked') as NodeListOf<HTMLInputElement>;
    const selected_assets: string[] = Array.from(checkedCheckboxes).map(cb => cb.value);

    // 2. リクエストペイロードの構築
    const payload = {
        global_goal: (document.getElementById('global-goal') as HTMLInputElement).value,
        current_chapter: (document.getElementById('current-chapter') as HTMLInputElement).value,
        immediate_instruction: (document.getElementById('immediate-instruction') as HTMLTextAreaElement).value,
        current_text: (document.getElementById('current-text') as HTMLTextAreaElement).value,
        selected_assets: selected_assets,
        assets: ASSETS_MASTER
    };

    appendLog("[API] パイプライン成形完了。Ollamaへ送信します。");

    try {
        // 3. Colab上で動いているFastAPIにリクエスト（同一ホスト想定なので相対パスでOK）
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error(await response.text());

        const data = await response.json();
        
        // 4. エディタのテキストエリアの末尾にAIの出力を追加
        const textEditor = document.getElementById('current-text') as HTMLTextAreaElement;
        textEditor.value += "\n" + data.generated_text;
        
        appendLog(`[SUCCESS] 新しい描写を肉付けしました（+${data.generated_text.length}文字）`);
    } catch (error) {
        appendLog(`[ERROR] 生成失敗: ${error}`);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerText = "✦ 次の展開を肉付け（生成）";
    }
});

function appendLog(message: string) {
    const p = document.createElement('p');
    p.innerText = message;
    logOutput.appendChild(p);
    logOutput.scrollTop = logOutput.scrollHeight;
}