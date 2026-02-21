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

if st.button("🚀 スクショから店舗を判断する", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("スクショをアップロードしてください")
        st.stop()

    # 2段階OCRで精度を最大限上げる
    with st.spinner("1段階目：店舗情報を抽出中..."):
        prompt1 = """この画像はGoogle Business Profileのスクショです。
店舗名、住所、カテゴリを正確に抽出してください。
形式：
店舗名: 
住所: 
カテゴリ: """
        msgs = [{"role": "user", "content": [{"type": "text", "text": prompt1}]}]
        for f in uploaded_files:
            b64 = base64.b64encode(f.getvalue()).decode()
            ext = f.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            msgs[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})

        res1 = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=msgs, max_tokens=400, temperature=0.0)
        store1 = res1.choices[0].message.content

    st.success("✅ 1段階目抽出完了")
    st.info(store1)

    # 2段階目確認
    if st.button("✅ この店舗情報で合ってます。診断を進める", type="primary", use_container_width=True):
        with st.spinner("2段階目：診断中..."):
            prompt2 = f"""あなたはGBPの最高位専門家です。

このスクショは以下の店舗のGBPです：
{store1}

この店舗として正確に分析してください。

出力形式：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 先進施策（合法的なもののみ）

最後に免責事項を必ず入れてください。"""

            msgs2 = [{"role": "system", "content": prompt2}]
            if text_info.strip():
                msgs2.append({"role": "user", "content": f"追加情報:\n{text_info}"})
            for f in uploaded_files:
                b64 = base64.b64encode(f.getvalue()).decode()
                ext = f.name.split(".")[-1].lower()
                mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
                msgs2.append({"role": "user", "content": [
                    {"type": "text", "text": f"画像：{f.name}"},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                ]})

            res2 = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=msgs2, max_tokens=2500, temperature=0.3)
            result = res2.choices[0].message.content

        st.success("✅ 診断完了！")
        st.markdown(result)

        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("📄 診断結果をダウンロード（HTMLでPDF保存可能）", result, f"GBP診断_{today}.html", "text/html")

st.caption("Powered by Groq | 04.sampleapp.work")
