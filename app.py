import streamlit as st
from groq import Groq
import base64
from datetime import datetime
import re

# パスワード
if "authenticated" not in st.session_state:
    st.title("💼 GBPチェックアプリ")
    pw = st.text_input("パスワードを入力", type="password")
    if st.button("ログイン"):
        if pw == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

st.set_page_config(page_title="GBPチェック", page_icon="💼", layout="centered")
st.title("💼 Google Business Profile 規約違反チェックアプリ")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Groqキーが設定されていません")
    st.stop()

uploaded_files = st.file_uploader("スクショをアップロード（複数OK）", type=["jpg","jpeg","png"], accept_multiple_files=True)
text_info = st.text_area("追加テキスト情報（任意）", height=100)

if st.button("🚀 診断を開始", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("スクショをアップロードしてください")
        st.stop()

    # 高精度OCR
    with st.spinner("店舗情報を高精度で抽出中..."):
        ocr_msg = [{"role": "user", "content": [{"type": "text", "text": "このGBPスクショから店舗名、住所、カテゴリを正確に抽出せよ。形式：店舗名: XXX\n住所: XXX\nカテゴリ: XXX"}]}]
        for f in uploaded_files:
            b64 = base64.b64encode(f.getvalue()).decode()
            mime = f"image/{'jpeg' if f.name.lower().endswith(('jpg','jpeg')) else f.name.split('.')[-1].lower()}"
            ocr_msg[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
        res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=ocr_msg, max_tokens=300, temperature=0.0)
        store = res.choices[0].message.content

    st.success("✅ 店舗情報抽出完了")
    st.info(store)

    # 診断
    with st.spinner("精密診断中..."):
        prompt = f"""このスクショは以下の店舗のGBPです：
{store}

出力形式：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正案
4. 改善優先順位トップ5
5. 先進施策（合法的なもののみ・違反リスクは必ず注意喚起）

免責事項を最後に必ず入れる。"""
        msgs = [{"role": "system", "content": prompt}]
        if text_info:
            msgs.append({"role": "user", "content": f"追加情報:\n{text_info}"})
        for f in uploaded_files:
            b64 = base64.b64encode(f.getvalue()).decode()
            mime = f"image/{'jpeg' if f.name.lower().endswith(('jpg','jpeg')) else f.name.split('.')[-1].lower()}"
            msgs.append({"role": "user", "content": [{"type": "text", "text": f"画像：{f.name}"}, {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]})

        res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=msgs, max_tokens=2200, temperature=0.3)
        result = res.choices[0].message.content

    st.success("✅ 診断完了")
    st.markdown(result)

    today = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button("📄 診断結果をダウンロード（HTMLでPDF保存可能）", result, f"GBP診断_{today}.html", "text/html")

st.caption("Powered by Groq | 04.sampleapp.work")
