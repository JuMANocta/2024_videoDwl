def remove_links(file_path):
    """
    Filtre un fichier M3U pour ne conserver que les flux en direct français.
    Supprime les entrées contenant '/movie/' ou '/series/' et celles ne contenant pas '|FR|'.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Liste pour stocker les lignes filtrées
    filtered_lines = []
    skip_next = False
    i = 0
    while i < len(lines):
        # On s'attend à ce qu'une entrée commence par #EXTINF
        if lines[i].startswith("#EXTINF") and (i + 1) < len(lines):
            info_line = lines[i]
            url_line = lines[i+1]

    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue

        # Vérifie si la ligne actuelle contient '/movie/' ou '/serie/'
        if '/movie/' in lines[i] or '/series/' in lines[i] or '|FR|' not in lines[i]:
            # Ignore également la ligne précédente si elle existe
            if filtered_lines and filtered_lines[-1].startswith("#EXTINF"):
                filtered_lines.pop()
            skip_next = True
            # Conditions pour CONSERVER une ligne
            # 1. Doit contenir |FR|
            # 2. Ne doit PAS contenir /movie/
            # 3. Ne doit PAS contenir /series/
            if '|FR|' in info_line and '/movie/' not in url_line and '/series/' not in url_line:
                filtered_lines.append(info_line)
                filtered_lines.append(url_line)
            
            i += 2  # Passe à la prochaine paire de lignes
        else:
            filtered_lines.append(lines[i])
            i += 1 # Avance d'une ligne si elle n'est pas une ligne #EXTINF attendue

    # Écrit les lignes filtrées dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(filtered_lines)
    
    print(f"✅ Filtrage terminé. {len(filtered_lines) // 2} flux conservés.")

# Exemple d'utilisation
file_path = 'Z_PREMIUMplaylist.m3u'  # Remplacez par le chemin de votre fichier
remove_links(file_path)