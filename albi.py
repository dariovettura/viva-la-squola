
import requests
from bs4 import BeautifulSoup
import os
import json




# Funzione per ottenere i dati da una pagina
def get_page_data(page_url, id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(page_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
       
        article = soup.find(class_="article-body")
        article_header = article.find(class_="article-header")

         # Estrai il titolo dall'elemento con classe "itemTitle"
        title = article_header.find('a').get_text(strip=True)
        content = ""
        layout_area = soup.find(class_="layoutArea")
    
        if layout_area:
            # Trova tutti gli elementi 'span' all'interno della sezione trovata
            span_tags = layout_area.find_all("span")
            
            # Controlla se ci sono elementi 'span'
            if span_tags:
                # Estrai il testo da ciascun elemento 'span' e uniscilo con una virgola
                span_texts = [span.get_text(strip=True) for span in span_tags]
                content = ", ".join(span_texts)
            
        date = article.find('time').get_text(strip=True)

        # Estrai gli allegati, se presenti
        allegati = download_attachments(soup)
        
        return {
            "id": id,
            "title": title,
            "content": content,
            "date": date,
            "allegati": allegati,
        }
    else:
        return None

# # Funzione per scaricare gli allegati da una pagina
def download_attachments(page_soup):
    section = page_soup.find('div', class_="attachmentsContainer")
    allegati = []
    
    if section:
        item_attachments = section.find_all('a', class_="at_url")
        
        if item_attachments:
            for link in item_attachments:
                attachment_url = link.get("href")
                url_parts = attachment_url.split("/")
                attachment_name = url_parts[-1]
                download_url = attachment_url
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
                
                try:
                    response = requests.get(download_url, headers=headers, stream=True)
                    response.raise_for_status()
                except requests.exceptions.HTTPError as http_err:
                    print(f"Errore HTTP durante il download di {attachment_name}: {http_err}")
                    # allegati.append({"name": "Niente"})
                    continue
                except requests.exceptions.ConnectionError as conn_err:
                    print(f"Errore di connessione durante il download di {attachment_name}: {conn_err}")
                    # allegati.append({"name": "Niente"})
                    continue
                except requests.exceptions.Timeout as timeout_err:
                    print(f"Timeout durante il download di {attachment_name}: {timeout_err}")
                    # allegati.append({"name": "Niente"})
                    continue
                except requests.exceptions.RequestException as req_err:
                    print(f"Errore durante il download di {attachment_name}: {req_err}")
                    # allegati.append({"name": "Niente"})
                    continue
                
                if response.status_code == 200:
                    attachment_name = os.path.basename(attachment_url)
                    new_attachment_name = f"{attachment_name}"
                    save_directory = "polo_media"
                    os.makedirs(save_directory, exist_ok=True)
                    file_path = os.path.join(save_directory, new_attachment_name)
                    
                    with open(file_path, "wb") as file:
                        file.write(response.content)
                    
                    print("Scaricato: {}".format(new_attachment_name))
                    allegati.append(new_attachment_name)
                else:
                    print(f"Errore durante il download di {attachment_name}: Status Code {response.status_code}")
                    continue
    
    return allegati

# Lista per memorizzare gli oggetti estratti
result_data = []

base_url = ""
ids = range(1, 128, +1)
# 1458
# 84
# Lista per memorizzare gli oggetti estratti
result_data = []

# Itera attraverso gli ID e ottieni i dati da ciascuna pagina
for id in ids:
    page_url = f"{base_url}{id}"
    page_data = get_page_data(page_url,id)
    if page_data:
        result_data.append(page_data)
    else:
        print(f"Errore durante il recupero dei dati dalla pagina {page_url}")


# Specifica il nome del file in cui salvare i dati JSON
output_file = "polo_result.json"

# Serializza result_data in formato JSON e scrivilo su un file
with open(output_file, "w") as json_file:
    json.dump(result_data, json_file)

print(f"I dati sono stati salvati nel file {output_file}")
