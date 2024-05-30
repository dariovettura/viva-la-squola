import os
import re
import requests
from bs4 import BeautifulSoup
import json


def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    tbody = soup.find("tbody")
    if tbody:
        rows = tbody.find_all("tr")
        data = []
        for row in rows:
            title = row.find("a").text.strip()
            href = row.find("a")["href"]
            full_link = "metti il link corretto/" + href
            date = row.find(class_="list-date").text.strip()

            attachments = download_attachments(full_link)

            data.append({"title": title, "date": date, "allegati": attachments})
        return data
    else:
        print("Nessun tag <tbody> trovato nel file HTML.")
def download_attachments(link):
    attachments = []
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        filenames = soup.select('.at_filename a.at_url')
        for filename in filenames:
            attachment_link = filename['href']
            attachment_name = filename.text.strip()
            attachment_filename = f"{attachment_name}" 
            download_path = os.path.join("muro_media", attachment_filename)
            
            try:
                with open(download_path, 'wb') as f:
                    attachment_response = requests.get(attachment_link)
                    f.write(attachment_response.content)
            except FileNotFoundError as e:
                print(f"Errore: {e}. Impossibile salvare il file '{attachment_filename}'.")
            else:
                attachments.append(attachment_filename)
    return attachments




def save_to_json(data, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    html_file = "albi.html"
    json_file = "muro.json"

    if not os.path.exists("muro_media"):
        os.makedirs("muro_media")

    parsed_data = parse_html(html_file)
    if parsed_data:
        save_to_json(parsed_data, json_file)
        print("File JSON creato con successo.")
    else:
        print("Errore durante l'analisi del file HTML.")
