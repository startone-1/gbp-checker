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
st.title("💼 Google Business Profile 運用サポートアプリ")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

tab1, tab2 = st.tabs(["🔗 GBP診断", "💬 レビュー返信アシスタント"])

# ==================== タブ1: GBP診断 ====================
with tab1:
    maps_url = st.text_input("🔗 Google Mapsの店舗URLを貼り付けてください", placeholder="https://www.google.com/maps/place/...")
    text_info = st.text_area("追加テキスト情報（任意）", height=100)
    if st.button("🚀 URLから本格診断を開始", type="primary", use_container_width=True):
        if not maps_url:
            st.error("URLを入力してください")
            st.stop()
        # （診断部分は前回の充実版と同じ）
        with st.spinner("最高レベルの精密診断中..."):
            system_prompt = f"""あなたはGBPの最高位専門家です。
このURLの店舗を徹底的に詳細に分析してください：{maps_url}

出力形式：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 先進施策（詳細に）
6. 近隣同業種との差分分析（実際の店舗名を挙げて）

長く細かく書いてください。最後に免責事項を必ず。"""

            messages = [{"role": "system", "content": system_prompt}]
            if text_info.strip():
                messages.append({"role": "user", "content": f"追加情報:\n{text_info}"})
            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=messages, max_tokens=4000, temperature=0.3)
            result = res.choices[0].message.content

        st.success("✅ 診断完了！")
        st.markdown(result)

        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("📄 診断結果をダウンロード", result, f"GBP診断_{today}.html", "text/html")

# ==================== タブ2: レビュー返信アシスタント ====================
with tab2:
    st.subheader("💬 レビュー返信アシスタント")
    st.write("悪いレビュー・良いレビューを貼り付けてください。GBPガイドラインに準拠した誠実な返信文を複数パターン作成します。")

    review_text = st.text_area("お客様からのレビューを貼り付けてください", height=150, placeholder="例：対応が遅くて残念でした...")

    review_type = st.radio("レビューの種類を選択", ["悪いレビュー（対応が必要）", "良いレビュー（感謝を伝えたい）"])

    if st.button("🚀 返信文を作成する", type="primary", use_container_width=True):
        if not review_text:
            st.error("レビューを入力してください")
            st.stop()

        with st.spinner("GBPガイドラインに準拠した返信文を作成中..."):
            prompt = f"""あなたはGBPの最高位専門家です。
以下のレビューに対して、**誠実で丁寧で、Googleのガイドラインに完全に準拠した返信文**を3パターン作成してください。

レビュー：
{review_text}

レビュー種類：{review_type}

返信のポイント：
- 常に感謝の気持ちを最初に伝える
- 悪いレビューでも感情的にならず、事実ベースで対応
- 改善への意欲を明確に伝える
- 過度な謝罪や責任のなすりつけは避ける
- 自然で人間味のある文章にする

各パターンを「パターン1」「パターン2」「パターン3」として、明確に分けて出力してください。"""

            res = client.chat.completions.create(
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=1500,
                temperature=0.5
            )
            reply = res.choices[0].message.content

        st.success("✅ 返信文を作成しました")
        st.markdown(reply)

st.caption("Powered by Groq | 04.sampleapp.work")
