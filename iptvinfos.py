import requests
import configparser
import datetime

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

def get_xtream_data(iptv_config, headers, action):
    """
    Récupère des données depuis un serveur Xtream Codes pour une action donnée.

    :param iptv_config: Configuration IPTV avec URL et paramètres
    :param headers: En-têtes HTTP à inclure dans la requête
    :param action: Action spécifique (ex: validate, get_account_info)
    :return: Réponse JSON ou message d'erreur
    """
    endpoint = f"{iptv_config['base_url']}"
    params = {
        "username": iptv_config["username"],
        "password": iptv_config["password"],
        "action": action
    }

    try:
        print(f"🌐 Envoi de la requête pour l'action : {action}")
        response = requests.get(endpoint, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        
        print("🔍 Réponse brute du serveur :")
        print(response.text)

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"❌ Erreur de requête : {str(e)}"}
    except ValueError as e:
        return {"error": f"❌ Erreur JSON : {str(e)}"}

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

# Exemple d'utilisation
if __name__ == "__main__":
    # Charge la configuration depuis le fichier
    config_path = "config.ini"  # Chemin vers le fichier de configuration
    try:
        iptv_config, headers = load_config(config_path)
        print("⚙️ Configuration chargée avec succès.")
    except Exception as e:
        print(f"⚙️ Erreur de configuration : {e}")
        exit(1)

    actions = ["validate", "get_account_info"]

    for action in actions:
        print(f"🌐 Test de l'action : {action}")
        data = get_xtream_data(iptv_config, headers, action)

        if "error" in data:
            print(f"❌ {data['error']}")
        else:
            print(f"✅ Résultat pour l'action '{action}' :")
            if action == "validate":
                user_info = data.get('user_info', {})
                print(f"  - 🔒 Statut : {user_info.get('status', 'Inconnu')}")
                print(f"  - 📶 Connexions actives : {user_info.get('active_cons', 'Inconnu')}")
            elif action == "get_account_info":
                account_info = data.get("user_info", {})
                print(f"  - 🧑 Nom d'utilisateur : {account_info.get('username', 'Inconnu')}")
                print(f"  - 📺 Connexions maximales : {account_info.get('max_connections', 'Inconnu')}")
                print(f"  - 📆 Date d'expiration : {format_timestamp(account_info.get('exp_date'))}")
