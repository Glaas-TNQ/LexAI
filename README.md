# LexAI
Demo Material

https://youtu.be/3DhYOJO5-2U

Create Table
```sql
CREATE TABLE Articoli (
 Id INT IDENTITY(1,1) PRIMARY KEY,
 Fonte NVARCHAR(255) NOT NULL,
 Titolo NVARCHAR(255) NOT NULL,
 Contenuto NVARCHAR(MAX),
 Link NVARCHAR(500),
 Keywords NVARCHAR(500),
 EstrazioneKeywords NVARCHAR(1),
 Errore NVARCHAR(100),
 DataInserimento DATETIME DEFAULT GETDATE()
);
```
