import sys
import requests
from bs4 import BeautifulSoup
import re
import m3u8_To_MP4
import os
import logging
from urllib.parse import urlparse

URL = 'riotdv'

class CustomLogFilter(logging.Filter):
    def filter(self, record):
        return "segment set:" in record.getMessage() or record.levelno >= logging.ERROR

logging.getLogger("m3u8_To_MP4").addFilter(CustomLogFilter())

# Session globale
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/139.0.0.0 Safari/537.36"
})

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

def get_soup(url, timeout=33):
    """Récupère un BeautifulSoup avec cookies persistants."""
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"⚠️ Erreur lors de la requête : {e}")
        return None

def suivre_redirection(url):
    try:
        response = session.get(url, allow_redirects=True, timeout=5)
        return response.url
    except requests.RequestException as e:
        print(f"🚧 Erreur lors de la redirection : {e}")
        return None

def trouver_url_video(url):
    """Trouve l'URL m3u8 + referer (iframe) à partir de la page du film."""
    soup = get_soup(url)
    if not soup:
        return None, None

    iframe = soup.find('iframe')
    if not iframe or not iframe.get('src'):
        print("🚫 Aucun iframe trouvé.")
        return None, None

    iframe_src = iframe['src']
    soup_iframe = get_soup(iframe_src)
    if not soup_iframe:
        print("🚫 Impossible d'obtenir le contenu de l'iframe.")
        return None, None

    for script in soup_iframe.find_all('script'):
        if script.string:
            pattern = re.compile(r'file:\s*["\'](https?://.*?\.m3u8)["\']', re.DOTALL)
            match = pattern.search(script.string)
            if match:
                video_url = match.group(1)
                # print(f"🎯 m3u8 trouvé : {video_url}")
                return video_url, iframe_src
    print("❌ Aucun m3u8 trouvé dans les scripts.")
    return None, None

def verifier_url(url):
    try:
        response = session.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
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
    print(toptxt)
    print("="*(len(toptxt)+6))

def list_videos_from_search(base_url, url, search_keyword):
    try:
        response = session.post(url, data={'searchword': search_keyword}, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"🔴 Erreur lors de la recherche : {e}")
        return {}
    videos = {}
    items = soup.find_all('div', id='hann')
    for index, video in enumerate(items, start=1):
        if video.a:
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
                video_url, referer_url = trouver_url_video(url)
                if video_url:
                    headers = build_headers_for(video_url, referer_url)
                    try:
                        session.get(video_url, headers=headers, timeout=10, allow_redirects=True)
                    except requests.RequestException as e:
                        print(f"⚠️ Warm-up cookies échoué (non bloquant) : {e}")
                    host = urlparse(video_url).netloc
                    ck = cookies_for_domain(session, host)
                    if ck:
                        headers["Cookie"] = ck
                    filename = re.sub(r'[^\w\-_\. ]', '_', titre) + ".mp4"
                    print(f"📥 Téléchargement de {filename}")
                    m3u8_To_MP4.multithread_download(video_url, mp4_file_name=filename, customized_http_header=headers)
                    print("✅ Téléchargement terminé !")
                    return "ok"
                else:
                    print("❌ Vidéo introuvable ou inaccessible.")
                return "ok"
        except ValueError:
            print("🚫 Entrez un **nombre valide**.")

def build_headers_for(target_url: str, referer_url: str) -> dict:
    """Construit les headers pour le domaine HLS avec Referer/Origin corrects."""
    h = dict(session.headers or {})
    h["Accept"] = h.get("Accept", "*/*")
    h["Accept-Language"] = h.get("Accept-Language", "fr-FR,fr;q=0.9")

    # Referer/Origin basés sur la page
    if referer_url:
        ref = referer_url
        parsed_ref = urlparse(ref)
        origin = f"{parsed_ref.scheme}://{parsed_ref.netloc}"
        h["Referer"] = ref
        h["Origin"] = origin

    # IMPORTANT: Cookie ne sera ajouté qu'après un warm-up request
    h.pop("Cookie", None)
    return h

def cookies_for_domain(session: requests.Session, host: str) -> str:
    """Retourne 'k=v; k2=v2' des cookies pertinents pour le domaine cible."""
    jar = session.cookies
    parts = host.split(".")
    domain_suffixes = [".".join(parts[i:]) for i in range(len(parts)-2, -1, -1)]
    kv = []
    for c in jar:
        # on inclut cookie si le suffixe du domaine matche le host
        if any(c.domain.endswith(suf) for suf in domain_suffixes):
            kv.append(f"{c.name}={c.value}")
    return "; ".join(kv)

def main():
    site = URL[4]+URL[2]+URL[3]+URL[0]+URL[1]+URL[5]
    base_url = f'https://{site}.com'
    if not verifier_url(base_url):
        print("❌ Le site est inaccessible. Vérifiez votre connexion ou l'URL.")
        sys.exit(1)
    clear_terminal()
    upload()
    print(f"\n🎬 Bienvenue sur le téléchargeur vidéo !")

    # Récupérer l'URL de recherche (et de top)
    soup_accueil = get_soup(base_url)
    if not soup_accueil:
        return
    search_path = soup_accueil.find('a', id=f'{site}c')['href'] if soup_accueil.find('a', id=f'{site}c') else ''
    home_url = f"{base_url}/{search_path}/home/{site}"

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
        search_keyword = input("\n🔎 Entrez un mot-clé de recherche (0 pour quitter) : ")
        if search_keyword.strip() == "0":
            break
        videos = list_videos_from_search(base_url, home_url, search_keyword)
        if not videos:
            print("❌ Aucun résultat. Essayez un autre mot.")
            continue
        result = selectionner_et_telecharger(videos)
        if result == "quitter":
            break

    print("\n👋 Merci d’avoir utilisé le téléchargeur !")

if __name__ == '__main__':
    main()
