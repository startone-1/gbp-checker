import streamlit as st
from groq import Groq
from datetime import datetime
import requests

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

# 現在の安定したレスポンシブデザインを維持
st.markdown("""
<style>
    .main {background-color: #0a0f1c;}
    .big-tab {
        width: 100%;
        padding: 35px 25px;
        font-size: 1.65rem;
        font-weight: 700;
        border-radius: 20px;
        margin-bottom: 22px;
        text-align: center;
        transition: all 0.4s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .big-tab-active {
        background: linear-gradient(135deg, #3b82f6, #1e40af) !important;
        color: white !important;
        box-shadow: 0 15px 40px rgba(59, 130, 246, 0.5);
        transform: translateY(-6px);
    }
    .big-tab-inactive {
        background: #1e2937;
        color: #94a3b8;
    }
    @media (max-width: 768px) {
        .big-tab { font-size: 1.4rem; padding: 28px 20px; }
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

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "gbp"

st.markdown(f"""
<div style="display:flex; gap:20px; margin-bottom:40px;">
    <div class="big-tab {'big-tab-active' if st.session_state.current_tab == 'gbp' else 'big-tab-inactive'}">🔗 GBP診断</div>
    <div class="big-tab {'big-tab-active' if st.session_state.current_tab == 'review' else 'big-tab-inactive'}">💬 レビュー返信アシスタント</div>
</div>
""", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==================== GBP診断 ====================
if st.session_state.current_tab == "gbp":
    st.subheader("🔗 Google Maps URLから診断")
    maps_url = st.text_input("Google Mapsの店舗リンクを貼り付けてください（短縮リンクも自動対応）", 
                            placeholder="https://maps.app.goo.gl/xxxxxx", key="maps_url")

    if maps_url:
        with st.spinner("リンクを展開して診断中..."):
            if "maps.app.goo.gl" in maps_url:
                try:
                    r = requests.get(maps_url, allow_redirects=True, timeout=10)
                    maps_url = r.url
                except:
                    pass

            system_prompt = f"""あなたはGoogle Business Profile公式Product Experts Programの全階層の知見を総合した最高位の専門家です。

このGoogle Mapsリンクの店舗を、**本当にこの店舗をしっかり見て**徹底的に詳細に分析してください：
{maps_url}

**特に厳密にチェックすること**：
- 店舗URLの項目に公式ホームページ以外のURL（Instagram.com、Facebook.com、hotpepper.jp、gurunavi.com、tabelog.comなど）が1つでも入っていないか
- 入っている場合は具体的にどのURLが入っているかをリストアップして、赤字で強い警告を出す

出力形式（各項目を長く、じっくり、細かく書いてください）：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック（特に店舗URLの項目を厳密に確認し、違反があれば赤字で強い警告 + 凍結リスクを明記）
3. 即修正できる具体的な改善案（この店舗に合わせた具体的な提案、コピペOK文例を複数付きで長く）
4. 改善優先順位トップ5（この店舗固有の理由を詳しく）
5. 先進施策（合法的なもののみ・この店舗に合わせた具体的な提案）

最後に免責事項を必ず入れてください。"""

            messages = [{"role": "system", "content": system_prompt}]
            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=messages, max_tokens=4800, temperature=0.3)
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

各パターンを「パターン1」「パターン2」「パターン3」として明確に分けて出力してください。"""

            res = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=[{"role": "system", "content": prompt}], max_tokens=1500, temperature=0.5)
            reply = res.choices[0].message.content

        st.success("✅ 返信文を作成しました")
        st.markdown(reply)

# ==================== お問い合わせセクション ====================
st.markdown("---")
st.subheader("📩 もっとサポートが必要ですか？")
st.write("以下の内容でサポートいたします。お気軽にご連絡ください。")

st.write("""
**よくあるサポート依頼例**
- GBPの運用をまるごと任せたい
- 月次診断レポートを毎月欲しい
- 投稿文を定期的に作成してほしい
- 悪いレビューの返信を代行してほしい
- 競合店との比較分析を詳しくしてほしい
- 写真撮影や投稿戦略のアドバイスが欲しい
- その他、GBPに関する相談全般
""")

st.markdown(f"""
<div style="text-align:center; margin:30px 0;">
    <a href="mailto:gyoum2024@gmail.com?subject=GBP運用サポートのお問い合わせ" target="_blank">
        <button style="background:#3b82f6; color:white; border:none; padding:18px 45px; font-size:1.25rem; border-radius:12px;">
            ✉️ gyoum2024@gmail.com へ問い合わせる
        </button>
    </a>
</div>
""", unsafe_allow_html=True)

st.caption("Powered by Groq | 04.sampleapp.work")
