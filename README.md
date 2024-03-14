# Video Streaming Downloader

## Description

Ce script Python permet de rechercher et de télécharger des vidéos depuis le site directement sur votre machine locale. Il offre une interface simple en ligne de commande pour rechercher des vidéos par mot-clé, choisir parmi les résultats, et lancer le téléchargement.

## Fonctionnalités

- Recherche de vidéos sur SITE par mot-clé.
- Liste des vidéos trouvées avec titres.
- Sélection et téléchargement de vidéos en format `.m3u8` converti en `.mp4`.

## Prérequis

- Python 3.6+
- Bibliothèques Python : `requests`, `beautifulsoup4`, `m3u8_to_mp4`
- `ffmpeg` installé sur votre système pour le traitement des vidéos.

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
   Assurez-vous que `ffmpeg` est correctement installé et accessible dans le PATH de votre système. Pour vérifier, exécutez :
   ```bash
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
   - Entrez le mot-clé pour rechercher des vidéos.
   - Sélectionnez le numéro de la vidéo que vous souhaitez télécharger parmi les résultats listés.
   - Le script télécharge la vidéo choisie.

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer le script, veuillez suivre ces étapes :
1. Forkez le dépôt.
2. Créez votre branche (`git checkout -b feature/amazing-feature`).
3. Commitez vos changements (`git commit -m 'Add some amazing feature'`).
4. Poussez la branche (`git push origin feature/amazing-feature`).
5. Ouvrez une Pull Request.
