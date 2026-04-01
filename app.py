# 🚀 PYTHON 3.14 VE SQLITE YAMALARI
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

# 🧠 Veri Tabanı Yükleme
@st.cache_resource
def veri_tabanini_yukle():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory="sinif_programi_vektor", embedding_function=embeddings)

vektor_tabani = veri_tabanini_yukle()

# 🛡️ GÜVENLİK SÜZGECİ
def suzgec_kontrolu(metin):
    harita = {'1':'i', '0':'o', '3':'e', '4':'a', '5':'s', '7':'t', '8':'b', '@':'a', '$':'s'}
    temiz = metin.lower()
    for eski, yeni in harita.items(): temiz = temiz.replace(eski, yeni)
    sıkı = re.sub(r'[^a-z0-9çşğüöı]', '', temiz)
    yasakli = ["oc", "aq", "amk", "sik", "orospu", "teror", "siyaset", "askim", "bebegim"]
    return any(k in sıkı for k in yasakli)

# 🎨 CSS TASARIMI (Tüm Sayfa İçin Zorunlu Stil)
st.set_page_config(page_title="Okul Asistanı GPT", layout="centered")

st.markdown("""
<style>
    /* Arka plan ve genel yazı rengi */
    .stApp { background-color: #0E1117 !important; }
    
    /* Mavi Buton Sabitleme */
    .yuzen-buton { position: fixed; bottom: 85px; right: 25px; z-index: 1000; }
    
    .stLinkButton a {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 25px !important;
        border: 2px solid #FFFFFF !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        text-decoration: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    }

    /* Kartların CSS Yapısı */
    .ozel-kart {
        background-color: #161922 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        min-height: 180px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
        border-top: 5px solid #FF4B4B; /* Varsayılan renk */
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 30px;'>🏛️ Okul Ders Programı Asistanı</h1>", unsafe_allow_html=True)

# 🏛️ Mavi Buton
st.markdown('<div class="yuzen-buton">', unsafe_allow_html=True)
st.link_button("🏛️ MEB Yönetmelik", "https://meb-yonetmelik.streamlit.app/")
st.markdown('</div>', unsafe_allow_html=True)

# 💡 HIZLI SORULAR (KARTLAR)
st.markdown("<h3 style='color: white;'>💡 Hızlı Sorular</h3>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="ozel-kart" style="border-top-color: #FF4B4B;">
        <div style="color: #FF4B4B; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">🔍 Sınıf Programı</div>
        <div style="color: #808495; font-size: 0.85rem; line-height: 1.6;">
            • 9A Pazartesi?<br>• 11B Cuma dersleri?<br>• 10C Salı ilk ders?
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="ozel-kart" style="border-top-color: #FF8C00;">
        <div style="color: #FF8C00; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">👨‍🏫 Öğretmenler</div>
        <div style="color: #808495; font-size: 0.85rem; line-height: 1.6;">
            • U.TRK Salı nerede?<br>• Matematik hocası?<br>• Ahmet Yılmaz ders?
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="ozel-kart" style="border-top-color: #1E90FF;">
        <div style="color: #1E90FF; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">📚 Okul Bilgisi</div>
        <div style="color: #808495; font-size: 0.85rem; line-height: 1.6;">
            • Öğle arası kaçta?<br>• Bilişim sınıfı neresi?<br>• Seçmeli ders günü?
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><hr style='border-color: #333;'>", unsafe_allow_html=True)

# 💬 SOHBET AKIŞI
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if girdi := st.chat_input("Ders programı hakkında bir soru sorun..."):
    if suzgec_kontrolu(girdi):
        st.error("⚠️ Uygunsuz içerik algılandı.")
    else:
        st.session_state.messages.append({"role": "user", "content": girdi})
        with st.chat_message("user"): st.markdown(girdi)
        with st.chat_message("assistant"):
            with st.spinner("⏳ Program inceleniyor..."):
                cevap, kaynaklar = okul_asistani_sorgula(girdi, vektor_tabani)
                st.markdown(cevap)
                st.session_state.messages.append({"role": "assistant", "content": cevap})
                st.rerun()
