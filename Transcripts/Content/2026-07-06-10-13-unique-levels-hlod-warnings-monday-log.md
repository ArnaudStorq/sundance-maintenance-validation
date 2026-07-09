# Unique Levels Hlod Warnings Monday Log

- Date: 2026-07-06 10:13
- Source transcript: `8057bcf1-507f-4b67-b48c-3360d2b0d9c6`

---

### User

donne moi le nom des levels uniques referencés (avec le nombre de reference) dans 
D:\Sandbox\HLODLayerWarnings_Monday6.txt

**Assistant:** I'm going to read the file.

<details><summary>Tools used</summary>

- `Read` D:\Sandbox\HLODLayerWarnings_Monday6.txt

</details>

**Assistant:** I'll start by examining the file structure.

<details><summary>Tools used</summary>

- `Read` D:\Sandbox\HLODLayerWarnings_Monday6.txt

</details>

**Assistant:** Je vais extraire les noms de levels avec PowerShell et les compter.

I'm going to use PowerShell to extract the level names from the text and tally how many times each one appears.

<details><summary>Tools used</summary>

- `Shell` Extract and count unique level references

</details>

**Assistant:** Le passage en ligne de commande pose des problèmes d'échappement. Je vais écrire un script.

The escaping approach isn't working well, so I'll switch to writing this as a script file instead.

<details><summary>Tools used</summary>

- `Write` D:\Sandbox\AI\count_levels.ps1
- `Shell` Run level counting script

</details>

**Assistant:** Voici les levels uniques référencés dans `HLODLayerWarnings_Monday6.txt`, avec leur nombre de références (**14 levels uniques**, 758 références au total) :

| Nb réf. | Level |
|---:|---|
| 243 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_DragonClaw` |
| 204 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_UnicornHorn_B` |
| 123 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_UnicornHorn_A` |
| 87 | `/Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Entrance` |
| 29 | `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_B` |
| 21 | `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_C` |
| 17 | `/Game/Experimental/Levels/Vault/Vault_Resource_Platforming_01/LI_Resource_Horklump_01` |
| 14 | `/Game/Levels/Overland/Hamlets/GransHouse/LI_Hamlets_GransHouse_EXT_Rock_A` |
| 6 | `/Game/Environment/Population/Camp/LI_Camp_StorageLarge_E` |
| 6 | `/Game/Levels/Overland/Ruins/Castle_Saints/LI_Castle_Brath_Annex_A` |
| 2 | `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Manor_Blockout` |
| 2 | `/Game/Environment/Population/Camp/LI_Camp_WoodenBox_A` |
| 1 | `/Game/Experimental/Levels/Overland/Ruins/LI_HV_A02_Ruins_Redcaps` |
| 1 | `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Cottage_Blockout` |

Toutes les références correspondent au même warning : `RuntimeGrid override` bloqué car la règle `DA_SmallGrid_Rules` ne peut pas utiliser le HLOD layer `LV_Overland_HLODLayer_Near` sur cette partition.

Je nettoie le script temporaire créé pour l'analyse.

Now I'm organizing the script and getting ready to show the results.

<details><summary>Tools used</summary>

- `Delete` D:\Sandbox\AI\count_levels.ps1

</details>

**Assistant:** C'est fait. Résumé : **14 levels uniques** sont référencés dans le fichier, dominés par les crates de Poacher (`DragonClaw`, `UnicornHorn_A/B`) qui totalisent à eux seuls 570 des 758 références.
