# Tools

Ensemble d'outils/scripts utilitaires pour le projet Sundance (Unreal Engine).

## Outils disponibles

### ProcessLevelInstances

Dossier : [`ProcessLevelInstances/`](ProcessLevelInstances/)

Script batch Windows (`process_li.bat`) qui exécute la commandlet
`WorldPartitionBuilderCommandlet` (builder `WorldPartitionRuleBuilder`) sur une
liste de Level Instances, l'une après l'autre.

Pour chaque Level Instance de la liste, le script lance l'éditeur Unreal en
mode ligne de commande avec les règles de build (DataLayer, HLOD, RuntimeGrid)
et affiche un statut `[OK]` / `[ERREUR]` pour chaque traitement.

#### Configuration

À adapter en haut du fichier `process_li.bat` :

| Variable | Description | Valeur actuelle |
| --- | --- | --- |
| `EDITOR_CMD` | Chemin vers l'exécutable de l'éditeur Unreal | `D:\Sun\Engine\Binaries\Win64\UnrealEditor-Win64-DebugGame.exe` |
| `UPROJECT` | Chemin vers le fichier `.uproject` | `D:\Sun\Sundance\Sundance.uproject` |
| `ARGS` | Arguments passés à la commandlet (contient le marqueur `<NOM_DU_LI>`) | voir le fichier |
| `LI_LIST` | Liste des Level Instances à traiter (un nom par ligne) | voir le fichier |

Le marqueur `<NOM_DU_LI>` présent dans `ARGS` est automatiquement remplacé,
à chaque itération, par le nom du Level Instance courant.

#### Utilisation

1. Vérifier / ajuster `EDITOR_CMD`, `UPROJECT` et `LI_LIST`.
2. Double-cliquer sur `process_li.bat` ou l'exécuter depuis une invite de commandes :

```bat
process_li.bat
```

Le script traite tous les Level Instances puis attend une touche (`pause`)
avant de fermer la fenêtre.
