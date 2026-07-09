# Resave Actorfolder Actors Ue5

- Date: 2026-05-04 14:59
- Source transcript: `a55167ec-7809-42ee-85c6-b54813b51913`

---

### User

es-tu disponible

**Assistant:** Oui, je suis disponible. Comment puis-je t'aider aujourd'hui ?


---

### User

avec UE5, comment faire pour que tous les acteurs de type ActorFolder soit resauvegardés
de temps en temps j'ai des actor folders qui demandent a etre resauvegardés
regarde en reference cette dialog D:\Sandbox\1.png

**Assistant:** Je vais regarder l'image de référence et chercher des informations sur ce sujet.

<details><summary>Tools used</summary>

- `Read` D:\Sandbox\1.png

</details>

**Assistant:** Je comprends bien ton problème. Tu as la dialog "Save Content" d'UE5 qui te montre plein d'`ActorFolder` (fichiers `__ExternalObjects__`) qui demandent à être resauvegardés. C'est un problème classique avec le système **One File Per Actor (OFPA)** / **World Partition** dans UE5.

Voici plusieurs solutions pour automatiser ce nettoyage :

## Solution 1 : Editor Utility Widget / Blueprint (recommandé pour usage ponctuel)

Tu peux créer un Editor Utility Blueprint qui parcourt et resauvegarde tous les `ActorFolder` dirty :

**Étapes :**
1. Crée un *Editor Utility Blueprint* basé sur `EditorUtilityWidget` ou simplement un `Blueprint` avec un bouton qui appelle un node custom
2. Utilise les nodes suivants dans une fonction :

```
Get Assets by Class (ActorFolder) 
  → For Each Loop 
    → Load Asset 
    → Save Loaded Asset (ou Save Package)
```

## Solution 2 : Script Python (le plus efficace)

UE5 a un excellent support Python pour ce genre d'opération. Crée un fichier `resave_actor_folders.py` :

```python
import unreal

@unreal.uclass()
class ResaveActorFolders:
    
    @staticmethod
    def resave_all_actor_folders():
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        
        filter = unreal.ARFilter(
            class_names=["ActorFolder"],
            recursive_paths=True,
            package_paths=["/Game"]
        )
        
        assets = asset_registry.get_assets(filter)
        
        unreal.log(f"Found {len(assets)} ActorFolder assets")
        
        packages_to_save = []
        for asset_data in assets:
            asset = asset_data.get_asset()
            if asset:
                package = asset.get_outermost()
                packages_to_save.append(package)
        
        if packages_to_save:
            result = unreal.EditorLoadingAndSavingUtils.save_packages(
                packages_to_save, 
                only_dirty=False
            )
            unreal.log(f"Saved {len(packages_to_save)} packages: {result}")

ResaveActorFolders.resave_all_actor_folders()
```

**Pour l'exécuter :**
- Active le plugin **Python Editor Script Plugin** dans Edit > Plugins
- Lance via `Tools > Execute Python Script` ou via la console : `py resave_actor_folders.py`

## Solution 3 : Commandlet `ResavePackages` (le plus puissant pour batch)

C'est la méthode recommandée par Epic pour resauvegarder massivement. Lance depuis une ligne de commande PowerShell :

```powershell
& "C:\Program Files\Epic Games\UE_5.x\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" `
  "D:\Path\To\YourProject.uproject" `
  -run=ResavePackages `
  -PackageFolder=/Game/__ExternalObjects__ `
  -AutoCheckOut `
  -SkipDirty=false `
  -IgnoreChangelist
```

**Options utiles :**
- `-PackageFolder=/Game/__ExternalObjects__` : limite aux external objects
- `-IncludeOnlyClasses=ActorFolder` : limite aux ActorFolders
- `-AutoCheckOut` : check-out auto si tu utilises Perforce/Git
- `-AutoCheckIn` : commit auto après resave
- `-ResaveOnDemand` : ne resauve que ce qui en a besoin

## Solution 4 : Hook automatique au save de la map

Si le problème revient régulièrement (ce qui semble être ton cas), tu peux créer un *Editor Subsystem* en C++ ou Blueprint qui réagit à `OnPreSaveWorld` ou `OnLevelActorAdded` pour forcer le save des ActorFolders en même temps que la map.

---

**Ma recommandation** vu ton cas (ça arrive "de temps en temps") : commence par la **Solution 2 (Python)** car elle est rapide à mettre en place, exécutable d'un clic, et tu peux la relancer dès que la dialog réapparaît. Si le problème devient vraiment fréquent, passe à la **Solution 3** en commandlet pour automatiser ça dans ton workflow de build/CI.

Veux-tu que je t'aide à créer le script Python ou un Editor Utility Blueprint adapté à ton projet ?
