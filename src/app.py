import streamlit as st
import os

# Import our backend functions
from rag import build_vector_store, ask_contract_question

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="LegalMind — Contract Intelligence",
    page_icon="§",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Handcrafted Design System ────────────────────────────────────────────────
# Palette: Midnight navy + warm copper/terracotta + dusty sage
# Aesthetic: "Editorial law journal meets modern fintech"
st.markdown("""
<style>
    /* ── Typography ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ══════════════════════════════════════════════════════
       GLOBAL RESET — Kill all white backgrounds
       ══════════════════════════════════════════════════════ */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"], .stApp,
    [data-testid="stAppViewBlockContainer"],
    .main, .main .block-container,
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    section.main,
    section.main > div,
    section.main > div > div,
    section.main > div > div > div,
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"],
    [data-testid="stMainBlockContainer"] {
        background-color: #0a0e1a !important;
        color: #e8e4dd !important;
    }

    .stApp {
        background: #0a0e1a !important;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stDeployButton"], .stDeployButton { display: none !important; }

    /* Keep header visible but dark */
    header[data-testid="stHeader"] {
        background: rgba(10, 14, 26, 0.95) !important;
        backdrop-filter: blur(16px) !important;
        border-bottom: 1px solid rgba(193, 127, 89, 0.06) !important;
        visibility: visible !important;
    }

    /* ── Force sidebar always visible ── */
    section[data-testid="stSidebar"] {
        transform: none !important;
        min-width: 280px !important;
        max-width: 320px !important;
        transition: none !important;
    }

    section[data-testid="stSidebar"][aria-expanded="false"] {
        transform: none !important;
        display: block !important;
        visibility: visible !important;
        min-width: 280px !important;
        margin-left: 0 !important;
        left: 0 !important;
    }

    /* ── Sidebar collapse button inside sidebar — Keep it visible ── */
    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
    section[data-testid="stSidebar"] button[kind="header"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNavCollapseButton"] {
        visibility: visible !important;
        display: none !important; /* Hide collapse button since sidebar is always shown */
    }

    /* ── If sidebar does collapse somehow, make the open button VERY visible ── */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: 1000000 !important;
        background: #c17f59 !important;
        color: #0a0e1a !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        cursor: pointer !important;
        box-shadow: 0 2px 12px rgba(193, 127, 89, 0.4) !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: #0a0e1a !important;
        stroke: #0a0e1a !important;
        color: #0a0e1a !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* ══════════════════════════════════════════════════════
       SIDEBAR — Deep charcoal with warm accent line
       ══════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: #080b14 !important;
        border-right: 1px solid rgba(193, 127, 89, 0.1) !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        background: #080b14 !important;
    }

    section[data-testid="stSidebar"] * {
        color: #a09b91 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e8e4dd !important;
        font-family: 'DM Serif Display', Georgia, serif !important;
    }

    /* ── File Uploader ── */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(193, 127, 89, 0.04) !important;
        border: 1.5px dashed rgba(193, 127, 89, 0.18) !important;
        border-radius: 10px !important;
        padding: 0.8rem !important;
        transition: all 0.4s ease !important;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
        border-color: rgba(193, 127, 89, 0.35) !important;
        background: rgba(193, 127, 89, 0.07) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        background: rgba(193, 127, 89, 0.12) !important;
        color: #c8a878 !important;
        border: 1px solid rgba(193, 127, 89, 0.2) !important;
        border-radius: 6px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
    }

    /* Force dark on every inner uploader element */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] *,
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div,
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] > div > div,
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section,
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] label,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
        background-color: transparent !important;
        background: transparent !important;
        color: #7a756c !important;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: rgba(193, 127, 89, 0.03) !important;
        border: none !important;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] small {
        color: #4a4640 !important;
    }

    /* ══════════════════════════════════════════════════════
       TYPOGRAPHY — Warm editorial feel
       ══════════════════════════════════════════════════════ */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'DM Serif Display', Georgia, serif !important;
        color: #e8e4dd !important;
    }

    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        font-family: 'DM Sans', sans-serif !important;
        color: #a09b91 !important;
    }

    /* ══════════════════════════════════════════════════════
       BUTTONS — Understated copper accent
       ══════════════════════════════════════════════════════ */
    div.stButton > button:first-child, div.stDownloadButton > button:first-child {
        background: transparent !important;
        border: 1px solid rgba(193, 127, 89, 0.2) !important;
        border-radius: 8px !important;
        color: #c8a878 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.65rem 1.2rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1) !important;
    }

    div.stButton > button:first-child:hover, div.stDownloadButton > button:first-child:hover {
        background: rgba(193, 127, 89, 0.1) !important;
        border-color: rgba(193, 127, 89, 0.4) !important;
        color: #dfc09a !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(193, 127, 89, 0.1) !important;
    }

    /* ══════════════════════════════════════════════════════
       CHAT — Dark containers, warm accents
       ══════════════════════════════════════════════════════ */
    [data-testid="stChatInput"] {
        background: #0a0e1a !important;
        border-top: 1px solid rgba(193, 127, 89, 0.08) !important;
    }

    [data-testid="stChatInput"] > div {
        background: #0a0e1a !important;
    }

    [data-testid="stChatInput"] textarea {
        background: #0f1322 !important;
        border: 1px solid rgba(193, 127, 89, 0.12) !important;
        border-radius: 10px !important;
        color: #e8e4dd !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.92rem !important;
        caret-color: #c17f59 !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(193, 127, 89, 0.35) !important;
        box-shadow: 0 0 0 3px rgba(193, 127, 89, 0.06) !important;
    }

    [data-testid="stChatInput"] button {
        background: rgba(193, 127, 89, 0.15) !important;
        color: #c8a878 !important;
        border: 1px solid rgba(193, 127, 89, 0.2) !important;
        border-radius: 8px !important;
    }

    [data-testid="stChatInput"] button svg {
        fill: #c8a878 !important;
        stroke: #c8a878 !important;
    }

    /* ── Nuclear: kill ALL remaining white backgrounds ── */
    [data-testid="stChatInput"] *,
    [data-testid="stBottom"] *,
    [data-testid="stBottomBlockContainer"] *,
    .stChatInput *,
    [data-baseweb] {
        background-color: transparent !important;
    }

    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] > div > div,
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottomBlockContainer"] > div {
        background: #0a0e1a !important;
        background-color: #0a0e1a !important;
    }

    [data-testid="stChatInput"] textarea {
        background: #0f1322 !important;
        background-color: #0f1322 !important;
    }

    /* Chat messages — unified style for BOTH user and assistant bubbles */
    [data-testid="stChatMessage"],
    [data-testid="stChatMessage-user"],
    [data-testid="stChatMessage-assistant"] {
        background: rgba(15, 19, 34, 0.8) !important;
        border: 1px solid rgba(193, 127, 89, 0.06) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        margin-bottom: 0.6rem !important;
        animation: msgReveal 0.5s cubic-bezier(0.22, 1, 0.36, 1) !important;
    }

    /* Kill Streamlit's role-specific inner container backgrounds */
    [data-testid="stChatMessage"] > div,
    [data-testid="stChatMessage"] > div > div,
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"] [class*="Message"],
    [data-testid="stChatMessage"] [class*="message"] {
        background: transparent !important;
        background-color: transparent !important;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span {
        color: #d4d0c8 !important;
        line-height: 1.75 !important;
        font-size: 0.92rem !important;
    }

    [data-testid="stChatMessage"] strong {
        color: #e8e4dd !important;
    }

    [data-testid="stChatMessage"] code {
        background: rgba(193, 127, 89, 0.08) !important;
        color: #c8a878 !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
    }

    /* ── Alerts ── */
    .stAlert, div[data-testid="stAlert"] {
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* ── Spinner ── */
    .stSpinner > div { border-top-color: #c17f59 !important; }
    .stSpinner > div > span { color: #a09b91 !important; }

    /* ── Divider ── */
    hr { border-color: rgba(193, 127, 89, 0.08) !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(193, 127, 89, 0.15); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(193, 127, 89, 0.3); }

    /* ══════════════════════════════════════════════════════
       ANIMATIONS
       ══════════════════════════════════════════════════════ */
    @keyframes msgReveal {
        0% { opacity: 0; transform: translateY(8px) scale(0.99); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes fadeUp {
        0% { opacity: 0; transform: translateY(16px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes drawLine {
        0% { width: 0; }
        100% { width: 100%; }
    }
    @keyframes subtlePulse {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
    }
    @keyframes slideInLeft {
        0% { opacity: 0; transform: translateX(-12px); }
        100% { opacity: 1; transform: translateX(0); }
    }

    /* ══════════════════════════════════════════════════════
       CUSTOM COMPONENT CLASSES
       ══════════════════════════════════════════════════════ */

    /* ── Monogram Brand Mark ── */
    .brand-mark {
        display: flex;
        align-items: center;
        gap: 14px;
        padding-bottom: 1.5rem;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(193, 127, 89, 0.1);
    }
    .brand-seal {
        width: 44px;
        height: 44px;
        border: 2px solid rgba(193, 127, 89, 0.35);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 1.15rem;
        color: #c8a878;
        letter-spacing: -0.02em;
        flex-shrink: 0;
    }
    .brand-name {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 1.15rem;
        color: #e8e4dd;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }
    .brand-tag {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.68rem;
        color: #5a5650;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-weight: 500;
        margin-top: 2px;
    }

    /* ── Section Label (small uppercase) ── */
    .sec-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.68rem;
        font-weight: 600;
        color: #5a5650;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.85rem;
    }

    /* ── Hero ── */
    .hero-wrap {
        padding: 2.5rem 0 1rem 0;
        animation: fadeUp 0.7s ease;
    }
    .hero-eyebrow {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
        color: #c17f59;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hero-eyebrow::before {
        content: '';
        display: block;
        width: 24px;
        height: 1.5px;
        background: #c17f59;
    }
    .hero-title {
        font-family: 'DM Serif Display', Georgia, serif !important;
        font-size: 3.2rem !important;
        font-weight: 400 !important;
        line-height: 1.08 !important;
        color: #e8e4dd !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 1.2rem !important;
    }
    .hero-title em {
        font-style: italic;
        color: #c17f59;
    }
    .hero-desc {
        font-family: 'DM Sans', sans-serif;
        font-size: 1.05rem;
        color: #6b6760;
        line-height: 1.7;
        max-width: 520px;
    }

    /* ── Horizontal Rule with Accent ── */
    .accent-rule {
        height: 1px;
        background: linear-gradient(90deg, rgba(193,127,89,0.25) 0%, rgba(193,127,89,0.02) 100%);
        margin: 2rem 0;
        animation: drawLine 1s ease forwards;
    }

    /* ── Stat Blocks (editorial style) ── */
    .stat-row {
        display: flex;
        gap: 0;
        border: 1px solid rgba(193, 127, 89, 0.08);
        border-radius: 12px;
        overflow: hidden;
        animation: fadeUp 0.9s ease;
    }
    .stat-block {
        flex: 1;
        padding: 1.4rem 1.5rem;
        border-right: 1px solid rgba(193, 127, 89, 0.08);
        transition: background 0.3s ease;
    }
    .stat-block:last-child { border-right: none; }
    .stat-block:hover { background: rgba(193, 127, 89, 0.03); }
    .stat-num {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 1.6rem;
        color: #c17f59;
        margin-bottom: 4px;
    }
    .stat-text {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.76rem;
        color: #5a5650;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500;
    }

    /* ── Process Steps (numbered editorial) ── */
    .step-card {
        background: rgba(15, 19, 34, 0.5);
        border: 1px solid rgba(193, 127, 89, 0.07);
        border-radius: 12px;
        padding: 1.6rem;
        transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
        animation: fadeUp 1s ease;
        position: relative;
    }
    .step-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 1.5rem;
        right: 1.5rem;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(193, 127, 89, 0.15), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .step-card:hover {
        border-color: rgba(193, 127, 89, 0.18);
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
    }
    .step-card:hover::after { opacity: 1; }
    .step-num {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 2rem;
        color: rgba(193, 127, 89, 0.2);
        line-height: 1;
        margin-bottom: 0.8rem;
    }
    .step-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.92rem;
        font-weight: 600;
        color: #e8e4dd;
        margin-bottom: 0.4rem;
    }
    .step-desc {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.82rem;
        color: #6b6760;
        line-height: 1.6;
    }

    /* ── Action Cards (for quick prompts) ── */
    .qaction-card {
        background: rgba(15, 19, 34, 0.5);
        border: 1px solid rgba(193, 127, 89, 0.07);
        border-radius: 12px;
        padding: 1.4rem;
        transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
        animation: fadeUp 0.8s ease;
        cursor: default;
    }
    .qaction-card:hover {
        border-color: rgba(193, 127, 89, 0.2);
        background: rgba(193, 127, 89, 0.04);
    }
    .qaction-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.65rem;
        font-weight: 600;
        color: #c17f59;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.5rem;
    }
    .qaction-title {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 1.05rem;
        color: #e8e4dd;
        margin-bottom: 0.35rem;
        line-height: 1.3;
    }
    .qaction-desc {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.78rem;
        color: #5a5650;
        line-height: 1.55;
    }

    /* ── Document Banner ── */
    .doc-banner {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 1rem 1.2rem;
        background: rgba(90, 138, 128, 0.06);
        border: 1px solid rgba(90, 138, 128, 0.12);
        border-left: 3px solid #5a8a80;
        border-radius: 4px 10px 10px 4px;
        margin-bottom: 2rem;
        animation: slideInLeft 0.6s ease;
    }
    .doc-indicator {
        width: 8px;
        height: 8px;
        background: #5a8a80;
        border-radius: 50%;
        animation: subtlePulse 2.5s ease-in-out infinite;
        flex-shrink: 0;
    }
    .doc-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        color: #5a5650;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500;
    }
    .doc-name {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.92rem;
        color: #7ab5a8;
        font-weight: 600;
    }

    /* ── Sidebar Extras ── */
    .cap-tag {
        display: inline-block;
        padding: 4px 10px;
        background: rgba(193, 127, 89, 0.05);
        border: 1px solid rgba(193, 127, 89, 0.1);
        border-radius: 5px;
        color: #7a756c;
        font-size: 0.68rem;
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        margin: 2px;
        letter-spacing: 0.02em;
    }

    .sidebar-doc-card {
        background: rgba(90, 138, 128, 0.05);
        border: 1px solid rgba(90, 138, 128, 0.1);
        border-radius: 8px;
        padding: 0.8rem 1rem;
    }
    .sidebar-doc-name {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.82rem;
        color: #7ab5a8;
        font-weight: 600;
    }
    .sidebar-doc-meta {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.7rem;
        color: #4a4640;
        margin-top: 3px;
    }

    .sidebar-empty {
        text-align: center;
        padding: 1.8rem 1rem;
        color: #3a3630;
        font-family: 'DM Sans', sans-serif;
    }
    .sidebar-empty-icon {
        font-size: 1.5rem;
        color: #2a2620;
        margin-bottom: 0.4rem;
        font-family: 'DM Serif Display', Georgia, serif;
    }

    .sidebar-footer {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.65rem;
        color: #2a2825;
        text-align: center;
        padding-top: 0.5rem;
        line-height: 1.6;
    }

    .processing-bar {
        background: rgba(193, 127, 89, 0.05);
        border: 1px solid rgba(193, 127, 89, 0.1);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        margin: 0.6rem 0;
    }
    .processing-text {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.82rem;
        color: #c8a878;
        font-weight: 500;
    }

    .empty-state-wrap {
        text-align: center;
        padding: 3.5rem 2rem;
        animation: fadeUp 0.8s ease;
    }
    .empty-initial {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 3rem;
        color: rgba(193, 127, 89, 0.12);
        margin-bottom: 0.8rem;
    }
    .empty-title {
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 1.2rem;
        color: #e8e4dd;
        margin-bottom: 0.4rem;
    }
    .empty-desc {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.85rem;
        color: #5a5650;
        max-width: 360px;
        margin: 0 auto;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Monogram brand
    st.markdown("""
    <div class="brand-mark">
        <div class="brand-seal">LM</div>
        <div>
            <div class="brand-name">LegalMind</div>
            <div class="brand-tag">Contract Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload section
    st.markdown('<div class="sec-label">Upload Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload contract PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        os.makedirs("data/contracts", exist_ok=True)
        file_path = os.path.join("data/contracts", uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
            st.markdown("""
            <div class="processing-bar">
                <div class="processing-text">Analyzing document structure...</div>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Building knowledge base..."):
                build_vector_store(file_path)
                st.session_state.last_uploaded = uploaded_file.name
                st.session_state.messages = []

            st.success("Analysis complete. Ready for questions.")

        # Active document
        st.markdown("---")
        st.markdown('<div class="sec-label">Active Document</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sidebar-doc-card">
            <div class="sidebar-doc-name">{uploaded_file.name}</div>
            <div class="sidebar-doc-meta">{round(uploaded_file.size / 1024, 1)} KB  /  PDF</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-empty">
            <div class="sidebar-empty-icon">{ }</div>
            <div style="font-size: 0.8rem; color: #4a4640;">No document loaded</div>
            <div style="font-size: 0.7rem; color: #3a3630; margin-top: 3px;">Upload a PDF to begin</div>
        </div>
        """, unsafe_allow_html=True)

    # Capabilities
    st.markdown("---")
    st.markdown('<div class="sec-label">Capabilities</div>', unsafe_allow_html=True)
    st.markdown("""
    <div>
        <span class="cap-tag">Entity Extraction</span>
        <span class="cap-tag">Date Detection</span>
        <span class="cap-tag">Risk Analysis</span>
        <span class="cap-tag">Clause Summary</span>
        <span class="cap-tag">Party Identification</span>
        <span class="cap-tag">Obligation Mapping</span>
    </div>
    """, unsafe_allow_html=True)

    # ─── NEW: Export Chat Feature ─────────────────────────────────────────────
    # Only show the download button if there is an active conversation
    if len(st.session_state.messages) > 0:
        st.markdown("---")
        st.markdown('<div class="sec-label">Export</div>', unsafe_allow_html=True)
        
        # Build the Markdown string for export
        export_text = f"# LegalMind Analysis Transcript\n**Document Analysed:** {st.session_state.last_uploaded}\n\n---\n\n"
        for msg in st.session_state.messages:
            role_title = "User" if msg["role"] == "user" else "LegalMind AI"
            export_text += f"### {role_title}\n{msg['content']}\n\n"
            
        st.download_button(
            label="📥 Download Chat Transcript",
            data=export_text,
            file_name="legalmind_transcript.md",
            mime="text/markdown",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-footer">
        Powered by Gemini 2.5 Flash<br>
        LangChain + ChromaDB RAG Pipeline
    </div>
    """, unsafe_allow_html=True)


# ─── Main Content ─────────────────────────────────────────────────────────────
if "last_uploaded" not in st.session_state:
    # ─── WELCOME SCREEN (no document) ─────────────────────────────────────
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-eyebrow">Contract Intelligence Platform</div>
        <div class="hero-title">
            Analyze contracts<br>
            with <em>precision</em>, not guesswork.
        </div>
        <div class="hero-desc">
            Upload any legal contract and surface parties, key dates,
            obligations, and hidden risks in seconds. Built on retrieval-augmented
            generation for grounded, cited answers you can trust.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="accent-rule"></div>', unsafe_allow_html=True)

    # Use-case showcase — what contracts you can analyze
    st.markdown('<div class="sec-label">What You Can Analyze</div>', unsafe_allow_html=True)
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        st.markdown("""
        <div class="step-card" style="padding: 1.2rem;">
            <div style="font-family: 'DM Serif Display', Georgia, serif; font-size: 1.2rem; color: #c17f59; margin-bottom: 0.5rem;">&sect;</div>
            <div class="step-title">Non-Disclosure</div>
            <div class="step-desc">NDAs, confidentiality clauses, trade secret protections.</div>
        </div>
        """, unsafe_allow_html=True)
    with u2:
        st.markdown("""
        <div class="step-card" style="padding: 1.2rem;">
            <div style="font-family: 'DM Serif Display', Georgia, serif; font-size: 1.2rem; color: #c17f59; margin-bottom: 0.5rem;">&para;</div>
            <div class="step-title">Employment</div>
            <div class="step-desc">Offer letters, non-competes, IP assignment agreements.</div>
        </div>
        """, unsafe_allow_html=True)
    with u3:
        st.markdown("""
        <div class="step-card" style="padding: 1.2rem;">
            <div style="font-family: 'DM Serif Display', Georgia, serif; font-size: 1.2rem; color: #c17f59; margin-bottom: 0.5rem;">&dagger;</div>
            <div class="step-title">Vendor Agreements</div>
            <div class="step-desc">MSAs, SLAs, service contracts, procurement terms.</div>
        </div>
        """, unsafe_allow_html=True)
    with u4:
        st.markdown("""
        <div class="step-card" style="padding: 1.2rem;">
            <div style="font-family: 'DM Serif Display', Georgia, serif; font-size: 1.2rem; color: #c17f59; margin-bottom: 0.5rem;">&copy;</div>
            <div class="step-title">Licensing</div>
            <div class="step-desc">Software licenses, IP licensing, royalty agreements.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # How it works — numbered steps
    st.markdown('<div class="sec-label">How It Works</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="step-card">
            <div class="step-num">01</div>
            <div class="step-title">Upload Your Contract</div>
            <div class="step-desc">
                Drop any PDF into the sidebar — NDAs, service agreements,
                employment contracts. The parser handles multi-page documents.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="step-card">
            <div class="step-num">02</div>
            <div class="step-title">Automatic Indexing</div>
            <div class="step-desc">
                The RAG pipeline chunks your document, creates vector embeddings,
                and builds a searchable knowledge base on the fly.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="step-card">
            <div class="step-num">03</div>
            <div class="step-title">Ask in Plain Language</div>
            <div class="step-desc">
                Chat naturally about your contract. The AI retrieves the most
                relevant clauses and delivers precise, grounded answers.
            </div>
        </div>
        """, unsafe_allow_html=True)


elif len(st.session_state.messages) == 0:
    # ─── DOCUMENT LOADED, NO CHAT YET — Quick Actions ────────────────────
    st.markdown(f"""
    <div class="doc-banner">
        <div class="doc-indicator"></div>
        <div>
            <div class="doc-label">Active Document</div>
            <div class="doc-name">{st.session_state.last_uploaded}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Quick Analysis</div>', unsafe_allow_html=True)

    # Row 1
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="qaction-card">
            <div class="qaction-label">Parties</div>
            <div class="qaction-title">Identify All Parties</div>
            <div class="qaction-desc">Extract disclosing and receiving parties, signatories, and their corporate roles.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Run analysis", key="btn_parties", use_container_width=True):
            st.session_state.quick_prompt = "Who is the Disclosing Party and who is the Receiving Party? List all parties mentioned in the contract with their roles."

    with col2:
        st.markdown("""
        <div class="qaction-card">
            <div class="qaction-label">Dates & Terms</div>
            <div class="qaction-title">Extract Key Dates</div>
            <div class="qaction-desc">Find effective dates, termination windows, renewal clauses, and notice periods.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Run analysis", key="btn_dates", use_container_width=True):
            st.session_state.quick_prompt = "What is the effective date and termination date of this agreement? List all important dates mentioned."

    with col3:
        st.markdown("""
        <div class="qaction-card">
            <div class="qaction-label">Risk Review</div>
            <div class="qaction-title">Restrictions & Risks</div>
            <div class="qaction-desc">Analyze confidentiality restrictions, non-compete clauses, and unusual obligations.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Run analysis", key="btn_risks", use_container_width=True):
            st.session_state.quick_prompt = "What are the main confidentiality restrictions placed on the Receiving Party? Are there any unusual or high-risk clauses?"

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="qaction-card">
            <div class="qaction-label">Overview</div>
            <div class="qaction-title">Executive Summary</div>
            <div class="qaction-desc">Generate a comprehensive summary covering purpose, key terms, and notable provisions.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Run analysis", key="btn_summary", use_container_width=True):
            st.session_state.quick_prompt = "Provide a comprehensive executive summary of this contract including the purpose, key terms, obligations of each party, and any notable clauses."

    with col5:
        st.markdown("""
        <div class="qaction-card">
            <div class="qaction-label">Obligations</div>
            <div class="qaction-title">Map Obligations</div>
            <div class="qaction-desc">Identify what each party is required to do, deliver, or refrain from under this agreement.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Run analysis", key="btn_obligations", use_container_width=True):
            st.session_state.quick_prompt = "What are the specific obligations of each party in this contract? List them separately for each party."

    with col6:
        st.markdown("""
        <div class="qaction-card">
            <div class="qaction-label">Liability</div>
            <div class="qaction-title">Liability & Indemnity</div>
            <div class="qaction-desc">Review limitation of liability caps, indemnification terms, and damages provisions.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Run analysis", key="btn_liability", use_container_width=True):
            st.session_state.quick_prompt = "Are there any limitation of liability clauses, indemnification provisions, or clauses about damages in this contract? Explain them."

    st.markdown("---")


# ─── Chat History Display ─────────────────────────────────────────────────────
for message in st.session_state.messages:
    role_avatar = "LM" if message["role"] == "assistant" else "You"
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

# ─── Chat Input ──────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask anything about your contract...")

if "quick_prompt" in st.session_state:
    user_input = st.session_state.quick_prompt
    del st.session_state.quick_prompt

if user_input:
    st.chat_message("user", avatar=None).markdown(user_input)

    # Build transcript
    chat_transcript = ""
    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "AI"
        chat_transcript += f"{role}: {msg['content']}\n"

    with st.chat_message("assistant", avatar=None):
        try:
            # ask_contract_question is a generator (yields streamed chunks).
            # st.write_stream() iterates it and renders each chunk live (typewriter effect),
            # then returns the full concatenated string so we can save it to history.
            answer = st.write_stream(ask_contract_question(user_input, chat_transcript))

            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error("Please ensure a document is uploaded and fully processed before asking questions.")
            print(f"Detailed Error: {e}")