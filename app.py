import streamlit as st
from groq import Groq
import base64
from datetime import datetime

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
st.markdown("**スクショ / Google Maps URL / ホームページURL から診断**")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

tab1, tab2, tab3 = st.tabs(["📸 スクショから診断", "🔗 Google Maps URLから診断", "🌐 ホームページURLから診断"])

# ==================== タブ1: スクショ ====================
with tab1:
    uploaded_files = st.file_uploader("GBPページのスクショをアップロード（複数OK）", type=["jpg","jpeg","png"], accept_multiple_files=True)
    text_info1 = st.text_area("追加テキスト情報（任意）", height=100, key="text1")
    if st.button("🚀 スクショから診断開始", type="primary", use_container_width=True, key="btn1"):
        if not uploaded_files:
            st.error("スクショをアップロードしてください")
            st.stop()
        # OCR + 診断（省略せず）
        with st.spinner("スクショから店舗情報を抽出中..."):
            ocr_prompt = """この画像はGoogle Business Profileのスクショです。店舗名、住所、カテゴリを正確に抽出してください。
形式：
店舗名: 
住所: 
カテゴリ: """
            ocr_messages = [{"role": "user", "content": [{"type": "text", "text": ocr_prompt}]}]
            for f in uploaded_files:
                b64 = base64.b64encode(f.getvalue()).decode()
                ext = f.name.split(".")[-1].lower()
                mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
                ocr_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=ocr_messages, max_tokens=400, temperature=0.0)
            store_info = res.choices[0].message.content

        st.success("✅ 店舗情報抽出完了")
        st.info(store_info)

        if st.button("✅ この店舗で診断を進める", type="primary", use_container_width=True, key="confirm1"):
            # 診断処理
            with st.spinner("診断中..."):
                prompt = f"""あなたはGBPの最高位専門家です。
このスクショは以下の店舗のGBPです：
{store_info}

この店舗として正確に分析してください。

出力形式：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 先進施策（合法的なもののみ）

最後に免責事項を必ず入れてください。"""

                messages = [{"role": "system", "content": prompt}]
                if text_info1.strip():
                    messages.append({"role": "user", "content": f"追加情報:\n{text_info1}"})
                for f in uploaded_files:
                    b64 = base64.b64encode(f.getvalue()).decode()
                    ext = f.name.split(".")[-1].lower()
                    mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
                    messages.append({"role": "user", "content": [{"type": "text", "text": f"画像：{f.name}"}, {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]})
                res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=messages, max_tokens=2500, temperature=0.3)
                result = res.choices[0].message.content

            st.success("✅ 診断完了！")
            st.markdown(result)

            today = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button("📄 診断結果をダウンロード", result, f"GBP診断_{today}.html", "text/html")

# ==================== タブ2: Google Maps URL ====================
with tab2:
    maps_url = st.text_input("Google Mapsの店舗URLを貼り付けてください", placeholder="https://www.google.com/maps/place/...")
    text_info2 = st.text_area("追加テキスト情報（任意）", height=100, key="text2")
    if st.button("🚀 Google Maps URLから診断開始", type="primary", use_container_width=True, key="btn2"):
        if not maps_url:
            st.error("URLを入力してください")
            st.stop()
        with st.spinner("URLから診断中..."):
            prompt = f"""あなたはGBPの最高位専門家です。
このGoogle Maps URLの店舗のGBPを分析してください：
{maps_url}

この店舗として正確に分析してください。

出力形式：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 先進施策（合法的なもののみ）

最後に免責事項を必ず入れてください。"""

            messages = [{"role": "system", "content": prompt}]
            if text_info2.strip():
                messages.append({"role": "user", "content": f"追加情報:\n{text_info2}"})
            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=messages, max_tokens=2500, temperature=0.3)
            result = res.choices[0].message.content

        st.success("✅ Google Maps URLから診断完了！")
        st.markdown(result)

        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("📄 診断結果をダウンロード", result, f"GBP診断_Maps_{today}.html", "text/html")

# ==================== タブ3: ホームページURL ====================
with tab3:
    homepage_url = st.text_input("店舗のホームページURLを貼り付けてください", placeholder="https://www.example.com")
    text_info3 = st.text_area("追加テキスト情報（任意）", height=100, key="text3")
    if st.button("🚀 ホームページURLから診断開始", type="primary", use_container_width=True, key="btn3"):
        if not homepage_url:
            st.error("URLを入力してください")
            st.stop()
        with st.spinner("ホームページから店舗情報を認識して診断中..."):
            prompt = f"""あなたはGBPの最高位専門家です。
このホームページURLの店舗のGBPを分析してください：
{homepage_url}

ホームページの内容から店舗情報を推測し、この店舗のGBPとして正確に分析してください。

出力形式：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 先進施策（合法的なもののみ）

最後に免責事項を必ず入れてください。"""

            messages = [{"role": "system", "content": prompt}]
            if text_info3.strip():
                messages.append({"role": "user", "content": f"追加情報:\n{text_info3}"})
            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=messages, max_tokens=2500, temperature=0.3)
            result = res.choices[0].message.content

        st.success("✅ ホームページURLから診断完了！")
        st.markdown(result)

        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("📄 診断結果をダウンロード", result, f"GBP診断_Homepage_{today}.html", "text/html")

st.caption("Powered by Groq | 04.sampleapp.work")
