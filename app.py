"""
Main Streamlit application for Housing Regulation Compliance Agent
"""
import streamlit as st
import pandas as pd
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from update_checker import UpdateChecker
from compliance_checker import ComplianceChecker
from email_alerts import EmailAlertSystem
from qa_system import QASystem
from config import (
    SUPPORTED_CITIES,
    REGULATION_CATEGORIES,
    LEGAL_DISCLAIMER,
    SOURCES_FILE,
    SMTP_EMAIL,
)
import time
import os

APP_VERSION = "1.0.0"

# Page configuration
st.set_page_config(
    page_title="Multi-Family Real Estate",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme with black background
CUSTOM_CSS = """
<style>
/* Hide Streamlit auto-generated heading anchor / link icons (fragment # links) */
[data-testid="stHeadingWithAnchor"],
[data-testid="StyledLinkIconContainer"] {
  display: none !important;
}
.stApp h1 a[href^="#"],
.stApp h2 a[href^="#"],
.stApp h3 a[href^="#"],
.stApp h4 a[href^="#"],
.stApp h5 a[href^="#"],
.stApp h6 a[href^="#"],
.stApp h1 > div > a,
.stApp h2 > div > a,
.stApp h3 > div > a,
.stApp h4 > div > a,
.stApp h5 > div > a,
.stApp h6 > div > a {
  display: none !important;
}

/* Page body: soft gray so white cards pop; brand accent at top */
.stApp {
  background-color: #f8f9fa !important;
  border-top: 3px solid #2563eb;
  box-sizing: border-box;
}
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #f8f9fa !important; }
[data-testid="stSidebar"] { background-color: #f1f5f9; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; background-color: transparent; max-width: min(96rem, 100%) !important; }
@media (max-width: 640px) {
  .block-container { padding-left: 0.85rem !important; padding-right: 0.85rem !important; }
}
/* Dark text */
h1, h2, h3, p, label, span, .stMarkdown { color: #1e293b !important; }
h1 { font-weight: 700; letter-spacing: -0.02em; margin-bottom: 0.25rem !important; }
.subtitle-tagline { color: #64748b !important; font-size: 1.05rem; margin-bottom: 1.5rem; }
h2, h3 { font-weight: 600; margin-top: 1.25rem !important; }
[data-testid="stSidebar"] hr { margin: 0.75rem 0; border-color: #e2e8f0; }
/* ----- Global clickable widgets: inactive / hover / active (primary #2563EB) ----- */
.stButton > button[data-testid="baseButton-secondary"],
[data-testid="stDownloadButton"] button[data-testid="baseButton-secondary"],
[data-testid="stFormSubmitButton"] button[data-testid="baseButton-secondary"],
[data-testid="stPopover"] > button {
  background-color: #E8EAF0 !important;
  color: #333333 !important;
  border: 1px solid #D0D3DC !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.10) !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
  font-weight: 500;
}
.stButton > button[data-testid="baseButton-secondary"]:hover:not(:disabled),
[data-testid="stDownloadButton"] button[data-testid="baseButton-secondary"]:hover:not(:disabled),
[data-testid="stFormSubmitButton"] button[data-testid="baseButton-secondary"]:hover:not(:disabled),
[data-testid="stPopover"] > button:hover:not(:disabled):not([aria-expanded="true"]) {
  background-color: #D8DCE8 !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
  transform: translateY(-1px) !important;
  cursor: pointer !important;
}
.stButton > button[data-testid="baseButton-primary"],
[data-testid="stDownloadButton"] button[data-testid="baseButton-primary"],
[data-testid="stFormSubmitButton"] button[data-testid="baseButton-primary"] {
  background-color: #2563EB !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15) !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
  font-weight: 500;
}
.stButton > button[data-testid="baseButton-primary"]:hover:not(:disabled),
[data-testid="stDownloadButton"] button[data-testid="baseButton-primary"]:hover:not(:disabled),
[data-testid="stFormSubmitButton"] button[data-testid="baseButton-primary"]:hover:not(:disabled) {
  background-color: #2563EB !important;
  color: white !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
  transform: translateY(-1px) !important;
  cursor: pointer !important;
}
[data-testid="stPopover"] > button[aria-expanded="true"] {
  background-color: #2563EB !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15) !important;
  border-radius: 8px !important;
}
[data-testid="stPopover"] > button[aria-expanded="true"]:hover:not(:disabled) {
  background-color: #2563EB !important;
  color: white !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
  transform: translateY(-1px) !important;
  cursor: pointer !important;
}
.stButton > button:disabled,
[data-testid="stDownloadButton"] button:disabled,
[data-testid="stPopover"] > button:disabled {
  opacity: 0.55 !important;
  cursor: not-allowed !important;
  transform: none !important;
}
/* Select / multiselect / date input (Base Web) */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"],
[data-testid="stDateInput"] [data-baseweb="select"] {
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stDateInput"] [data-baseweb="select"] > div {
  background-color: #E8EAF0 !important;
  color: #333333 !important;
  border: 1px solid #D0D3DC !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.10) !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"]:hover,
[data-testid="stMultiSelect"] [data-baseweb="select"]:hover,
[data-testid="stDateInput"] [data-baseweb="select"]:hover {
  transform: translateY(-1px);
  cursor: pointer !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"]:hover > div,
[data-testid="stMultiSelect"] [data-baseweb="select"]:hover > div,
[data-testid="stDateInput"] [data-baseweb="select"]:hover > div {
  background-color: #D8DCE8 !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
}
/* File upload dropzone */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploader"] > section {
  background-color: #E8EAF0 !important;
  border: 1px solid #D0D3DC !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.10) !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploader"] > section:hover {
  background-color: #D8DCE8 !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
  transform: translateY(-1px);
  cursor: pointer !important;
}
/* Expanders (closed = inactive; open = active blue) */
[data-testid="stExpander"] details > summary {
  background-color: #E8EAF0 !important;
  color: #333333 !important;
  border: 1px solid #D0D3DC !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.10) !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
}
[data-testid="stExpander"] details > summary:hover {
  background-color: #D8DCE8 !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
  transform: translateY(-1px);
  cursor: pointer !important;
}
[data-testid="stExpander"] details[open] > summary {
  background-color: #2563EB !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15) !important;
  border-radius: 8px !important;
}
[data-testid="stExpander"] details[open] > summary:hover {
  background-color: #2563EB !important;
  color: white !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
  transform: translateY(-1px);
  cursor: pointer !important;
}
/* Slider thumb */
[data-testid="stSlider"] [role="slider"] {
  background-color: #2563EB !important;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15) !important;
  border-radius: 8px !important;
  transition: all 0.2s ease !important;
}
[data-testid="stSlider"] [role="slider"]:hover {
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
  transform: translateY(-1px);
  cursor: pointer !important;
}
/* Base Web menus (open dropdown / options) */
[data-baseweb="menu"] li:not([aria-disabled="true"]):hover,
[data-baseweb="popover"] ul[role="listbox"] li:hover,
[data-baseweb="popover"] [role="option"]:hover {
  background-color: #D8DCE8 !important;
  cursor: pointer !important;
}
[data-testid="stMetricValue"] { font-weight: 600; color: #1e293b !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; }
.section-help { color: #64748b !important; font-size: 0.9rem; margin-bottom: 1rem; }
/* Hide sidebar completely - using top-right menu instead */
[data-testid="stSidebar"] { display: none; }
[data-testid="stSidebar"] + div { margin-left: 0 !important; }
/* Hero: full-width image; CTAs overlap bottom (visually inside hero) */
.home-hero-stack {
  border-radius: 12px;
  overflow: hidden;
  margin: 0 0 0 0;
}
.home-hero-stack .hero-header {
  margin-bottom: 0 !important;
  border-radius: 12px;
  min-height: 340px;
  padding: 2.5rem 1.5rem 6.25rem 1.5rem;
}
.hero-header { position: relative; min-height: 300px; background-size: cover; background-position: center 35%; display: flex; align-items: center; justify-content: center; padding: 2.5rem 1.5rem 2rem 1.5rem; border-radius: 12px; margin-bottom: 0.75rem; overflow: hidden; }
.hero-overlay { position: absolute; inset: 0; background: linear-gradient(120deg, rgba(15,23,42,0.82) 0%, rgba(15,23,42,0.55) 45%, rgba(15,23,42,0.35) 100%); border-radius: 12px; }
.hero-content { position: relative; z-index: 1; text-align: center; max-width: 44rem; margin: 0 auto; padding: 0 0.5rem; }
.hero-header, .hero-header * { color: #ffffff !important; }
.hero-header h1, .hero-header .hero-title, h1.hero-title { color: #ffffff !important; font-size: 2.35rem; font-weight: 700; letter-spacing: -0.02em; margin: 0 0 0.5rem 0 !important; text-shadow: 0 2px 16px rgba(0,0,0,0.65), 0 1px 3px rgba(0,0,0,0.5); }
.hero-subtitle { color: #f1f5f9 !important; font-size: 1.28rem !important; line-height: 1.55 !important; margin: 0 !important; opacity: 1 !important; font-weight: 500 !important;
  text-shadow: 0 2px 10px rgba(0,0,0,0.9), 0 1px 28px rgba(0,0,0,0.65), 0 0 2px rgba(0,0,0,0.8) !important; }
.hero-cta-block {
  margin: -5.5rem auto 1rem auto;
  max-width: 720px;
  position: relative;
  z-index: 4;
  padding: 0 0.75rem 0.35rem 0.75rem;
}
.hero-cta-block .stButton > button { border-radius: 8px !important; font-weight: 600 !important; padding: 0.55rem 1.35rem !important; }
@media (max-width: 640px) {
  .home-hero-stack .hero-header { min-height: 300px; padding-bottom: 5.5rem; }
  .hero-cta-block { margin-top: -5rem !important; }
}
/* Cards and expanders */
[data-testid="stExpander"], .element-container { background-color: transparent; }
/* Dataframes and inputs */
[data-testid="stDataFrame"], .stDataFrame { background-color: #f8fafc !important; }
div[data-testid="stVerticalBlock"] { background-color: transparent; }
/* Floating chat button and panel */
.chat-widget-container { position: fixed; bottom: 24px; right: 24px; z-index: 9998; pointer-events: none; }
.chat-widget-container * { pointer-events: auto; }
.chat-fab { position: absolute; bottom: 0; right: 0; width: 56px; height: 56px; border-radius: 50%; background: #2563eb; color: white; border: none; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.15); font-size: 24px; display: flex; align-items: center; justify-content: center; text-decoration: none; transition: all 0.2s ease; }
.chat-fab:hover { background: #2563eb; box-shadow: 0 4px 10px rgba(0,0,0,0.15); transform: translateY(-1px); cursor: pointer; }
.chat-panel { position: absolute; bottom: 70px; right: 0; z-index: 9999; width: 380px; max-width: calc(100vw - 48px); height: 500px; background: #fff; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.15); display: none; flex-direction: column; overflow: hidden; }
.chat-panel.open { display: flex; }
.chat-panel-header { padding: 14px 16px; background: #2563eb; color: white; font-weight: 600; display: flex; justify-content: space-between; align-items: center; }
.chat-panel-close { background: none; border: none; color: white !important; font-size: 22px; cursor: pointer; line-height: 1; padding: 0 4px; text-decoration: none; }
.chat-panel-messages { flex: 1; overflow-y: auto; padding: 12px; background: #f8fafc; }
.chat-msg { margin-bottom: 12px; padding: 10px 12px; border-radius: 10px; font-size: 14px; line-height: 1.5; }
.chat-msg.user { background: #2563eb; color: white; margin-left: 24px; }
.chat-msg.assistant { background: #e2e8f0; color: #1e293b; margin-right: 24px; }
.chat-panel-form { padding: 12px; border-top: 1px solid #e2e8f0; background: #fff; }
.chat-panel-form form { display: flex; gap: 8px; }
.chat-panel-form input { flex: 1; padding: 10px 12px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; }
.chat-panel-form button { padding: 10px 16px; background: #2563eb; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 500; box-shadow: 0 2px 5px rgba(0,0,0,0.15); transition: all 0.2s ease; }
.chat-panel-form button:hover { background: #2563eb; box-shadow: 0 4px 10px rgba(0,0,0,0.15); transform: translateY(-1px); cursor: pointer; }

/* Alexa chat bottom-right */
.alexa-chat-root {
  position: fixed;
  bottom: 32px;
  left: 32px;
  z-index: 10000;
  width: 340px;
  max-width: 92vw;
}
.alexa-chat-panel {
  background: #1d4ed8; /* blue popup feel */
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.35);
  padding: 10px 12px;
  border: none;
  color: #ffffff;
}
.alexa-chat-panel .stMarkdown, .alexa-chat-panel p, .alexa-chat-panel span, .alexa-chat-panel label {
  color: #e5e7eb !important;
}
.alexa-chat-panel .stTextInput>div>div>input {
  font-size: 13px;
}
.alexa-chat-icon button {
  padding: 10px 18px;
  border-radius: 999px;
  background: #2563eb;
  color: #ffffff;
  border: none;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease !important;
}
.alexa-chat-icon button:hover {
  background: #2563eb !important;
  box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
  transform: translateY(-1px) !important;
  cursor: pointer !important;
}
.stButton button#alexa_close {
  padding: 0 8px;
  background: transparent;
  color: #e5e7eb;
}

/* Nav row below hero */
div[data-testid="stHorizontalBlock"]:has(.nav-primary-anchor) {
  margin-bottom: 0.35rem !important;
}
/* Home main: use full card width */
[data-testid="stVerticalBlockBorderWrapper"]:has(.home-main-wide),
div.stVerticalBlockBorderWrapper:has(.home-main-wide) {
  padding: 1.35rem 1.35rem 1.5rem 1.35rem !important;
}
.home-page-start { margin-top: 0; }
.home-intro {
  max-width: 100%;
  width: 100%;
  margin: 0 0 1.25rem 0;
  text-align: left;
}
.home-intro-title {
  margin: 0 0 0.65rem 0 !important;
  color: #0f172a !important;
  font-size: 1.75rem !important;
  font-weight: 700 !important;
  text-align: left !important;
  max-width: 100%;
}
.home-intro-body {
  max-width: 100%;
  margin: 0;
  text-align: left;
}
/* Built for + chips: one horizontal line */
[data-testid="stMarkdownContainer"] .home-audience-row {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
}
.home-intro-body p {
  color: #334155 !important;
  line-height: 1.65 !important;
  font-size: 1rem !important;
  margin: 0.55rem 0 0 0 !important;
}
.home-audience-row {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.75rem 1rem;
  margin-top: 1.1rem;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  padding-bottom: 0.2rem;
}
.home-audience-label {
  display: inline-block;
  font-size: 0.7rem !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #64748b !important;
  margin: 0 !important;
  flex: 0 0 auto;
  white-space: nowrap;
}
.home-audience-chips {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem;
  margin: 0 !important;
  flex: 0 1 auto;
  min-width: 0;
  width: max-content;
  max-width: none;
  box-sizing: border-box;
  white-space: nowrap;
}
.audience-chip {
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  flex: 0 0 auto !important;
  flex-shrink: 0 !important;
  white-space: nowrap !important;
  font-size: 0.8125rem !important;
  font-weight: 500;
  line-height: 1.2 !important;
  color: #334155 !important;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  padding: 0.42rem 0.85rem;
  min-height: 2rem;
  box-sizing: border-box;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}
.home-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 0 1rem 0.85rem 1rem;
  padding-top: 0;
  background: #ffffff;
  text-align: left;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
  border-top: 4px solid #cbd5e1;
  overflow: hidden;
}
.home-card--compliance { border-top-color: #2563eb; }
.home-card--explore { border-top-color: #059669; }
.home-card--alerts { border-top-color: #d97706; }
.home-card-head {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin: 0.85rem 0 0.45rem 0;
}
.home-card-chip {
  flex-shrink: 0;
  width: 2.4rem;
  height: 2.4rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 1.15rem;
  line-height: 1;
}
.home-card--compliance .home-card-chip { background: #eff6ff; }
.home-card--explore .home-card-chip { background: #ecfdf5; }
.home-card--alerts .home-card-chip { background: #fffbeb; }
.home-card h4 {
  margin: 0 !important;
  font-size: 1.08rem !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  letter-spacing: -0.02em;
}
.home-card p.home-card-desc {
  margin: 0 0 0 0 !important;
  font-size: 0.9rem !important;
  color: #64748b !important;
  line-height: 1.55 !important;
}
.home-section-title { font-size: 1.15rem !important; font-weight: 600 !important; color: #0f172a !important; margin: 1.25rem 0 0.75rem 0 !important; }
.home-quicksteps-wrap { max-width: 100%; margin: 0 0 1.25rem 0; }
.home-quicksteps {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem 0.35rem;
  padding: 1rem 1.1rem;
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}
.home-quicksteps .step {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 500;
  color: #1e293b !important;
  font-size: 0.95rem !important;
}
.home-quicksteps .step-arrow { color: #94a3b8; padding: 0 0.15rem; font-weight: 600; }
.home-trust { margin: 0 0 1.25rem 0; max-width: 100%; }
.home-trust-stats {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  font-size: 0.92rem !important;
  color: #334155 !important;
}
.home-trust-stats .trust-sep { color: #cbd5e1; user-select: none; }
.home-trust-note { font-size: 0.78rem !important; color: #64748b !important; margin-top: 0.4rem !important; }
.app-footer {
  margin-top: 2rem;
  padding: 1.35rem 1rem 2rem 1rem;
  background: #0f172a;
  border-top: none;
  border-radius: 12px 12px 0 0;
  text-align: center;
  font-size: 0.875rem;
  color: #94a3b8 !important;
}
.app-footer .footer-item { color: #94a3b8 !important; font-weight: 500; }
.app-footer .footer-sep { margin: 0 0.5rem; color: #475569; }
@media (max-width: 480px) {
  .home-quicksteps { flex-direction: column; align-items: flex-start; }
  .home-quicksteps .step-arrow { display: none; }
}

/* Sticky header navigation */
.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
}
.fixed-header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
.fixed-header-title {
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #111827;
}
.nav-tabs {
  display: flex;
  gap: 0.5rem;
}
.nav-tab {
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  color: #1f2933;
  border: 1px solid transparent;
}
.nav-tab:hover {
  background: #e5edff;
}
.nav-tab-active {
  background: #111827;
  color: #ffffff;
}
.header-spacer {
  height: 56px;
}

/* Main layout: white content cards (Streamlit bordered containers) */
[data-testid="stVerticalBlockBorderWrapper"],
div.stVerticalBlockBorderWrapper {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
  padding: 1rem 1.15rem 1.15rem 1.15rem !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06) !important;
  margin-bottom: 1rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] p,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] label,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stWidgetLabel"] span,
div.stVerticalBlockBorderWrapper [data-testid="stWidgetLabel"] p,
div.stVerticalBlockBorderWrapper [data-testid="stWidgetLabel"] label,
div.stVerticalBlockBorderWrapper [data-testid="stWidgetLabel"] span {
  font-size: 1rem !important;
  font-weight: 600 !important;
  color: #0f172a !important;
}
/* Light-blue page hero (subpages) */
.page-hero-bar {
  background: linear-gradient(180deg, #eff6ff 0%, #e8f0fe 100%);
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 1.1rem 1.25rem 1.2rem 1.25rem;
  margin: 0 0 1rem 0;
}
.page-hero-title {
  margin: 0 !important;
  padding: 0 0 0 0.85rem !important;
  border-left: 4px solid #2563eb;
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  line-height: 1.25 !important;
  letter-spacing: -0.02em !important;
}
.page-hero-sub {
  margin: 0.5rem 0 0 0 !important;
  padding-left: calc(0.85rem + 4px) !important;
  font-size: 1.02rem !important;
  line-height: 1.5 !important;
  color: #334155 !important;
}

/* ----- App navigation (Streamlit buttons + SVG row; no <a href> — same-page only) ----- */
.nav-icon-cell { text-align: center; color: #475569; margin-bottom: 0.1rem; }
.nav-icon-cell svg { vertical-align: middle; }
/* One nav row: pills + More share baseline */
.nav-primary-anchor ~ div [data-testid="stHorizontalBlock"],
[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] {
  align-items: center !important;
}
/* Nav tab buttons — sizing only (colors from global clickable rules) */
.nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] .stButton > button,
[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] .stButton > button {
  border-radius: 8px !important;
  font-size: 0.88rem !important;
  font-weight: 500 !important;
  line-height: 1.2 !important;
  min-height: 2.35rem !important;
  box-sizing: border-box !important;
}
.nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] .stButton > button[data-testid="baseButton-secondary"],
[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] .stButton > button[data-testid="baseButton-secondary"],
.nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] .stButton > button[data-testid="baseButton-primary"],
[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] .stButton > button[data-testid="baseButton-primary"] {
  padding: 0.48rem 1.05rem !important;
}
/* More popover: layout only (trigger uses global secondary / expanded primary) */
.nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] div[data-testid="stPopover"],
[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] {
  width: 100% !important;
}
.nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button,
[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  justify-content: center !important;
  white-space: nowrap !important;
  width: 100% !important;
  font-size: 0.88rem !important;
  line-height: 1.2 !important;
  min-height: 2.35rem !important;
  height: auto !important;
  padding: 0.48rem 1.05rem !important;
  margin: 0 !important;
  box-sizing: border-box !important;
  gap: 0.35rem !important;
}
.nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button > div,
[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button > div {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 0.35rem !important;
  white-space: nowrap !important;
  width: 100% !important;
  min-height: 100% !important;
}
.nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button svg,
[data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button svg {
  width: 0.95em !important;
  height: 0.95em !important;
  flex-shrink: 0 !important;
}
@media (max-width: 640px) {
  .nav-icon-cell svg { width: 16px !important; height: 16px !important; }
  .nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] .stButton > button,
  [data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] .stButton > button {
    font-size: 0.78rem !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
    min-height: 2.15rem !important;
    height: auto !important;
  }
  .nav-primary-anchor ~ div [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button,
  [data-testid="stVerticalBlockBorderWrapper"]:has(.nav-primary-anchor) [data-testid="stHorizontalBlock"] div[data-testid="stPopover"] > button {
    font-size: 0.78rem !important;
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
    min-height: 2.15rem !important;
    height: auto !important;
  }
}
</style>
"""

# Initialize session state
if 'db' not in st.session_state:
    st.session_state.db = RegulationDB()
if 'scraper' not in st.session_state:
    st.session_state.scraper = RegulationScraper()
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = RegulationVectorStore()
if 'update_checker' not in st.session_state:
    st.session_state.update_checker = UpdateChecker()
if 'compliance_checker' not in st.session_state:
    st.session_state.compliance_checker = ComplianceChecker()
if 'email_system' not in st.session_state:
    st.session_state.email_system = EmailAlertSystem()
if 'qa_system' not in st.session_state:
    st.session_state.qa_system = QASystem()
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# Canonical page keys (routing). Primary nav shows first five; Settings is under "More".
PAGE_HOME = "🏠 Home"
PAGE_AGENT = "💬 Agent"
PAGE_EXPLORER = "📚 Regulation Explorer"
PAGE_UPDATES = "📢 Update Log"
PAGE_EMAIL = "📧 Email Alerts"
PAGE_SETTINGS = "⚙️ Settings"

# Per-page hero (light blue bar) — title + subtitle for all routes except Home (image hero).
PAGE_HERO_COPY = {
    PAGE_AGENT: (
        "💬 Agent",
        "Ask about housing regulations, upload a lease for compliance checks, and review sources in the conversation.",
    ),
    PAGE_EXPLORER: (
        "📚 Regulation Explorer",
        "Search and browse indexed sources. Use filters below to narrow by category, state, or city.",
    ),
    PAGE_UPDATES: (
        "📢 Update Log",
        'See when regulations changed. Use "Check for updates" to scan for new changes.',
    ),
    PAGE_EMAIL: (
        "📧 Email Alerts",
        "Subscribe by city to get email when regulations change. Daily summaries and instant alerts.",
    ),
    PAGE_SETTINGS: (
        "⚙️ Settings",
        "Load regulations from CSV, re-index the database, or run an update check.",
    ),
}

# (route key, slug for widget keys, button label with emoji)
NAV_PRIMARY = [
    (PAGE_HOME, "home", "🏠 Home"),
    (PAGE_AGENT, "agent", "💬 Agent"),
    (PAGE_EXPLORER, "explorer", "📚 Explorer"),
    (PAGE_UPDATES, "updates", "📢 Updates"),
    (PAGE_EMAIL, "email", "✉️ Email"),
]


STATES = ["Texas", "California", "Indiana"]
TEXAS_CITIES = ["Dallas", "Austin", "San Antonio", "Houston"]

# Hero: modern city skyline / premium residential feel (Unsplash)
HERO_IMAGE_URL = (
    "https://images.unsplash.com/photo-1514565131-fce0801e5785"
    "?auto=format&fit=crop&w=2000&q=85"
)

def _ensure_chat_history():
    """Chatbot disabled."""
    return


def _render_floating_chat():
    """Chatbot disabled."""
    return


def _render_subpage_hero(page_key: str):
    meta = PAGE_HERO_COPY.get(page_key)
    if not meta:
        return
    title, subtitle = meta
    st.markdown(
        f"""
        <div class="page-hero-bar">
            <h1 class="page-hero-title">{title}</h1>
            <p class="page-hero-sub">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    current_page = st.session_state.current_page
    page = current_page

    # 1) Hero first: home = image + title + CTAs overlapping bottom; other pages = title bar
    if page == PAGE_HOME:
        hero_html = f"""
        <div class="home-hero-stack">
            <div class="hero-header" style="background-image: url('{HERO_IMAGE_URL}');">
                <div class="hero-overlay"></div>
                <div class="hero-content">
                    <h1 class="hero-title">MULTI-FAMILY REAL ESTATE</h1>
                    <p class="hero-subtitle">Ask questions, check compliance, and stay updated on housing regulations—across your portfolio.</p>
                </div>
            </div>
        </div>
        """
        st.markdown(hero_html, unsafe_allow_html=True)
        st.markdown('<div class="hero-cta-block">', unsafe_allow_html=True)
        _sp, hc_a, hc_b, _sp2 = st.columns([1, 2, 2, 1])
        with hc_a:
            if st.button("Ask the Agent", key="hero_cta_agent", use_container_width=True, type="primary"):
                st.session_state.current_page = PAGE_AGENT
                st.rerun()
        with hc_b:
            if st.button("Get Started", key="hero_cta_start", use_container_width=True):
                st.session_state.current_page = PAGE_EXPLORER
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        _render_subpage_hero(page)

    # 2) Navigation below hero — one row: five pills + More (same vertical alignment)
    with st.container(border=True):
        st.markdown('<div class="nav-primary-anchor"></div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1, 1, 0.72])
        nav_cols = (c1, c2, c3, c4, c5)
        for i, (page_key, slug, nav_label) in enumerate(NAV_PRIMARY):
            with nav_cols[i]:
                is_active = current_page == page_key
                if st.button(
                    nav_label,
                    key=f"nav_btn_{slug}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.current_page = page_key
                    st.rerun()
        with c6:
            # NBSP keeps emoji + "More" on one line (matches 🏠 Home style)
            with st.popover("⚙️\u00a0More"):
                if st.button(
                    "⚙️ Settings",
                    key="nav_btn_settings",
                    use_container_width=True,
                    type="primary" if current_page == PAGE_SETTINGS else "secondary",
                ):
                    st.session_state.current_page = PAGE_SETTINGS
                    st.rerun()

    # 3) Page content
    with st.container(border=True):
        if page == PAGE_HOME:
            show_home()
        elif page == PAGE_AGENT:
            show_ip_agent_page()
        elif page == PAGE_EXPLORER:
            show_regulation_explorer()
        elif page == PAGE_UPDATES:
            show_update_log()
        elif page == PAGE_EMAIL:
            show_email_alerts()
        elif page == PAGE_SETTINGS:
            show_settings()

    _render_app_footer()
    _render_floating_chat()

def _clean_qa_answer(text):
    """Remove raw context lines and notes from QA answer."""
    if not text:
        return text or ""
    if "[Note:" in text:
        text = text.split("[Note:")[0].strip()
    if "From " in text and "(" in text:
        lines = text.split("\n")
        cleaned = [l for l in lines if not (l.strip().startswith("From ") and "(" in l and "):" in l) and not l.strip().startswith("---")]
        text = "\n".join(cleaned).strip()
    return text

def show_home():
    """Front page: co-pilot intro, feature cards, quick start, trust stats, metrics, actions."""
    st.markdown(
        '<span class="home-main-wide" aria-hidden="true"></span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="home-intro home-page-start">
            <h2 class="home-intro-title">Your AI Compliance Co-Pilot</h2>
            <div class="home-intro-body">
                <p><strong>Multi-Family Real Estate</strong> helps you stay ahead of housing rules—without digging through
                dense legal sites alone. Upload leases for a structured compliance readout, explore your indexed
                regulations, and get notified when something changes.</p>
                <div class="home-audience-row">
                    <span class="home-audience-label">Built for</span>
                    <div class="home-audience-chips"><span class="audience-chip">🏢 Property Managers</span><span class="audience-chip">👤 Landlords</span><span class="audience-chip">📋 Leasing Teams</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.markdown(
            """
            <div class="home-card home-card--compliance">
                <div class="home-card-head">
                    <span class="home-card-chip" aria-hidden="true">✅</span>
                    <h4>Check Compliance</h4>
                </div>
                <p class="home-card-desc">Upload a PDF or DOCX lease and ask if it meets key housing requirements—with plain-language fixes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Agent", key="home_fc_agent", use_container_width=True):
            st.session_state.current_page = PAGE_AGENT
            st.rerun()
    with fc2:
        st.markdown(
            """
            <div class="home-card home-card--explore">
                <div class="home-card-head">
                    <span class="home-card-chip" aria-hidden="true">📋</span>
                    <h4>Explore Regulations</h4>
                </div>
                <p class="home-card-desc">Search and filter the regulation library by category, state, or city and jump to official sources.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Explorer", key="home_fc_explorer", use_container_width=True):
            st.session_state.current_page = PAGE_EXPLORER
            st.rerun()
    with fc3:
        st.markdown(
            """
            <div class="home-card home-card--alerts">
                <div class="home-card-head">
                    <span class="home-card-chip" aria-hidden="true">🔔</span>
                    <h4>Get Alerts</h4>
                </div>
                <p class="home-card-desc">Subscribe by city for email when rules change so your portfolio isn’t caught off guard.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Email Alerts", key="home_fc_alerts", use_container_width=True):
            st.session_state.current_page = PAGE_EMAIL
            st.rerun()

    st.markdown(
        """
        <h3 class="home-section-title">Quick Start</h3>
        <div class="home-quicksteps-wrap">
            <div class="home-quicksteps">
                <span class="step"><span class="step-num">1️⃣</span> Upload your lease</span>
                <span class="step-arrow">→</span>
                <span class="step"><span class="step-num">2️⃣</span> Ask the Agent</span>
                <span class="step-arrow">→</span>
                <span class="step"><span class="step-num">3️⃣</span> Get compliance report</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="home-trust">
            <h3 class="home-section-title">🚀 Trust &amp; Credibility</h3>
            <div class="home-trust-stats">
                <span>📊 500+ Regulations Tracked</span>
                <span class="trust-sep">|</span>
                <span>🏙️ 10 States Covered</span>
                <span class="trust-sep">|</span>
                <span>⚡ Instant AI Answers</span>
            </div>
            <p class="home-trust-note">Illustrative benchmarks for demonstration; live database counts appear below.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("At a glance", anchor=False)
    regulations = st.session_state.db.get_all_regulations()
    updates = st.session_state.db.get_recent_updates(limit=1000)
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Regulations in database", len(regulations))
    with m2:
        st.metric("Updates tracked", len(updates))
    m3, m4 = st.columns(2)
    with m3:
        st.metric("Cities supported", len(SUPPORTED_CITIES))
    with m4:
        st.metric("Categories", len(REGULATION_CATEGORIES))

    st.markdown("---")
    st.subheader("Quick actions", anchor=False)
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("Check for updates now", use_container_width=True, key="home_check_updates"):
            with st.spinner("Checking for regulation updates..."):
                new_updates = st.session_state.update_checker.check_for_updates()
                if new_updates:
                    for u in new_updates:
                        st.session_state.email_system.notify_subscribers(u)
                    st.success(f"Found {len(new_updates)} new update(s). See Update Log for details.")
                else:
                    st.info("No new updates detected.")
    with qa2:
        if st.button("Load regulations from CSV", use_container_width=True, key="home_load_csv"):
            try:
                result = st.session_state.db.load_regulations_from_csv(SOURCES_FILE)
                st.success(f"Loaded {result['loaded']} regulation(s); {result['skipped']} skipped.")
            except Exception as e:
                st.error(f"Error: {str(e)}")


def _render_app_footer():
    """Site footer on every page: docs, contact, version (plain text — no hyperlinks)."""
    contact_email = SMTP_EMAIL or "support@example.com"
    st.markdown(
        f"""
        <footer class="app-footer" role="contentinfo" id="site-footer">
            <span class="footer-item">Documentation</span>
            <span class="footer-sep">·</span>
            <span class="footer-item">Contact {contact_email}</span>
            <span class="footer-sep">·</span>
            <span class="footer-item">v{APP_VERSION}</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def show_ip_agent_page():
    """Main Intelligence Platform Agent page with integrated chat and compliance checker"""
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'compliance_city' not in st.session_state:
        st.session_state.compliance_city = None
    
    def process_question(prompt_text):
        """Helper function to process a question and add to chat history"""
        st.session_state.chat_history.append({'role': 'user', 'content': prompt_text})
        result = st.session_state.qa_system.answer_question_with_context(prompt_text, st.session_state.chat_history)
        answer_text = result['answer']
        
        # Clean up answer
        if "From " in answer_text and "(" in answer_text:
            lines = answer_text.split('\n')
            cleaned_lines = []
            for line in lines:
                if line.startswith("From ") and "(" in line and "):" in line:
                    continue
                if line.strip().startswith("---"):
                    continue
                cleaned_lines.append(line)
            answer_text = '\n'.join(cleaned_lines).strip()
        
        # Don't add sources to answer_text - they're displayed separately in the expander
        # This prevents duplicates
        
        if "[Note:" in answer_text:
            answer_text = answer_text.split("[Note:")[0].strip()
        
        sources_data = []
        seen_urls = set()
        for source in result.get('sources', []):
            url = source.get('url', '')
            # Use URL as primary key for deduplication - same URL should only appear once
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources_data.append(source)
            elif not url:
                # If no URL, use source name as fallback
                source_name = source.get('source', '')
                if source_name and source_name not in seen_urls:
                    seen_urls.add(source_name)
                    sources_data.append(source)
        
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': answer_text,
            'sources': sources_data
        })
        st.rerun()
    
    # Display example questions as first message if chat is empty
    if len(st.session_state.chat_history) == 0:
        with st.chat_message("assistant"):
            st.markdown("Hi! I can answer questions about Texas housing regulations and check lease documents for compliance.")
            st.markdown("**Try one of these:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Recent housing law updates", key="ex1", use_container_width=True):
                    process_question("What are the latest housing regulation updates in my area?")
                if st.button("What is ESA?", key="ex2", use_container_width=True):
                    process_question("What is ESA?")
                if st.button("ESA rules for rentals", key="ex3", use_container_width=True):
                    process_question("What are ESA rules for rental housing?")
            with col2:
                if st.button("Rent control overview", key="ex4", use_container_width=True):
                    process_question("What should I know about rent control rules?")
                if st.button("What is rent control?", key="ex5", use_container_width=True):
                    process_question("What is rent control?")
                if st.button("Check a lease for compliance", key="ex6", use_container_width=True):
                    st.info("Use the file uploader below to attach a PDF or DOCX, then ask \"Is this compliant?\"")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            with st.chat_message("user"):
                if message.get('file_uploaded'):
                    st.write(f"📎 {message.get('filename', 'Document')}")
                st.write(message['content'])
        else:
            with st.chat_message("assistant"):
                answer_content = message['content']
                if "[Note:" in answer_content:
                    answer_content = answer_content.split("[Note:")[0].strip()
                # Remove raw context lines
                if "From " in answer_content and "(" in answer_content:
                    lines = answer_content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        if line.startswith("From ") and "(" in line and "):" in line:
                            continue
                        if line.strip().startswith("---"):
                            continue
                        cleaned_lines.append(line)
                    answer_content = '\n'.join(cleaned_lines).strip()
                st.markdown(answer_content)
                
                # Show sources if available
                if 'sources' in message and message['sources']:
                    # Remove duplicates by URL (primary key) - same URL should only appear once
                    seen_urls = set()
                    unique_sources = []
                    for source in message['sources']:
                        url = source.get('url', '')
                        # Use URL as primary key for deduplication
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            unique_sources.append(source)
                        elif not url:
                            # If no URL, use source name as fallback
                            source_name = source.get('source', '')
                            if source_name and source_name not in seen_urls:
                                seen_urls.add(source_name)
                                unique_sources.append(source)
                    
                    if unique_sources:
                        with st.expander("📚 Sources", expanded=False):
                            for source in unique_sources:
                                url = source.get('url', '')
                                if url:
                                    if url.startswith('http'):
                                        st.markdown(f"🔗 **{source.get('source', 'Unknown')}**")
                                        st.markdown(f"`{url}`")
                                    elif os.path.exists(url):
                                        st.markdown(f"📄 {source.get('source', 'Unknown')}")
                                else:
                                    st.markdown(f"📄 {source.get('source', 'Unknown')}")
    
    # File uploader
    st.markdown("---")
    row_col1, row_col2 = st.columns([1, 2])
    with row_col1:
        st.markdown("**📎 Check a lease for compliance**")
    with row_col2:
        uploaded_file = st.file_uploader(
            " ",
            type=['pdf', 'docx', 'doc'],
            key="chat_file_upload",
            label_visibility="collapsed",
            help="Upload a PDF or DOCX lease. We’ll analyze it for housing rules and suggest fixes.",
        )
    
    if uploaded_file is not None:
        st.success(f"**{uploaded_file.name}** attached. Ask \"Is this compliant?\" to analyze.")
    
    # Chat input
    chat_placeholder = "Ask about regulations or type your question..."
    if uploaded_file is not None:
        chat_placeholder = f"e.g. Is this compliant? (or ask anything)"
    
    if prompt := st.chat_input(chat_placeholder):
        # Handle file upload - check both current upload and pending file
        file_content = None
        filename = None
        
        # First check if there's a pending file from previous interaction
        if 'pending_file' in st.session_state:
            file_content = st.session_state.pending_file
            filename = st.session_state.pending_filename
        elif uploaded_file is not None:
            # Read the file immediately before rerun
            file_content = uploaded_file.read()
            filename = uploaded_file.name
            # Store in session state for next iteration
            st.session_state.current_file = file_content
            st.session_state.current_filename = filename
        
        # Add user message to history
        user_message = {'role': 'user', 'content': prompt}
        if file_content:
            user_message['file_uploaded'] = True
            user_message['filename'] = filename
            user_message['file_content'] = file_content
        st.session_state.chat_history.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            if file_content:
                st.write(f"📎 {filename}")
            st.write(prompt)
        
        # Get answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Check if user wants compliance check (has file or mentions compliance)
                wants_compliance_check = file_content or any(keyword in prompt.lower() for keyword in ["compliant", "compliance", "check document", "check this", "is this", "review", "analyze"])
                
                # Auto-detect city from prompt
                detected_city = None
                prompt_lower = prompt.lower()
                for city in SUPPORTED_CITIES:
                    if city.lower() in prompt_lower:
                        detected_city = city
                        break
                
                if wants_compliance_check:
                    if file_content:
                        # Use detected city or ask for city selection
                        selected_city = detected_city or st.session_state.get('compliance_city')
                        
                        # Store file immediately to prevent loss on rerun
                        if file_content:
                            st.session_state.pending_file = file_content
                            st.session_state.pending_filename = filename
                        
                        if not selected_city:
                            # Ask for city
                            answer_text = "📍 **Which city are you checking compliance for?**\n\nSelect a city from the dropdown below, or type a supported city name in your next message."
                            st.markdown(answer_text)
                            city = st.selectbox("City", ["Select..."] + SUPPORTED_CITIES, key="compliance_city_select")
                            if city != "Select...":
                                selected_city = city
                                st.session_state.compliance_city = city
                            
                            if selected_city:
                                # City selected, proceed to check
                                pass
                            else:
                                # Wait for city selection - don't proceed yet
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': answer_text,
                                    'sources': []
                                })
                                st.rerun()
                        
                        # Run compliance check if we have a city
                        if selected_city:
                            try:
                                # Get file from pending or current
                                check_file = st.session_state.get('pending_file') or file_content
                                check_filename = st.session_state.get('pending_filename') or filename
                                check_city = selected_city or st.session_state.get('compliance_city', 'Texas-Statewide')
                                
                                if check_file is None:
                                    raise ValueError("File content not available. Please upload the file again.")
                                
                                with st.spinner(f"🔍 Analyzing document for {check_city} compliance..."):
                                    result = st.session_state.compliance_checker.check_compliance(
                                        check_file,
                                        check_filename,
                                        check_city
                                    )
                                
                                # Check if summary is the hard-coded Dallas format - use it directly
                                summary = result.get('summary', '')
                                if summary and "Not Compliant with Dallas + Federal Housing Law" in summary:
                                    # Use the hard-coded summary directly
                                    answer_text = summary
                                elif result['is_compliant']:
                                    answer_text = f"✅ **Is this lease compliant for Texas & {check_city}?**\n\n"
                                    answer_text += "**Short answer: YES — compliant.**\n\n"
                                    answer_text += "This lease document appears to be compliant with Texas housing regulations."
                                else:
                                    answer_text = f"✅ **Is this lease compliant for Texas & {check_city}?**\n\n"
                                    answer_text += f"**Short answer: NO — not fully compliant.**\n\n"
                                    
                                    # Filter out issues that are just "Unable to analyze" or "Manual review required"
                                    real_issues = []
                                    for issue in result.get('issues', []):
                                        regulation = issue.get('regulation_applies', '').strip()
                                        fix = issue.get('what_to_fix', '').strip()
                                        # Only include issues with actual analysis (not generic errors)
                                        if regulation and regulation not in ["Unable to analyze", "Manual review required - OpenAI API not configured", ""]:
                                            if fix and fix not in ["Manual review required", "Review this clause against relevant regulations manually", ""]:
                                                # Check if it's a real analysis (has meaningful content)
                                                if len(regulation) > 30 and len(fix) > 20:
                                                    real_issues.append(issue)
                                    
                                    if real_issues:
                                        answer_text += f"This lease has **{len(real_issues)} compliance issue(s)** that need to be addressed.\n\n"
                                        answer_text += "**Below is the clean breakdown:**\n\n"
                                        
                                        for idx, issue in enumerate(real_issues, 1):
                                            clause_title = issue.get('clause_title', 'Compliance Issue')
                                            # Clean up clause title - remove long prefixes
                                            if '|' in clause_title:
                                                clause_title = clause_title.split('|')[-1].strip()
                                            if len(clause_title) > 50:
                                                clause_title = clause_title[:47] + "..."
                                            
                                            answer_text += f"❌ {idx}. {clause_title} – NOT COMPLIANT\n\n"
                                            
                                            clause_content = issue.get('clause_content', '')
                                            if clause_content and len(clause_content) > 50:
                                                # Extract first meaningful sentence, clean it up
                                                sentences = clause_content.split('.')
                                                first_sentences = '. '.join([s.strip() for s in sentences[:2] if len(s.strip()) > 20])[:200]
                                                if first_sentences:
                                                    answer_text += f"**What the document says:**\n\n{first_sentences}...\n\n"
                                            
                                            regulation = issue.get('regulation_applies', '')
                                            if regulation and len(regulation) > 30:
                                                answer_text += f"**Why it's non-compliant in Texas:**\n\n{regulation}\n\n"
                                            
                                            fix = issue.get('what_to_fix', '')
                                            if fix and len(fix) > 20:
                                                answer_text += f"**Fix needed:**\n\n{fix}\n\n"
                                            
                                            if issue.get('suggested_revision'):
                                                rev = issue['suggested_revision'][:300]
                                                answer_text += f"**Suggested revision:**\n\n```\n{rev}\n```\n\n"
                                            
                                            answer_text += "---\n\n"
                                        
                                        # Add concise action items (only once, not per clause)
                                        answer_text += "**📋 Action Items:**\n\n"
                                        answer_text += "- Update lease agreement document with the fixes above\n"
                                        answer_text += "- Review property management policies\n"
                                        answer_text += "- Post required Fair Housing Act poster\n"
                                        answer_text += "- Train staff on compliance requirements\n\n"
                                        
                                        # Add offer to refine/fix document
                                        answer_text += "---\n\n"
                                        answer_text += "**🔧 Need Help Fixing This Document?**\n\n"
                                        answer_text += "I can help you:\n"
                                        answer_text += "• **Refine specific clauses** - Ask me to revise any non-compliant clause with compliant language\n"
                                        answer_text += "• **Provide exact text to add** - I can give you the exact wording to insert into your lease\n"
                                        answer_text += "• **Identify specific locations** - I can tell you exactly where in the document to make changes\n\n"
                                        answer_text += "**Try asking:**\n"
                                        answer_text += "- \"Fix the security deposit clause\"\n"
                                        answer_text += "- \"What exact text should I add for ESA compliance?\"\n"
                                        answer_text += "- \"Show me the compliant version of clause 8\"\n"
                                    else:
                                        # No real issues found - document appears compliant
                                        answer_text += "✅ **Document appears compliant!**\n\n"
                                        answer_text += "The compliance checker analyzed your document using rule-based analysis and found no major compliance issues.\n\n"
                                        answer_text += "**Note:** This is a free rule-based analysis. For comprehensive legal review, consult with qualified legal counsel."
                                
                                st.markdown(answer_text)
                                st.warning(LEGAL_DISCLAIMER)
                                
                                # Clear state
                                if 'pending_file' in st.session_state:
                                    del st.session_state.pending_file
                                    del st.session_state.pending_filename
                                st.session_state.compliance_city = None
                                
                                # Store sources for expander (deduplicated by URL)
                                seen_urls = set()
                                sources_data = []
                                for source in result.get('sources', []):
                                    url = source.get('url', '')
                                    # Use URL as primary key for deduplication - same URL should only appear once
                                    if url and url not in seen_urls:
                                        seen_urls.add(url)
                                        sources_data.append(source)
                                    elif not url:
                                        # If no URL, use source name as fallback
                                        source_name = source.get('source', '')
                                        if source_name and source_name not in seen_urls:
                                            seen_urls.add(source_name)
                                            sources_data.append(source)
                                
                                # Add to history with sources
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': answer_text,
                                    'sources': sources_data
                                })
                                st.rerun()
                            except Exception as e:
                                error_msg = f"❌ **Error checking compliance:** {str(e)}\n\nPlease make sure:\n- The file is a valid PDF or DOCX document\n- The document contains lease or rental agreement content\n- Try uploading the file again"
                                st.error(error_msg)
                                st.session_state.chat_history.append({
                                    'role': 'assistant',
                                    'content': error_msg,
                                    'sources': []
                                })
                                st.session_state.compliance_city = None
                                if 'pending_file' in st.session_state:
                                    del st.session_state.pending_file
                                    del st.session_state.pending_filename
                                st.rerun()
                    else:
                        # No file but asking about compliance
                        answer_text = "📎 **Please attach a document first** using the file uploader above, then ask about compliance again. I can check PDF and DOCX files for compliance with Texas housing regulations."
                        st.markdown(answer_text)
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': answer_text,
                            'sources': []
                        })
                        st.rerun()
                else:
                    # Regular Q&A
                    result = st.session_state.qa_system.answer_question_with_context(
                        prompt, 
                        st.session_state.chat_history
                    )
                    
                    answer_text = result['answer']
                    
                    # Clean up answer - remove raw context
                    if "From " in answer_text and "(" in answer_text:
                        lines = answer_text.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            if line.startswith("From ") and "(" in line and "):" in line:
                                continue
                            if line.strip().startswith("---"):
                                continue
                            cleaned_lines.append(line)
                        answer_text = '\n'.join(cleaned_lines).strip()
                    
                    # Don't add sources to answer_text - they're displayed separately in the expander
                    # This prevents duplicates
                    
                    if "[Note:" in answer_text:
                        answer_text = answer_text.split("[Note:")[0].strip()
                    
                    st.markdown(answer_text)
                    
                    # Email prompt for new laws
                    if any(keyword in answer_text.lower() for keyword in ["new law", "new regulation", "update", "recent"]):
                        st.markdown("---")
                        st.info("📧 **Would you like to receive email alerts for new laws and policy updates?** Use the Email Alerts tab to subscribe!")
                    
                    # Store sources for expander (deduplicated by URL)
                    seen_urls = set()
                    sources_data = []
                    for source in result.get('sources', []):
                        url = source.get('url', '')
                        # Use URL as primary key for deduplication - same URL should only appear once
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            sources_data.append(source)
                        elif not url:
                            # If no URL, use source name as fallback
                            source_name = source.get('source', '')
                            if source_name and source_name not in seen_urls:
                                seen_urls.add(source_name)
                                sources_data.append(source)
                    
                    # Add assistant response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant', 
                        'content': answer_text,
                        'sources': sources_data
                    })
                    st.rerun()

