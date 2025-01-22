import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import pyodbc

# URL della homepage di **********
base_url = "********"

def fetch_page(url):
    """Scarica il contenuto HTML della pagina specificata."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Errore durante il download della pagina {url}: {e}")
        return None

def extract_article_links(html):
    """Estrae i link degli articoli completi dalla homepage."""
    soup = BeautifulSoup(html, 'html.parser')
    article_links = []
    # Trova tutti i link con il testo "Articolo completo »"
    for a_tag in soup.find_all('a', string="Articolo completo »"):
        href = a_tag.get('href')
        if href:
            # Costruisce l'URL completo
            #full_url = base_url + href
            full_url = href
            article_links.append(full_url)
    return article_links

def extract_article_content(html):
    """Estrae il titolo e il contenuto dell'articolo dalla pagina."""
    soup = BeautifulSoup(html, 'html.parser')
    # Trova il titolo dell'articolo
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else 'Titolo non trovato'
    # Trova il contenuto dell'articolo
    content_tag = soup.find('div', class_='entry-content')
    content = content_tag.get_text(strip=True) if content_tag else 'Contenuto non trovato'
    return title, content

# Configura la connessione a SQL Server
def get_db_connection():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=*********\\SQLEXPRESS;"
        "Database=LEXAI;"
        "Trusted_Connection=yes;"
    )
    return conn

def save_to_database(data, fonte):
    """Inserisce i dati estratti nel database, gestendo il campo 'Errore'."""
    conn = get_db_connection()
    cursor = conn.cursor()

    for article in data:
        errore = "Contenuto non trovato" if article['content'] == "Contenuto non trovato" else None
        cursor.execute(
            """
            IF NOT EXISTS (
                SELECT 1 FROM Articoli
                WHERE Fonte = ? AND Titolo = ?
            )
            BEGIN
                INSERT INTO Articoli (Fonte, Titolo, Contenuto, Link, Keywords, EstrazioneKeywords, Errore)
                VALUES (?, ?, ?, ?, NULL, 'N', ?)
            END
            """,
            fonte,                    # Controllo per duplicati
            article['title'],         # Controllo per duplicati
            fonte,                    # Nome del sito
            article['title'],         # Titolo dell'articolo
            article['content'],       # Contenuto dell'articolo
            article['url'],           # Link dell'articolo
            errore                    # Errore (se presente)
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("Articoli salvati nel database.")

def main():
    # Scarica la homepage
    fonte = "****"  # Nome del sito da cui estraggo i dati, nell'ottica di avere uno scraper dedicato per ogni sito in modo da poter intervenire in maniera mirata in caso di cambiamenti nelle politiche o nella struttura del sito 
    homepage_html = fetch_page(base_url)
    if not homepage_html:
        return

    # Estrae i link degli articoli
    article_links = extract_article_links(homepage_html)
    if not article_links:
        print("Nessun link di 'Articolo completo »' trovato.")
        return

    articles = []
    for link in article_links:
        print(f"Elaborazione dell'articolo: {link}")
        article_html = fetch_page(link)
        if article_html:
            title, content = extract_article_content(article_html)
            articles.append({'title': title, 'content': content, 'url': link})
            # Rispetta le buone pratiche di scraping aggiungendo una pausa tra le richieste
            time.sleep(1)

    # Salva gli articoli in un file CSV
    df = pd.DataFrame(articles)
    df.to_csv('articoli_legalmente.csv', index=False, encoding='utf-8')
    print("Articoli salvati in 'articoli_legalmente.csv'.")


    # Salva nel database con il nome del sito
    save_to_database(articles, fonte)
    print("Scraping completato e articoli salvati nel database.")

if __name__ == "__main__":
    main()
