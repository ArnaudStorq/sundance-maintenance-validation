# Knowledge Recap Export To Onenote

- Date: 2026-07-07 11:10
- Source transcript: `65559f5e-fcdc-4441-ae75-bff5f2045092`

---

### User

j'aimerais que tu me fasses un resumé point par point, topics par topics, des grandes connaissances indispensables dont on a evoqué depuis que l'on travaille ensemble

**Assistant:** Je vais parcourir nos échanges passés pour te faire un résumé fidèle. Laisse-moi consulter l'historique de nos sessions de travail.

I need to look through the agent transcripts to understand what topics we've covered so I can provide a comprehensive summary of the key knowledge we've discussed.

<details><summary>Tools used</summary>

- `Shell` List agent transcript files
- `Glob` *.jsonl

</details>

**Assistant:** Il y a 39 sessions. Je vais en extraire les sujets principaux. Regardons d'abord la structure d'un fichier.

I've got 39 transcript files to work through, so I'll start by examining the structure of one to understand the format, then extract the first user message or title from each to identify the topics they cover.

<details><summary>Tools used</summary>

- `Shell` List transcripts sorted by time

</details>

**Assistant:** Je vais extraire les messages utilisateur de chaque session pour comprendre les sujets abordés. Regardons d'abord le format d'un fichier.

I'm going to extract the key information from these transcripts by pulling out the titles and initial user messages rather than reading through all 39 files completely. Let me start by examining the structure of one JSONL file to understand how the data is organized.

<details><summary>Tools used</summary>

- `Read` C:\Users\Arnaud.Storq\.cursor\projects\d-Sandbox-AI\agent-transcripts\83abcd27-28c7-4c46-b918-9a69067451c7\83abcd27-28c7-4c46-b918-9a69067451c7.jsonl

</details>

**Assistant:** Je vais extraire toutes les questions utilisateur de chaque session pour cartographier les sujets.

I need to write a script that parses through the JSONL files to extract all the user query text, handling the fact that these messages might span multiple lines within the JSON structure.

<details><summary>Tools used</summary>

- `Shell` Extract user questions from transcripts

</details>

**Assistant:** Beaucoup de sessions ont un format différent. Je vais cibler spécifiquement le contenu des balises `user_query` de manière plus robuste.

I'm realizing my filter was too aggressive—it's removing legitimate content that starts with `<user_query>` tags. After stripping those tags, there's often leading whitespace before the actual message text, so I need to relax the filtering approach to capture more of these transcripts.

<details><summary>Tools used</summary>

- `Shell` Extract user_query blocks robustly
- `Read` C:\Users\Arnaud.Storq\.cursor\projects\d-Sandbox-AI\agent-tools\f5e4e654-68ae-4ccb-86ab-7fed0162fcb6.txt

</details>

**Assistant:** J'ai parcouru l'ensemble de nos ~39 sessions depuis le 17 avril. Voici le résumé structuré, topic par topic, des connaissances essentielles qu'on a bâties ensemble. Je nettoie d'abord le fichier temporaire.

I'm organizing the key topics I've covered into a structured summary—starting with Unreal Engine's world partitioning system including HLOD layers and data layers, then moving into level instances and their different configurations, and wrapping up with some mapcheck validation issues.

Now I'm laying out the remaining topics: the relative location drift problems, Perforce workflows, converting legacy levels to world partition, the various builder systems and validation tools, plus all the supporting infrastructure like Git and the cursor workflow with AI skills and batch processes. I should write this in French since that's what the user used, keeping it substantial but well-organized by topic with clear bullet points throughout.

<details><summary>Tools used</summary>

- `Shell` Remove temp extraction file

</details>

**Assistant:** # Résumé de nos connaissances essentielles — topic par topic

Voici la synthèse de tout ce qu'on a exploré ensemble sur ton projet **Sundance / LV_Overland** (Unreal Engine 5.7, WB Games Montréal), organisée par grands thèmes.

