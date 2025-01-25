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

def lire_flux_vlc(url):
    """Lance un flux IPTV en direct avec VLC Media Player."""
    try:
        print(f"🔄 Lecture du flux en direct : {url}")
        os.system(f'vlc --play-and-exit "{url}"')
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du flux : {e}")

def choisir_flux_et_lire(contenu):
    """Affiche les flux disponibles, permet de choisir et de les lire avec VLC."""
    if not contenu:
        print("❌ Aucun flux disponible.")
        return

    # Afficher la liste des flux
    print("\nListe des flux disponibles :")
    for i, flux in enumerate(contenu, 1):
        print(f"{i}. {flux['titre']}")

    try:
        choix = int(input("\nEntrez le numéro du flux à lire (ou 0 pour quitter) : "))
        if choix == 0:
            print("🖖 Fin du programme.")
        elif 1 <= choix <= len(contenu):
            url_flux = contenu[choix - 1]["url"]
            lire_flux_vlc(url_flux)
        else:
            print("❌ Choix invalide.")
    except ValueError:
        print("❌ Veuillez entrer un numéro valide.")

if __name__ == "__main__":
    chemin_fichier_m3u = "playlist.m3u"  # Nom du fichier M3U récupéré
    if os.path.exists(chemin_fichier_m3u):
        contenu_flux = lire_fichier_m3u(chemin_fichier_m3u)
        choisir_flux_et_lire(contenu_flux)
    else:
        print(f"❌ Le fichier '{chemin_fichier_m3u}' est introuvable.")
