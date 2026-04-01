from groq import Groq
import os

def okul_asistani_sorgula(soru, vector_db):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=api_key)

        docs = vector_db.similarity_search(soru, k=4)
        baglam = "\n\n".join([doc.page_content for doc in docs])
        
        system_prompt = f"""Sen profesyonel bir okul asistanısın. 
        SADECE şu ders programı verilerine dayanarak cevap ver: {baglam}
        
        ÖNEMLİ KURALLAR:
        1. Eğer bir program listesi veriyorsan MUTLAKA Markdown TABLO kullan.
        2. Tablo sütunları: | Saat/Sıra | Ders | Öğretmen | Yer | şeklinde olsun.
        3. Bilgi yoksa uydurma, 'Programda bulunamadı' de.
        4. Cevapların kibar ve net olsun.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": soru}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        
        return chat_completion.choices[0].message.content, [d.page_content[:100] for d in docs]
    except Exception as e:
        return f"❌ Hata oluştu: {str(e)}", []
