import streamlit as st
from groq import Groq
import base64

# ページの見た目をきれいにする
st.set_page_config(page_title="GBP規約チェック", page_icon="💼", layout="centered")

st.title("💼 Google Business Profile 規約違反チェックアプリ")
st.markdown("**無料・Vision対応** スクショをアップロードするだけで公式ルールに基づく的確アドバイスを即出力！")

# Groqキーを最初から入れる（秘密の鍵）
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Groqキーがまだ設定されてないよ！\nManage app → Settings → Secrets で設定してね")
    st.stop()

client = Groq(api_key=groq_key)

# スクショをアップロードするところ
uploaded_files = st.file_uploader(
    "GBPページのスクリーンショットをアップロード（複数OK：基本情報・写真・投稿など）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# テキストを貼り付けるところ
text_info = st.text_area(
    "またはテキスト情報を貼り付け（任意・より精度が上がるよ）",
    placeholder="店舗名: 〇〇ラーメン\n住所: 東京都新宿区...\nカテゴリ: ラーメン屋",
    height=150
)

# チェック開始ボタン
if st.button("🚀 AIで規約チェック開始", type="primary", use_container_width=True):
    if not uploaded_files and not text_info.strip():
        st.error("スクショかテキストを入れてね！")
        st.stop()

    with st.spinner("Groqが公式ガイドラインと照らし合わせて分析中...（5〜20秒）"):
        # AIへの指示（簡単バージョン）
        system_prompt = """あなたはGoogle Business Profileの公式プロの先生です。
公式ルールに従って見て、アドバイスしてね。
1. 規約違反チェック（危険度：高/中/低）
2. すぐ直せる具体的な直し方（コピペで使える文例付き）
3. 改善優先順位トップ3
4. もっと良くするおすすめ施策
全部日本語で優しく丁寧に教えて。
最後に「これは参考情報です。Google公式で最終確認してね。」と書いてね。"""

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

        # AIに聞く（Vision対応の最新モデル）
        chat_completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=messages,
            max_tokens=1500,
            temperature=0.3
        )
        result = chat_completion.choices[0].message.content

        st.success("✅ 分析完了！")
        st.markdown(result)
