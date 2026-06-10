import os
import re
import requests
import time
import configparser
import json
from urllib.parse import urlparse
from tqdm import tqdm
from http.client import RemoteDisconnected

# Initialisation de la session globale
session = requests.Session()

try:
    # Initialisation du fichier de configuration
    config = configparser.ConfigParser()
    fichier_config = "config.ini"
    if not os.path.exists(fichier_config):
        fichier_config = "config.ini.example"
    
    config.read(fichier_config)
    
    # Déterminer la section à utiliser
    section = "premium" if config.has_section("premium") else "iptv"
    
    base_url = config.get(section, "base_url")
    username = config.get(section, "username")
    password = config.get(section, "password")
    
    # Nettoyage de la base_url pour avoir le serveur racine
    parsed_url = urlparse(base_url)
    server_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    api_url = f"{server_url}/player_api.php"
    
    user_agent = config.get("header", "User-Agent", fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    referer = config.get(section, "referer", fallback=server_url + "/")
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

cache_file = "vod_cache.json"

def fetch_all_data():
    """Récupère Live, VOD et Séries via l'API Xtream."""
    data = {"live": [], "vod": [], "series": []}
    
    actions = [
        ("live", "get_live_streams"),
        ("vod", "get_vod_streams"),
        ("series", "get_series")
    ]
    
    for key, action in actions:
        params = {
            "username": username,
            "password": password,
            "action": action
        }
        try:
            print(f"🔄 Récupération de {key}...")
            response = session.get(api_url, params=params, headers=headers, timeout=(10, 30))
            if response.status_code == 200:
                data[key] = response.json()
                print(f"✅ {len(data[key])} {key} trouvé(s).")
            else:
                print(f"⚠️ Échec pour {key}. Code : {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de {key} : {e}")
            
    return data

def fetch_series_info(series_id):
    """Récupère les détails d'une série (saisons/épisodes)."""
    params = {
        "username": username,
        "password": password,
        "action": "get_series_info",
        "series_id": series_id
    }
    try:
        response = session.get(api_url, params=params, headers=headers, timeout=(10, 30))
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des infos de la série : {e}")
    return None

def save_cache(data):
    """Sauvegarde les données dans un fichier JSON local."""
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"💾 Cache mis à jour : {cache_file}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde du cache : {e}")

def load_cache():
    """Charge les données depuis le fichier JSON local."""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture du cache : {e}")
    return None

def rechercher_contenu(data, mot_cle):
    """Recherche dans Live, VOD et Séries."""
    resultats = []
    
    # 1. LIVE
    for item in data.get("live", []):
        if mot_cle.lower() in item.get("name", "").lower():
            stream_id = item.get("stream_id")
            url = f"{server_url}/live/{username}/{password}/{stream_id}.ts"
            resultats.append({
                "type": "LIVE",
                "titre": item.get("name"),
                "url": url,
                "id": stream_id
            })

    # 2. VOD
    for item in data.get("vod", []):
        if mot_cle.lower() in item.get("name", "").lower():
            stream_id = item.get("stream_id")
            ext = item.get("container_extension", "mkv")
            url = f"{server_url}/movie/{username}/{password}/{stream_id}.{ext}"
            resultats.append({
                "type": "VOD",
                "titre": item.get("name"),
                "url": url,
                "id": stream_id,
                "ext": ext
            })

    # 3. SERIES
    for item in data.get("series", []):
        if mot_cle.lower() in item.get("name", "").lower():
            resultats.append({
                "type": "SERIE",
                "titre": item.get("name"),
                "id": item.get("series_id")
            })
    
    if resultats:
        print(f"\n✅ {len(resultats)} résultat(s) trouvé(s) pour '{mot_cle}':")
        for i, item in enumerate(resultats, 1):
            cat = f"[{item['type']}]"
            print(f"🎞️  {i}. {cat:<7} {item['titre']}")
    else:
        print(f"❌ Aucun résultat trouvé pour '{mot_cle}'.")
    return resultats

