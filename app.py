import streamlit as st
from groq import Groq
import base64
from datetime import datetime
import re

# パスワード認証
if "authenticated" not in st.session_state:
    st.title("💼 GBPチェックアプリ")
    pw = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if pw == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

st.set_page_config(page_title="GBPチェックアプリ", page_icon="💼", layout="centered")
st.title("💼 Google Business Profile 規約違反チェックアプリ")
st.markdown("**スクショから高精度で店舗を判断して精密診断**")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

uploaded_files = st.file_uploader("📸 GBPスクショをアップロード（複数OK）", type=["jpg","jpeg","png"], accept_multiple_files=True)
text_info = st.text_area("追加テキスト情報（任意）", height=120)

if st.button("🚀 スクショから店舗を判断して診断開始", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("スクショをアップロードしてください")
        st.stop()

    # 高精度OCR（2段階で精度を最大限上げる）
    with st.spinner("スクショから店舗情報を高精度で抽出中..."):
        ocr_prompt = """この画像はGoogle Business Profileのスクリーンショットです。
以下の情報を**できるだけ正確に**抽出してください。
- 店舗名（最も重要）
- 住所（完全な住所を優先）
- カテゴリ
- 電話番号（あれば）
- ウェブサイト（あれば）

形式：
店舗名: 
住所: 
カテゴリ: 
電話: 
ウェブサイト: """

        ocr_messages = [{"role": "user", "content": [{"type": "text", "text": ocr_prompt}]}]
        for file in uploaded_files:
            b64 = base64.b64encode(file.getvalue()).decode()
            ext = file.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            ocr_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})

        ocr_res = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=ocr_messages,
            max_tokens=400,
            temperature=0.0
        )
        store_info = ocr_res.choices[0].message.content

    st.success("✅ 店舗情報を高精度で抽出しました")
    st.info(store_info)

    # 診断
    with st.spinner("抽出情報をもとに精密診断中..."):
        system_prompt = f"""あなたはGBPの最高位専門家です。

このスクショは以下の店舗のGBPです：
{store_info}

この店舗のGBPとして、スクショの内容を正確に分析してください。

出力形式：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 先進施策（合法的なもののみ）

最後に必ず免責事項を入れてください。"""

        messages = [{"role": "system", "content": system_prompt}]
        if text_info.strip():
            messages.append({"role": "user", "content": f"追加情報:\n{text_info}"})

        for file in uploaded_files:
            b64 = base64.b64encode(file.getvalue()).decode()
            ext = file.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            messages.append({"role": "user", "content": [
                {"type": "text", "text": f"画像：{file.name}"},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
            ]})

        chat_res = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=messages,
            max_tokens=2500,
            temperature=0.3
        )
        result = chat_res.choices[0].message.content

    st.success("✅ 診断完了！")
    st.markdown(result)

    today = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="📄 診断結果をダウンロード（HTML形式・印刷してPDF保存してください）",
        data=result,
        file_name=f"GBP診断結果_{today}.html",
        mime="text/html"
    )

st.caption("Powered by Groq | 04.sampleapp.work")
