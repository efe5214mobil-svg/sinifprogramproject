from groq import Groq
import os

def okul_asistani_sorgula(soru, vector_db):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=api_key)

        # Sınıf araması için soruyu temizle (9-A -> 9A)
        arama_normal = soru.upper().replace("-", "").replace(" ", "")
        
        docs = vector_db.similarity_search(arama_normal, k=5)
        baglam = "\n\n".join([doc.page_content for doc in docs])
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": f"""Sen bir okul ders programı asistanısın. 
                    PDF verisindeki sınıflar '9A', '9B', '10C' gibi bitişik yazılmıştır.
                    
                    ELİNDEKİ VERİ:
                    {baglam}
                    
                    CEVAPLAMA KURALLARI:
                    1. Kullanıcı 9-A dese bile sen verideki '9A' bilgisine odaklan.
                    2. Programı SADECE tablo şeklinde ver.
                    3. Tablo Sütunları: | Sıra/Saat | Ders Adı | Öğretmen | Sınıf |
                    4. Eğer dökümanda o gün/saat için ders yoksa 'Ders Boş' veya 'Bilgi Yok' de.
                    5. Sadece sana verilen bağlama sadık kal, dışarıdan bilgi ekleme."""
                },
                {"role": "user", "content": soru}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        
        return chat_completion.choices[0].message.content, [d.page_content[:100] for d in docs]
    except Exception as e:
        return f"❌ Hata: {str(e)}", []