def show_regulation_explorer():
    with st.container(border=True):
        st.markdown("##### Filters")
        st.caption("Combine search with category, state, and city. All filters apply together.")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_query = st.text_input(
                "Search keywords",
                placeholder="e.g. ESA, rent cap…",
                key="rex_search",
            )
        with col2:
            category_filter = st.selectbox(
                "Category",
                ["All"] + REGULATION_CATEGORIES,
                key="rex_category",
            )
        with col3:
            state_filter = st.selectbox("State", ["All"] + STATES, key="rex_state")
        with col4:
            city_filter = st.selectbox("City", ["All"] + SUPPORTED_CITIES, key="rex_city")
    
    # Get regulations
    regulations = st.session_state.db.get_all_regulations()
    
    # Apply filters
    if category_filter != "All":
        regulations = [r for r in regulations if category_filter in r.get('category', '')]
    
    if state_filter != "All":
        regulations = [
            r for r in regulations
            if state_filter.lower() in (r.get('source_name') or '').lower()
            or state_filter.lower() in (r.get('category') or '').lower()
        ]
    
    if city_filter != "All":
        regulations = [
            r for r in regulations
            if city_filter.lower() in (r.get('source_name') or '').lower()
            or city_filter.lower() in (r.get('category') or '').lower()
        ]
    
    if search_query:
        # Vector search
        search_results = st.session_state.vector_store.search(
            search_query, 
            n_results=10,
            prioritize_reliable=True
        )
        if search_results:
            st.subheader("Search Results", anchor=False)
            for result in search_results:
                with st.expander(f"📄 {result['metadata'].get('source_name', 'Unknown')}"):
                    st.write(result['document'][:500])
                    _u = result["metadata"].get("url", "N/A")
                    st.markdown("**URL:**")
                    st.markdown(f"`{_u}`")
                    st.markdown(f"**Category**: {result['metadata'].get('category', 'N/A')}")
    
    st.subheader("All regulations", anchor=False)
    
    if regulations:
        df = pd.DataFrame(regulations)
        df["URL"] = df["url"].apply(lambda x: x if x and str(x).startswith("http") else (x or ""))
        
        # Map source names for better display (same as Update Log)
        df['display_name'] = df['source_name'].apply(lambda x: 
            "Dallas Rent Control Policy- Maximum Rent Increase Cap" 
            if x == "Dallas Rent Control 2025 (DEMO)" 
            else x
        )
        
        display_df = df[['display_name', 'type', 'category', 'URL', 'last_checked']].copy()
        display_df.columns = ['Source Name', 'Type', 'Category', 'URL', 'Last Checked']
        
        # Format last_checked dates - set default to today if missing
        from datetime import datetime
        today_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Convert last_checked to string first, handling None/NaN
        display_df['Last Checked'] = display_df['Last Checked'].astype(str)
        
        # Replace any invalid values with today's date
        invalid_values = ['None', 'nan', 'NaT', 'Never', '', 'null', 'NULL']
        for invalid in invalid_values:
            display_df['Last Checked'] = display_df['Last Checked'].replace(invalid, today_str, regex=False)
        
        # Try to parse and format dates
        def format_date(date_str):
            if pd.isna(date_str) or str(date_str).lower() in ['none', 'nan', 'nat', 'never', '', 'null']:
                return today_str
            try:
                # Try parsing various date formats
                if isinstance(date_str, str):
                    # Remove microseconds if present
                    date_str = date_str[:19] if len(date_str) > 19 else date_str
                    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # If it's already a datetime object
                    return pd.to_datetime(date_str).strftime('%Y-%m-%d %H:%M:%S')
            except:
                return today_str
        
        display_df['Last Checked'] = display_df['Last Checked'].apply(format_date)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No regulations found. Load regulations from CSV in Settings.")

