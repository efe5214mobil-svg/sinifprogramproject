from groq import Groq
import os

def okul_asistani_sorgula(soru, vector_db):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=api_key)

        # 1. Vektör DB'den en yakın 4 dökümanı çek
        docs = vector_db.similarity_search(soru, k=4)
        baglam = "\n\n".join([doc.page_content for doc in docs])
        
        # 2. Groq'a Tablo Formatı Talimatı Veriyoruz
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": f"""Sen bir okul ders programı asistanısın. 
                    SADECE sana verilen şu verilere göre cevap ver: {baglam}
                    
                    KURALLAR:
                    1. Eğer cevap bir program veya liste içeriyorsa, MUTLAKA Markdown TABLO yapısında sun.
                    2. Tablo sütunları şunlar olsun: | Saat/Sıra | Ders Adı | Öğretmen | Sınıf/Yer |
                    3. Bilgi yoksa uydurma, 'Aradığınız bilgi programda bulunamadı' de.
                    4. Cevapların kısa, net ve anlaşılır olsun."""
                },
                {"role": "user", "content": soru}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        
        cevap = chat_completion.choices[0].message.content
        kaynaklar = [doc.page_content[:100] for doc in docs]

        return cevap, kaynaklar
    except Exception as e:
        return f"❌ Hata: {str(e)}", []
