import pyodbc
import os

# Configura la connessione al database
def get_db_connection():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=localhost\\SQLEXPRESS;"
        "Database=LexAI;"
        "Trusted_Connection=yes;"
    )
    return conn

# Funzione per cercare articoli nella tabella
def search_articles(question):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query per cercare nel testo e nelle parole chiave
    query = """
    SELECT Id, Titolo, Contenuto, Link, Fonte
    FROM Articoli
    WHERE Contenuto LIKE ? OR Keywords LIKE ?
    """
    search_term = f"%{question}%"
    cursor.execute(query, search_term, search_term)
    results = cursor.fetchall()

    cursor.close()
    conn.close()
    return results

# Funzione per salvare un risultato in un file .txt
def save_to_file(article):
    file_name = f"{article['Titolo']}.txt".replace(" ", "_")
    file_path = os.path.join("C:\\Temp\\", file_name)
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"Titolo: {article['Titolo']}\n")
            file.write(f"Fonte: {article['Fonte']}\n")
            file.write(f"Link: {article['Link']}\n")
            file.write(f"Contenuto:\n{article['Contenuto']}\n")
        print(f"Risultato salvato in: {file_path}")
    except Exception as e:
        print(f"Errore durante il salvataggio del file: {e}")

# Funzione principale
def main():
    question = input("Inserisci la tua domanda: ")
    results = search_articles(question)

    if results:
        print("\nRisultati trovati:\n")
        for result in results:
            article = {
                "Id": result[0],
                "Titolo": result[1],
                "Contenuto": result[2],
                "Link": result[3],
                "Fonte": result[4],
            }
            print(f"- Titolo: {article['Titolo']}")
            print(f"  Fonte: {article['Fonte']}")
            print(f"  Link: {article['Link']}")
            print(f"  Contenuto: {article['Contenuto'][:200]}...")  # Mostra solo un estratto del contenuto
            print("\n")

            save_option = input("Vuoi salvare questo articolo in un file .txt? (Y/N): ").strip().upper()
            if save_option == "Y":
                save_to_file(article)
    else:
        print("\nNessun risultato trovato.")

# Esegui lo script
if __name__ == "__main__":
    main()
