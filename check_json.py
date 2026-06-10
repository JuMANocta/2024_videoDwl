import json
import os
import sys
import time

def check_json_file(file_path):
    """Vérifie si un fichier JSON est bien formé sans forcément charger tout en RAM si possible, 
    bien que json.load construise l'objet en mémoire."""
    
    if not os.path.exists(file_path):
        print(f"❌ Erreur : Le fichier '{file_path}' n'existe pas.")
        return

    taille_mo = os.path.getsize(file_path) / (1024 * 1024)
    print(f"🔍 Analyse de '{file_path}' ({taille_mo:.2f} Mo)...")
    
    start_time = time.time()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # json.load est le moyen le plus sûr de vérifier la structure complète
            json.load(f)
        
        end_time = time.time()
        print(f"✅ Succès : Le fichier est parfaitement valide. (Temps : {end_time - start_time:.2f}s)")
        
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de syntaxe JSON détectée !")
        print(f"   👉 Message : {e.msg}")
        print(f"   👉 Ligne : {e.lineno}")
        print(f"   👉 Colonne : {e.colno}")
        print(f"   👉 Position : {e.pos}")
        
        # Optionnel : afficher un extrait autour de l'erreur
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.seek(max(0, e.pos - 50))
                extrait = f.read(100)
                print(f"\nExtrait autour de l'erreur :\n{'...' if e.pos > 50 else ''}{extrait}...")
        except:
            pass

    except MemoryError:
        print("❌ Erreur : Le fichier est trop lourd pour être chargé en RAM avec cette méthode.")
        print("   Considérez l'utilisation d'une bibliothèque de streaming comme 'ijson'.")
    
    except Exception as e:
        print(f"❌ Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_json_file(sys.argv[1])
    else:
        fichier = input("Entrez le nom du fichier JSON à vérifier (ex: vod_cache.json) : ").strip()
        if fichier:
            check_json_file(fichier)
        else:
            print("Usage: python check_json.py <nom_du_fichier>")
