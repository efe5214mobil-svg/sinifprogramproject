from groq import Groq
import os

def okul_asistani_sorgula(soru, vector_db):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        docs = vector_db.similarity_search(soru, k=4)
        baglam = "\n\n".join([d.page_content for d in docs])
        
        system_msg = f"""Sen okul ders programı asistanısın. 
        Sadece bu verilere göre cevap ver: {baglam}
        Cevabında ders programı varsa mutlaka Markdown TABLO kullan.
        Sütunlar: | Saat | Ders | Öğretmen | Yer |
        """
        
        yanit = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": soru}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        return yanit.choices[0].message.content, [d.page_content for d in docs]
    except Exception as e:
        return f"Hata: {e}", []
