# Video Streaming Downloader

## Description

Ce script Python permet de rechercher et de télécharger des vidéos depuis le site cible directement sur votre machine locale. Il offre une interface en ligne de commande simple pour :
- Rechercher des vidéos par mot-clé.
- Choisir une vidéo parmi les résultats affichés.
- Télécharger la vidéo au format `.m3u8`, convertie en `.mp4`.

## Fonctionnalités

- **Recherche dynamique** : Recherchez des vidéos sur le site cible en entrant simplement un mot-clé.
- **Affichage des résultats** : Obtenez la liste des vidéos trouvées avec leurs titres.
- **Téléchargement** : Sélectionnez la vidéo à télécharger, qui sera ensuite convertie en format `.mp4`.

## Prérequis

- Python 3.6 ou version supérieure.
- Bibliothèques Python :
  - `requests`
  - `beautifulsoup4`
  - `m3u8_to_mp4`
- `ffmpeg` doit être installé sur votre système pour la conversion des vidéos.

## Installation

1. **Cloner le dépôt Git** :
   ```bash
   git clone https://.git
   cd 2024_videoDwl
   ```

2. **Installer les dépendances** :
   Utilisez `pip` pour installer les dépendances nécessaires.
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer ffmpeg** :
   Vérifiez que ffmpeg est correctement installé et accessible dans le PATH de votre système. Par exemple, sous Windows :
   ```bash
   winget install ffmpeg
   ffmpeg -version
   ```
   Si `ffmpeg` n'est pas installé, référez-vous à la [documentation officielle de ffmpeg](https://ffmpeg.org/download.html) pour les instructions d'installation.

## Utilisation

1. **Lancer le script** :
   Exécutez le script via la ligne de commande.
   ```bash
   python fluxvideo.py
   ```
   
2. **Suivez les instructions** :
   - Entrez un mot-clé du titre pour rechercher des vidéos.
   - Sélectionnez le numéro de la vidéo que vous souhaitez télécharger parmi les résultats listés.
   - Le script télécharge la vidéo choisie.