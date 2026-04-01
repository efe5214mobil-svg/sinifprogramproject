# 🚀 KRİTİK YAMALAR (Python 3.14 ve SQLite için)
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

# 🛡️ ÇELİK ZIRH SÜZGECİ
def suzgec_kontrolu(metin):
    harita = {'1':'i', '0':'o', '3':'e', '4':'a', '5':'s', '7':'t', '8':'b', '@':'a', '$':'s'}
    temiz = metin.lower()
    for eski, yeni in harita.items(): temiz = temiz.replace(eski, yeni)
    sıkı = re.sub(r'[^a-z0-9çşğüöı]', '', temiz)
    yasakli = ["oc", "aq", "amk", "sik", "orospu", "teror", "siyaset", "askim", "bebegim"]
    return any(k in sıkı for k in yasakli)

# 🎨 CSS TASARIMI (Mavi Buton ve Genel Stil)
st.set_page_config(page_title="Okul Asistanı GPT", layout="centered")
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .yuzen-buton { position: fixed; bottom: 80px; right: 20px; z-index: 999; }
    .stLinkButton a {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 25px !important;
        border: 2px solid white !important;
        font-weight: bold !important;
        padding: 0.5rem 1.5rem !important;
        text-decoration: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>🏛️ Okul Ders Programı Asistanı</h1>", unsafe_allow_html=True)

# 🏛️ Sağ Alt Köşedeki Mavi Buton
st.markdown('<div class="yuzen-buton">', unsafe_allow_html=True)
st.link_button("🏛️ MEB Yönetmelik", "https://meb-yonetmelik.streamlit.app/")
st.markdown('</div>', unsafe_allow_html=True)

# 💡 HIZLI SORULAR (ŞIK KARTLAR)
st.markdown("### 💡 Hızlı Sorular")

# Kartlar için ortak stil fonksiyonu
def soru_karti(renk, baslik, icerik):
    return f"""
    <div style="
        background-color: #161922;
        border-radius: 15px;
        padding: 20px;
        border-top: 5px solid {renk};
        height: 180px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    ">
        <div style="color: {renk}; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">{baslik}</div>
        <div style="color: #808495; font-size: 0.9rem; line-height: 1.6;">{icerik}</div>
    </div>
    """

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(soru_karti("#FF4B4B", "🔍 Sınıf Programı", "• 9-A Pazartesi?<br>• 11-B Cuma dersleri?<br>• 10-C Salı ilk ders?"), unsafe_allow_html=True)

with col2:
    st.markdown(soru_karti("#FF8C00", "👨‍🏫 Öğretmenler", "• U.TRK Salı nerede?<br>• Matematik hocası?<br>• Ahmet Yılmaz ders?"), unsafe_allow_html=True)

with col3:
    st.markdown(soru_karti("#1E90FF", "📚 Okul Bilgisi", "• Öğle arası kaçta?<br>• Bilişim sınıfı neresi?<br>• Seçmeli ders günü?"), unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# 💬 SOHBET AKIŞI
if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if girdi := st.chat_input("Ders programı hakkında bir soru sorun..."):
    if suzgec_kontrolu(girdi):
        st.error("⚠️ Güvenlik Süzgeci: Uygunsuz dil algılandı.")
    else:
        st.session_state.messages.append({"role": "user", "content": girdi})
        with st.chat_message("user"): st.markdown(girdi)
        
        with st.chat_message("assistant"):
            with st.spinner("⏳ Program inceleniyor..."):
                cevap, kaynaklar = okul_asistani_sorgula(girdi, vektor_tabani)
                st.markdown(cevap)
                if kaynaklar:
                    with st.expander("📌 Kaynak Bilgi"):
                        for k in kaynaklar: st.caption(k)
                st.session_state.messages.append({"role": "assistant", "content": cevap})
                st.rerun()
