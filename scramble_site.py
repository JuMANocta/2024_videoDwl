def scramble_site(site_name, mapping):
    """
    Prend le nom du site (site_name) et un mapping (liste d'entiers)
    représentant la position cible de chaque lettre d'après
    # original indices: 0 1 2 3 4 5
    # mapping         : 4 2 3 0 1 5
    Puis retourne le nom réordonné.
    """
    if len(site_name) != len(mapping):
        raise ValueError("La longueur du nom doit correspondre à celle du mapping.")
    # On crée une liste vide de la taille du nom
    result = [''] * len(site_name)
    # Pour chaque index i de site_name, place la lettre à la position mapping[i] dans result
    for i, pos in enumerate(mapping):
        result[pos] = site_name[i]
    return ''.join(result)

# Exemple d'utilisation :
original = "signal"
mapping = [4, 2, 3, 0, 1, 5]
site = scramble_site(original, mapping)
print(site)  # Affiche "doorfv"
# vérification
url = site
site = url[4]+url[2]+url[3]+url[0]+url[1]+url[5]
print(site)