import streamlit as st
from groq import Groq
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
st.markdown("**Google Maps URL または 店舗名で簡単に診断**")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

tab1, tab2 = st.tabs(["🔗 Google Maps URLから診断", "🔍 店舗名で検索して診断"])

# ==================== タブ1: Google Maps URL ====================
with tab1:
    maps_url = st.text_input("Google Mapsの店舗URLを貼り付けてください", placeholder="https://www.google.com/maps/place/...", key="maps_url")
    text_info1 = st.text_area("追加テキスト情報（任意）", height=100, key="text_maps")
    if st.button("🚀 Google Maps URLから診断開始", type="primary", use_container_width=True, key="btn_maps"):
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
            if text_info1.strip():
                messages.append({"role": "user", "content": f"追加情報:\n{text_info1}"})
            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=messages, max_tokens=2500, temperature=0.3)
            result = res.choices[0].message.content

        st.success("✅ 診断完了！")
        st.markdown(result)

        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("📄 診断結果をダウンロード", result, f"GBP診断_Maps_{today}.html", "text/html")

# ==================== タブ2: 店舗名で検索 ====================
with tab2:
    store_name = st.text_input("🏬 店舗名を入力してください", placeholder="例：東武ストア みずほ台店", key="store_name")
    address_hint = st.text_input("住所の一部（わかれば）", placeholder="立川市錦町 など", key="address_hint")
    text_info2 = st.text_area("追加テキスト情報（任意）", height=100, key="text_search")
    if st.button("🚀 店舗名で検索して診断開始", type="primary", use_container_width=True, key="btn_search"):
        if not store_name:
            st.error("店舗名を入力してください")
            st.stop()

        query = store_name
        if address_hint:
            query += " " + address_hint

        st.success(f"「{query}」で検索して診断を開始します")

        with st.spinner("診断中..."):
            prompt = f"""あなたはGBPの最高位専門家です。

店舗名「{query}」のGBPを分析してください。

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

        st.success("✅ 診断完了！")
        st.markdown(result)

        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("📄 診断結果をダウンロード", result, f"GBP診断_{today}.html", "text/html")

st.caption("Powered by Groq | 04.sampleapp.work")