---

## 1. World Partition : les 3 propriétés de streaming au cœur de tout

Le fil rouge de presque tout notre travail tourne autour de 3 propriétés d'acteurs :

- **HLODLayer** — le layer de Hierarchical LOD assigné à un acteur.
- **DataLayers** — les data layers auxquels un acteur est assigné.
- **RuntimeGrid** — la grille de streaming runtime.

Points clés retenus :
- Un acteur ne peut être **HLOD-relevant** que s'il est *spatially loaded* et a un HLODLayer valide **compatible avec sa RuntimeGrid**.
- Le warning central qu'on a traqué pendant des semaines : `Actor ... has an invalid HLOD layer ...` → il apparaît quand un acteur porte un HLODLayer qui n'est **pas valide pour la grille sur laquelle il se trouve**.
- Un acteur peut être `Include In HLOD = true` **sans** avoir de HLODLayer explicite (use-case : il hérite/participe au HLOD via la grille par défaut sans layer dédié).

---

## 2. Level Instances : partitionné vs non-partitionné, et OFPA

Distinction fondamentale qu'on a martelée :

- **Level Instance partitionné** : embarqué dans le Persistent Level, ses inner actors vivent dans des fichiers `__ExternalActors__/...` (One File Per Actor).
- **Level Instance non-partitionné** : ses inner actors sont stockés **dans le sub-world lui-même** (l'asset `.umap`), pas dans des fichiers `_ExternalActors_` séparés.
- **OFPA (One File Per Actor)** : chaque acteur est sérialisé dans son propre `.uasset` sous `__ExternalActors__`. C'est ce qui fait qu'un acteur peut être checkout/save individuellement.
- La propriété **`Level`** d'un `ALevelInstance` (visible dans Details) pointe vers le `.umap` cible — c'est cette valeur qu'on collectait dans un `TSet`.
- On parcourt la hiérarchie **récursivement depuis `LV_Overland`** pour découvrir tous les level instances (il faut souvent les *charger dynamiquement* car ils ne sont pas ouverts).
- `RuntimeGrid` et `HLODLayer` sont des **propriétés parfois cachées du UI** dans le panneau Details.

---

## 3. Les builders / commandlets qu'on a développés

Plusieurs itérations d'outils C++ pour corriger en masse les propriétés de streaming :

- **`UWorldPartitionRuleBuilder`** — le builder d'origine (logging Location/Rotation avant/après load/save).
- **`FWorldPartitionHLODFixupHelper` / `WorldPartitionHLODFixupHelper.cpp`** — reset conditionnel de HLODLayer / DataLayers / RuntimeGrid, avec checkout Perforce, save, et **rapport final des fichiers lockés**.
- **`UWorldPartitionFixupNonPartitionedActorsBuilder`** — cible les inner actors des levels non-partitionnés (via `GetNonPartitionedLevels`), en 3 phases, avec options `-DryRun`, `-SkipLevelPackage`, génération de rapport `NonPartitionedLI_InnerActors_Report.txt`.
- Hooks dans **`ITokenizedMessageErrorHandler`** (`OnInvalidHLODLayer`, `OnInvalidRuntimeGrid`, `OnInvalidReference`...) et dans `WorldPartitionStreamingGeneration.cpp` (`FixupInvalidHLODLayerOnAsset`).

Principes de dev qu'on a adoptés :
- **Ne modifier que si nécessaire** (skip si la propriété était déjà vide → pas de checkout/resave inutile).
- **Live Coding** systématique pour itérer vite.
- Préfixer les logs de diagnostic (ex. `HLODFIX`, `[Diag-Hook]`) pour les retrouver.
- Prévoir une commande commandlet type : `-run=WorldPartitionBuilderCommandlet -Builder=... -SCCProvider=Perforce -DryRun -Unattended -NoShaderCompile LV_Overland`.

---

## 4. Le problème du "drift" RelativeLocation / Rotation / Scale3D

Un des combats les plus longs :

- En resauvegardant des packages, on introduisait involontairement des changements de **`RelativeLocation` / `RelativeRotation` / `RelativeScale3D`** (et parfois `EditorOnlySeasonsDefaultMesh`) → **inacceptable**.
- Solution adoptée : après chaque save, faire un **diff Perforce** ; si ces champs ont changé → **revert complet** de l'asset.
- Le vrai souci n'était pas la modif *en mémoire* mais le fait que le **package soit sauvegardé avec les valeurs driftées**.
- Leçon finale : tu as préféré **gérer toi-même** la vérification du drift et garder l'implémentation du fixup **la plus simple possible**.

---

## 5. Perforce (P4) — source control

Connaissances pratiques accumulées :

- **Checkout automatique** avant save : vérifier `IPlatformFile::IsReadOnly()` sur le package et faire un checkout si read-only.
- Diagnostic des **fichiers lockés** : `FPerforceSourceControlState::GetHistoryItem()`, récupérer `checkedOutBy` (ex. `jprice @ //sun/Dev`), le fullpath P4 (`//sun/Dev/...`), et générer un rapport **"actions à prendre"** (qui doit release quel fichier).
- **Changelists** : déplacer les acteurs problématiques d'une grosse CL vers une petite CL.
- **Validation de changelist** : `WorldPartitionChangelistValidator` / `DataValidationChangelist::IsDataValid` échoue si un objet référencé (ex. `WorldDataLayers`) n'est pas aussi ajouté à la CL. Piège récurrent : les External Actors référencés doivent être dans la même CL.

---

## 6. Convertir un Level non-partitionné en World Partition

- Menu **Tools → Convert Level**, ou clic droit sur l'asset → **Add Partitioned Streaming Support** (équivalents), ou **"Setup Level Instance for World Partition"**.
- Option **"In Place"** utile.
- En batch : `WorldPartitionEditorModule.ConvertMap` fait spawner ~100 dialogs → on a fait une **version headless sans dialog** avec auto-checkout P4 (`UWEditorImprovementsBlueprintFunctionLibrary::ConvertLevelsToWorldPartition`).
- Piège : en **headless/commandlet**, le build d'assembly **Nanite** peut crasher (`SK_HardFern_C_Nanite`) → override cvar pour empêcher le build de rendu (la conversion n'a besoin que de load/resave).
- Un level déjà converti se reprocesse beaucoup plus vite la 2ᵉ fois.