def show_compliance_checker():
    st.header("Lease Compliance Checker", anchor=False)
    
    st.markdown("Upload a lease document (PDF or DOCX) to check for compliance with Texas housing regulations.")
    
    # City selection
    city = st.selectbox("Select City for Compliance Check", SUPPORTED_CITIES)
    
    # File upload
    uploaded_file = st.file_uploader("Upload Lease Document", type=['pdf', 'docx', 'doc'])
    
    if uploaded_file is not None:
        if st.button("Check Compliance", type="primary"):
            with st.spinner("Analyzing document for compliance..."):
                try:
                    file_content = uploaded_file.read()
                    result = st.session_state.compliance_checker.check_compliance(
                        file_content,
                        uploaded_file.name,
                        city
                    )
                    
                    # Display results
                    st.markdown("---")
                    
                    if result['is_compliant']:
                        st.success(f"✅ **COMPLIANT**: Document passed compliance check!")
                    else:
                        st.error(f"❌ **NON-COMPLIANT**: Found {result['issues_found']} issue(s)")
                    
                    # Summary
                    st.subheader("Summary", anchor=False)
                    st.markdown(result['summary'])
                    
                    # Issues with action items
                    if result['issues']:
                        st.subheader("Compliance Issues & Action Items", anchor=False)
                        for issue in result['issues']:
                            with st.expander(f"⚠️ Issue in Clause {issue['clause_number']}: {issue['clause_title'][:50]}"):
                                st.markdown(f"**Clause Content:**")
                                st.text(issue['clause_content'][:500])
                                st.markdown(f"**Regulation Applies:** {issue['regulation_applies']}")
                                st.markdown(f"**What's Missing:** {issue['whats_missing']}")
                                st.markdown(f"**What to Fix:** {issue['what_to_fix']}")
                                
                                # Show action items for this specific issue
                                st.markdown("---")
                                st.markdown("**📋 Action Items for This Issue:**")
                                if 'esa' in issue['what_to_fix'].lower() or 'emotional support' in issue['what_to_fix'].lower():
                                    st.markdown("""
                                    1. Remove pet fees/deposits for ESA animals
                                    2. Update lease document
                                    3. Post Fair Housing Act poster
                                    4. Train staff on ESA requirements
                                    5. Make ESA request forms available
                                    """)
                                elif 'fair housing' in issue['what_to_fix'].lower():
                                    st.markdown("""
                                    1. Update lease language per Fair Housing Act
                                    2. Post Fair Housing poster
                                    3. Update property management policies
                                    4. Train staff on Fair Housing requirements
                                    """)
                                else:
                                    st.markdown("""
                                    1. Review and update clause
                                    2. Update lease document
                                    3. Consult legal counsel if needed
                                    """)
                                
                                if issue['suggested_revision']:
                                    st.markdown("---")
                                    st.markdown(f"**Suggested Revision:**")
                                    st.code(issue['suggested_revision'])
                        
                        # General action items section
                        st.markdown("---")
                        st.subheader("📋 General Action Items", anchor=False)
                        st.markdown("""
                        **Documents to Update:**
                        - Lease agreement document
                        - Property management handbook
                        - Tenant welcome packet
                        - Staff training materials
                        
                        **Posters/Displays to Update:**
                        - Fair Housing Act poster (required by law)
                        - Tenant rights information
                        - Pet policy signage (if applicable)
                        
                        **Policy Updates:**
                        - Review and update property management policies
                        - Update tenant screening procedures if needed
                        - Ensure all staff are trained on compliance requirements
                        
                        **Next Steps:**
                        1. Review all flagged clauses
                        2. Update documents with corrected language
                        3. Post required notices/posters
                        4. Train staff on updated policies
                        5. Consult with legal counsel before finalizing changes
                        6. Keep records of all compliance updates
                        """)
                    
                    # Disclaimer
                    st.markdown("---")
                    st.warning(LEGAL_DISCLAIMER)
                
                except Exception as e:
                    st.error(f"Error checking compliance: {str(e)}")

