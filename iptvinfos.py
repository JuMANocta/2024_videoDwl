import requests
import configparser

def load_config(config_path):
    """
    Charge les informations de configuration à partir d'un fichier INI.

    :param config_path: Chemin du fichier de configuration
    :return: Dictionnaire contenant les paramètres de configuration et les en-têtes HTTP
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    
    if "iptv" not in config or "header" not in config:
        raise ValueError("Sections 'iptv' ou 'header' manquantes dans le fichier de configuration.")
    
    iptv_config = {
        "base_url": config.get("iptv", "base_url"),
        "username": config.get("iptv", "username"),
        "password": config.get("iptv", "password")
    }
    
    headers = dict(config.items("header"))  # Convertit les en-têtes en dictionnaire
    return iptv_config, headers

def get_account_info(base_url, username, password, headers):
    """
    Récupère les informations du compte IPTV à partir de l'API du serveur.

    :param base_url: URL de base du serveur IPTV (ex: http://example.com:8000)
    :param username: Nom d'utilisateur de l'abonné
    :param password: Mot de passe de l'abonné
    :param headers: En-têtes HTTP à inclure dans la requête
    :return: Détails du compte ou message d'erreur
    """
    endpoint = f"{base_url}/player_api.php"
    params = {
        "username": username,
        "password": password,
        "action": "get_account_info"
    }

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        data = response.json()

        if "user_info" in data:
            return data["user_info"]
        else:
            return {"error": "❌ Impossible de récupérer les informations du compte."}

    except requests.exceptions.RequestException as e:
        return {"error": f"❌ Erreur de requête : {str(e)}"}

# Exemple d'utilisation
if __name__ == "__main__":
    # Charge la configuration depuis le fichier
    config_path = "config.ini"  # Chemin vers le fichier de configuration
    try:
        iptv_config, headers = load_config(config_path)
    except Exception as e:
        print(f"⚙️ Erreur de configuration : {e}")
        exit(1)

    print("🌐 Connexion au serveur IPTV...")
    account_info = get_account_info(
        iptv_config["base_url"],
        iptv_config["username"],
        iptv_config["password"],
        headers
    )

    if "error" in account_info:
        print(f"❌ {account_info['error']}")
    else:
        print("✅ Informations du compte récupérées avec succès :")
        print(f"  - 🧑 Nom d'utilisateur : {account_info.get('username')}")
        print(f"  - 🔒 Statut : {account_info.get('status')}")
        print(f"  - 📶 Connexions actives : {account_info.get('active_cons')}")
        print(f"  - 📺 Connexions maximales : {account_info.get('max_connections')}")
        print(f"  - 📆 Date d'expiration : {account_info.get('exp_date')}")
