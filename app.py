import streamlit as st
from groq import Groq
import base64
from datetime import datetime
import re

# パスワード認証
if "authenticated" not in st.session_state:
    st.title("💼 Google Business Profile 規約違反チェックアプリ")
    password = st.text_input("🔒 パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

st.set_page_config(page_title="GBPチェックアプリ", page_icon="💼", layout="centered")

st.title("💼 Google Business Profile 規約違反チェックアプリ")
st.markdown("**Diamond〜Bronze Product Expertの全知見を活かした精密診断**")

try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("Groqキーを設定してください")
    st.stop()

client = Groq(api_key=groq_key)

uploaded_files = st.file_uploader("📸 GBPページのスクリーンショットをアップロード（複数OK）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
text_info = st.text_area("テキスト情報（任意・精度UP）", height=150)

if st.button("🚀 店舗名を自動抽出して診断を開始", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("スクショをアップロードしてください")
        st.stop()

    with st.spinner("スクショから店舗名を自動抽出中..."):
        ocr_messages = [{"role": "user", "content": [{"type": "text", "text": "この画像はGoogle Business Profileのスクショです。店舗名、住所、カテゴリを正確に抽出して教えてください。店舗名を最優先で。"}]}]
        for file in uploaded_files:
            bytes_data = file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            ext = file.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            ocr_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}})

        ocr_completion = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=ocr_messages, max_tokens=300, temperature=0.1)
        store_info = ocr_completion.choices[0].message.content

    st.success("✅ 店舗名を自動抽出しました")
    st.info(f"**抽出された店舗情報**\n{store_info}")

    with st.spinner("精密分析中..."):
        system_prompt = f"""あなたはGoogle Business Profile公式Product Experts Programの全階層の知見を総合した最高位の専門家です。

このスクショは以下の店舗のGBPです：
{store_info}

**厳格ルール（絶対遵守）**：
- レビューや評価を金銭・割引・ポイント・景品・特典などで誘導する行為は一切提案しない。
- 「クチコミキャンペーン」「レビュー投稿のお願いキャンペーン」など、Googleガイドラインで禁止されている施策は絶対に出さない。
- 提案する施策に**関連する可能性のあるルール違反**があれば、必ず事前に注意喚起を入れる（例：「利益供与に該当する恐れがあるため、代わりに以下の合法的な方法をおすすめします」）。

出力形式（必ずこの順番で）：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 全国および近隣同業種の成功事例に基づく先進施策（非常に詳細に・合法的なもののみ。各施策にリスクがあれば事前注意喚起を必ず入れる）

最後に必ず免責事項を入れてください。"""

        messages = [{"role": "system", "content": system_prompt}]
        if text_info.strip():
            messages.append({"role": "user", "content": f"追加情報:\n{text_info}"})

        for file in uploaded_files:
            bytes_data = file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            ext = file.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            messages.append({"role": "user", "content": [
                {"type": "text", "text": f"画像：{file.name}"},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}}]
            })

        chat_completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=messages,
            max_tokens=2800,
            temperature=0.3
        )
        result = chat_completion.choices[0].message.content

    # スコア大きく表示
    score_match = re.search(r'総合スコア[:：]\s*(\d{1,3})/100', result)
    if score_match:
        score = int(score_match.group(1))
        color = "#22c55e" if score >= 90 else "#3b82f6" if score >= 80 else "#f59e0b" if score >= 70 else "#ef4444"
        emoji = "🏆" if score >= 90 else "🌟" if score >= 80 else "👍" if score >= 70 else "⚠️"
        st.markdown(f'<div style="text-align:center; padding:40px; background:#1e2937; border-radius:20px; margin:25px 0;"><h1 style="font-size:6rem; color:{color}; margin:0;">{emoji} {score}/100点</h1><p style="font-size:1.8rem; color:#e2e8f0;">この店舗のGBP総合評価</p></div>', unsafe_allow_html=True)

    st.success("✅ 診断完了！")
    st.markdown(result)

    today = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="📄 診断結果をダウンロード（HTML形式・印刷してPDF保存してください）",
        data=result,
        file_name=f"GBP診断結果_{today}.html",
        mime="text/html"
    )

st.caption("💼 Powered by 全Product Expert知見 | 04.sampleapp.work")
