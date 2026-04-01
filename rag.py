from groq import Groq
import os

def okul_asistani_sorgula(soru, vector_db):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=api_key)

        # 1. Kullanıcın sorusundaki sınıf ismini normalize et (9-A -> 9A gibi)
        # Bu, arama motorunun doğru dökümanı bulmasına yardımcı olur.
        arama_sorusu = soru.replace("-", "").replace(" ", "")

        # 2. Vektör DB'den en alakalı dökümanları çek
        docs = vector_db.similarity_search(arama_sorusu, k=4)
        baglam = "\n\n".join([doc.page_content for doc in docs])
        
        # 3. Groq'a Sınıf Formatı ve Tablo Talimatı Ver
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": f"""Sen bir okul ders programı asistanısın. 
                    Veritabanındaki sınıf isimleri '9A', '9B', '10C' gibi bitişik yazılmaktadır.
                    
                    SADECE şu verilere göre cevap ver: {baglam}
                    
                    KURALLAR:
                    1. Cevap verirken sınıf ismini kullanıcının sorduğu gibi değil, verideki gibi (örn: 9A) kullan.
                    2. Program bilgilerini MUTLAKA Markdown TABLO formatında sun.
                    3. Tablo sütunları: | Saat/Sıra | Ders | Öğretmen | Yer |
                    4. Eğer dökümanda o sınıfa ait bilgi yoksa, 'Üzgünüm, {soru} için program verisi bulunamadı' de.
                    5. Gereksiz yorum yapma, doğrudan tabloyu paylaş."""
                },
                {"role": "user", "content": soru}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        
        cevap = chat_completion.choices[0].message.content
        return cevap, [d.page_content[:100] for d in docs]
    except Exception as e:
        return f"❌ Bir hata oluştu: {str(e)}", []
