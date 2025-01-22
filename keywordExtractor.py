import pyodbc
import openai 

# Configura la connessione al database
def get_db_connection():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=localhost\\SQLEXPRESS;"
        "Database=LexAI;"
        "Trusted_Connection=yes;"
    )
    return conn


openai.api_key = "*********"  # Sostituisci con la tua chiave OpenAI
# Funzione per chiamare l'API di OpenAI
def get_keywords_from_gpt(content):
    # Configura OpenAI

    # Prompt shell per l'elaborazione delle parole chiave
    PROMPT_SHELL = "Sei esperto nell'analizzare testi giuridici e identificare le parole chiave"

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "developer", "content": f"{PROMPT_SHELL}"},
                {
                    "role": "user",
                    "content": (f"Estrai fino a 20 parole chiave significative dal seguente testo. "
                               f"Rispondi elencando solo le keywords separate da una virgola, solo questo e basta:\n\n{content}"
                                )
                }
            ]
        )
        keywords=completion.choices[0].message.content
        #keywords = response.choices[0].text.strip()
        print(keywords)
        return keywords
    
    except Exception as e:
        print(f"Errore durante la chiamata all'API OpenAI: {e}")
        return None
    
    

# Funzione per elaborare i record e aggiornare il database
def process_records():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Seleziona i record con EstrazioneKeywords = 'N'
    cursor.execute("SELECT top 1 Id, Contenuto FROM Articoli WHERE EstrazioneKeywords = 'N'")
    records = cursor.fetchall()

    for record in records:
        article_id = record[0]
        content = record[1]

        print(f"Elaborazione articolo ID: {article_id}")

        # Chiamata all'API per ottenere le keywords
        keywords = get_keywords_from_gpt(content)
        if keywords:
            # Aggiorna il record con le keywords estratte
            cursor.execute(
                """
                UPDATE Articoli
                SET Keywords = ?, EstrazioneKeywords = 'Y'
                WHERE Id = ?
                """,
                str(keywords), article_id
            )
            conn.commit()
            print(f"Articolo ID {article_id} aggiornato con keywords.")
        else:
            print(f"Errore nell'elaborazione dell'articolo ID {article_id}.")

    cursor.close()
    conn.close()

# Esegui il processo
if __name__ == "__main__":
    process_records()