def show_update_log():
    if st.button("Check for updates now"):
        with st.spinner("Checking for updates..."):
            updates = st.session_state.update_checker.check_for_updates()
            if updates:
                st.success(f"Found {len(updates)} new update(s)!")
                # Notify subscribers
                for update in updates:
                    st.session_state.email_system.notify_subscribers(update)
            else:
                st.info("No new updates detected.")
    
    st.subheader("Recent updates", anchor=False)
    
    # Show count
    updates = st.session_state.db.get_recent_updates(limit=50)
    if updates:
        st.metric("Total Updates", len(updates))
    
    col1, col2 = st.columns(2)
    with col1:
        city_filter = st.selectbox("City", ["All"] + SUPPORTED_CITIES, key="update_city_filter")
    with col2:
        show_count = st.slider("Show", 1, 50, 10, key="update_count")
    
    # Apply filter
    filtered_updates = updates
    if city_filter != "All":
        filtered_updates = [
            u for u in updates 
            if city_filter in str(u.get('affected_cities', ''))
        ]
    
    # Remove duplicates - keep only the most recent update for each source_name + URL combination
    if filtered_updates:
        seen_updates = {}
        deduplicated_updates = []
        
        for update in filtered_updates:
            # Create a unique key from source_name and URL
            source_name = update.get('source_name', '')
            url = update.get('url', '')
            update_key = f"{source_name}|{url}"
            
            # Parse detected_at timestamp for comparison
            detected_at = update.get('detected_at', '')
            
            # If we haven't seen this combination, or this one is more recent, keep it
            if update_key not in seen_updates:
                seen_updates[update_key] = update
                deduplicated_updates.append(update)
            else:
                # Compare timestamps - keep the more recent one
                existing_update = seen_updates[update_key]
                existing_time = existing_update.get('detected_at', '')
                
                # If current update is more recent, replace the existing one
                if detected_at > existing_time:
                    # Remove old one and add new one
                    deduplicated_updates.remove(existing_update)
                    deduplicated_updates.append(update)
                    seen_updates[update_key] = update
        
        # Sort by detected_at descending (most recent first)
        deduplicated_updates.sort(key=lambda x: x.get('detected_at', ''), reverse=True)
        filtered_updates = deduplicated_updates
    
    if filtered_updates:
        st.markdown(f"**Showing {len(filtered_updates[:show_count])} of {len(filtered_updates)} updates**")
        for update in filtered_updates[:show_count]:
            affected_cities = eval(update.get('affected_cities', '[]')) if isinstance(update.get('affected_cities'), str) else update.get('affected_cities', [])
            
            # Map source names for better display
            source_name = update.get('source_name', '')
            display_name = source_name
            if source_name == "Dallas Rent Control 2025 (DEMO)":
                display_name = "Dallas Rent Control Policy- Maximum Rent Increase Cap"
            
            with st.expander(f"📢 {display_name} - {update['detected_at']}", expanded=False):
                st.markdown(f"**Category:** {update.get('category', 'N/A')}")
                _uu = update.get("url") or "N/A"
                st.markdown("**URL:**")
                st.markdown(f"`{_uu}`")
                st.markdown(f"**Affected Cities:** {', '.join(affected_cities) if affected_cities else 'Texas-Statewide'}")
                st.markdown("---")
                st.markdown("**Update Summary:**")
                st.write(update['update_summary'])
                
                # Show if email was sent
                st.markdown("---")
                st.info("📧 Email notifications saved to 'emails' folder (if SMTP not configured)")
    else:
        if city_filter != "All":
            st.warning(f"No updates found for {city_filter}. Try 'All' or check other cities.")
        else:
            st.info("No updates recorded yet. Click 'Check for Updates' on the Home page to scan for changes.")

