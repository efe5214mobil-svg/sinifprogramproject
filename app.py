# 1. EN ÜSTTE OLMALI: Veritabanı ve Protobuf Yamaları
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
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
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Klasör isminin GitHub'da birebir aynı olduğundan emin ol
    return Chroma(persist_directory="sinif_programi_vektor", embedding_function=embeddings)

vektor_tabani = veri_tabanini_yukle()

# 🛡️ GÜVENLİK SÜZGECİ
def suzgec_kontrolu(metin):
    harita = {'1':'i', '0':'o', '3':'e', '4':'a', '5':'s', '7':'t', '8':'b', '@':'a', '$':'s'}
    temiz = metin.lower()
    for eski, yeni in harita.items():
        temiz = temiz.replace(eski, yeni)
    sıkı_metin = re.sub(r'[^a-z0-9çşğüöı]', '', temiz)
    yasakli = ["oc", "aq", "amk", "sik", "orospu", "teror", "siyaset", "askim", "bebegim"]
    return any(kelime in sıkı_metin for kelime in yasakli)

# 🎨 TASARIM
st.set_page_config(page_title="Okul Asistanı", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .yuzen-buton {
        position: fixed; bottom: 80px; right: 20px; z-index: 999;
    }
    .stLinkButton a {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 20px !important;
        border: 1px solid white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 Okul Ders Programı Asistanı")

# Mavi Yönlendirme Butonu
st.markdown('<div class="yuzen-buton">', unsafe_allow_html=True)
st.link_button("🏛️ MEB Yönetmelik", "https://meb-yonetmelik.streamlit.app/")
st.markdown('</div>', unsafe_allow_html=True)

# Sohbet Sistemi
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if girdi := st.chat_input("Sınıf veya hoca ismi sorabilirsiniz..."):
    if suzgec_kontrolu(girdi):
        st.error("⚠️ Uygunsuz içerik algılandı.")
    else:
        st.session_state.messages.append({"role": "user", "content": girdi})
        with st.chat_message("user"):
            st.markdown(girdi)

        with st.chat_message("assistant"):
            cevap, kaynaklar = okul_asistani_sorgula(girdi, vektor_tabani)
            st.markdown(cevap)
            if kaynaklar:
                with st.expander("📚 Kaynaklar"):
                    for k in kaynaklar: st.write(k)
            st.session_state.messages.append({"role": "assistant", "content": cevap})
