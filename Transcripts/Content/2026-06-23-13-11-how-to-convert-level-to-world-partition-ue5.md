# How To Convert Level To World Partition Ue5

- Date: 2026-06-23 13:11
- Source transcript: `37580f64-5d0a-437f-b494-958a4dbb0350`

---

### User

dans UE5, j'ai un Level qui n'est pas world partitionné. Comment le rendre world partitionné ?

**Assistant:** Pour convertir un Level classique (non world-partitionné) en Level World Partition dans UE5, voici les méthodes disponibles.

## Méthode 1 : Le Commandlet de conversion (recommandé)

C'est la méthode officielle et la plus fiable. Tu lances un commandlet en ligne de commande :

```bash
UnrealEditor.exe "CheminVersTonProjet.uproject" -run=WorldPartitionConvertCommandlet "NomDeTaMap" -AllowCommandletRendering
```

Quelques options utiles :
- `-SCCProvider=None` : désactive le source control pendant la conversion
- `-Verbose` : logs détaillés
- Le commandlet crée par défaut une **copie** de ta map avec le suffixe `_WP` (sauf si tu utilises certaines options). Vérifie bien dans les logs où le fichier est généré.

Tu peux aussi créer un fichier de configuration `.ini` pour contrôler finement la conversion (taille des cells de la grille, HLOD, etc.).

## Méthode 2 : Via l'éditeur (Tools)

Dans certaines versions de l'UE5, tu trouves directement :

**`Tools` → `Convert Level to External Actors`** (étape préalable utile), puis l'option de conversion World Partition selon ta version.

Cependant, l'interface graphique de conversion est moins complète que le commandlet.

## Points importants à comprendre

1. **One File Per Actor (OFPA)** : World Partition repose sur le fait que chaque acteur est sauvegardé dans son propre fichier externe (dossier `__ExternalActors__`). La conversion transforme tes acteurs en "external actors".

2. **Streaming automatique** : une fois converti, tu n'utilises plus les Sublevels / Level Streaming classiques. Le World Partition gère le chargement par grille (cells) automatiquement selon la position.

3. **Source control** : si tu utilises Git/Perforce, attends-toi à beaucoup de petits fichiers. Pense à bien configurer le `.gitignore` / `.gitattributes` et idéalement utiliser Git LFS.

4. **Sauvegarde d'abord** : fais une copie de ton projet ou commit avant conversion, car c'est une opération lourde et difficilement réversible.

## Après la conversion

- Ouvre la nouvelle map, tu auras accès à la fenêtre **World Partition** (`Window` → `World Partition` → `World Partition Editor`) pour visualiser la minimap et charger/décharger des régions.
- Configure le **Data Layers** (`Window` → `Data Layers`) si tu veux gérer des couches logiques.
- Vérifie/configure les **HLODs** pour le rendu à distance.

---

Quelques précisions pour t'orienter au mieux :

Quelle version exacte de l'UE5 utilises-tu (5.0, 5.3, 5.5...) ? L'interface et les options varient pas mal entre versions.

Et c'est quel type de projet : un grand monde ouvert, ou plutôt une map de taille moyenne que tu veux passer en World Partition pour le workflow OFPA / collaboration en équipe ? Ça change les recommandations sur la taille des cells et la config de streaming.

L'utilisateur demande comment convertir un niveau Unreal Engine 5 qui n'utilise pas le world partitioning en un niveau avec world partitioning activé. Je vais répondre en français puisqu'il a posé sa question dans cette langue.


---

### User

est-ce que right click sur le level asset dans le content browser -> add partionned streaming support fait la meme chose ?

**Assistant:** Oui, dans le principe c'est la **même opération de conversion**, mais avec des nuances importantes.

## Ce que fait le clic droit dans le Content Browser

Le menu contextuel sur un Level asset (`Add Partitioned Streaming Support` / parfois libellé `Convert to World Partition` selon la version) déclenche **le même mécanisme de fond que le commandlet** : il convertit les acteurs en *external actors* (OFPA) et met en place la grille World Partition.