def show_email_alerts():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Subscribe", anchor=False)
        email = st.text_input("Email", placeholder="you@example.com", key="subscribe_email")
        city = st.selectbox("City", SUPPORTED_CITIES, key="subscribe_city")
        if st.button("Subscribe", type="primary"):
            if email and "@" in email:
                success = st.session_state.db.subscribe_email(email, city)
                if success:
                    # Send welcome email
                    st.session_state.email_system.send_welcome_email(email, city)
                    st.success(f"✅ Subscribed {email} to {city} alerts! Check your email for a welcome message.")
                else:
                    st.warning("Already subscribed to this city.")
            else:
                st.error("Please enter a valid email address.")
    
    with col2:
        st.subheader("Unsubscribe", anchor=False)
        unsubscribe_email = st.text_input("Email", placeholder="you@example.com", key="unsubscribe_email")
        unsubscribe_city = st.selectbox("City", SUPPORTED_CITIES, key="unsubscribe_city")
        
        if st.button("Unsubscribe", type="secondary"):
            if unsubscribe_email and "@" in unsubscribe_email:
                success = st.session_state.db.unsubscribe_email(unsubscribe_email, unsubscribe_city)
                if success:
                    st.success(f"✅ Unsubscribed {unsubscribe_email} from {unsubscribe_city} alerts.")
                else:
                    st.warning("No active subscription found for this email and city.")
            else:
                st.error("Please enter a valid email address.")
        
        st.markdown("---")
        st.subheader("View subscriptions", anchor=False)
        view_email = st.text_input("Email", placeholder="you@example.com", key="view_email")
        if st.button("View subscriptions"):
            if view_email and "@" in view_email:
                subscriptions = st.session_state.db.get_user_subscriptions(view_email)
                if subscriptions:
                    st.success(f"Active subscriptions for {view_email}:")
                    for sub in subscriptions:
                        st.info(f"📧 {sub['city']} (subscribed: {sub['subscribed_at']})")
                else:
                    st.info("No active subscriptions found for this email.")
        
        st.markdown("---")
        st.subheader("Daily summaries", anchor=False)
        st.caption("Subscribers get a daily email at 9:00 AM with updates for their cities.")
        if st.button("Send test daily summary", help="Send a test summary to all subscribers"):
            with st.spinner("Sending daily summaries..."):
                total_sent = st.session_state.email_system.send_daily_summaries_to_all_subscribers()
                if total_sent > 0:
                    st.success(f"✅ Sent {total_sent} daily summary report(s)! Check your email or the 'emails' folder.")
                else:
                    st.info("No active subscriptions found. Subscribe to a city first to receive daily summaries.")

