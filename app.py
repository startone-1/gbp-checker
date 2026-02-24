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

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

tab1, tab2 = st.tabs(["🔗 GBP診断", "💬 レビュー返信アシスタント"])

# ==================== GBP診断 ====================
with tab1:
    st.subheader("Google Mapsのリンクを貼るか、店舗名で検索してください")

    maps_url = st.text_input("Google Mapsの店舗リンクを貼り付けてください", 
                            placeholder="https://maps.app.goo.gl/xxxxxx", key="maps_url")

    store_name_search = st.text_input("または店舗名で検索", placeholder="例：東武ストア みずほ台店", key="store_search")

    text_info = st.text_area("追加テキスト情報（任意）", height=100)

    if maps_url or store_name_search:
        if maps_url:
            query = maps_url
        else:
            query = store_name_search

        with st.spinner("店舗情報を確認中..."):
            # 店舗名抽出
            name_prompt = f"""以下の情報から正確な店舗名を抽出してください：
{query}
「店舗名: XXX」の形式で答えてください。"""
            name_res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=[{"role": "user", "content": name_prompt}], max_tokens=100, temperature=0.0)
            store_name = name_res.choices[0].message.content.strip().replace("店舗名: ", "")

        st.success(f"✅ **{store_name}** と認識しました")

        # 確認用リンク（確実に新しいタブで開く）
        if maps_url:
            st.link_button(f"📍 {store_name} のGoogle Mapsページを確認", maps_url, use_container_width=True)

        if st.button("✅ この店舗で合っています。診断を開始", type="primary", use_container_width=True):
            with st.spinner("精密診断中..."):
                system_prompt = f"""あなたはGoogle Business Profileの最高位専門家です。

店舗名: **{store_name}**

この店舗のGBPを徹底的に詳細に分析してください。

出力形式（各項目を長く詳細に）：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 先進施策（合法的なもののみ）

最後に免責事項を必ず入れてください。"""

                messages = [{"role": "system", "content": system_prompt}]
                if text_info.strip():
                    messages.append({"role": "user", "content": f"追加情報:\n{text_info}"})
                res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=messages, max_tokens=4000, temperature=0.3)
                result = res.choices[0].message.content

            st.success(f"✅ **{store_name}** の診断完了！")
            st.markdown(result)

            today = datetime.now().strftime("%Y%m%d_%H%M")
            st.download_button("📄 診断結果をダウンロード", result, f"GBP診断_{today}.html", "text/html")

# ==================== レビュー返信アシスタント ====================
with tab2:
    st.subheader("💬 レビュー返信アシスタント")
    st.write("お客様のレビューを貼り付けてください。GBPガイドラインに完全に準拠した誠実な返信文を複数パターン作成します。")

    review_text = st.text_area("お客様からのレビューを貼り付けてください", height=180, placeholder="例：対応が遅くて残念でした...")
    review_type = st.radio("レビューの種類", ["悪いレビュー（丁寧に対応したい）", "良いレビュー（感謝を伝えたい）"])

    if st.button("🚀 返信文を作成する", type="primary", use_container_width=True):
        if not review_text:
            st.error("レビューを入力してください")
            st.stop()

        with st.spinner("GBPガイドラインに準拠した返信文を作成中..."):
            prompt = f"""あなたはGBPの最高位専門家です。
以下のレビューに対して、誠実で丁寧でGoogleガイドラインに完全に準拠した返信文を**3パターン**作成してください。

レビュー：
{review_text}

種類：{review_type}

各パターンを「パターン1」「パターン2」「パターン3」として明確に分けて出力してください。"""

            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=[{"role": "system", "content": prompt}], max_tokens=1500, temperature=0.5)
            reply = res.choices[0].message.content

        st.success("✅ 返信文を作成しました")
        st.markdown(reply)

st.caption("Powered by Groq | 04.sampleapp.work")
