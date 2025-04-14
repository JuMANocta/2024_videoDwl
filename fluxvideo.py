import requests
from bs4 import BeautifulSoup
import re
import m3u8_To_MP4
import os
import logging

URL = 'doorfv'

class CustomLogFilter(logging.Filter):
    def filter(self, record):
        if "segment set:" in record.getMessage():
            return True
        if record.levelno >= logging.ERROR:
            return True
        return False

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

def list_videos_from_search(base_url, url, search_keyword):
    try:
        response = requests.post(url, data={'searchword': search_keyword})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"🔴 Erreur lors de la recherche : {e}")
        return {}
    videos = {}
    for index, video in enumerate(soup.find_all('div', id='hann'), start=1):
        title = re.sub(r'\s+', ' ', video.a.text).strip()
        videos[index] = {'title': title, 'url': base_url + video.a['href']}
        print(f"🎥 {index}: {title}")
    return videos

def verifier_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"🚨 Erreur : Statut HTTP {response.status_code} pour l'URL {url}")
            return False
    except requests.exceptions.MissingSchema:
        print(f"⚠️ URL malformée : {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"🚧 Erreur réseau : {e}")
        return False

def main():
    """Script principal pour rechercher et télécharger une vidéo."""
    site = URL[4]+URL[2]+URL[3]+URL[0]+URL[1]+URL[5]
    base_url = f'https://{site}.com'
    print(f"\n🎬 Bienvenue dans le téléchargeur de vidéos !\n")

    soup = get_soup(base_url)
    if not soup:
        return

    search_path = soup.find('a', id=f'{site}c')['href'] if soup.find('a', id=f'{site}c') else ''
    search_url = f"{base_url}/{search_path}/home/{site}"

    while True:        
        search_keyword = input("\n🔎 Entrez votre mot-clé de recherche : ")
        videos = list_videos_from_search(base_url, search_url, search_keyword)
        if not videos:
            print("❌ Aucune vidéo trouvée. Essayez avec un autre mot-clé.")
            continue
        print("\n⚠ Pour effectuer une nouvelle recherche, entrez 0.")
        print("🛑 Pour quitter, entrez 99.")
        selected = None
        while True:
            try:
                choice = int(input("\n🎬 Entrez le numéro de la vidéo que vous souhaitez télécharger ou 0 ou 99 : "))
                if choice == 0:
                    clear_terminal()
                    upload()
                    print("\n🔄 Nouvelle recherche demandée...")
                    selected = 0
                    break
                elif choice == 99:
                    print("\n👋 Au revoir et à bientôt !")
                    return
                elif choice in videos:
                    selected = choice
                    chosen_video_url = videos[choice]['url']
                    print(f"📌 Vous avez choisi : {videos[choice]['title']}\n🔗 URL : {chosen_video_url}")
                    video_url = trouver_url_video(chosen_video_url)
                    if video_url:
                        print('🔍 URL de la vidéo trouvée, vérification en cours...')
                        if verifier_url(video_url):
                            filename = f"{videos[choice]['title'].replace(' ', '_').replace(':', '').replace('/', '')}.mp4"
                            print(f"📁 Le fichier sera enregistré sous : {filename}")
                            m3u8_To_MP4.multithread_download(video_url, mp4_file_name=filename)
                            print("🎞️ Téléchargement terminé avec succès !")
                        else:
                            print('❌ Téléchargement annulé : L’URL de la vidéo est inaccessible.')
                    else:
                        print('❌ Aucune URL de vidéo trouvée.')
                    break
                else:
                    print("⚠️ Choix invalide. Veuillez entrer un numéro valide parmi la liste ou 0 pour une nouvelle recherche.")
            except ValueError:
                print("🚫 Entrée invalide. Veuillez entrer un **nombre**.")
        if selected == 0:
            continue
        while True:
            restart = input("\n🔄 Voulez-vous faire une nouvelle recherche ? (O/N) ").strip().lower()
            if restart in ["o", "n"]:
                break
            print("🚨 Réponse invalide. Tapez 'O' pour Oui ou 'N' pour Non.")

        if restart == "n":
            print("\n👋 Merci d'avoir utilisé le téléchargeur de vidéos. À bientôt !")
            break

if __name__ == '__main__':
    clear_terminal()
    upload()
    main()