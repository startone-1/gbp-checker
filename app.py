import streamlit as st
from groq import Groq
import base64
from datetime import datetime

# ============== プロフェッショナルデザイン ==============
st.set_page_config(
    page_title="GBP規約違反チェックアプリ",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main {background-color: #0f172a; color: #e2e8f0;}
    .stApp {background-color: #0f172a;}
    h1 {font-size: 2.8rem !important; color: #60a5fa; text-align: center; margin-bottom: 0.2rem;}
    .subtitle {font-size: 1.3rem; color: #94a3b8; text-align: center; margin-bottom: 2rem;}
    .stButton>button {width: 100%; height: 3.2rem; font-size: 1.1rem; background: linear-gradient(90deg, #3b82f6, #1e40af); border: none;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1>💼 Google Business Profile 規約違反チェックアプリ</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Diamond Product Expertレベルの知見をすべて活かした、公式ガイドライン準拠の精密診断</p>', unsafe_allow_html=True)

st.markdown("""
**このアプリは**  
Diamond / Platinum / Gold / Silver / Bronze Product Expertの全階層の知見を総合的に学び、  
Google公式ルール・ガイドライン・ヘルプコミュニティの最新情報を基に、  
**規約違反チェック・具体的な修正案・優先順位・先進施策**を瞬時に診断します。
""")

# ============== Groqキー ==============
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("Groqキーが設定されていません。")
    st.stop()

client = Groq(api_key=groq_key)

uploaded_files = st.file_uploader(
    "📸 GBPページのスクリーンショットをアップロード（複数OK）",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    help="基本情報・写真・投稿・レビュー画面など、できるだけ多くで精度UP"
)

text_info = st.text_area(
    "またはテキスト情報を貼り付け（任意・さらに精度が上がります）",
    placeholder="店舗名: 〇〇ラーメン\n住所: 東京都新宿区...\nカテゴリ: ラーメン屋",
    height=150
)

if st.button("🚀 Diamond〜Bronze Product Expertの知見で規約チェックを開始", type="primary", use_container_width=True):
    if not uploaded_files and not text_info.strip():
        st.error("スクショまたはテキストを入力してください")
        st.stop()

    with st.spinner("Diamond Product Expertレベルの知見を総動員して精密分析中...（10〜25秒）"):
        system_prompt = """あなたはGoogle Business Profile公式Product Experts Programの全階層（Diamond Product Expert、Platinum Product Expert、Gold Product Expert、Silver Product Expert、Bronze Member）の知見を総合的に学び、最高レベルの専門家です。

【参照する専門家階層】
- Diamond Product Expert（最高位・5000ポイント以上）
- Platinum Product Expert（2500ポイント以上）
- Gold Product Expert（1000ポイント以上）
- Silver Product Expert（300ポイント以上）
- Bronze Member（基礎レベル）

これら全レベルの実践知見を学び、公式ルール・ガイドライン・ヘルプコミュニティの最新情報を厳密に守って分析してください。

【厳守ルール（2026年最新）】
- ビジネス名：看板・名刺と完全に一致。キーワード詰め込みNG
- Primaryカテゴリ：1つだけ
- 写真：オリジナル・実際の店舗。広告・水印・個人情報NG
- 投稿：有用で正確。宣伝過多NG
- レビュー返信：全レビューに誠実対応
など

入力データを分析し、以下の形式で**日本語でとても丁寧・具体的に**出力してください：

1. 規約違反チェック（危険度：高/中/低 + 該当ルール引用）
2. 即修正できる具体的な改善案（コピペOKの文例付き）
3. 改善優先順位トップ3
4. Diamond〜Bronze Product Expertが実際に実践している先進的な施策とベストプラクティス（各レベルから学んだ実例を織り交ぜて）

最後に必ず「これは参考情報です。最終判断はGoogle公式ツールで確認してください。」を入れてください。"""

        # （以下は前回と同じ部分なので省略せず全部貼る）
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
            max_tokens=2000,
            temperature=0.3
        )
        result = chat_completion.choices[0].message.content

        st.success("✅ 分析完了！Diamond〜Bronze全エキスパートの知見を活かした診断結果です")

        st.markdown("### 📋 診断結果")
        st.markdown(result)

        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="📄 診断結果をダウンロード（Markdown形式・印刷してPDF保存も簡単）",
            data=result,
            file_name=f"GBPチェック結果_{today}.md",
            mime="text/markdown"
        )

st.caption("💼 Powered by Diamond〜Bronze Product Expertの総合知見 | 04.sampleapp.work")
