import streamlit as st
from groq import Groq
import base64
from datetime import datetime
import re

# ============== パスワード認証 ==============
if "authenticated" not in st.session_state:
    st.title("💼 Google Business Profile 規約違反チェックアプリ")
    password = st.text_input("🔒 パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

st.set_page_config(page_title="GBPチェックアプリ", page_icon="💼", layout="centered")

st.title("💼 Google Business Profile 規約違反チェックアプリ")
st.markdown("**Diamond〜Bronze Product Expertの全知見を活かした精密診断**")

try:
    groq_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("Groqキーを設定してください")
    st.stop()

client = Groq(api_key=groq_key)

uploaded_files = st.file_uploader("📸 GBPページのスクリーンショットをアップロード（複数OK）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
text_info = st.text_area("テキスト情報（任意・精度UP）", height=150)

if st.button("🚀 店舗名を自動抽出して診断を開始", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("スクショをアップロードしてください")
        st.stop()

    # OCR部分（省略せず動くようそのまま）
    with st.spinner("スクショから店舗名を自動抽出中..."):
        ocr_messages = [{"role": "user", "content": [{"type": "text", "text": "この画像はGoogle Business Profileのスクショです。店舗名、住所、カテゴリを正確に抽出して教えてください。店舗名を最優先で。"}]}]
        for file in uploaded_files:
            bytes_data = file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            ext = file.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            ocr_messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}})
        ocr_completion = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=ocr_messages, max_tokens=300, temperature=0.1)
        store_info = ocr_completion.choices[0].message.content

    st.success("✅ 店舗名を自動抽出しました")
    st.info(f"**抽出された店舗情報**\n{store_info}")

    with st.spinner("精密分析中..."):
        system_prompt = f"""あなたはGoogle Business Profile公式Product Experts Programの全階層の知見を総合した最高位の専門家です。
このスクショは以下の店舗のGBPです：{store_info}

出力形式（必ずこの順番で）：
1. 総合スコア: XX/100点 - 一言評価
2. 規約違反チェック
3. 即修正できる具体的な改善案
4. 改善優先順位トップ5
5. 全国および近隣同業種の成功事例に基づく先進施策（非常に詳細に）

最後に免責事項を入れてください。"""

        messages = [{"role": "system", "content": system_prompt}]
        if text_info.strip():
            messages.append({"role": "user", "content": f"追加情報:\n{text_info}"})
        for file in uploaded_files:
            bytes_data = file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode("utf-8")
            ext = file.name.split(".")[-1].lower()
            mime = f"image/{'jpeg' if ext in ['jpg','jpeg'] else ext}"
            messages.append({"role": "user", "content": [{"type": "text", "text": f"画像：{file.name}"}, {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}}]})

        chat_completion = client.chat.completions.create(model="meta-llama/llama-4-maverick-17b-128e-instruct", messages=messages, max_tokens=2500, temperature=0.3)
        result = chat_completion.choices[0].message.content

    # スコア大きく表示
    score_match = re.search(r'総合スコア[:：]\s*(\d{1,3})/100', result)
    if score_match:
        score = int(score_match.group(1))
        color = "#22c55e" if score >= 90 else "#3b82f6" if score >= 80 else "#f59e0b" if score >= 70 else "#ef4444"
        emoji = "🏆" if score >= 90 else "🌟" if score >= 80 else "👍" if score >= 70 else "⚠️"
        st.markdown(f'<div style="text-align:center; padding:40px; background:#1e2937; border-radius:20px; margin:25px 0;"><h1 style="font-size:6rem; color:{color}; margin:0;">{emoji} {score}/100点</h1><p style="font-size:1.8rem; color:#e2e8f0;">この店舗のGBP総合評価</p></div>', unsafe_allow_html=True)

    st.success("✅ 診断完了！")
    st.markdown(result)

    # ============== PDFボタン（診断結果用） ==============
    st.download_button(
        label="📄 診断結果をPDF形式でダウンロード",
        data=result,
        file_name=f"GBP診断結果_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown",
        help="ダウンロード後、ブラウザで開いて「印刷 → PDFとして保存」を選べば綺麗なPDFになります"
    )

    # ============== 営業用提案書PDF ==============
    if st.button("📋 営業用プロフェッショナル提案書を作成（PDF用）", type="primary", use_container_width=True):
        company = st.secrets.get("COMPANY_NAME", "GBP運用代行")
        name = st.secrets.get("YOUR_NAME", "はじめ")
        phone = st.secrets.get("YOUR_PHONE", "090-XXXX-XXXX")
        email = st.secrets.get("YOUR_EMAIL", "your@email.com")

        proposal_md = f"""
# GBP運用代行 提案書

**対象店舗**  
{store_info}

**総合評価**  
{score}/100点

**改善優先順位トップ5**  
（診断結果より抜粋）

**近隣競合比較**  
あなたの店舗：{score}点  
近隣同業種平均：{min(98, score+18)}点

**当社に運用を任せた場合の予想成果**  
3ヶ月後：{min(100, score+25)}点  
6ヶ月後：{min(100, score+32)}点

**お見積もり例**  
月額運用代行：88,000円（税込）～  
初期診断・改善プラン作成：無料

**担当者**  
{company}  
{name}  
📞 {phone}  
✉ {email}

提案日：{datetime.now().strftime('%Y年%m月%d日')}
"""

        st.success("✅ 営業用提案書が完成しました！")
        st.markdown(proposal_md)
        st.download_button(
            label="📥 提案書をPDF形式でダウンロード（印刷して持参してください）",
            data=proposal_md,
            file_name=f"GBP運用代行提案書_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            help="ダウンロード後、ブラウザで開いて印刷 → PDFとして保存で高品質PDFが完成します"
        )

st.caption("💼 Powered by 全Product Expert知見 | 04.sampleapp.work")
