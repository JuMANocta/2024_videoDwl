import requests
import configparser
import datetime

def load_config():
    """
    Charge les informations de configuration à partir d'un fichier INI.
    :return: Dictionnaire contenant les paramètres de configuration et les en-têtes HTTP
    """
    config = configparser.ConfigParser()
    fichier_config="config.ini"
    config.read(fichier_config)
    # Récupérer les paramètres
    base_url = config.get("premium", "base_url")
    username = config.get("premium", "username")
    password = config.get("premium", "password")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    referer = config.get("premium", "referer")
    
    if "premium" not in config:
        raise ValueError("Section 'premium' manquante dans le fichier de configuration.")
    
    iptv_config = {
        "base_url": base_url,
        "username": username,
        "password": password
    }

    headers = {
        "User-Agent": user_agent,
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Referer": referer,
    }
    return iptv_config, headers

def get_xtream_data(iptv_config, headers, action):
    """
    Récupère des données depuis un serveur Xtream Codes pour une action donnée.

    :param iptv_config: Configuration IPTV avec URL et paramètres
    :param headers: En-têtes HTTP à inclure dans la requête
    :param action: Action spécifique (ex: get_profile, get_account_info)
    :return: Réponse JSON ou message d'erreur
    """
    # L'endpoint pour les actions de l'API est 'player_api.php', et non 'get.php' qui sert à télécharger la playlist.
    api_endpoint = iptv_config['base_url'].replace('/get.php', '/player_api.php')

    params = {
        "username": iptv_config["username"],
        "password": iptv_config["password"],
        "action": action
    }

    try:
        print(f"🌐 Envoi de la requête pour l'action '{action}' à : {api_endpoint}")
        response = requests.get(api_endpoint, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP (4xx ou 5xx)
        
        print("🔍 Réponse brute du serveur :")
        print(response.text)

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erreur de requête : {str(e)}"}
    except ValueError:
        return {"error": "La réponse du serveur n'est pas au format JSON."}

def format_timestamp(timestamp):
    """
    Convertit un timestamp UNIX en une date lisible.

    :param timestamp: Timestamp UNIX
    :return: Date lisible
    """
    try:
        dt = datetime.datetime.fromtimestamp(int(timestamp))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Inconnu"

def check_auth_and_get_info(iptv_config, headers):
    """
    Vérifie l'authentification et retourne les informations du compte si elle réussit.
    Utilise 'get_account_info' pour ne faire qu'un seul appel.
    :return: Le dictionnaire 'user_info' en cas de succès, None en cas d'échec.
    """
    print("\n🛡️  Vérification de l'authentification et récupération des infos...")
    # On utilise 'get_account_info' pour récupérer toutes les infos en un seul appel
    data = get_xtream_data(iptv_config, headers, "get_account_info")

    if "error" in data:
        print(f"❌ Échec de la requête : {data['error']}")
        return None
    
    user_info = data.get('user_info', {})
    # 'auth: 0' est le signal standard d'échec d'authentification de l'API Xtream
    if user_info.get('auth') == 0:
        print("❌ Échec de l'authentification : Identifiants invalides ou compte désactivé.")
        return None

    status = user_info.get('status', 'Inconnu')
    print(f"✅ Authentification réussie. Statut du compte : {status}")
    return user_info

# Exemple d'utilisation
if __name__ == "__main__":
    # Charge la configuration depuis le fichier
    try:
        iptv_config, headers = load_config()
        print("⚙️ Configuration chargée avec succès.")
    except Exception as e:
        print(f"⚙️ Erreur de configuration : {e}")
        exit(1)

    # 1. Valider l'authentification et récupérer les infos en un seul appel
    account_info = check_auth_and_get_info(iptv_config, headers)
    
    if not account_info:
        print("\n🛑 Arrêt du script. Vérifiez vos identifiants ou l'URL du serveur dans config.ini.")
        exit(1)

    # 2. Afficher les informations détaillées du compte
    print("\n" + "="*40)
    print("🔍 Informations détaillées du compte :")
    print("="*40)
    
    print(f"  - 🧑 Nom d'utilisateur : {account_info.get('username', 'Inconnu')}")
    print(f"  - 📺 Connexions maximales : {account_info.get('max_connections', 'Inconnu')}")
    print(f"  - 📶 Connexions actives : {account_info.get('active_cons', 'Inconnu')}")
    print(f"  - 📆 Date d'expiration : {format_timestamp(account_info.get('exp_date'))}")
    print(f"  - ⚖️ Statut : {account_info.get('status', 'Inconnu')}")
    print(f"  - ⏳ Compte d'essai : {'Oui' if str(account_info.get('is_trial')) == '1' else 'Non'}")
