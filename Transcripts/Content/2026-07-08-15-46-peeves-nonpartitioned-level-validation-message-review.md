# Peeves Nonpartitioned Level Validation Message Review

- Date: 2026-07-08 15:46
- Source transcript: `e59c1b93-450f-4ff7-84ae-5d5436f66023`

---

### User

est-ce que cette requete est pertinente ? peux-tu l'ameliorer techniquement ?


---

### User

Hello David :wave: 
I would like to add a new Peeves validation (at pre-submit time in the Editor).
If a changelist includes changes to a Level that is not World Partition-enabled, I would like Peeves to raise an ERROR (and not a warning). This should apply whether the changelist modifies the Level asset itself or any of its internal actors, including cases where OFPA is not enabled. The check should only apply to Levels that are outside the folders //sun/Dev/Sundance/Content/Developers/ and //sun/Dev/Sundance/Plugins/.

Proposed error message:
"This Level must be converted to World Partition. In the Content Browser, right-click the Level and select 'Add Partitioned Streaming Support'."

The goal is to enforce World Partition on all Levels used by LV_Overland. This excludes custom Gyms for quick prototyping etc.
This is required so actor-level metadata can be authored consistently (for example HLOD settings, Runtime Grid assignment, and Data Layers), rather than being limited to the parent Level. That granularity is necessary to avoid, for example, HLOD-related conflicts and DataLayer mismatches.

**Assistant:** Je vais d'abord vérifier si le code de Peeves (ou du projet Sundance) est présent dans ce workspace, pour pouvoir être précis techniquement.

L'utilisateur me demande en français d'évaluer la pertinence d'une requête technique et de l'améliorer. Il s'agit d'un message Slack destiné à David concernant l'ajout d'une validation Peeves dans l'éditeur Unreal Engine pour un projet appelé Sundance qui utilise World Partition. Je dois examiner le contexte du projet pour mieux comprendre cet outil de validation interne et formuler une demande plus solide techniquement. I'm working through the technical details now—how to detect World Partition status efficiently without loading every level, handling external actor files under __ExternalActors__, distinguishing between error and warning severity, and accounting for edge cases like level instances and sub-levels. I should also structure the response to validate the message's pertinence, suggest clarity improvements, and outline implementation considerations like using AssetRegistry tags to avoid expensive level loads during presubmit checks.

<details><summary>Tools used</summary>

