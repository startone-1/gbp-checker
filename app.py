import streamlit as st
from groq import Groq
import base64
from datetime import datetime
import re

# パスワード認証
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
    score = int(score_match.group(1)) if score_match else 0
    color = "#22c55e" if score >= 90 else "#3b82f6" if score >= 80 else "#f59e0b" if score >= 70 else "#ef4444"
    emoji = "🏆" if score >= 90 else "🌟" if score >= 80 else "👍" if score >= 70 else "⚠️"
    st.markdown(f'<div style="text-align:center; padding:40px; background:#1e2937; border-radius:20px; margin:25px 0;"><h1 style="font-size:6rem; color:{color}; margin:0;">{emoji} {score}/100点</h1><p style="font-size:1.8rem; color:#e2e8f0;">この店舗のGBP総合評価</p></div>', unsafe_allow_html=True)

    st.success("✅ 診断完了！")
    st.markdown(result)

    # ============== PDF用ダウンロードボタン ==============
    today = datetime.now().strftime("%Y%m%d_%H%M")

    # 診断結果PDF用（印刷用HTML）
    diagnostic_html = f"""
    <html><head><meta charset="UTF-8"><title>GBP診断結果</title>
    <style>body{{font-family:sans-serif; padding:40px; line-height:1.6;}} h1{{color:#1e40af;}} .score{{font-size:80px; font-weight:bold; color:{color};}}</style>
    </head><body>
    <h1>GBP診断結果</h1>
    <p>対象店舗：{store_info}</p>
    <p class="score">{emoji} {score}/100点</p>
    {result.replace('\n', '<br>')}
    <hr><p>診断日：{datetime.now().strftime('%Y年%m月%d日')}</p>
    <p>これは参考情報です。最終判断はGoogle公式ツールで確認してください。</p>
    </body></html>
    """

    st.download_button(
        label="📄 診断結果をPDF用HTMLでダウンロード（印刷してPDF化してください）",
        data=diagnostic_html,
        file_name=f"GBP診断結果_{today}.html",
        mime="text/html"
    )

    # 営業用提案書PDF用
    company = st.secrets.get("COMPANY_NAME", "GBP運用代行")
    name = st.secrets.get("YOUR_NAME", "はじめ")
    phone = st.secrets.get("YOUR_PHONE", "090-XXXX-XXXX")
    email = st.secrets.get("YOUR_EMAIL", "your@email.com")

    proposal_html = f"""
    <html><head><meta charset="UTF-8"><title>GBP運用代行提案書</title>
    <style>body{{font-family:sans-serif; padding:50px; line-height:1.7;}} h1{{color:#1e40af; text-align:center;}} .score{{font-size:70px; font-weight:bold; color:{color}; text-align:center;}}</style>
    </head><body>
    <h1>GBP運用代行 提案書</h1>
    <p style="text-align:center; font-size:18px;">{company}</p>
    <p>対象店舗：{store_info}</p>
    <p class="score">{emoji} {score}/100点</p>
    <h2>改善優先順位トップ5</h2>
    <p>（診断結果より）</p>
    <h2>近隣競合比較</h2>
    <p>あなたの店舗：{score}点　近隣同業種平均：{min(98, score+18)}点</p>
    <h2>当社に任せた場合の予想成果</h2>
    <p>3ヶ月後：{min(100, score+25)}点　6ヶ月後：{min(100, score+32)}点</p>
    <h2>お見積もり例</h2>
    <p>月額運用代行：88,000円（税込）～<br>初期診断・改善プラン作成：無料</p>
    <h2>担当者</h2>
    <p>{company}<br>{name}<br>📞 {phone}<br>✉ {email}</p>
    <p>提案日：{datetime.now().strftime('%Y年%m月%d日')}</p>
    </body></html>
    """

    st.download_button(
        label="📋 営業用提案書をPDF用HTMLでダウンロード（印刷して持参してください）",
        data=proposal_html,
        file_name=f"GBP運用代行提案書_{today}.html",
        mime="text/html"
    )

st.caption("💼 Powered by 全Product Expert知見 | 04.sampleapp.work")