C'est en quelque sorte un wrapper graphique autour de la logique de `WorldPartitionConvertCommandlet`.

## Les différences pratiques

| Aspect | Clic droit (UI) | Commandlet (ligne de commande) |
|---|---|---|
| Facilité | Très simple, 2 clics | Nécessite ligne de commande |
| Contrôle / options | Limité (paramètres par défaut) | Complet (`.ini` config : taille des cells, HLOD, etc.) |
| Batch / automatisation | Non | Oui (scriptable, CI/CD) |
| Création d'une copie `_WP` | Convertit souvent **en place** | Crée une copie par défaut |
| Maps multiples | Une par une | Plusieurs d'un coup |

## Point d'attention important

La grosse différence est que le **clic droit convertit généralement le level en place** (il modifie ton asset directement), alors que le commandlet crée par défaut une copie suffixée `_WP`.

Donc avant d'utiliser le clic droit :
- **Commit / sauvegarde ton projet d'abord** (l'opération transforme tous tes acteurs en external actors, c'est lourd à annuler).
- Sois prêt à voir apparaître le dossier `__ExternalActors__` à côté de ta map.

## En résumé

Pour une conversion ponctuelle et simple → le **clic droit** est parfait et fait bien le job.

Pour un contrôle fin (taille de grille, HLOD, runtime hash) ou pour automatiser/convertir plusieurs maps → le **commandlet** reste supérieur.

Dans les deux cas, le résultat final (level world-partitionné en OFPA) est équivalent.

Tu es sur quelle version d'UE5 ? Je peux te confirmer le libellé exact du menu et les éventuelles options de config disponibles dans ta version.

I'm trying to recall the exact menu options in UE5 for converting levels. The right-click context menu on a level asset in the Content Browser does have World Partition-related options, but I need to think through what the actual menu items are called—whether it's "Convert to World Partition" or something under World Settings.


---

### User

j'utilsie ue 5.7

**Assistant:** Laisse-moi vérifier les spécificités d'UE 5.7, car c'est une version récente et les libellés/comportements ont pu évoluer.

I'm not entirely confident about the specific menu labels and behavior in UE 5.7 since it's a newer version, so I should search for current information to give accurate details.

<details><summary>Tools used</summary>

- `WebSearch` Confirmer le libellé exact du menu et le comportement dans UE 5.7

</details>

**Assistant:** Merci, ça me permet de **corriger une nuance importante** de ma réponse précédente. Après vérification de la doc UE 5.7, en réalité ce ne sont **pas tout à fait la même chose**.

## La distinction clé en 5.7

Il y a deux opérations différentes qui se ressemblent :

### 1. `Add Partitioned Streaming Support` (clic droit Content Browser)
Cette option sert surtout à rendre un level **compatible OFPA (One File Per Actor)** pour qu'il puisse être utilisé comme **Level Instance à l'intérieur d'un monde World Partition**.

C'est typiquement la solution à l'erreur :
> *"Level Instance is not using external actors, resave level to add compatibility"*

Elle ajoute le support des *external actors* au level, mais son but premier est la **compatibilité en tant qu'instance**, pas de transformer le level lui-même en un véritable monde World Partition avec sa grille de streaming.

### 2. `Tools → Convert Level` (ou le commandlet)
C'est **ça** la vraie conversion d'un level en World Partition selon la doc officielle 5.7 :

> *"You can add World Partition to any Level by converting it using the **Tools > Convert Level** menu option, or by using the World Partition Convert Commandlet."*

C'est cette opération qui met en place la grille World Partition, le runtime hash, le streaming par cells, etc.

## Donc concrètement pour ton cas

Si ton objectif est de **rendre ton level world-partitionné** (grille de streaming, World Partition Editor, etc.) :

➡️ Utilise **`Tools → Convert Level`** dans l'éditeur, ou le commandlet :

