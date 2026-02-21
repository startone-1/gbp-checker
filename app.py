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

# 目立つ切り替えUI
st.markdown("""
<style>
    .big-tab {
        width: 100%;
        padding: 28px 20px;
        font-size: 1.45rem;
        font-weight: bold;
        border-radius: 16px;
        margin-bottom: 18px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .big-tab-active {
        background: linear-gradient(90deg, #3b82f6, #1e40af) !important;
        color: white !important;
        box-shadow: 0 12px 25px rgba(59, 130, 246, 0.4);
        transform: translateY(-3px);
    }
    .big-tab-inactive {
        background: #1e2937;
        color: #94a3b8;
    }
    @media (max-width: 768px) {
        .big-tab { font-size: 1.3rem; padding: 22px 15px; }
    }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("🔗 GBP診断", use_container_width=True, key="tab_gbp"):
        st.session_state.current_tab = "gbp"

with col2:
    if st.button("💬 レビュー返信アシスタント", use_container_width=True, key="tab_review"):
        st.session_state.current_tab = "review"

# 現在のタブ管理
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "gbp"

st.markdown(f"""
<div style="display:flex; gap:15px; margin-bottom:30px;">
    <div class="big-tab {'big-tab-active' if st.session_state.current_tab == 'gbp' else 'big-tab-inactive'}">🔗 GBP診断</div>
    <div class="big-tab {'big-tab-active' if st.session_state.current_tab == 'review' else 'big-tab-inactive'}">💬 レビュー返信アシスタント</div>
</div>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==================== GBP診断 ====================
if st.session_state.current_tab == "gbp":
    st.subheader("🔗 Google Maps URLから診断")
    maps_url = st.text_input("Google Mapsの店舗URLを貼り付けてください", placeholder="https://www.google.com/maps/place/...")
    text_info = st.text_area("追加テキスト情報（任意）", height=150)
    
    if st.button("🚀 URLから本格診断を開始", type="primary", use_container_width=True):
        if not maps_url:
            st.error("URLを入力してください")
            st.stop()
        # 高品質診断（前回の充実版）
        with st.spinner("最高レベルの精密診断中..."):
            system_prompt = f"""あなたはGoogle Business Profileの最高位専門家です。
このGoogle Maps URLの店舗を徹底的に詳細に分析してください：
{maps_url}

出力形式：
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

        st.success("✅ 診断完了！")
        st.markdown(result)

        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button("📄 診断結果をダウンロード", result, f"GBP診断_{today}.html", "text/html")

# ==================== レビュー返信アシスタント ====================
if st.session_state.current_tab == "review":
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

ポイント：
- 常に感謝を最初に伝える
- 悪いレビューでも感情的にならず、改善意欲を明確に
- 自然で人間味のある文章にする

各パターンを「パターン1」「パターン2」「パターン3」として明確に分けて出力してください。"""

            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=[{"role": "system", "content": prompt}], max_tokens=1500, temperature=0.5)
            reply = res.choices[0].message.content

        st.success("✅ 返信文を作成しました")
        st.markdown(reply)

st.caption("Powered by Groq | 04.sampleapp.work")
