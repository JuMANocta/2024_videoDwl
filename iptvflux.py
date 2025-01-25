import os
import requests
import subprocess
import configparser
from urllib.parse import urlencode

# Initialisation de la session globale
session = requests.Session()
try:
    # Initialisation du fichier de configuration
    config = configparser.ConfigParser()
    fichier_config="config.ini"
    config.read(fichier_config)
    # Récupérer les paramètres
    base_url = config.get("iptv", "base_url")
    username = config.get("iptv", "username")
    password = config.get("iptv", "password")
    type_ = config.get("iptv", "type")
    output = config.get("iptv", "output")
except (configparser.NoSectionError, configparser.NoOptionError, FileNotFoundError) as e:
    print(f"❌ Erreur lors de la lecture du fichier de configuration : {e}")
    session.close()
    exit(1)


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
    """Télécharge le fichier M3U depuis l'URL avec une session persistante."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Referer": base_url
    }
    try:
        print("🔄 Téléchargement en cours...")
        response = session.get(url, headers=headers, timeout=(5, 15))
        if response.status_code == 200:
            with open(nom_fichier, "wb") as fichier:
                fichier.write(response.content)
            print(f"✅ Fichier M3U téléchargé et sauvegardé sous : {nom_fichier}")
            return nom_fichier
        else:
            print(f"❌ Échec du téléchargement. Code HTTP : {response.status_code}")
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
            print(f"🎞️ {i}. {flux['titre']} -> {flux['url']}")
    else:
        print(f"❌ Aucun résultat trouvé pour '{mot_cle}'.")
    return resultats

def telecharger_flux(url, nom_fichier="video.mp4"):
    """Télécharge un flux à partir de son URL en utilisant FFmpeg."""
    try:
        commande = ["ffmpeg", "-i", url, "-c", "copy", nom_fichier]
        subprocess.run(commande, check=True)
        print(f"✅ Téléchargement terminé : {nom_fichier}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du téléchargement avec FFmpeg : {e}")

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
                                choix_flux = int(input("Entrez le numéro du flux à télécharger : "))
                                if 1 <= choix_flux <= len(resultats):
                                    url_flux = resultats[choix_flux - 1]["url"]
                                    titre_flux = resultats[choix_flux - 1]["titre"]
                                    nom_sortie = input(f"Entrez le nom de la vidéo de sortie pour '{titre_flux}' (avec extension .mp4) : ").strip()
                                    telecharger_flux(url_flux, nom_sortie)
                                else:
                                    print("❌ Numéro de flux invalide.")
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