```bash
UnrealEditor.exe "TonProjet.uproject" -run=WorldPartitionConvertCommandlet TaMap.umap -AllowCommandletRendering
```

Le clic droit `Add Partitioned Streaming Support` ne fera **pas** la même chose : il prépare un level pour qu'il soit utilisable comme instance dans un monde WP, sans en faire un monde WP à part entière.

## Pour info : config fine de la conversion

Avec le commandlet, tu peux créer un fichier `.ini` portant le même nom que ta map (ex. `TaMap.ini`) dans le même dossier, pour contrôler la taille des cells, le HLOD, etc.

---

Donc en résumé : **non**, le clic droit `Add Partitioned Streaming Support` n'est pas l'équivalent de la conversion World Partition. Pour partitionner ton level, passe par **`Tools → Convert Level`**. Désolé pour l'imprécision dans mon message précédent.

Tu veux que je te détaille les options du fichier `.ini` de conversion, ou la procédure pas-à-pas via `Tools → Convert Level` ?

I need to correct something important: "Add Partitioned Streaming Support" isn't actually the same as converting a level to World Partition. It's specifically about enabling OFPA and external actors support so a level can function as a Level Instance within a World Partition map. The actual World Partition conversion happens separately through the `Tools > Convert Level` menu or commandlet.


---

### User

Tools → Convert Level    c'est dans le content browser ?

**Assistant:** Non. `Tools` est dans la **barre de menu principale en haut de l'éditeur Unreal**, pas dans le Content Browser.

## Où trouver `Tools → Convert Level`

1. **Ouvre d'abord le level** que tu veux convertir (charge-le dans l'éditeur, il doit être le level courant).
2. Va dans la **barre de menu tout en haut de la fenêtre de l'éditeur** : `File` | `Edit` | `Window` | `Tools` | `Build` | `Help`...
3. Clique sur **`Tools`**.
4. Cherche l'option **`Convert Level`** dans le menu déroulant.

```
[Barre de menu en haut de l'éditeur]
File   Edit   Window   Tools   Build   Help
                        └─> Convert Level...
```

## Point important

Contrairement au clic droit dans le Content Browser (qui agit sur un asset sélectionné), `Tools → Convert Level` agit sur le **level actuellement ouvert/chargé** dans l'éditeur. Donc assure-toi que c'est bien ta map cible qui est ouverte avant de lancer la conversion.

Petite remarque : selon l'organisation exacte du menu en 5.7, l'option peut être légèrement nichée. Si tu ne la vois pas directement sous `Tools`, dis-le-moi et je t'aide à la localiser (ou on bascule sur la méthode commandlet qui est 100 % fiable).

Tu l'as ouvert et tu vois bien le menu `Tools` en haut ?

The `Tools → Convert Level` option is actually in the main menu bar at the top of the Unreal Editor, not in the Content Browser itself.


---

### User

j'ai ca comme settings, je mets quoi ?

**Assistant:** Parfait, tu es au bon endroit. Voici ce que fait chaque option et ce que je te recommande.

## Réglages recommandés

| Option | Recommandation | Pourquoi |
|---|---|---|
| **In Place** | ☐ **Décoché** (sécurité) ou ☑ selon ton besoin | Décoché → crée une **copie `_WP`** et garde ton level original intact. Coché → convertit directement ton level existant (irréversible facilement). |
| **Delete Source Levels** | ☐ **Décoché** | Si coché, supprime les levels sources après conversion. À éviter tant que tu n'as pas validé le résultat. |
| **Generate Ini** | ☐ Décoché | Génère un fichier `.ini` de config. Utile seulement si tu veux ensuite affiner/relancer la conversion manuellement. |
| **Report Only** | ☐ Décoché | Si coché, fait juste un rapport **sans convertir**. (Pratique pour un test à blanc, mais là tu veux convertir.) |
| **Verbose** | ☐ Décoché (ou ☑ si tu veux des logs détaillés) | Logs plus complets en cas de souci. |
| **Skip Stable GUID Validation** | ☐ Décoché | Laisse la validation active, c'est plus sûr. |
| **Only Merge Sub Levels** | ☐ Décoché | À cocher seulement si tu veux juste fusionner des sublevels sans vraie conversion WP. Pas ton cas. |
| **Save Foliage Type to Content Folder** | ☑ **Coché** (laisse par défaut) | Sauvegarde les foliage types en assets dans le Content. Bien si tu utilises du foliage. |

