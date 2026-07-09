# Mapchecks Editor Report

- Date: 2026-07-09 08:30
- Source transcript: `726ba3a5-4f2e-4754-a6a4-c352380a680f`

---

### User

fais moi un rapport concernant ce fichier de MapChecks dans l'editeur : D:\Sandbox\MapChecks_20260709.txt

**Assistant:** I need to look at the MapChecks file to understand what the user is asking for.

<details><summary>Tools used</summary>

- `Read` D:\Sandbox\MapChecks_20260709.txt

</details>

**Assistant:** I need to work through this file systematically, reading it in sections to grasp how it's organized.

<details><summary>Tools used</summary>

- `Read` D:\Sandbox\MapChecks_20260709.txt

</details>

**Assistant:** Ce fichier est un log de MapCheck d'Unreal Engine. Je vais l'analyser en profondeur pour catégoriser les problèmes.

I'm analyzing this Unreal Engine MapCheck log to identify and categorize the different error types, then counting how many of each appear throughout the file.

<details><summary>Tools used</summary>

- `Shell` Count total lines in file

</details>

**Assistant:** I'm looking at a 914-line file and need to identify the distinct message types using grep patterns to categorize them.

<details><summary>Tools used</summary>

- `Grep` doesn't exist in the AWorldDataLayers
- `Grep` references Non-spatially loaded actor
- `Grep` has an invalid HLOD layer
- `Grep` Actor needs resave
- `Grep` does not comply with the rules

</details>

**Assistant:** La grande majorité (765) sont des HLOD invalides. Analysons ces catégories plus finement.

I'm breaking down the error categories in the file—765 invalid HLOD layer messages dominate, with smaller groups of non-spatial issues, missing datalayer references, compliance rule violations, and resave requests accounting for the remaining entries out of 914 total lines.

Now I need to dig into which specific HLOD layers are flagged as invalid and at what levels they're occurring.

<details><summary>Tools used</summary>

- `Grep` invalid HLOD layer (.*)$
- `Read` D:\Sandbox\MapChecks_20260709.txt

</details>

**Assistant:** Faisons une analyse statistique complète du fichier avec PowerShell pour regrouper les problèmes.

I'm going to analyze the distinct HLOD layer values and see which levels are affected by them, using PowerShell to group and examine the data in detail.

<details><summary>Tools used</summary>

- `Shell` Group invalid HLOD layers

</details>

**Assistant:** Écrivons un script pour éviter les problèmes d'échappement.

The `$lines` variable got emptied because of how the pipe was interpreted — it became just ` | Select-String` without the variable, likely due to the `$_` inside getting mangled. I'll write this as a script file instead to avoid the substitution issues.

<details><summary>Tools used</summary>

- `Write` D:\Sandbox\AI\analyze_mapcheck.ps1
- `Shell` Run mapcheck analysis script

</details>

**Assistant:** Analysons maintenant les références spatiales et la ligne "AUTRE".

I'm diving into the spatial-to-non-spatial references and the "AUTRE" entries, checking which specific line that refers to and examining the DataLayer gaps. Let me work through a second pass to analyze the spatial references by level.

<details><summary>Tools used</summary>

- `Write` D:\Sandbox\AI\analyze_mapcheck2.ps1
- `Shell` Run second analysis script

</details>

**Assistant:** J'ai toutes les données. Je nettoie les scripts temporaires et je rédige le rapport.

I'm working through what the user actually wants—they asked for a report "dans l'editeur" about the MapChecks file, which could mean they want it displayed in the editor or as a separate file. The phrasing is a bit ambiguous, but I should probably create a markdown report to accompany the analysis.

Looking at the data, I've got a clear breakdown: 912 total warnings with no errors. The main issues are 765 invalid HLOD warnings concentrated in a few actors, 125 spatial-to-non-spatial reference problems, 20 missing DataLayers across 17 distinct ones, 2 non-conforming DataLayers, and 1 actor needing a resave. The numbers add up correctly to the summary count.

Now I'll clean up the temporary scripts and generate the markdown report file.

<details><summary>Tools used</summary>

- `Delete` D:\Sandbox\AI\analyze_mapcheck.ps1
- `Delete` D:\Sandbox\AI\analyze_mapcheck2.ps1
- `Write` D:\Sandbox\Rapport_MapChecks_20260709.md

</details>

**Assistant:** J'ai analysé le fichier et créé un rapport complet : `D:\Sandbox\Rapport_MapChecks_20260709.md`.

## Synthèse rapide

Le fichier est un log **MapCheck Unreal Engine** : **0 erreur, 912 avertissements**. Voici la répartition :

| Catégorie | Nombre | Part |
|---|---:|---:|
| HLOD invalide | 765 | ~84 % |
| Référence acteur *spatial → non-spatial* | 125 | ~14 % |
| DataLayer manquant | 20 | ~2 % |
| DataLayer non conforme | 2 | <1 % |
| Actor needs resave | 1 | <1 % |

## Points clés

- **Le gros du problème est centralisé** : les 765 warnings HLOD pointent tous vers **une seule couche invalide**, `LV_Overland_HLODLayer_Near`. La réparer/réassigner élimine ~84 % des warnings d'un coup. Les acteurs les plus touchés sont `LI_Poachers_Basket_JobberknollFeather` (359), `LA_Road_Mound_02` (175) et `LA_Road_Mound_01` (140).
- **125 références spatial → non-spatial** (risque de streaming), concentrées dans les donjons `SDA_01`, `SBC_01`, `MFT` et diverses missions — souvent des acteurs de mise en scène (SceneRig/SR/CIV/VOM).
- **22 problèmes DataLayer** faciles à traiter : 17 DataLayers introuvables (familles `VAR`, `VSM`, `NEX`, `LON_Lab*`) + le `DL_M_MFF_01_BasiliskEscape` à retirer de 2 acteurs.
- **1 resave** simple : `LI_Cauldron_A2`.

Le rapport contient le détail complet, les tableaux par niveau/mission et un plan d'action priorisé. Traiter les points 1 et 2 (HLOD + DataLayers) ne laisserait qu'environ **125 warnings** à nettoyer ensuite.

Veux-tu que je génère aussi une **liste d'actions exploitable** (ex. CSV des acteurs à corriger par niveau) ou que je place le rapport ailleurs ?

The report is ready to share with the user.
