import requests
import os
import json
import csv
from urllib.parse import quote
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime, timezone, time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def setup_browser():
    options = Options()
    # options.use_chromium = True
    # options.add_argument("headless")  # Para ejecutar en modo headless, elimina esta línea si quieres ver el navegador
    pathBrowser = os.path.dirname(os.path.abspath(__file__))
    joinedpath = os.path.join(pathBrowser, "msedgedriver.exe")
    print("directory: ", joinedpath)
    try:
        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Failed to download WebDriver: {e}. Trying to use local driver...")
        try:
            service = EdgeService(executable_path=joinedpath)
            driver = webdriver.Edge(service=service, options=options)
            print("Using local WebDriver.")
            return driver
        except Exception as ex:
            print(f"Failed to use local WebDriver: {ex}")
            return None


async def press_button(driver, by_type, value):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((by_type, value))
        )
        element.click()
        time.sleep(2)  # espera 2 segundos
    except Exception as e:
        print("Fail pressing button: ", e)


if __name__ == "__main__":
    url = "https://clinicalavina.com/especialidadesmedicas"
    url2 = "https://clinicalavina.com/tumedico/especialidad"
    driver = setup_browser()
    driver.get(url)
    driver.implicitly_wait(10)
    lista = []
    lista_medicos = []
    print(url)
    nombre_archivo = f"medicos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    html = driver.page_source
    # print(html)
    # call-btn button orange

    specialties = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".borderEspeciality"))
    )

    print(f"Se encontraron {len(specialties)} especialidades.")

    if not html:
        print("error")
    if not specialties:
        print("No se encontraron botones con la clase 'call-btn button orange'.")

    for i, specialty in enumerate(specialties, 1):
        try:
            # Obtener el texto del elemento <h4> dentro de cada "borderEspeciality"
            h4_element = specialty.find_element(By.TAG_NAME, "h4")
            h4_text = h4_element.text
            # url_encoded_text = quote(h4_text)
            url_encoded_text = h4_text.replace(" ", "%20")
            # print(f"Especialidad {i}: {url_encoded_text}")
            lista.append(f"{url2}/{url_encoded_text}")
            print(lista)

        except Exception as e:
            print(f"Error al procesar especialidad {i}: {e}")

    for j, url_list in enumerate(lista, 1):
        try:
            driver.get(url_list)
            driver.implicitly_wait(3)

            tabla = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#table_id"))
            )
            
            # Definimos manualmente los encabezados correctos
            encabezados = ["Nombre de Médico", "Especialidad", "Ubicación de consultorio", "Teléfonos"]
            #encabezados = [th.text for th in tabla.find_element(By.TAG_NAME, "thead").find_elements(By.TAG_NAME, "th")]
            
            # Obtenemos todas las filas de datos (ignorando el encabezado que está en thead)
            filas = tabla.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")
            
            for fila in filas:
                celdas = fila.find_elements(By.TAG_NAME, "td")
                #print("celdas", celdas)
                #if len(celdas) == 4:  # Verificamos que tenga las 4 columnas esperadas
                medico = {
                    encabezados[0]: celdas[0].text,  # Nombre
                    encabezados[1]: celdas[1].text,  # Especialidad
                    encabezados[2]: celdas[2].text,  # Ubicación
                    encabezados[3]: celdas[3].text   # Teléfonos
                }
                lista_medicos.append(medico)
                #print(f"Datos médico: {medico}")

        except Exception as e:
            print(f"Error al procesar URL {j} ({url_list}): {e}")

    # Resultado final
    print("\n=== LISTA COMPLETA DE MÉDICOS ===")
    for medico in lista_medicos:
        print(medico)
        
    # Campos/columnas del CSV (deben coincidir con las claves de los diccionarios)
    campos = ["Nombre de Médico", "Especialidad", "Ubicación de consultorio", "Teléfonos"]

    try:
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
            escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
            
            # Escribir encabezados
            escritor.writeheader()
            
            # Escribir todos los registros
            escritor.writerows(lista_medicos)
        
        print(f"\n✅ Datos exportados correctamente a: {nombre_archivo}")
        print(f"📝 Total de registros exportados: {len(lista_medicos)}")

    except Exception as e:
        print(f"\n❌ Error al exportar CSV: {e}")