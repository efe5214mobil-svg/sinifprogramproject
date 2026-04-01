from groq import Groq
import os
import pandas as pd # Excel okumak için

def okul_asistani_sorgula(soru, dosya_yolu="ders_programi.xlsx"):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # 1. Excel'den veriyi metne dönüştür (En Garanti Yol)
        # Eğer PDF kullanacaksan burada pdf_plumber gibi bir kütüphane gerekir.
        df = pd.read_excel(dosya_yolu)
        program_metni = df.to_string() # Tüm tabloyu yazıya döküyoruz
        
        system_msg = f"""Sen bir okul asistanısın. 
        Aşağıdaki ham ders programı verisini kullanarak tablo oluştur.
        
        DERS PROGRAMI VERİSİ:
        {program_metni}
        
        KURALLAR:
        1. Sınıf isimleri 9A, 9B, 10C formatındadır.
        2. Yanıtı MUTLAKA Markdown TABLO olarak ver.
        3. Bilgi bulamazsan uydurma.
        """
        
        yanit = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": soru}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0
        )
        return yanit.choices[0].message.content
    except Exception as e:
        return f"Hata: {str(e)}"
