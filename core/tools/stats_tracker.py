"""
stats_tracker.py - Captura métricas reales de TikTok usando Selenium
Funciones:
- trackear_perfil_tiktok: obtiene seguidores y likes totales del perfil
- analizar_videos_recientes: obtiene datos de los últimos videos (título, vistas, etc.)
"""

import os
import time
import logging
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

# Configuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_CSV = "output/metricas_rendimiento.csv"
os.makedirs("output", exist_ok=True)

# ============================================================
# FUNCIÓN 1: Perfil
# ============================================================

def trackear_perfil_tiktok(usuario_url, headless=True):
    """
    Obtiene métricas reales de un perfil de TikTok usando Selenium.
    Ejemplo: https://www.tiktok.com/@datoscuriososmundo520
    """
    logger.info(f"🌐 Accediendo a {usuario_url}")
    
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(usuario_url)
        time.sleep(5)
        
        seguidores = "0"
        likes = "0"
        
        # Selectores para seguidores
        selectores_seguidores = [
            '[data-e2e="followers-count"]',
            'strong[title*="Followers"]',
            '.count-infos .number'
        ]
        for selector in selectores_seguidores:
            try:
                elemento = driver.find_element(By.CSS_SELECTOR, selector)
                seguidores = elemento.text.strip()
                logger.info(f"Seguidores encontrados con {selector}: {seguidores}")
                break
            except NoSuchElementException:
                continue
        
        # Selectores para likes totales
        selectores_likes = [
            '[data-e2e="likes-count"]',
            'strong[title*="Likes"]',
            '.count-infos .number'
        ]
        for selector in selectores_likes:
            try:
                elemento = driver.find_element(By.CSS_SELECTOR, selector)
                likes = elemento.text.strip()
                logger.info(f"Likes encontrados con {selector}: {likes}")
                break
            except NoSuchElementException:
                continue
        
        if seguidores == "0" and likes == "0":
            screenshot = f"output/debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot)
            logger.warning(f"No se encontraron datos. Pantalla guardada en {screenshot}")
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        data = {
            "fecha": fecha,
            "seguidores": seguidores,
            "likes_totales": likes,
            "url": usuario_url
        }
        
        df = pd.DataFrame([data])
        header = not os.path.exists(OUTPUT_CSV)
        df.to_csv(OUTPUT_CSV, mode='a', header=header, index=False, encoding="utf-8")
        
        logger.info(f"✅ Datos guardados: {data}")
        return data
        
    except Exception as e:
        logger.error(f"Error durante el scraping: {e}")
        return None
    finally:
        driver.quit()

# ============================================================
# FUNCIÓN 2: Videos recientes (mejorada)
# ============================================================

def analizar_videos_recientes(usuario_url, max_videos=10, headless=True):
    """
    Extrae métricas de los últimos videos del perfil.
    Retorna lista de diccionarios con:
    - titulo, vistas, likes, comentarios, shares, guardados, url
    """
    logger.info(f"📹 Analizando últimos {max_videos} videos de {usuario_url}")
    
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    videos_data = []
    
    try:
        driver.get(usuario_url)
        time.sleep(5)
        
        # Guardar HTML inicial para depuración
        with open("output/debug_page_initial.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        logger.info("HTML inicial guardado en output/debug_page_initial.html")
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        # Lista de posibles selectores para videos (actualiza según lo que encuentres)
        selectores_video = [
            'div[data-e2e="user-post-item"]',
            'div[data-e2e="video-card"]',
            'div[class*="DivVideoCard"]',
            'a[href*="/video/"]'  # Enlaces directos a videos
        ]
        
        while len(videos_data) < max_videos and scroll_attempts < max_scrolls:
            # Buscar con cada selector
            video_elements = []
            for selector in selectores_video:
                elems = driver.find_elements(By.CSS_SELECTOR, selector)
                if elems:
                    logger.info(f"Selector '{selector}' encontró {len(elems)} elementos")
                    video_elements = elems
                    break
            
            if video_elements:
                # Procesar cada elemento encontrado
                for idx, video in enumerate(video_elements[:max_videos]):
                    try:
                        # Extraer título (puede estar en un atributo alt o texto)
                        titulo = ""
                        try:
                            # Intentar con el texto alternativo de la imagen
                            img = video.find_element(By.CSS_SELECTOR, 'img')
                            titulo = img.get_attribute('alt') or ""
                        except:
                            pass
                        if not titulo:
                            try:
                                desc = video.find_element(By.CSS_SELECTOR, '[data-e2e="video-desc"]')
                                titulo = desc.text.strip()
                            except:
                                pass
                        
                        # Vistas
                        vistas = "0"
                        try:
                            vistas_elem = video.find_element(By.CSS_SELECTOR, 'strong[data-e2e="video-views"]')
                            vistas = vistas_elem.text.strip()
                        except:
                            pass
                        
                        # Enlace
                        enlace = ""
                        try:
                            link_elem = video.find_element(By.CSS_SELECTOR, 'a')
                            enlace = link_elem.get_attribute('href')
                        except:
                            pass
                        
                        video_info = {
                            "titulo": titulo,
                            "vistas": vistas,
                            "url": enlace,
                            "likes": "0",
                            "comentarios": "0",
                            "shares": "0",
                            "guardados": "0"
                        }
                        
                        videos_data.append(video_info)
                        logger.info(f"Video {idx+1}: {vistas} vistas - {titulo[:30]}...")
                        
                    except StaleElementReferenceException:
                        logger.warning("Elemento obsoleto, reintentando...")
                        continue
                    except Exception as e:
                        logger.warning(f"Error procesando video {idx}: {e}")
                        continue
                
                break  # Salir del bucle si ya encontramos videos
            
            # Si no hay videos, hacer scroll y esperar
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_attempts += 1
        
        # Si después de todo no hay videos, guardar HTML final
        if not videos_data:
            with open("output/debug_page_final.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.warning("No se encontraron videos. HTML final guardado en output/debug_page_final.html")
        else:
            logger.info(f"Total videos procesados: {len(videos_data)}")
        
        # Guardar en CSV
        df = pd.DataFrame(videos_data)
        csv_path = "output/metricas_videos.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")
        logger.info(f"Datos de videos guardados en {csv_path}")
        
        return videos_data
        
    finally:
        driver.quit()

def _extraer_metricas_video(driver, video_url):
    """Navega a la página del video y extrae métricas (opcional)."""
    driver.get(video_url)
    time.sleep(3)
    metricas = {}
    
    try:
        likes = driver.find_element(By.CSS_SELECTOR, '[data-e2e="like-count"]').text.strip()
        metricas["likes"] = likes
    except:
        pass
    try:
        comments = driver.find_element(By.CSS_SELECTOR, '[data-e2e="comment-count"]').text.strip()
        metricas["comentarios"] = comments
    except:
        pass
    try:
        shares = driver.find_element(By.CSS_SELECTOR, '[data-e2e="share-count"]').text.strip()
        metricas["shares"] = shares
    except:
        pass
    try:
        saves = driver.find_element(By.CSS_SELECTOR, '[data-e2e="save-count"]').text.strip()
        metricas["guardados"] = saves
    except:
        pass
    
    return metricas

# ============================================================
# EJECUCIÓN DIRECTA (prueba)
# ============================================================
if __name__ == "__main__":
    # Prueba con tu perfil (ventana visible para depurar)
    trackear_perfil_tiktok("https://www.tiktok.com/@datoscuriososmundo520", headless=False)
    # También puedes probar videos:
    # analizar_videos_recientes("https://www.tiktok.com/@datoscuriososmundo520", max_videos=3, headless=False)