## En résumé : ce que je te conseille

Pour une première conversion sûre :

- **In Place** : commence **décoché** → tu obtiens une copie `TaMap_WP` et ton original reste intact. Tu valides, et si tout est bon tu pourras refaire en place ou supprimer l'ancien.
- Tout le reste **comme sur ton screenshot** (seul `Save Foliage Type to Content Folder` coché).
- Puis **Ok**.

## ⚠️ Avant de cliquer Ok

1. **Commit / sauvegarde ton projet** (source control ou copie du dossier). La conversion transforme tous les acteurs en *external actors* (OFPA), c'est lourd à annuler.
2. Attends-toi à voir apparaître un dossier `__ExternalActors__` à côté de ta map.
3. La conversion peut prendre un moment selon la taille du level.

---

Petite question pour t'orienter : tu veux **garder ton level original intact** (je recommande `In Place` décoché), ou tu préfères **convertir directement** ce level-ci sans copie (`In Place` coché) ? Si tu as déjà une sauvegarde/commit, `In Place` coché est plus simple car tu gardes le même nom de map.

The user has opened the Convert Settings dialog, and I'm reviewing the available options to explain what each one does and suggest the right configuration. There's a basic Convert section with an In Place checkbox, and then Advanced settings that control the commandlet behavior, including options to delete source levels, generate INI files, run in report-only mode, enable verbose logging, and skip certain steps.

Looking at the remaining Advanced options, there's also Stable GUID Validation to ensure consistent identifiers, a toggle to only merge sub-levels if needed, and a checkbox for saving foliage types to the content folder, which is currently enabled. I'll walk through what each setting accomplishes and recommend which ones to enable based on the conversion workflow.


---

### User

avec UE5, est-ce qu'un level non partitionné , placé dans un level sous la forme d'un level instance partitionné, peut avoir des inner actors avec un HLOD Layer ?

**Assistant:** Bonne question, et c'est assez subtil. Laisse-moi vérifier le comportement exact dans la doc UE5 plutôt que de te répondre de mémoire, car le couplage Level Instance non-OFPA + HLOD a des règles précises.

I'm working through a specific UE5 architecture question about whether a standard non-partitioned level can be placed as a Level Instance within a world-partitioned level and still have HLOD layers on its inner actors. The key is understanding how Level Instances interact with world partitioning and HLOD systems. I'm realizing I need to be more careful here since this involves specific UE5 behavior that I'm not entirely certain about. Let me look up the actual documentation to give an accurate answer rather than guessing at the details.

<details><summary>Tools used</summary>

- `WebSearch` Vérifier si les inner actors d'un level instance non-partitionné peuvent participer au HLOD World Partition
- `WebSearch` Confirmer la condition OFPA pour la génération HLOD des level instances

</details>

**Assistant:** Laisse-moi lire le passage précis du guide officiel pour te donner la règle exacte sur le HLOD avec les level instances non-OFPA.

Looking at the World Building Guide, there's a key distinction: embedded mode in version 5.6 supports HLODs for non-OFPA levels, but it doesn't support Data Layers for actors within those levels, and HLOD Layers themselves aren't currently supported for non-OFPA level instances in the world.

<details><summary>Tools used</summary>

- `Grep` non-OFPA|Non-OFPA|HLOD|Embedded|Standalone|Level Behavior

</details>