---

## 7. Rules, SmallGrid & IncludeInHLOD (le sujet "chef")

- **`AvaStreamingGenerationMutator` / `ApplyRuntimeGridRule`** applique les rules à la streaming generation.
- Le warning : `Skipped RuntimeGrid override ('None' -> 'SmallGrid') ... rule 'DA_SmallGrid_Rules' cannot use HLOD layer 'LV_Overland_HLODLayer_Near' on that partition`.
- Compréhension clé : les rules s'appliquent aux **level instance actors** pointant vers des levels convertis en WP (hiérarchie depuis `LV_Overland`), **pas** à un Level standalone.
- **HogsmeadeGrid** (32 m cell / 64 m loading) est plus petite que **SmallGrid** (76.2 m cell / 128 m loading).
- Pistes de résolution discutées : convertir les levels en WP pour avoir la granularité à l'acteur ; régler `IncludeInHLOD=false` + `TargetHLODLayer=None` sur les acteurs problématiques ; créer une `UHLODLayerRuleAsset` alignée sur les bornes de taille de `DA_SmallGrid_Rules`.
- Le mutator **ne change pas** les attributs des acteurs (rôle de reporting/override runtime).
- On réapplique les rules **au save** → resauvegarder suffit souvent.

---

## 8. Peeves — validation au submit

