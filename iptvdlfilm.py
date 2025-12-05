import os
import re
import requests
import time
import configparser
from urllib.parse import urlencode
from tqdm import tqdm
from http.client import RemoteDisconnected

# Initialisation de la session globale
session = requests.Session()
try:
    # Initialisation du fichier de configuration
    config = configparser.ConfigParser()
    fichier_config="config.ini"
    config.read(fichier_config)
    # Récupérer les paramètres
    base_url = config.get("premium", "base_url")
    username = config.get("premium", "username")
    password = config.get("premium", "password")
    type_ = config.get("premium", "type")
    output = config.get("premium", "output")
    # user_agent = config.get("header", "user-agent")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    referer = config.get("premium", "referer")
except (configparser.NoSectionError, configparser.NoOptionError, FileNotFoundError) as e:
    print(f"❌ Erreur lors de la lecture du fichier de configuration : {e}")
    session.close()
    exit(1)

headers = {
    "User-Agent": user_agent,
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Referer": referer,
}

cookies = {
    # Ajouter des cookies capturés si nécessaire
    # "sessionid": "votre_cookie_session"
}

def lire_url_config():
    """Assemble l'URL complète à partir des parties définies dans le fichier de configuration."""
    # Construire l'URL complète avec les paramètres
    params = {
        "username": username,
        "password": password,
        "type": type_,
        "output": output,
    }
    url_complete = f"{base_url}?{urlencode(params)}"
    print(f"URL complète assemblée 🚀")
    print(f"{url_complete}")
    return url_complete

def telecharger_fichier_m3u(url, nom_fichier="playlist.m3u", session=None):
    """Télécharge le fichier M3U depuis l'URL avec une session persistante et gère les erreurs."""
    if session is None:
        session = requests.Session()

    try:
        print("🔄 Téléchargement en cours...")
        response = session.get(url, headers=headers, timeout=(15, 30))
        
        if response.status_code == 200:
            try:
                with open(nom_fichier, "wb") as fichier:
                    fichier.write(response.content)
                print(f"✅ Fichier M3U téléchargé et sauvegardé sous : {nom_fichier}")
                return nom_fichier
            except IOError as e:
                print(f"❌ Erreur lors de l'écriture du fichier : {e}")
                return None
        else:
            print(f"❌ Échec du téléchargement. Code HTTP : {response.status_code}")
            return None
    
    except requests.exceptions.ConnectionError as e:
        cause = getattr(e, "__cause__", None)
        if isinstance(cause, RemoteDisconnected):
            print("❌ Le serveur IPTV a coupé la connexion sans envoyer de réponse.")
            print("   👉 Souvent : URL/identifiants invalides, abonnement expiré ou protection anti-bot.")
        else:
            print(f"❌ Erreur de connexion : {e}")
        return None

    except requests.RequestException as e:
        print(f"❌ Erreur lors du téléchargement : {e}")
        return None

def lire_fichier_m3u(chemin_fichier):
    """Lit un fichier M3U et extrait les titres et URLs."""
    contenu = []
    try:
        with open(chemin_fichier, "r", encoding="utf-8") as fichier:
            lignes = fichier.readlines()

        # Analyser le contenu pour extraire les titres et URLs
        for i in range(len(lignes)):
            if lignes[i].startswith("#EXTINF"):
                titre = lignes[i].split(",", 1)[1].strip()
                url = lignes[i + 1].strip() if i + 1 < len(lignes) else None
                if url and url.startswith("http"):
                    contenu.append({"titre": titre, "url": url})

        print(f"✅ {len(contenu)} flux trouvés dans le fichier M3U.")
        return contenu
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier M3U : {e}")
    return []

def rechercher_flux(contenu, mot_cle):
    """Recherche les flux contenant le mot-clé dans leur titre."""
    resultats = [flux for flux in contenu if mot_cle.lower() in flux["titre"].lower()]
    if resultats:
        print(f"\n✅ {len(resultats)} résultat(s) trouvé(s) pour '{mot_cle}':")
        for i, flux in enumerate(resultats, 1):
            print(f"🎞️  {i}. {flux['titre']} -> {flux['url']}")
    else:
        print(f"❌ Aucun résultat trouvé pour '{mot_cle}'.")
    return resultats