def gerer_selection_serie(series_id, series_name):
    """Gère le choix des épisodes pour une série."""
    print(f"🔄 Chargement des épisodes pour : {series_name}...")
    info = fetch_series_info(series_id)
    if not info or "episodes" not in info:
        print("❌ Impossible de charger les épisodes.")
        return

    episodes_data = info["episodes"]
    all_episodes = []
    
    print(f"\n📺 {series_name}")
    for season_num in sorted(episodes_data.keys()):
        print(f"  Saison {season_num}:")
        for ep in episodes_data[season_num]:
            idx = len(all_episodes) + 1
            ep_num = ep.get('episode_num')
            ep_name = ep.get("title", f"Episode {ep_num}")
            print(f"    {idx}. E{ep_num} - {ep_name}")
            all_episodes.append(ep)

    try:
        choix = int(input("\nEntrez le numéro de l'épisode à télécharger (0 pour annuler) : "))
        if choix == 0: return
        if 1 <= choix <= len(all_episodes):
            ep = all_episodes[choix-1]
            stream_id = ep.get("id")
            ext = ep.get("container_extension", "mkv")
            url = f"{server_url}/series/{username}/{password}/{stream_id}.{ext}"
            titre_ep = f"{series_name} S{ep.get('season')}E{ep.get('episode_num')} {ep.get('title', '')}"
            print(f"🔄 Téléchargement de : {titre_ep}")
            telecharger_flux(url, titre_ep)
        else:
            print("❌ Numéro invalide.")
    except ValueError:
        print("❌ Veuillez entrer un nombre.")

def telecharger_flux(url, titre=None):
    """Télécharge un flux."""
    nom_base = titre or url.split("/")[-1]
    ext_match = re.search(r'\.([a-z0-9]+)$', url, re.IGNORECASE)
    ext = ext_match.group(0) if ext_match else ".mkv"
    
    nom_base = re.sub(r'(\.mp4|\.mkv|\.ts)$', '', nom_base, flags=re.IGNORECASE)
    nom_fichier = sanitize_filename(nom_base) + ext

    for tentative in range(3):
        try:
            print(f"🔄 Tentative {tentative + 1} pour : {nom_fichier}")
            with session.get(url, headers=headers, stream=True, timeout=(10, 60)) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                with open(nom_fichier, "wb") as fichier, tqdm(
                    desc=nom_fichier[:30],
                    total=total_size,
                    unit='B', unit_scale=True, unit_divisor=1024,
                ) as barre:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            fichier.write(chunk)
                            barre.update(len(chunk))
            print(f"✅ Terminé : {nom_fichier}")
            return nom_fichier
        except Exception as e:
            print(f"⚠️ Erreur : {e}")
            time.sleep(5)
    return None

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', '_', filename).strip()

if __name__ == "__main__":
    try:
        all_data = load_cache()
        if all_data and isinstance(all_data, dict) and "vod" in all_data:
            print(f"👍 Cache chargé ({len(all_data.get('live', []))} TV, {len(all_data.get('vod', []))} Films, {len(all_data.get('series', []))} Séries).")
            choix = input("Mettre à jour via l'API ? (o/n) : ").strip().lower()
            if choix == "o":
                all_data = fetch_all_data()
                save_cache(all_data)
            else:
                print("ℹ️ Utilisation du cache existant.")
        else:
            all_data = fetch_all_data()
            if all_data:
                save_cache(all_data)

        if all_data:
            while True:
                mot_cle = input("\nRechercher (TV, Film, Série) ou 'exit' : ").strip()
                if mot_cle.lower() == "exit": break
                if not mot_cle: continue

                resultats = rechercher_contenu(all_data, mot_cle)

                if resultats:
                    choix_action = input("\n(1) Choisir un élément ou (2) Autre recherche ? (1/2) : ").strip()
                    if choix_action == "1":
                        try:
                            n = int(input("Numéro : ")) - 1
                            if 0 <= n < len(resultats):
                                item = resultats[n]
                                if item["type"] == "SERIE":
                                    gerer_selection_serie(item["id"], item["titre"])
                                else:
                                    print(f"🔄 Téléchargement de : {item['titre']}")
                                    telecharger_flux(item["url"], item["titre"])
                            else:
                                print("❌ Numéro invalide.")
                        except ValueError:
                            print("❌ Veuillez entrer un nombre.")
    finally:
        session.close()