- Système de validation maison **Peeves**.
- Objectif : afficher une **erreur bloquante au submit** si un level non-partitionné est soumis, en invitant à le partitionner.
- Décision clé : si le level **n'est PAS référencé par `LV_Overland`**, on **skip complètement** la validation (à tester en premier).
- Réserve soulevée : valider au submit est fastidieux (l'artiste découvre tard qu'il faut convertir, risque de perte de data) → réflexion sur le bon moment de validation.

---

## 9. Outils annexes & workflow

- **Blueprint / Editor Utility** : créer un *Asset Action Utility* (piège : il n'apparaît pas dans le sous-menu Asset Actions selon la config ; distinction avec Scripted Asset Actions).
- **Fichiers `.bat`** : `process_li.bat` pour traiter en batch une liste de Level Instances via `UnrealEditor-Win64-DebugGame.exe` + `Sundance.uproject` (attention au placeholder `<NOM_DU_LI>` non substitué).
- **Git** : repo `D:\CustomGitRepos`, README (traduit en anglais), commit + publish.
- **Erreurs de compilation UE** récurrentes qu'on a résolues : `C2665 GetNameSafe`, `C2338 TWeakObjectPtr` (types UObject only), `C2065 LogWorldPartition undeclared`, **dépendances circulaires** dans `Engine.Build.cs` (Engine → SourceControl → EditorFramework → Engine), checkout de `.Build.cs`.
- Extraction récurrente : **liste unique des levels** (avec compte d'occurrences) depuis les logs `HLODLayerWarnings_*.txt`.

---

## 10. Environnement & infra

- **Git avancé** : `core.protectNTFS false`, `core.longpaths true`, `reset --hard`, `clean -fd`, création de branche depuis `origin/...`, rôle de `git pull`.
- **ActorFolders** (UE5) : resauvegarde périodique des acteurs de type ActorFolder ; remplacement de `FActorFolderDescsContext::GetActorFolderDesc` par `FActorFolderDesc::GetPath`.

---

## 11. Transcription & veille (Unreal Fest + vidéos de Phil)

- Transcription fidèle d'images/notes (Unreal Fest 2026 Chicago, 17–18 juin), datation d'images via **tags EXIF**, renommage en `.jpg`, extraction de notes Confluence.
- Transcripts + résumés + actions de plusieurs vidéos de **Phil / William** sur HLOD, Include In HLOD, World Partition Rules, SmallGrid (avec timelines ciblées).
- Retouche d'image : remplacement du logo Ubisoft par WB Games Montréal.

---

## 12. Outillage Cursor & Miro

- Amélioration du workflow via les **AI Skills** de Cursor.
- **Miro** : accès via le plugin MCP, embed de board en view-only, invitation de compte.

---

**En une phrase** : l'essentiel de notre collaboration a consisté à **faire disparaître proprement les warnings mapcheck "invalid HLOD layer / RuntimeGrid" sur `LV_Overland`**, en convertissant les levels en World Partition et en corrigeant les propriétés de streaming des acteurs — **sans jamais introduire de drift de transform**, le tout intégré à Perforce, à la validation Peeves, et outillé par des builders/commandlets, du Blueprint et des scripts batch.

Veux-tu que je développe un de ces thèmes en particulier, ou que j'en fasse un document markdown de référence dans le workspace ?

I'm organizing the main points to write a comprehensive summary in French.


---

### User

es-tu capable de me créer une nouvelle page dans OneNote avec toute cette info ?

**Assistant:** Je n'ai pas de connecteur OneNote natif (le seul MCP disponible ici est Miro). Mais sur Windows, OneNote 2016 desktop expose une API COM que je peux piloter via PowerShell. Laisse-moi vérifier ce qui est installé sur ta machine.

I'm checking what tools I have available for OneNote integration. Looking at the MCP servers, only Miro is available, so I can't directly create a OneNote page through an API. I'd need to either use the Microsoft Graph API with authentication or work with OneNote's desktop app, neither of which are accessible here.

Let me explore what's actually possible. I could create an HTML or markdown file that OneNote can import, or if OneNote 2016 desktop is installed, I might be able to use PowerShell COM automation to interact with it directly. Let me check if the OneNote COM API is available on this system.

<details><summary>Tools used</summary>

- `Shell` Test OneNote COM availability

</details>

**Assistant:** OneNote 2016 est accessible via COM. Je vais lister tes notebooks et sections pour savoir où créer la page.

The COM object for OneNote is working, but the enum type reference isn't loading properly. I can work around this by passing the scope value as an integer instead—I need to recall what the enum values are, starting with hsNotebooks being 0.

Now I'm calling GetHierarchy with integer values to retrieve the notebook hierarchy so I can find where to create the page.

<details><summary>Tools used</summary>

- `Shell` List OneNote notebooks and sections

</details>

**Assistant:** OneNote 2016 est pilotable. Tu as le notebook **"Arnaud @ WB Games"** avec une section **"Sundance"** — c'est l'endroit logique pour ce contenu. Je vais y créer une nouvelle page avec tout le résumé mis en forme.

Je prépare un script robuste pour générer la page.

I'm looking at the notebook structure for "Arnaud @ WB Games" and deciding where to create this new page. The Sundance section seems like the most logical fit since all the content relates to the Sundance project, so I'll place it there.

Now I need to create the page using the OneNote API, then populate it with content formatted in OneNote's XML schema. I'll write a PowerShell script to handle this reliably, building the page structure programmatically with the title and content formatted as HTML within the OneNote outline elements. Building the PowerShell script to construct the XML payload with the proper OneNote schema, then parse the returned page content to inject the title and HTML-formatted summary into the outline structure.

<details><summary>Tools used</summary>

- `Write` D:\Sandbox\AI\create_onenote_page.ps1
- `Shell` Run OneNote page creation script

</details>

**Assistant:** OneNote a rejeté le XML : les balises de bloc (`<ul>`, `<h2>`, `<div>`) ne sont pas valides dans un `<one:T>`. Il faut structurer chaque titre et chaque puce comme des éléments OneNote natifs (`OE` + `List/Bullet`). Je corrige le script.

The error code points to invalid XML in the schema—the issue is likely that rich HTML content inside CDATA sections isn't compatible with OneNote's strict requirements. While OneNote does support HTML within the text element, it's limited to inline formatting; block-level elements like headings, divs, and lists typically cause validation failures.

The real solution is to restructure the content using OneNote's proper element hierarchy: each line (heading, bullet, paragraph) needs its own outline element with a list structure for bullets, and inline HTML styling like bold and font size can be applied within the text node itself. I'm going to rebuild the script to generate individual outline elements for each content line rather than cramming everything into a single text node.

Rewriting the script... Rewriting the script fully...

<details><summary>Tools used</summary>

- `Write` D:\Sandbox\AI\create_onenote_page.ps1
- `Shell` Run corrected OneNote page creation

</details>

**Assistant:** Toujours un XML invalide. Je vais isoler le problème avec un test minimal pour comprendre ce que OneNote accepte.

I'm getting an XML validation error and need to isolate the problem. Let me start with a minimal test—just updating the page title and a single text element without any HTML formatting—to verify the basic mechanism works before adding complexity back in.

<details><summary>Tools used</summary>

- `Shell` Minimal OneNote update test

</details>

**Assistant:** Le schéma XML est en cause : j'utilise le namespace 2013 mais je passe `xsSchema=0` (2007). Je corrige avec le schéma 2013 (valeur 2).

I'm looking up the OneNote error code 0x80042001 to figure out what's actually going wrong here—it seems to be related to XML validation or section referencing issues rather than the HTML itself.

Actually, I think I found it: the UpdatePageContent method takes an xsSchema parameter that specifies which XML schema version to use, and I've been passing 0 (xs2007) when my namespace is actually 2013. That mismatch between the schema version and the namespace in the XML would definitely cause validation failures. I should pass 2 (xs2013) instead to match the 2013 namespace I'm using.

<details><summary>Tools used</summary>

- `Shell` Test update with schema variants

</details>

**Assistant:** Le schéma 2013 fonctionne, et le gras aussi. Mes essais ont créé quelques pages parasites (vides + tests) dans la section Sundance. Je les liste pour faire le ménage avant de créer la vraie page.

The schema=2 approach is working well with inline bold formatting, so I need to update the full script to use it. But I've accumulated some clutter—the test runs created several empty pages in the Sundance section when CreateNewPage succeeded but UpdatePageContent failed, plus the extra test pages from my experiments. I should clean those up first before running the real version.

I'll query the pages in the Sundance section to see their creation times and titles, then delete the test pages and any empty ones I created in the last 15 minutes or so.

<details><summary>Tools used</summary>

- `Shell` List pages with creation time in Sundance

</details>

**Assistant:** La page "Untitled" du 24 mars est préexistante (je n'y touche pas). Les 4 pages du 7 juillet 15:20–15:22 sont mes essais. Je les supprime puis je crée la vraie page.

I need to be careful here — there's an older untitled page from March that I should leave alone. The four pages I created today during that brief window are the ones to remove, so I'll delete those using the hierarchy deletion function. After clearing those out, I can create the final page with the correct schema version.

<details><summary>Tools used</summary>

- `Shell` Delete stray test pages

</details>

**Assistant:** Ménage fait. Je corrige le script pour utiliser le schéma 2013 et je lance la création finale.

<details><summary>Tools used</summary>

- `StrReplace` D:\Sandbox\AI\create_onenote_page.ps1
- `Shell` Create final OneNote page

</details>

**Assistant:** La page est créée. Je vérifie que le contenu s'est bien écrit.

I'm verifying the page was created correctly by checking that the title and content elements are in place.

<details><summary>Tools used</summary>

- `Shell` Verify created page content

</details>

**Assistant:** `$pid` est une variable réservée en PowerShell. Je réessaie avec un autre nom.

<details><summary>Tools used</summary>

- `Shell` Verify page content with valid var name

</details>

**Assistant:** La page est créée et vérifiée. Je supprime le script temporaire.

The page structure is set with 68 blocks total, and I'm deciding whether to keep the temporary script file. Since it was a one-off tool, I'll delete it to keep things tidy.

<details><summary>Tools used</summary>

- `Delete` D:\Sandbox\AI\create_onenote_page.ps1

</details>

**Assistant:** Oui, c'est fait. La page a été créée directement dans OneNote via l'API COM.

**Page créée :**
- **Notebook :** `Arnaud @ WB Games`
- **Section :** `Sundance`
- **Titre :** *Sundance / World Partition - Connaissances essentielles (recap collaboration)*
- **Contenu :** les 12 sections thématiques + la synthèse finale, avec titres en bleu/gras et **53 puces** de détails (68 blocs au total).

Ouvre OneNote et va dans la section **Sundance** — la page est là (si elle n'apparaît pas tout de suite, un petit rafraîchissement/sync suffit).

Quelques précisions utiles :
- Je n'ai pas de connecteur OneNote « natif » — j'ai piloté **OneNote 2016 desktop via son API COM** en PowerShell. Ça ne marche donc que tant que la version desktop est installée (pas l'app UWP « OneNote for Windows 10 » seule).
- Au passage, j'avais créé quelques pages d'essai (le temps de trouver le bon schéma XML 2013) : je les ai **toutes supprimées**, et j'ai **laissé intacte** ta page « Untitled » préexistante du 24 mars.
- Les accents ont été volontairement simplifiés (texte sans diacritiques) car le contenu source de nos transcripts était encodé de façon corrompue — je préférais un rendu propre et lisible plutôt que des caractères parasites.

Veux-tu que je la place plutôt dans une autre section (ex. `WB Games Montréal`), que j'ajoute des sous-pages par thème, ou que je réintègre les accents ?
