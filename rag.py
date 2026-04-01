from groq import Groq
import os

# API anahtarını doğrudan os.getenv ile çekiyoruz
# Streamlit'te kullanırken secrets.toml'dan çekmek için main'de ayar yapacağız
def okul_asistani_sorgula(soru, vector_db):
    try:
        # 1. API İstemcisini Başlat
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Hata: GROQ_API_KEY bulunamadı.", []
            
        client = Groq(api_key=api_key)

        # 2. Benzerlik araması (k=3 yeterli ama k=5 bazen daha iyi bağlam sunar)
        docs = vector_db.similarity_search(soru, k=4)
        
        # 3. Bağlamı birleştirme
        baglam = "\n\n".join([doc.page_content for doc in docs])
        
        # 4. Groq API çağrısı
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Sen profesyonel bir okul asistanısın. SADECE verilen bağlamdaki ders programı bilgilerini kullan. Eğer sorulan soru bağlamda (ders programında) yoksa, kibarca bu bilgiye sahip olmadığını belirt. Başka kaynaklardan bilgi uydurma."
                },
                {
                    "role": "user", 
                    "content": f"Bağlam (Ders Programı):\n{baglam}\n\nSoru: {soru}"
                }
            ],
            model="llama-3.3-70b-versatile", # Daha güçlü bir model önerisi
            temperature=0.1, # Daha kesin cevaplar için 0.1 idealdir
        )
        
        cevap = chat_completion.choices[0].message.content
        
        # Kaynakları metadata ile birlikte alalım (Daha profesyonel görünür)
        kaynaklar = []
        for doc in docs:
            sinif = doc.metadata.get("sinif", "Bilinmeyen Sınıf")
            kaynaklar.append(f"Kaynak: {sinif} - İçerik: {doc.page_content[:150]}...")

        return cevap, kaynaklar

    except Exception as e:
        return f"Bir hata oluştu: {str(e)}", []
