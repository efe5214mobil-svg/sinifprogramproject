# 🚀 KRİTİK YAMALAR (En Üstte Kalmalı)
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

load_dotenv()

# 🧠 Veri Tabanı
@st.cache_resource
def veri_tabanini_yukle():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory="sinif_programi_vektor", embedding_function=embeddings)

vektor_tabani = veri_tabanini_yukle()

# 🛡️ ÇELİK ZIRH SÜZGECİ
def suzgec_kontrolu(metin):
    harita = {'1':'i', '0':'o', '3':'e', '4':'a', '5':'s', '7':'t', '8':'b', '@':'a', '$':'s'}
    temiz = metin.lower()
    for eski, yeni in harita.items(): temiz = temiz.replace(eski, yeni)
    sıkı = re.sub(r'[^a-z0-9çşğüöı]', '', temiz)
    yasakli = ["oc", "aq", "amk", "sik", "orospu", "teror", "siyaset", "askim", "bebegim"]
    return any(k in sıkı for k in yasakli)

# 🎨 CSS TASARIMI
st.set_page_config(page_title="Okul Asistanı GPT", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .ana-baslik { font-size: 2.5rem; font-weight: 800; text-align: center; color: #1E90FF; margin-bottom: 20px; }
    .yuzen-buton { position: fixed; bottom: 80px; right: 20px; z-index: 999; }
    .stLinkButton a {
        background-color: #1E90FF !important; color: white !important;
        border-radius: 20px !important; border: 1px solid white !important;
    }
    .kategori-kutusu {
        background-color: rgba(255, 255, 255, 0.05); border-radius: 12px;
        padding: 15px; border-top: 4px solid #1E90FF; margin-bottom: 10px; height: 160px;
    }
    .kategori-basligi { font-weight: bold; color: #1E90FF; margin-bottom: 8px; }
    .kategori-maddesi { font-size: 0.85rem; color: #ccc; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='ana-baslik'>📅 Okul Ders Programı Asistanı</div>", unsafe_allow_html=True)

# Yönlendirme Butonu
st.markdown('<div class="yuzen-buton">', unsafe_allow_html=True)
st.link_button("🏛️ MEB Yönetmelik", "https://meb-yonetmelik.streamlit.app/")
st.markdown('</div>', unsafe_allow_html=True)

# 💡 Öneri Kartları
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">🔍 Sınıflar</div><div class="kategori-maddesi">• 9-A Pazartesi dersleri?</div><div class="kategori-maddesi">• 10-B Cuma son ders?</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">👨‍🏫 Hocalar</div><div class="kategori-maddesi">• U.TRK Salı nerede?</div><div class="kategori-maddesi">• Matematik hocası kim?</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">📚 Genel</div><div class="kategori-maddesi">• Öğle arası kaçta?</div><div class="kategori-maddesi">• Bilişim hangi sınıfta?</div></div>', unsafe_allow_html=True)

# Sohbet Akışı
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if girdi := st.chat_input("Ders programı hakkında sorun..."):
    if suzgec_kontrolu(girdi):
        st.error("⚠️ Uygunsuz içerik algılandı.")
    else:
        st.session_state.messages.append({"role": "user", "content": girdi})
        with st.chat_message("user"): st.markdown(girdi)
        with st.chat_message("assistant"):
            with st.spinner("⏳ Tablo oluşturuluyor..."):
                cevap, kaynaklar = okul_asistani_sorgula(girdi, vektor_tabani)
                st.markdown(cevap) # Tablo burada otomatik oluşur
                st.session_state.messages.append({"role": "assistant", "content": cevap})
                st.rerun()