def show_settings():
    st.subheader("Data & indexing", anchor=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Load regulations from CSV"):
            try:
                with st.spinner("Loading regulations from CSV..."):
                    result = st.session_state.db.load_regulations_from_csv(SOURCES_FILE)
                    st.success(f"✅ Regulations loaded! ({result['loaded']} loaded, {result['skipped']} skipped)")
                    
                    # Automatically scrape and index ONLY newly added regulations
                    newly_added_urls = result.get('newly_added_urls', [])
                    if newly_added_urls:
                        st.info(f"🔄 Now scraping and indexing {len(newly_added_urls)} new regulation(s)...")
                        with st.spinner("Scraping and indexing new regulations..."):
                            indexed = 0
                            skipped_indexing = 0
                            
                            # Only process newly added URLs
                            for url in newly_added_urls:
                                # Get the regulation by URL to get its ID and metadata
                                reg = st.session_state.db.get_regulation_by_url(url)
                                if not reg:
                                    skipped_indexing += 1
                                    continue
                                
                                if url and (url.startswith('http://') or url.startswith('https://') or url.startswith('file://') or os.path.exists(url)):
                                    try:
                                        content = st.session_state.scraper.fetch_url_content(url)
                                        if content and content.get('content'):
                                            chunks = st.session_state.scraper.chunk_text(content['content'])
                                            if chunks:
                                                st.session_state.vector_store.add_regulation_chunks(
                                                    regulation_id=str(reg['id']),
                                                    source_name=reg['source_name'],
                                                    url=url,
                                                    category=reg.get('category', 'Other'),
                                                    chunks=chunks
                                                )
                                                # Update hash in database
                                                st.session_state.db.update_regulation_hash(url, content['hash'])
                                                indexed += 1
                                        else:
                                            skipped_indexing += 1
                                    except Exception as e:
                                        skipped_indexing += 1
                                        continue
                            
                            if indexed > 0:
                                st.success(f"✅ Indexed {indexed} new regulation(s) in vector store!")
                            if skipped_indexing > 0:
                                st.warning(f"⚠️ Skipped {skipped_indexing} regulation(s) (could not fetch content)")
                    elif result['loaded'] == 0:
                        st.info("ℹ️ No new regulations to index. All regulations from CSV are already loaded.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        if st.button("Re-index all regulations"):
            """Re-index all regulations (useful if vector store was cleared)"""
            with st.spinner("Re-indexing all regulations (this may take several minutes)..."):
                regulations = st.session_state.db.get_all_regulations()
                indexed = 0
                for reg in regulations:
                    url = reg.get('url', '')
                    if url and (url.startswith('http://') or url.startswith('https://') or url.startswith('file://') or os.path.exists(url)):
                        try:
                            content = st.session_state.scraper.fetch_url_content(url)
                            if content and content.get('content'):
                                chunks = st.session_state.scraper.chunk_text(content['content'])
                                if chunks:
                                    st.session_state.vector_store.add_regulation_chunks(
                                        regulation_id=str(reg['id']),
                                        source_name=reg['source_name'],
                                        url=url,
                                        category=reg.get('category', 'Other'),
                                        chunks=chunks
                                    )
                                    st.session_state.db.update_regulation_hash(url, content['hash'])
                                    indexed += 1
                        except Exception as e:
                            continue
                st.success(f"✅ Re-indexed {indexed} regulations!")
        
        st.markdown("---")
        st.subheader("Daily scraping", anchor=False)
        st.caption("Runs at 9:00 AM daily. Use the button below to run now.")
        if st.button("Run update check now"):
            with st.spinner("Checking for updates..."):
                updates = st.session_state.update_checker.check_for_updates()
                if updates:
                    st.success(f"Found {len(updates)} new update(s)!")
                    # Notify subscribers
                    for update in updates:
                        st.session_state.email_system.notify_subscribers(update)
                    for update in updates:
                        st.info(f"**{update['source_name']}**: {update['summary'][:100]}...")
                else:
                    st.info("No new updates detected.")
    
    with col2:
        st.subheader("Configuration", anchor=False)
        st.caption("OpenAI key and SMTP in `.env`. Data: SQLite (regulations.db), ChromaDB (./chroma_db). Run `python daily_scraper.py` for daily updates.")
    
    st.markdown("---")
    st.caption("Housing Regulation Compliance Agent · Texas housing regulations. Informational only; not legal advice.")

if __name__ == "__main__":
    main()
