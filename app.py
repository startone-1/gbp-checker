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
st.markdown("**Google Mapsの店舗URLを貼るだけで、最高レベルの詳細診断**")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

maps_url = st.text_input("🔗 Google Mapsの店舗URLを貼り付けてください", 
                        placeholder="https://www.google.com/maps/place/...")
text_info = st.text_area("追加テキスト情報（任意でより精度が上がります）", height=150)

if st.button("🚀 URLから本格診断を開始", type="primary", use_container_width=True):
    if not maps_url:
        st.error("Google Mapsの店舗URLを入力してください")
        st.stop()

    with st.spinner("Google Maps URLから最高レベルの精密診断中..."):
        system_prompt = f"""あなたはGoogle Business Profile公式Product Experts Programの全階層（Diamond, Platinum, Gold, Silver, Bronze）の知見を総合した、最高位の専門家です。

このGoogle Maps URLの店舗のGBPを、徹底的に詳細に分析してください：
{maps_url}

分析は長く、細かく、プロフェッショナルに行ってください。

出力形式（必ずこの順番で、各項目を長く詳細に）：
1. 総合スコア: XX/100点 - 一言評価 + 詳細な評価理由
2. 規約違反チェック（危険度：高/中/低 + 該当ルール引用 + なぜ危険なのかの詳細説明）
3. 即修正できる具体的な改善案（各項目を長く、コピペOKの文例を複数付きで）
4. 改善優先順位トップ5（各項目を詳しく説明）
5. 全国および近隣同業種の成功事例に基づく先進施策（非常に詳細に。各施策に「なぜ効果的なのか」「具体的なやり方」「週ごとの実行例」「注意すべきルール違反リスクと回避方法」を必ず入れる）
6. 近隣の同じジャンルの施設との差分分析（抽出された住所から地域を推測し、同じジャンルの近隣施設との違いを具体的に比較。スコア・写真・投稿・属性・更新頻度など多角的に）

最後に必ず「これは参考情報です。最終判断はGoogle公式ツールで確認してください。」を入れてください。"""

        messages = [{"role": "system", "content": system_prompt}]
        if text_info.strip():
            messages.append({"role": "user", "content": f"追加情報:\n{text_info}"})

        res = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=messages,
            max_tokens=4000,
            temperature=0.3
        )
        result = res.choices[0].message.content

    st.success("✅ 診断完了！（最高レベルの詳細診断です）")
    st.markdown(result)

    today = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="📄 診断結果をダウンロード（HTML形式・印刷してPDF保存してください）",
        data=result,
        file_name=f"GBP詳細診断_{today}.html",
        mime="text/html"
    )

st.caption("Powered by Groq | 04.sampleapp.work")
