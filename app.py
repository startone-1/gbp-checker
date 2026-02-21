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

# カッコいいダークプロデザイン
st.markdown("""
<style>
    .main {background-color: #0f172a; color: #e2e8f0;}
    .stApp {background-color: #0f172a;}
    h1 {font-size: 2.8rem !important; color: #60a5fa; text-align: center; margin-bottom: 0.2rem;}
    .subtitle {font-size: 1.3rem; color: #94a3b8; text-align: center; margin-bottom: 2rem;}
    .stButton>button {width: 100%; height: 3.2rem; font-size: 1.1rem; background: linear-gradient(90deg, #3b82f6, #1e40af); border: none;}
    .upload {background: #1e2937; border-radius: 12px; padding: 2rem;}
</style>
""", unsafe_allow_html=True)

# ============== タイトル & ロゴ ==============
st.markdown('<h1>💼 Google Business Profile 規約違反チェックアプリ</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Gold Product Memberレベルの専門家が、公式ガイドラインに基づいて的確に診断・アドバイスします</p>', unsafe_allow_html=True)

# ============== 長いプロ説明文 ==============
st.markdown("""
**このアプリは**  
任意の店舗のGoogle Business Profile（GBP）をアップロードするだけで、  
**Google公式ルール・ガイドライン・ヘルプコミュニティ・Gold Product Memberの知見**をすべて参照して、  
**規約違反の有無・危険度・具体的な修正案**を瞬時に出します。

- 写真・投稿・カテゴリ・ビジネス名・住所などすべてチェック  
- コピペで使える改善文例付き  
- 優先順位トップ3 + Gold Memberが実際にやっている施策  
- すべて日本語で、丁寧で実践的なアドバイス  

**無料・Vision対応・完全匿名**  
今すぐご自身の店舗、またはお客様の店舗を診断してみてください。
""")

# ============== Groqキー（秘密のまま） ==============
try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("Groqキーが設定されていません。Manage app → SecretsでGROQ_API_KEYを設定してください。")
    st.stop()

client = Groq(api_key=groq_key)

# ============== 入力エリア ==============
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_files = st.file_uploader(
        "📸 GBPページのスクリーンショットをアップロード（複数OK）",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="基本情報・写真・投稿・レビュー画面など、できるだけ多くアップロードすると精度が上がります"
    )
with col2:
    text_info = st.text_area(
        "またはテキスト情報を貼り付け（任意・精度UP）",
        placeholder="店舗名: 〇〇ラーメン\n住所: 東京都新宿区...\nカテゴリ: ラーメン屋\nなど",
        height=180
    )

# ============== チェックボタン ==============
if st.button("🚀 AI専門家が規約チェックを開始する", type="primary", use_container_width=True):
    if not uploaded_files and not text_info.strip():
        st.error("スクショまたはテキストを入力してください")
        st.stop()

    with st.spinner("Gold Product Memberレベルの専門家が公式ガイドラインと照らし合わせて詳細に分析中...（10〜25秒程度）"):
        system_prompt = """あなたはGoogle Business Profile公式認定 Gold Product Memberレベルの専門家です。
公式ルール・ガイドライン・ヘルプコミュニティの最新知見を厳密に守って分析してください。

【厳守ルール（2026年最新）】
・ビジネス名：看板・名刺と完全に一致。キーワード詰め込みNG
・Primaryカテゴリ：1つだけ
・写真：オリジナル・実際の店舗商品。水印・広告・個人情報NG
・投稿：有用で正確。宣伝過多NG
・レビュー返信：全レビューに誠実対応
など

【Gold Member推奨ベストプラクティス】
・写真週1回更新、360°活用
・投稿週2回以上
・名前は実名優先 など

入力データを分析し、以下の形式で**日本語でとても丁寧・具体的に**出力してください：
1. 規約違反チェック（危険度：高/中/低 + 該当ルール引用）
2. 即修正できる具体的な改善案（コピペOKの文例付き）
3. 改善優先順位トップ3
4. Gold Memberが実際にやっている追加施策

最後に免責事項：「これは参考情報です。最終判断はGoogle公式ツールで確認してください。」を必ず入れてください。"""

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

        st.success("✅ 分析完了！専門家による詳細診断結果です")

        # 結果表示
        st.markdown("### 📋 診断結果")
        st.markdown(result)

        # ============== PDFダウンロード（超簡単） ==============
        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="📄 診断結果をMarkdownでダウンロード（印刷してPDF保存も簡単）",
            data=result,
            file_name=f"GBPチェック結果_{today}.md",
            mime="text/markdown"
        )

        st.caption("💡 ダウンロードしたファイルを開いて、ブラウザの「印刷」→「PDFとして保存」を選べばすぐにPDFになります！")

st.caption("Made with ❤️ for 04.sampleapp.work | Groq + Streamlit")
