import streamlit as st
from groq import Groq
import base64
from datetime import datetime

st.set_page_config(page_title="GBPチェックアプリ", page_icon="💼", layout="centered")

st.title("💼 Google Business Profile 規約違反チェックアプリ")
st.markdown("**Diamond〜Bronze Product Expertの全知見を活かした精密診断**")

try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("Groqキーを設定してください")
    st.stop()

client = Groq(api_key=groq_key)

uploaded_files = st.file_uploader(
    "📸 GBPページのスクリーンショットをアップロード（複数OK）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

text_info = st.text_area("テキスト情報（任意・精度UP）", height=150)

if st.button("🚀 店舗名を自動抽出して診断を開始", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("スクショをアップロードしてください")
        st.stop()

    with st.spinner("スクショから店舗名を自動抽出中..."):
        # OCRで店舗情報抽出
        ocr_messages = [{"role": "user", "content": [{"type": "text", "text": "この画像はGoogle Business Profileのスクショです。店舗名、住所、カテゴリを正確に抽出して教えてください。店舗名を最優先で。"}]}]
        for file in uploaded_files:
            bytes_data = file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            ext = file.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            ocr_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}})

        ocr_completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=ocr_messages,
            max_tokens=300,
            temperature=0.1
        )
        store_info = ocr_completion.choices[0].message.content

    st.success("✅ 店舗名を自動抽出しました")
    st.info(f"**抽出された店舗情報**\n{store_info}")

    # 自動で本診断を実行（ネストを解消）
    with st.spinner("この店舗のGBPとして、Diamond Product Expertレベルの知見で精密分析中..."):
        system_prompt = f"""あなたはGoogle Business Profile公式Product Experts Programの全階層（Diamond, Platinum, Gold, Silver, Bronze）の知見を総合した最高位の専門家です。

このスクショは以下の店舗のGBPです：
{store_info}

この特定の店舗の実際のGBPとして、スクショの内容を正確に分析してください。

出力形式：
1. 規約違反チェック（危険度：高/中/低 + 該当ルール引用）
2. 即修正できる具体的な改善案（コピペOKの文例付き）
3. 改善優先順位トップ3
4. Diamond〜Bronze Product Expertが実際にやっている追加施策

最後に必ず「これは参考情報です。最終判断はGoogle公式ツールで確認してください。」を入れてください。"""

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
            max_tokens=2000,
            temperature=0.3
        )
        result = chat_completion.choices[0].message.content

    st.success("✅ 診断完了！この店舗のGBPをしっかり考慮した結果です")
    st.markdown(result)

    today = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="📄 診断結果をダウンロード（PDF保存も簡単）",
        data=result,
        file_name=f"GBPチェック_{today}.md",
        mime="text/markdown"
    )

st.caption("💼 Powered by 全Product Expert知見 | 04.sampleapp.work")
