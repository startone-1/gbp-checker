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

    with st.spinner("最高レベルの精密診断中..."):
        system_prompt = f"""あなたはGoogle Business Profileの最高位専門家です。

このGoogle Maps URLの店舗を徹底的に詳細に分析してください：
{maps_url}

**特に重要な指示**：
- 総合スコアを出した直後に、そのスコアの理由となった問題点を具体的に挙げ、
- すぐに「具体的にどう改善すればいいか」を長く詳しくアドバイスする。
- 抽象的な表現は避け、必ず具体的な行動提案をする。

出力形式（必ずこの順番で）：
1. 総合スコア: XX/100点 - 一言評価
2. スコアの詳細な理由と問題点（具体的に）
3. 即修正できる具体的な改善案（各問題点に対して、コピペOKの文例を複数付きで長く詳しく）
4. 改善優先順位トップ5（各項目を詳しく説明）
5. 先進施策（合法的なもののみ・非常に詳細に）

最後に必ず免責事項を入れてください。"""

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

    st.success("✅ 診断完了！（問題点に対して具体的な改善案を必ず出しています）")
    st.markdown(result)

    today = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="📄 診断結果をダウンロード（HTML形式・印刷してPDF保存してください）",
        data=result,
        file_name=f"GBP詳細診断_{today}.html",
        mime="text/html"
    )

st.caption("Powered by Groq | 04.sampleapp.work")
