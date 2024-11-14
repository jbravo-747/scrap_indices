import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

# URL del sitio
url = "https://imco.org.mx/indices/#indices"
headers = {"User-Agent": "Mozilla/5.0"}

# Realizar solicitud a la página
try:
    print("Iniciando solicitud a la página web...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Lanza un error si la solicitud no es exitosa
    print("Solicitud exitosa.")
except requests.exceptions.RequestException as e:
    print(f"Error al realizar la solicitud: {e}")
    exit()

# Analizar el contenido de la página
soup = BeautifulSoup(response.content, 'html.parser')

# Estructuras para almacenar los datos extraídos
indices_data = []

# Buscar todas las secciones con la clase `panel-body`
panels = soup.find_all('div', class_='panel-body')

if not panels:
    print("No se encontraron elementos con la clase 'panel-body'. Verifica la estructura de la página.")
    exit()

print(f"Se encontraron {len(panels)} paneles.")

for i, panel in enumerate(panels, start=1):
    print(f"\nProcesando panel {i}...")
    
    # Obtener el título del índice (class="media-heading")
    title_tag = panel.find('h4', class_='media-heading')
    if title_tag:
        title = title_tag.get_text(strip=True)
        print(f"Título encontrado: {title}")
    else:
        print("Advertencia: No se encontró el título.")
        continue  # Si no hay título, omitir este panel
    
    # Crear una carpeta para cada índice utilizando el título
    folder_name = title.replace(" ", "_")
    os.makedirs(folder_name, exist_ok=True)
    
    # Obtener la imagen de portada (bo-src="indice.portada")
    portada_img = panel.find('img', {'bo-src': 'indice.portada'})
    if portada_img and 'src' in portada_img.attrs:
        portada_url = portada_img['src']
        try:
            print(f"Descargando imagen de portada de {portada_url}...")
            portada_response = requests.get(portada_url, headers=headers)
            portada_response.raise_for_status()
            portada_path = os.path.join(folder_name, "portada.jpg")
            with open(portada_path, 'wb') as file:
                file.write(portada_response.content)
            print("Imagen de portada descargada correctamente.")
        except requests.exceptions.RequestException as e:
            print(f"Error al descargar la imagen de portada: {e}")
    else:
        print("Advertencia: No se encontró la imagen de portada.")
    
    # Obtener el resumen (class="abstract ng-binding")
    resumen_tag = panel.find('p', class_='abstract ng-binding')
    if resumen_tag:
        resumen = resumen_tag.get_text(strip=True)
        print(f"Resumen encontrado: {resumen[:60]}...")  # Muestra una parte del resumen
    else:
        resumen = ""
        print("Advertencia: No se encontró el resumen.")
    
    # Obtener la lista de descargas (class="descargar list-unstyled")
    descargas = panel.find('ul', class_='descargar list-unstyled')
    descarga_urls = []
    
    if descargas:
        links = descargas.find_all('a', href=True)
        print(f"Se encontraron {len(links)} archivos para descargar.")
        for link in links:
            descarga_url = link['href']
            try:
                print(f"Descargando archivo de {descarga_url}...")
                descarga_response = requests.get(descarga_url, headers=headers)
                descarga_response.raise_for_status()
                filename = os.path.join(folder_name, os.path.basename(descarga_url))
                with open(filename, 'wb') as file:
                    file.write(descarga_response.content)
                descarga_urls.append(descarga_url)
                print("Archivo descargado correctamente.")
            except requests.exceptions.RequestException as e:
                print(f"Error al descargar el archivo: {e}")
    else:
        print("Advertencia: No se encontraron archivos para descargar.")
    
    # Añadir los datos a la lista para la exportación a Excel
    indices_data.append({
        'Título': title,
        'Resumen': resumen,
        'Descargas': ', '.join(descarga_urls)  # Lista de URLs de descarga
    })

# Crear un DataFrame de Pandas para exportar a Excel
if indices_data:
    try:
        df = pd.DataFrame(indices_data)
        excel_filename = 'indices_data.xlsx'
        df.to_excel(excel_filename, index=False)
        print(f"\nDatos guardados en {excel_filename}.")
    except Exception as e:
        print(f"Error al guardar el archivo de Excel: {e}")
else:
    print("No se recopilaron datos suficientes para guardar en Excel.")