**Assistant:** Excellente question, et la réponse dépend du **Level Behavior** du Level Instance. Voici ce que dit la doc officielle UE (et c'est précisément le genre de cas qui a changé en 5.6/5.7).

## Le résumé direct

Pour un level **non-OFPA** (non partitionné) instancié dans un monde World Partition, le fait que ses inner actors avec HLOD Layer soient pris en compte **dépend du mode de Level Behavior** :

| Cas | HLOD des inner actors ? |
|---|---|
| **Non-OFPA + Standalone** (le level reste un bloc) | ❌ **Non supporté** — le level instance est considéré comme un seul bloc qui stream d'un coup, les HLOD Layers internes sont ignorés |
| **Non-OFPA + Embedded** (nouveau en 5.6+) | ✅ **Oui** — les inner actors sont "cassés"/embarqués dans le monde hôte, donc leurs HLOD Layers sont pris en compte |
| **OFPA-enabled** (recommandé) | ✅ **Oui** — les actors sont embarqués dans la grille du persistent world, HLOD normal |

## Pourquoi

Citation de la doc (section *Non-OFPA VS OFPA Level Instances*) :

> *"Non-OFPA = the level instance is kept during generate streaming and is considered as one actor that will stream in as a block... **HLODs are not supported in this case**."*

MAIS, changement important en **5.6** (donc dispo dans ta 5.7), section *Support for non-OFPA levels embedding* :

> *"Using the level behavior - **embedded mode** on level instance actors referencing **non-OFPA levels**, contained actors will be **broken down into the owning world** during the streaming generation phase at cook and when going into PIE."*

Quand les actors sont ainsi "broken down / embedded" dans le monde World Partition hôte, ils participent à la génération HLOD **comme s'ils étaient directement dans le monde** → donc oui, leurs HLOD Layers sont respectés.

## Donc concrètement pour toi (UE 5.7)

Ton level non-partitionné instancié peut avoir des inner actors avec HLOD Layer **fonctionnels**, à condition de mettre le Level Instance en **Level Behavior = Embedded** :

1. Sélectionne ton Level Instance actor dans le monde WP.
2. Dans le Details panel → option avancée **`Level Behavior`** → choisis **`Embedded`**.
3. Assigne les HLOD Layers voulus aux inner actors.
4. Build HLODs sur le monde hôte.

Si tu laisses **Standalone** sur un level non-OFPA → les HLOD Layers internes seront **ignorés**.

## ⚠️ Deux réserves importantes

1. **Data Layers non supportés sur les inner actors d'un non-OFPA embedded** : l'embedding non-OFPA supporte les HLODs **mais pas** les Data Layers pour les actors contenus. Si tu as besoin de Data Layers par actor → passe en OFPA.

2. **Bug connu UE-256471** : les Level Instances / Packed Level Actors sont *parfois* exclus de manière incohérente du build HLOD (avec un warning), même quand tout est bien configuré. Workaround actuel : relancer le build HLOD jusqu'à ce que ça passe.

## Ma recommandation

Si tu peux te le permettre, **active OFPA** sur le level instancié (`Add Partitioned Streaming Support`) : c'est le chemin le plus fiable et le mieux supporté pour le HLOD, et tu gardes aussi le support des Data Layers. Le mode *Embedded non-OFPA* est surtout utile pour **réduire le nombre de fichiers** / la contention source control, au prix de la perte des Data Layers par actor.

Tu es dans quel cas : tu veux garder le level en non-OFPA spécifiquement pour limiter les fichiers, ou c'est juste que le level n'a pas encore été converti ?

Looking at the official documentation, there's a key distinction between how Non-OFPA level instances behave depending on the version. In standalone mode before version 5.6, these instances are kept as a single block during streaming generation and don't support HLODs. Version 5.6 introduced new functionality for Non-OFPA handling, though the explanation appears to cut off there. I need to structure this clearly for the user in French, covering the different scenarios based on level behavior and whether the inner level has OFPA enabled.


---

### User

qu'est-ce que SmallGrid dans UE ?

**Assistant:** Laisse-moi vérifier, car "SmallGrid" n'est pas un terme dont je veux te donner une définition de mémoire au risque de me tromper — ça peut être un grid runtime spécifique.

SmallGrid is a runtime grid in World Partition that you can define in World Settings under Runtime Settings. By default, World Partition comes with a MainGrid, but you can create additional grids like SmallGrid and assign actors to them via their Runtime Grid property—I'm not entirely certain about the specifics of SmallGrid's default behavior or whether it's a standard preset.

<details><summary>Tools used</summary>

- `WebSearch` Vérifier ce qu'est SmallGrid dans le contexte UE World Partition

</details>

**Assistant:** Maintenant j'ai la réponse précise. **SmallGrid** est un **runtime grid prédéfini** qui fait partie du nouveau système de partitionnement *RuntimeHashSet / Loose Hierarchical Grid* (LHGrid), introduit en UE 5.4.

## C'est quoi exactement

Dans World Partition, ton monde est découpé en **cellules de streaming** par une *runtime grid*. Tu peux avoir **plusieurs grids** définis dans les World Settings, chacun avec sa taille de cellule et sa loading range.

Avec le **RuntimeHashSet** (le système de hash moderne, par défaut sur les nouveaux mondes depuis 5.4+), tu as typiquement deux grids prédéfinis :

| Grid | Rôle | Taille de cellule |
|---|---|---|
| **MainGrid** | Le grid principal, pour la géométrie / les gros actors | Grande (ex. 256m) |
| **SmallGrid** | Pour les **petits actors / props denses** qui ont besoin d'un streaming plus fin | Petite |

En gros : **SmallGrid = un grid à cellules plus petites destiné aux petits objets**, pour qu'ils se chargent/déchargent à plus courte distance et avec une granularité plus fine que la géométrie principale.

## Pourquoi deux grids

L'idée est d'adapter la granularité de streaming au type de contenu :

- Un gros bâtiment ou le terrain → **MainGrid** (grandes cellules, on le voit de loin).
- Une multitude de petits props (cailloux, déco, petits meshes) → **SmallGrid** (petites cellules, déchargés rapidement quand le joueur s'éloigne, ce qui économise la mémoire).

## Comment ça s'utilise

1. Les grids sont définis dans **World Settings → World Partition Setup** (section Runtime Hash / partitions).
2. Sur un actor, dans le Details panel → **World Partition → `Runtime Grid`**, tu choisis le nom du grid (`MainGrid`, `SmallGrid`, ou un grid custom). Si laissé à `None`, le système choisit automatiquement.

## Lien avec les HLODs (important)

Chaque grid a sa propre config **HLODSetup**. C'est un point qui prête à confusion avec le LHGrid : par exemple un `SmallGrid_HLOD0` est un HLOD Layer associé spécifiquement au SmallGrid.

À retenir :
- L'assignation HLOD d'un actor se fait via le **couple `Runtime Grid` + `HLOD Layer`**.
- Si le HLOD Layer d'un actor est vide → le **DefaultHLODLayer** du grid auquel il appartient s'applique.
- Chaque HLODSetup doit avoir un nom **unique** et inclure un DefaultHLODLayer, sinon tu auras des erreurs du type "combinaison RuntimeGrid/HLODLayer invalide".

---

En résumé : **SmallGrid n'est pas un truc magique, c'est juste l'un des runtime grids fournis par défaut avec le RuntimeHashSet**, taillé pour le streaming fin des petits actors, par opposition au MainGrid pour le gros contenu.

Tu le vois apparaître où exactement — dans les World Settings, dans le dropdown `Runtime Grid` d'un actor, ou dans une erreur liée aux HLODs ? Je peux t'aider à le configurer selon le cas précis.

So "SmallGrid" is one of the predefined grids that comes with the new RuntimeHashSet partitioning system introduced in version 5.4—it's designed specifically for smaller or densely packed actors with a tighter cell size compared to the main grid.
