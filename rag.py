from groq import Groq
import os

def okul_asistani_sorgula(soru, vector_db):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=api_key)

        docs = vector_db.similarity_search(soru, k=4)
        baglam = "\n\n".join([doc.page_content for doc in docs])
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"Sen bir okul asistanısın. SADECE şu verilere göre cevap ver:\n{baglam}"},
                {"role": "user", "content": soru}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        
        cevap = chat_completion.choices[0].message.content
        kaynaklar = [doc.page_content[:100] for doc in docs]
        return cevap, kaynaklar
    except Exception as e:
        return f"Hata: {str(e)}", []
