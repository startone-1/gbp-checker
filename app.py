import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="GBP規約チェック", page_icon="💼", layout="centered")
st.title("💼 Google Business Profile 規約違反チェックアプリ")
st.markdown("**無料・Vision対応** スクショをアップロードするだけで公式ルールに基づく的確アドバイスを即出力！")

groq_key = st.text_input("Groq API Key (gsk_...)", type="password", help="console.groq.com/keys で取得")
if not groq_key:
    st.info("APIキーを入力してください（Free TierでOK）")
    st.stop()

client = Groq(api_key=groq_key)

uploaded_files = st.file_uploader(
    "GBPページのスクリーンショットをアップロード（複数OK）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

text_info = st.text_area(
    "またはテキスト情報を貼り付け（任意）",
    placeholder="店舗名: 〇〇ラーメン\n住所: 東京都...",
    height=150
)

if st.button("🚀 AIで規約チェック開始", type="primary", use_container_width=True):
    if not uploaded_files and not text_info.strip():
        st.error("スクショかテキストを入れてね")
        st.stop()

    with st.spinner("Groqが分析中...（5〜20秒）"):
        system_prompt = """あなたはGoogle Business Profileのプロの先生です。
公式ルールに従って見て、アドバイスしてね。
違反チェック → 直し方（コピペOK） → 優先順位 → もっと良くする方法
全部日本語で優しく教えて。
免責：これは参考だよ。Google公式で最終確認してね。"""

        messages = [{"role": "system", "content": system_prompt}]
        user_content = []
        if text_info.strip():
            user_content.append({"type": "text", "text": f"店舗情報:\n{text_info}"})

        for file in uploaded_files:
            bytes_data = file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            ext = file.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            user_content.append({"type": "text", "text": f"画像：{file.name}"})
            user_content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}})

        messages.append({"role": "user", "content": user_content})

        chat_completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=messages,
            max_tokens=1500,
            temperature=0.3
        )
        result = chat_completion.choices[0].message.content
        st.success("✅ 完了！")
        st.markdown(result)
