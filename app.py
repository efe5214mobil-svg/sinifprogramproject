import streamlit as st
import os
import re
import time
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from rag import okul_asistani_sorgula

# 🔐 Ayarlar
load_dotenv()

@st.cache_resource
def veri_tabanini_yukle():
    gomme_modeli = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory="okul_asistani_gpt_db", embedding_function=gomme_modeli)

vektor_tabani = veri_tabanini_yukle()

# 🎨 Sayfa Yapılandırması
st.set_page_config(page_title="Okul Asistanı", page_icon="📅", layout="centered")

# 🖌️ MODERN CSS (Mavi Buton ve Beyaz Yazı Dahil)
st.markdown("""
<style>
    .stApp { font-family: 'Inter', sans-serif; }
    .ana-baslik { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 1.5rem; }
    
    /* Yüzen Mavi Buton Ayarları */
    .yuzen-buton-alani {
        position: fixed;
        bottom: 85px; 
        right: 10%; 
        z-index: 999999;
    }
    .stLinkButton a {
        background-color: #1E90FF !important; /* Mavimsi */
        color: white !important;               /* Beyaz yazı */
        border-radius: 25px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 700 !important;
        border: 2px solid white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }

    /* Öneri Kartları */
    .kategori-kutusu {
        background-color: rgba(128, 128, 128, 0.1);
        border-radius: 15px;
        padding: 18px;
        border-top: 4px solid #1E90FF;
        height: 100%;
        margin-bottom: 10px;
    }
    .kategori-basligi { font-weight: bold; color: #1E90FF; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# 🛡️ GÜVENLİK SÜZGECİ
def suzgec_kontrolu(metin):
    temiz = re.sub(r'[^a-z0-9çşğüöı]', '', metin.lower())
    yasakli = ["oc", "aq", "amk", "sik", "piç"] 
    return any(y in temiz for y in yasakli)

# --- ARAYÜZ ---
st.markdown("<div class='ana-baslik'>📅 Okul Ders Programı Asistanı</div>", unsafe_allow_html=True)

# Mavi Buton
st.markdown('<div class="yuzen-buton-alani">', unsafe_allow_html=True)
st.link_button("🏛️ MEB Yönetmelik", "https://meb-yonetmelik.streamlit.app/")
st.markdown('</div>', unsafe_allow_html=True)

# 💡 Hızlı Sorular
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">🔍 Sınıflar</div>9-A Pazartesi dersleri neler?</div>', unsafe_allow_html=True)
with s2:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">👨‍🏫 Hocalar</div>U.TRK dersi ne zaman?</div>', unsafe_allow_html=True)
with s3:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">⏰ Saatler</div>İlk ders kaçta başlıyor?</div>', unsafe_allow_html=True)

if "chat_history" not in st.session_state: st.session_state.chat_history = []

for m in st.session_state.chat_history:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Sorunuzu sorun..."):
    if suzgec_kontrolu(prompt):
        st.error("⚠️ Uygunsuz içerik engellendi.")
    else:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("İnceleniyor..."):
                cevap, kaynaklar = okul_asistani_sorgula(prompt, vektor_tabani)
                st.markdown(cevap)
                st.session_state.chat_history.append({"role": "assistant", "content": cevap})
