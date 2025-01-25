import os

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

def rechercher_flux_par_chaine(contenu, chaine):
    """Recherche un flux IPTV contenant le nom de la chaîne."""
    resultats = [flux for flux in contenu if chaine.lower() in flux["titre"].lower()]
    if resultats:
        print(f"\n✅ {len(resultats)} résultat(s) trouvé(s) pour '{chaine}':")
        for i, flux in enumerate(resultats, 1):
            print(f"{i}. {flux['titre']} -> {flux['url']}")
    else:
        print(f"❌ Aucun résultat trouvé pour '{chaine}'.")
    return resultats

def lire_flux_vlc(url):
    """Lance un flux IPTV en direct avec VLC Media Player."""
    try:
        print(f"🔄 Lecture du flux en direct : {url}")
        os.system(f'vlc --play-and-exit "{url}"')
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du flux : {e}")

def rechercher_ou_lire(contenu_flux):
    """Permet à l'utilisateur de rechercher des chaînes ou de lire un flux."""
    while True:
        # Demander le nom de la chaîne
        chaine = input("\nEntrez le nom de la chaîne que vous souhaitez voir (ou 'exit' pour quitter) : ")
        if chaine.lower() == "exit":
            print("🖖 Fin du programme.")
            break

        # Rechercher la chaîne
        resultats = rechercher_flux_par_chaine(contenu_flux, chaine)

        if resultats:
            while True:
                choix_action = input("\nVoulez-vous (1) lire un flux ou (2) effectuer une autre recherche ? (1/2) : ").strip()
                if choix_action == "1":
                    try:
                        choix_flux = int(input("Entrez le numéro du flux à lire : "))
                        if 1 <= choix_flux <= len(resultats):
                            url_flux = resultats[choix_flux - 1]["url"]
                            lire_flux_vlc(url_flux)
                            break
                        else:
                            print("❌ Numéro de flux invalide.")
                    except ValueError:
                        print("❌ Veuillez entrer un numéro valide.")
                elif choix_action == "2":
                    break
                else:
                    print("❌ Choix invalide.")
        else:
            print("❌ Aucun résultat trouvé. Essayez une autre recherche.")

if __name__ == "__main__":
    chemin_fichier_m3u = "playlist.m3u"  # Nom du fichier M3U récupéré
    if os.path.exists(chemin_fichier_m3u):
        contenu_flux = lire_fichier_m3u(chemin_fichier_m3u)
        if contenu_flux:
            rechercher_ou_lire(contenu_flux)
    else:
        print(f"❌ Le fichier '{chemin_fichier_m3u}' est introuvable.")