- `Grep` Peeves|WorldPartition|IsPartitioned|ExternalActors
- `Glob` **/*.{cpp,h,cs}

</details>

**Assistant:** Ce workspace ne contient pas le code de Peeves (juste des scripts et des transcripts liés à Sundance/HLOD), donc je te réponds sur le fond et la forme de la demande elle-même.

## Est-ce que la requête est pertinente ?

Oui, très. La demande est bien fondée techniquement :

- **La justification est solide** : imposer World Partition (WP) pour permettre l'authoring de métadonnées *par acteur* (HLOD, Runtime Grid, Data Layers) plutôt que globalement au niveau du Level est un vrai besoin, et éviter les conflits HLOD / mismatches DataLayer est un argument concret.
- **Le choix ERROR plutôt que WARNING** est cohérent avec une contrainte que tu veux *bloquante* au pre-submit.
- **L'exclusion des dossiers `Developers/` et `Plugins/`** (gyms, prototypage) est un garde-fou raisonnable.

Là où elle mérite d'être renforcée avant d'être envoyée à David : elle mélange le *quoi* (règle métier) et laisse plusieurs zones grises sur le *comment* (détection technique, cas limites, perf). Un dev Peeves aura des questions. Autant y répondre d'avance.

## Points techniques à préciser / améliorer

**1. Détection « Level non-WP »**
- Préciser le critère exact. En pratique : un `UWorld` est partitionné si `World->GetWorldPartition() != nullptr` (ou `ULevel::bIsPartitioned`). 
- Mais charger chaque `.umap` au pre-submit est coûteux. Mieux vaut s'appuyer sur les **tags de l'Asset Registry** (le World expose des tags, ex. `LevelIsPartitioned` / présence de `WorldPartition`) pour éviter de charger la map complète. À valider avec l'équipe Peeves selon la version d'UE.

**2. « ou n'importe lequel de ses acteurs internes »**
C'est le point le plus ambigu. Il faut distinguer 3 cas de packaging :
- **Non-OFPA + non-WP** : les acteurs sont *dans* le `.umap` → toute modif d'acteur = modif de l'asset Level. Trivial.
- **OFPA activé mais non-WP** : possible dans UE. Les acteurs sont des fichiers séparés sous `__ExternalActors__/` (et `__ExternalObjects__/`). Il faut alors **résoudre le Level propriétaire** à partir du chemin du fichier acteur, puis vérifier le statut WP de ce Level.
- Donc la formule « including cases where OFPA is not enabled » gagnerait à être reformulée pour couvrir explicitement ces fichiers `__ExternalActors__` / `__ExternalObjects__`.

**3. Filtrage des chemins**
- Utiliser un **matching de préfixe normalisé** sur le package path (attention à la casse, aux séparateurs, et au préfixe `//sun/Dev/Sundance/…` vs chemin `/Game/…` monté).
- Suggérer de rendre la liste d'exclusion **pilotée par config** (`.ini` / DefaultEditor) plutôt que codée en dur, pour ne pas redéployer Peeves à chaque ajout de dossier.

**4. Cas limites à trancher explicitement**
- Nouveaux Levels créés dans le CL.
- Redirectors, Level Instances / sublevels, World Composition (legacy).
- Que faire si un CL touche uniquement un `__ExternalActors__` orphelin (Level supprimé) ?

**5. Critères d'acceptation**
Ajouter un mini scénario de test : « CL modifiant un acteur d'un Level non-WP hors des dossiers exclus → ERROR bloquante ; même CL dans `Developers/` → pass ».

## Version reformulée du message (prête à envoyer)

Voici une réécriture qui garde ton intention mais lève les ambiguïtés :

```
Hi David 👋

I'd like to add a new Peeves pre-submit validation (Editor) to enforce World Partition on all Levels used by LV_Overland.

Rule
- If a changelist touches a Level that is NOT World Partition-enabled, Peeves should raise an ERROR (blocking), not a warning.
- "Touches" must cover both:
  1. the Level asset (.umap) itself, and
  2. any of its actors — including OFPA files (__ExternalActors__ / __ExternalObjects__), which must be resolved back to their owning Level to check its WP status.
- Scope: only Levels OUTSIDE these folders (prototyping / custom gyms are excluded):
  - //sun/Dev/Sundance/Content/Developers/
  - //sun/Dev/Sundance/Plugins/
  (Ideally the exclusion list is config-driven so we can extend it without redeploying Peeves.)

Error message
"This Level must be converted to World Partition. In the Content Browser, right-click the Level and select 'Add Partitioned Streaming Support'."

Why
Enforcing WP lets us author metadata per-actor (HLOD settings, Runtime Grid assignment, Data Layers) instead of only at the parent Level. That granularity is required to avoid HLOD conflicts and DataLayer mismatches.

Open questions for you
- Best way to detect WP status at pre-submit without loading each .umap (Asset Registry tags?).
- How should we handle new Levels, Level Instances/sublevels, and orphaned __ExternalActors__ files?

Acceptance
- CL modifying an actor of a non-WP Level outside the excluded folders → blocking ERROR.
- Same CL under Developers/ → passes.
```

Veux-tu que je regarde les transcripts/scripts présents dans le workspace (`Phil_IncludeInHLOD`, `generate_changelist_report.py`) au cas où il y aurait déjà des conventions internes à réutiliser dans le message ?

I see this isn't the actual codebase—just scripts and transcripts related to the Sundance and HLOD project. The user wants me to review and improve a Slack message to David, so I'll assess whether the request is relevant and suggest technical improvements, responding in French.
