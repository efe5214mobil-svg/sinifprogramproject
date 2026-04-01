import streamlit as st
import os
import re
import time
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from rag import okul_asistani_sorgula  # rag.py'deki fonksiyonun

# 🔐 API ve Çevre Değişkenleri
load_dotenv()

# 🧠 Vektör DB Yükleme Fonksiyonu
@st.cache_resource
def veri_tabanini_yukle():
    # HuggingFace modelini tanımla (rag.py ile aynı model olmalı)
    gomme_modeli = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Kaydedilmiş klasörü oku
    return Chroma(persist_directory="okul_asistani_gpt_db", embedding_function=gomme_modeli)

vektor_tabani = veri_tabanini_yukle()

# 🎨 Sayfa Yapılandırması ve CSS (Senin Tasarımın)
st.set_page_config(page_title="Okul Asistanı", page_icon="📅", layout="centered")

st.markdown("""
<style>
    .stApp { font-family: 'Inter', sans-serif; }
    .ana-baslik { font-size: 2.5rem; font-weight: 800; text-align: center; margin-bottom: 1.5rem; color: #FFFFFF; }
    .kategori-kutusu {
        background-color: rgba(128, 128, 128, 0.05);
        border-radius: 15px;
        padding: 18px;
        border-top: 4px solid #FF8C00;
        height: 100%;
        margin-bottom: 10px;
    }
    .kategori-basligi { font-weight: bold; color: #FF8C00; margin-bottom: 10px; font-size: 1.15rem; }
    .kategori-maddesi { font-size: 0.88rem; margin-bottom: 6px; color: #ccc; }
</style>
""", unsafe_allow_html=True)

# 🛡️ ÇELİK ZIRHLI GÜVENLİK SÜZGECİ
def suzgec_kontrolu(metin):
    karakter_haritasi = {'1': 'i', '0': 'o', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '@': 'a', '$': 's'}
    temiz_metin = metin.lower()
    for eski, yeni in karakter_haritasi.items():
        temiz_metin = temiz_metin.replace(eski, yeni)
    
    sikistirilmis_metin = re.sub(r'[^a-z0-9çşğüöı]', '', temiz_metin)
    
    # Senin yasaklı listen (Kısaltılmış, sen tamamını ekle)
    yasakli_kelimeler = ["oc", "aq", "amk", "sik", "teror", "siyaset"] 
    return any(yasakli in sikistirilmis_metin for yasakli in yasakli_kelimeler)

# 💬 Sohbet Geçmişi Yönetimi
if "sohbet_gecmisi" not in st.session_state:
    st.session_state.sohbet_gecmisi = []

# --- ARAYÜZ BAŞLANGIÇ ---
st.markdown("<div class='ana-baslik'>📅 Okul Ders Programı Asistanı</div>", unsafe_allow_html=True)

# 💡 Hızlı Sorular (Öneri Kartları)
st.markdown("### 💡 Hızlı Sorular")
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">🔍 Sınıf Bazlı</div><div class="kategori-maddesi">9-A Pazartesi programı nedir?</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">👨‍🏫 Öğretmenler</div><div class="kategori-maddesi">U.TRK hocanın dersleri ne zaman?</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown('<div class="kategori-kutusu"><div class="kategori-basligi">📚 Dersler</div><div class="kategori-maddesi">Bilişim dersi hangi gün?</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Sohbet Akışı
for ileti in st.session_state.sohbet_gecmisi:
    with st.chat_message(ileti["role"]):
        st.markdown(ileti["content"])

# Giriş Alanı
if girdi := st.chat_input("Ders programı hakkında bir soru sorun..."):
    
    if suzgec_kontrolu(girdi):
        st.error("⚠️ İletiniz uygunsuz içerik barındırdığı için engellenmiştir.")
    else:
        # Kullanıcı mesajını ekle
        st.session_state.sohbet_gecmisi.append({"role": "user", "content": girdi})
        with st.chat_message("user"):
            st.markdown(girdi)

        # Asistan yanıtı
        with st.chat_message("assistant"):
            with st.spinner("⏳ Program inceleniyor..."):
                # rag.py içindeki fonksiyonu çağırıyoruz
                cevap, kaynaklar = okul_asistani_sorgula(girdi, vektor_tabani)
                
                st.markdown(cevap)
                
                # İstersen kaynakları küçük bir genişletilebilir alanda göster
                with st.expander("📚 Bilgi Kaynakları"):
                    for k in kaynaklar:
                        st.write(k)
                
                st.session_state.sohbet_gecmisi.append({"role": "assistant", "content": cevap})
                st.rerun()
