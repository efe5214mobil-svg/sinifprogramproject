import streamlit as st
import os
from rag import okul_asistani_sorgula
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Okul Asistanı", layout="centered")

# --- CSS (Kartlar ve Buton) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .kart {
        background-color: #161922;
        border-radius: 12px;
        padding: 20px;
        border-top: 5px solid #1E90FF;
        margin-bottom: 10px;
        min-height: 150px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ Okul Ders Programı")

# 💡 Kartlar (HTML/CSS Sorunu Yaşarsan st.info Kullanabiliriz)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="kart" style="border-color:#FF4B4B"><b style="color:#FF4B4B">🔍 Sınıflar</b><br><br>9A Pazartesi?</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="kart" style="border-color:#FF8C00"><b style="color:#FF8C00">👨‍🏫 Hocalar</b><br><br>U.TRK ne zaman?</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="kart" style="border-color:#1E90FF"><b style="color:#1E90FF">📚 Genel</b><br><br>Öğle arası?</div>', unsafe_allow_html=True)

st.divider()

if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if girdi := st.chat_input("Sorunuzu buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": girdi})
    with st.chat_message("user"): st.markdown(girdi)
    
    with st.chat_message("assistant"):
        # Vektör DB yerine doğrudan dosyayı referans alıyoruz
        cevap = okul_asistani_sorgula(girdi, "ders_programi.xlsx") 
        st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
