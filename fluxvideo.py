import requests
from bs4 import BeautifulSoup
import re
import m3u8_To_MP4
import m3u8_To_MP4.v2_abstract_task_processor as task_proc
import m3u8_To_MP4.v2_abstract_crawler_processor as crawler_proc
import os
import logging

URL = 'doorfv'

class CustomLogFilter(logging.Filter):
    def filter(self, record):
        return "segment set:" in record.getMessage() or record.levelno >= logging.ERROR

logging.getLogger("m3u8_To_MP4").addFilter(CustomLogFilter())

def upload():
    print(" (                                           (                                         ")
    print(" )\\ ) (                        (             )\\ )                   (            (     ")
    print("(()/( )\\  (     )   (   (  (   )\\ )  (      (()/(      (  (         )\\        )  )\\ )  ")
    print(" /(_)|(_)))\\ ( /(   )\\  )\\ )\\ (()/( ))\\ (    /(_))  (  )\\))(   (   ((_)(   ( /( (()/(  ")
    print("(_))_|_ /((_))\\()) ((_)((_|(_) ((_))((_))\\  (_))_   )\\((_)()\\  )\\ ) _  )\\  )(_)) ((_)) ")
    print("| |_ | (_))(((_)\\  \\ \\ / / (_) _| (_)) ((_)  |   \\ ((_)(()((_)_(_/(| |((_)((_)_  _| |  ")
    print("| __|| | || \\ \\ /   \\ V /  | / _` / -_) _ \\  | |) / _ \\ V  V / ' \\)) / _ \\/ _` / _` |  ")
    print("|_|  |_|\\_,_/_\\_\\    \\_/   |_\\__,_\\___\\___/  |___/\\___/\\_/\\_/|_||_||_\\___/\\__,_\\__,_|  ")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"⚠️ Erreur lors de la requête : {e}")
        return None