def telecharger_flux(url, titre=None):
    """Télécharge un flux à partir de son URL avec gestion des erreurs et options robustes."""
    # On part d'abord du titre, sinon du nom dans l'URL
    nom_base = titre or url.split("/")[-1]
    ext = detect_extension(nom_base, url)
    # Supprime l'extension si déjà là
    nom_base = re.sub(r'(\.mp4|\.mkv)$', '', nom_base, flags=re.IGNORECASE)
    nom_fichier = sanitize_filename(nom_base) + ext

    for tentative in range(3):  # Jusqu'à 3 tentatives
        try:
            print(f"🔄 Tentative {tentative + 1} pour télécharger : {nom_fichier}")

            # Télécharger avec une barre de progression
            with requests.get(url, headers=headers, stream=True, timeout=(10, 60)) as r, open(nom_fichier, "wb") as fichier, tqdm(
                desc=nom_fichier,
                total=int(r.headers.get('content-length', 0)),
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as barre:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        fichier.write(chunk)
                        barre.update(len(chunk))
            print(f"✅ Téléchargement terminé : {nom_fichier}")
            return nom_fichier

        except requests.RequestException as e:
            print(f"⚠️ Échec lors de la tentative {tentative + 1} : {e}")
            time.sleep(5)  # Pause avant la prochaine tentative

    print("❌ Échec après plusieurs tentatives.")
    return None

def sanitize_filename(filename):
    """Remplace les caractères interdits pour Windows."""
    return re.sub(r'[\\/*?:"<>|]', '_', filename)

def detect_extension(nom, url):
    # Détecte l'extension valide depuis le nom ou l'url, sinon retourne ".mkv"
    for ext in [".mp4", ".mkv"]:
        if nom and nom.lower().endswith(ext):
            return ext
        if url and url.lower().endswith(ext):
            return ext
    return ".mkv"

if __name__ == "__main__":
    try:
        # Charger l'URL complète depuis le fichier de configuration
        url_m3u = lire_url_config()
        if not url_m3u:
            print("❌ Impossible de charger l'URL depuis le fichier de configuration.")
            exit(1)

        nom_fichier = "playlist.m3u"

        # Vérifier l'existence du fichier et télécharger si nécessaire
        if os.path.exists(nom_fichier):
            print(f"👍 Le fichier '{nom_fichier}' existe déjà.")
            choix = input("Souhaitez-vous le mettre à jour ? (o/n) : ").strip().lower()
            if choix == "o":
                telecharger_fichier_m3u(url_m3u, nom_fichier, session)
            else:
                print("ℹ️ Mise à jour annulée. Utilisation du fichier existant.")
        else:
            telecharger_fichier_m3u(url_m3u, nom_fichier, session)

        # Lire et extraire les flux du fichier M3U
        if os.path.exists(nom_fichier):
            contenu_flux = lire_fichier_m3u(nom_fichier)

            if contenu_flux:
                while True:
                    # Recherche par mot-clé
                    mot_cle = input("\nEntrez un mot-clé pour rechercher dans les titres (ou 'exit' pour quitter) : ")
                    if mot_cle.lower() == "exit":
                        print("🖖 Fin du programme.")
                        break

                    resultats = rechercher_flux(contenu_flux, mot_cle)

                    if resultats:
                        choix_action = input("\nVoulez-vous (1) télécharger un flux ou (2) effectuer une autre recherche ? (1/2) : ").strip()
                        if choix_action == "1":
                            try:
                                if resultats:
                                    try:
                                        choix_flux = int(input("Entrez le numéro du flux à télécharger : ")) - 1
                                        if 0 <= choix_flux < len(resultats):
                                            url_flux = resultats[choix_flux]["url"]
                                            titre_flux = resultats[choix_flux]["titre"]
                                            print(f"🔄 Téléchargement du flux : {titre_flux}")
                                            telecharger_flux(url_flux, f"{titre_flux}")
                                        else:
                                            print("❌ Numéro de flux invalide.")
                                    except ValueError:
                                        print("❌ Veuillez entrer un numéro valide.")
                            except ValueError:
                                print("❌ Veuillez entrer un numéro valide.")
                        elif choix_action == "2":
                            continue
                        else:
                            print("❌ Choix invalide. Retour à la recherche.")
            else:
                print("❌ Aucun flux à afficher après lecture du fichier M3U.")
        else:
            print("❌ Le fichier M3U n'existe pas ou n'a pas pu être téléchargé.")
    finally:
        session.close()