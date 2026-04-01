import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from rag import okul_asistani_sorgula
from dotenv import load_dotenv

load_dotenv()

# Sayfa Ayarı
st.set_page_config(page_title="Okul Asistanı", layout="centered")

# CSS - Kartları ve Mavi Butonu Zorla Çizdiriyoruz
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    [data-testid="stVerticalBlock"] > div:has(div.ozel-kart) {
        display: flex;
        flex-direction: row;
        gap: 10px;
    }
    .ozel-kart {
        background-color: #161922;
        border-radius: 15px;
        padding: 20px;
        border-top: 5px solid #FF4B4B;
        min-height: 180px;
        color: #808495;
    }
    .yuzen-buton { position: fixed; bottom: 80px; right: 20px; z-index: 999; }
    .stLinkButton a {
        background-color: #1E90FF !important;
        border: 2px solid white !important;
        border-radius: 25px !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def veri_tabanini_yukle():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return Chroma(persist_directory="sinif_programi_vektor", embedding_function=embeddings)

vektor_tabani = veri_tabanini_yukle()

# Başlık
st.markdown("<h1 style='text-align: center; color: white;'>🏛️ Okul Ders Programı Asistanı</h1>", unsafe_allow_html=True)

# Mavi Buton (Sağ Alt)
st.markdown('<div class="yuzen-buton">', unsafe_allow_html=True)
st.link_button("🏛️ MEB Yönetmelik", "https://meb-yonetmelik.streamlit.app/")
st.markdown('</div>', unsafe_allow_html=True)

# 💡 HIZLI SORULAR - KARTLAR
st.markdown("### 💡 Hızlı Sorular")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="ozel-kart" style="border-top-color: #FF4B4B;"><b style="color: #FF4B4B;">🔍 Sınıf Programı</b><br><br>• 9A Pazartesi?<br>• 11B Cuma?<br>• 10C Salı?</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="ozel-kart" style="border-top-color: #FF8C00;"><b style="color: #FF8C00;">👨‍🏫 Öğretmenler</b><br><br>• U.TRK Salı nerede?<br>• Matematik hocası?<br>• Ahmet Yılmaz?</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="ozel-kart" style="border-top-color: #1E90FF;"><b style="color: #1E90FF;">📚 Okul Bilgisi</b><br><br>• Öğle arası?<br>• Bilişim sınıfı?<br>• Seçmeli günü?</div>', unsafe_allow_html=True)

st.divider()

# Sohbet
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if girdi := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": girdi})
    with st.chat_message("user"): st.markdown(girdi)
    with st.chat_message("assistant"):
        cevap, _ = okul_asistani_sorgula(girdi, vektor_tabani)
        st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
        st.rerun()