def suivre_redirection(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        return response.url
    except requests.RequestException as e:
        print(f"🚧 Erreur lors de la redirection : {e}")
        return None

def trouver_url_video(url):
    soup = get_soup(url)
    if not soup:
        return None
    iframe = soup.find('iframe')
    if not iframe or not iframe.get('src'):
        print("🚫 Aucun iframe trouvé.")
        return None
    iframe_src = suivre_redirection(iframe['src'])
    if not iframe_src:
        print("🚫 Aucun SRC IFRAME trouvé après redirection.")
        return None
    soup_iframe = get_soup(iframe_src)
    if not soup_iframe:
        print("🚫 Impossible d'obtenir le contenu de l'iframe.")
        return None
    for script in soup_iframe.find_all('script'):
        if script.string:
            pattern = re.compile(r'file:\s*["\'](https?://.*?\.m3u8)["\']', re.DOTALL)
            match = pattern.search(script.string)
            if match:
                return match.group(1)

def verifier_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        print(response)
        if(response.status_code == 200):
            return True
    except requests.RequestException as e:
        print(f"🚧 Erreur réseau : {e}")
        return False

def extraire_top_tendances(soup, base_url):
    tendances = {}
    top_section = soup.find('div', id='dernierescritiques')
    if not top_section:
        return tendances
    for index, a_tag in enumerate(top_section.find_all('a', href=True), 1):
        titre_tag = a_tag.find('div', class_='trend_title')
        info_tag = a_tag.find('div', class_='trend_info')
        if titre_tag and info_tag:
            tendances[index] = {
                'title': titre_tag.text.strip(),
                'url': base_url + a_tag['href']
            }
    return tendances

def afficher_banniere_top():
    toptxt = "🔥🔥🔥  TOP DES VIDÉOS LES PLUS DEMANDÉES  🔥🔥🔥"
    print("="*(len(toptxt)+6))
    print("🔥🔥🔥  TOP DES VIDÉOS LES PLUS DEMANDÉES  🔥🔥🔥")
    print("="*(len(toptxt)+6))

def list_videos_from_search(base_url, url, search_keyword):
    try:
        search_api_url = f"{url}/{search_keyword}/0"
        response = requests.get(search_api_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"🔴 Erreur lors de la recherche : {e}")
        return {}
    videos = {}
    for index, video in enumerate(soup.find_all('div', id='hann'), start=1):
        title = re.sub(r'\s+', ' ', video.a.text).strip()
        videos[index] = {'title': title, 'url': base_url + video.a['href']}
    return videos

def selectionner_et_telecharger(videos):
    for index, data in videos.items():
        print(f"{index}. {data['title']}")
    print("\n0. 🔁 Nouvelle recherche")
    print("99. ❌ Quitter")

    while True:
        try:
            choix = int(input("\n🎯 Votre choix : "))
            if choix == 0:
                return "recherche"
            if choix == 99:
                return "quitter"
            if choix in videos:
                titre = videos[choix]['title']
                url = videos[choix]['url']
                print(f"📌 Sélection : {titre}")
                video_url = trouver_url_video(url)
                if video_url:
                    filename = re.sub(r'[^\w\-_\. ]', '_', titre) + ".mp4"
                    print(f"📥 Téléchargement de {filename}")
                    telecharger_m3u8_secure(video_url, filename)
                    print("✅ Téléchargement terminé !")
                else:
                    print("❌ Vidéo introuvable ou inaccessible.")
                return "ok"
        except ValueError:
            print("🚫 Entrez un **nombre valide**.")

CUSTOM_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Origin": "https://sharecloudy.com",
    "Referer": "https://sharecloudy.com/",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "fr-FR,fr;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

_real_request = requests.Session.request

def custom_request(self, method, url, **kwargs):
    if "sharecloudy.com" in url:
        if "headers" in kwargs:
            kwargs["headers"].update(CUSTOM_HEADERS)
        else:
            kwargs["headers"] = CUSTOM_HEADERS
    return _real_request(self, method, url, **kwargs)

def telecharger_m3u8_secure(video_url, filename):
    if "sharecloudy.com" in video_url:
        # Patch global
        requests.Session.request = custom_request
        print("🔒 Headers ShareCloudy activés (global).")
    try:
        m3u8_To_MP4.multithread_download(video_url, mp4_file_name=filename)
    finally:
        # Restore
        requests.Session.request = _real_request
        if "sharecloudy.com" in video_url:
            print("♻️ Headers ShareCloudy désactivés.")

def main():
    site = URL[4]+URL[2]+URL[3]+URL[0]+URL[1]+URL[5]
    base_url = f'https://{site}.com'
    clear_terminal()
    upload()
    print(f"\n🎬 Bienvenue sur le téléchargeur vidéo !")

    # Récupérer l'URL de recherche (et de top)
    soup_accueil = get_soup(base_url)
    if not soup_accueil:
        return
    search_path = soup_accueil.find('a', id=f'{site}c')['href'] if soup_accueil.find('a', id=f'{site}c') else ''
    home_url = f"{base_url}/{search_path}/home/{site}"
    search_url = f"{base_url}/{search_path}/search/{site}"

    # Charger la page de recherche qui contient aussi le top
    soup = get_soup(home_url)
    if not soup:
        return

    # Affichage du top
    tendances = extraire_top_tendances(soup, base_url)
    if tendances:
        afficher_banniere_top()
        result = selectionner_et_telecharger(tendances)
        if result == "quitter":
            return

    # Boucle de recherche manuelle
    while True:
        search_keyword = input("\n🔎 Entrez un mot-clé de recherche : ")
        videos = list_videos_from_search(base_url, search_url, search_keyword)
        if not videos:
            print("❌ Aucun résultat. Essayez un autre mot.")
            continue
        result = selectionner_et_telecharger(videos)
        if result == "quitter":
            break

        restart = input("\n🔄 Nouvelle recherche ? (O/N) : ").strip().lower()
        if restart != "o":
            break

    print("\n👋 Merci d’avoir utilisé le téléchargeur !")

if __name__ == '__main__':
    main()
