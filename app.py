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
st.markdown("**Google Mapsの店舗URLを貼るだけで精密診断**")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

maps_url = st.text_input("🔗 Google Mapsの店舗URLを貼り付けてください", 
                        placeholder="https://www.google.com/maps/place/...")
text_info = st.text_area("追加テキスト情報（任意）", height=100)

if st.button("🚀 URLから診断開始", type="primary", use_container_width=True):
    if not maps_url:
        st.error("Google Mapsの店舗URLを入力してください")
        st.stop()

    with st.spinner("Google Maps URLから診断中..."):
        prompt = f"""あなたはGoogle Business Profileの最高位専門家です。

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
        if text_info.strip():
            messages.append({"role": "user", "content": f"追加情報:\n{text_info}"})

        res = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=messages,
            max_tokens=2500,
            temperature=0.3
        )
        result = res.choices[0].message.content

    st.success("✅ 診断完了！")
    st.markdown(result)

    today = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="📄 診断結果をダウンロード（HTML形式・印刷してPDF保存してください）",
        data=result,
        file_name=f"GBP診断_{today}.html",
        mime="text/html"
    )

st.caption("Powered by Groq | 04.sampleapp.work")
