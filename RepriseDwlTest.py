import os
import requests
import configparser
from urllib.parse import urlencode

# --- CONFIGURATION & SESSION ---
session = requests.Session()

# Simulation d'un vrai player (VLC/Browser)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Encoding": "identity;q=1, *;q=0",
}

def charger_config():
    """Charge la configuration ou retourne None si échec."""
    try:
        config = configparser.ConfigParser()
        config.read("config.ini")
        
        base_url = config.get("premium", "base_url")
        params = {
            "username": config.get("premium", "username"),
            "password": config.get("premium", "password"),
            "type": config.get("premium", "type"),
            "output": config.get("premium", "output"),
        }
        # Le Referer est souvent clé pour ne pas se faire jeter
        HEADERS["Referer"] = config.get("premium", "referer", fallback=base_url)
        return f"{base_url}?{urlencode(params)}"
    except Exception:
        return None

# --- MODULE DE TEST "STEALTH" ---
def tester_capacite_reprise(url, nom_flux):
    """
    Sonde furtive : Tente directement un GET partiel sans demander la permission (pas de HEAD).
    """
    print(f"\n--- 🕵️‍♂️ SCAN STEALTH : {nom_flux} ---")
    print(f"📡 URL: {url}")
    
    # On simule une reprise à 1 Mo (comme si on avançait dans la vidéo)
    # C'est un comportement standard que le serveur ne devrait pas bloquer.
    OFFSET = 1024 * 1024 
    
    headers_attaque = HEADERS.copy()
    headers_attaque['Range'] = f'bytes={OFFSET}-'

    try:
        print(f">>> 🚀 Injection payload (GET Range: bytes={OFFSET}-)...")
        
        # stream=True est CRITIQUE. On ouvre le robinet mais on ne boit pas l'eau.
        # timeout court pour ne pas pendre si le serveur lag.
        with session.get(url, headers=headers_attaque, timeout=10, allow_redirects=True, stream=True) as r:
            
            status = r.status_code
            cr_header = r.headers.get('content-range', 'NON DÉTECTÉ')
            ctype = r.headers.get('content-type', 'inconnu')
            
            print(f"   Réponse : {status} | Type: {ctype}")

            # --- ANALYSE ---
            if status == 206:
                print(f"✅ SUCCÈS (206). Le serveur a accepté le saut.")
                print(f"   Preuve : {cr_header}")
                print("   CONCLUSION : Reprise supportée.")
            elif status == 200:
                print(f"❌ ÉCHEC (200). Le serveur ignore le saut et renvoie tout.")
                print("   CONCLUSION : Reprise impossible (flux continu ou serveur mal configuré).")
            elif status == 416:
                print(f"⚠️ ERREUR (416). Range Not Satisfiable.")
                print("   Le fichier est peut-être plus petit que 1Mo ?")
            else:
                print(f"⚠️ COMPORTEMENT SUSPECT ({status}).")

            # La connexion se ferme proprement ici grâce au 'with'
            
    except requests.exceptions.ConnectionError:
        print("💀 CONNEXION TUÉE. Le serveur détecte et bloque activement ce type de requête.")
    except requests.RequestException as e:
        print(f"💀 ERREUR RÉSEAU : {e}")


# --- LOGIQUE M3U (Identique) ---
def main():
    url_source = charger_config()
    if not url_source:
        print("⚠️ Config.ini manquant ou invalide.")
        exit(1)

    fichier_m3u = "playlist.m3u"
    if not os.path.exists(fichier_m3u):
        print("📥 Téléchargement playlist...")
        try:
            r = session.get(url_source, headers=HEADERS, stream=True)
            if r.status_code == 200:
                with open(fichier_m3u, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        except Exception as e:
            print(f"❌ Erreur DL Playlist: {e}")
            exit()
    
    print("📂 Parsing playlist...")
    playlist = []
    try:
        with open(fichier_m3u, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                titre = lines[i].split(",", 1)[1].strip()
                url = lines[i+1].strip() if i+1 < len(lines) else None
                if url and url.startswith("http"): playlist.append({"t": titre, "u": url})
    except: pass

    while True:
        q = input("\n🔍 Recherche (ou 'exit'): ").strip().lower()
        if q == 'exit': break
        res = [p for p in playlist if q in p['t'].lower()]
        if not res: print("❌ Rien trouvé."); continue
        
        for i, p in enumerate(res): print(f"   [{i+1}] {p['t']}")
        
        try:
            idx = int(input("\n🎯 Cible : ")) - 1
            if 0 <= idx < len(res): tester_capacite_reprise(res[idx]['u'], res[idx]['t'])
        except ValueError: pass

if __name__ == "__main__":
    main()
