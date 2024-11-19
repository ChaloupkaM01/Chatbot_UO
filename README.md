Tento projekt slouží k vytvoření komunikace s API ChatGPT pro školní účely Univerzity obrany.

Postup spuštění:
1. Nainstalování requirements.txt
2. Vytvoření .env s položkami
    API_KEY="API KLÍČ ZÍSKANÝ Z WEBU CHATGPT"
    ASSISTANT_ID="ID SPECIFICKÉHO ASISTENTA"
    
    X_API_KEY="API klíč od https://console.x.ai/"
3. Spuštění main.py
4. Spuštění FastAPI přes konzoli - uvicorn main:app --reload