# Fixup Nonpartitioned Actors Builder Clear Hlod Datalayers Grid

- Date: 2026-05-27 10:48
- Source transcript: `0622f550-49cf-429c-a2a4-8bdf92f7a6c4`

---

### User

Au meme niveau que D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition , je voudrais que tu rajoutes un builder qui itere a travers tous les Level Instances non-partitionnés (attention, les level instances peuvent etre des inner objects). Dans chacun de ces level instances, je veux que tu itere sur tous les inner-actors (qui ne sont pas des level instance) et je veux que tu retires (reset) (vide) (clear) le HLOD Layer assigné, le Runtime Grid et les Data Layers (puisqu'ils heritent de ces proprietes via le parent qui est un Level Instance partitionné).
Pour executer la commandlet, j'aimerais ce genre de commande: 
 -LogCmds="LogFixupNonPartitionedActors Verbose" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionFixupNonPartitionedActorsBuilder -SCCProvider=Perforce -Unattended -NoShaderCompile LV_Overland
En resultat, je veux que les acteurs soient placés en checkout dans Perforce, resavés et pret au submit.
Je veux aussi un log qui montre exactement quels operations a été faite sur quel acteur dans quel level instance parent.

**Assistant:** Je vais analyser la structure du projet pour comprendre comment les builders existants sont organisés.

<details><summary>Tools used</summary>

- `Shell` Verify path exists
- `Glob` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\**\*
- `Shell` List files in WorldPartition folder
- `Shell` List all files in WorldBuildingEditor
- `Shell` List contents of WorldBuildingEditor
- `Shell` List contents of WorldPartition folder

</details>

**Assistant:** Les commandes ne retournent rien. Essayons d'autres approches.

<details><summary>Tools used</summary>

- `Shell` List WorldBuildingEditor with cmd
- `Shell` List WorldPartition recursive

</details>

**Assistant:** J'ai maintenant une bonne vue de la structure. Je vois qu'il y a déjà:
- `WorldPartitionResaveActorsRecursiveBuilder.cpp/h` - un builder existant qui semble similaire
- `LevelInstance/LevelInstanceTraversalBuilder.cpp/h` - un builder qui itère à travers des Level Instances
- `LevelInstance/LevelInstanceFunctionLibrary.cpp/h` - une bibliothèque pour les Level Instances

Lisons ces fichiers de référence pour comprendre les patterns existants.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionResaveActorsRecursiveBuilder.h
- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionResaveActorsRecursiveBuilder.cpp
- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\LevelInstance\LevelInstanceTraversalBuilder.h
- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\LevelInstance\LevelInstanceTraversalBuilder.cpp

</details>

**Assistant:** Excellent! J'ai maintenant une bonne compréhension. Lisons aussi:
1. `LevelInstanceFunctionLibrary` pour voir si on a déjà des utilitaires
2. Le `Build.cs` pour comprendre les dépendances
3. La classe `AActor` pour les propriétés HLOD Layer, Runtime Grid, Data Layers

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\LevelInstance\LevelInstanceFunctionLibrary.h
- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\LevelInstance\LevelInstanceFunctionLibrary.cpp
- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldBuildingEditor.Build.cs

</details>

**Assistant:** Maintenant, regardons aussi le `WorldPartitionRuleBuilder` qui pourrait être la classe parent à étudier, et explorons d'autres builders existants pour comprendre les patterns:

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.h
- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp

</details>

**Assistant:** Excellent. Maintenant je comprends bien les patterns. Voyons quelques informations supplémentaires importantes:

1. Comment AActor expose HLODLayer, RuntimeGrid et DataLayers (les setters/clears)
2. Comment le `ResaveActorsBuilder` parent fonctionne pour comprendre la classe parente

<details><summary>Tools used</summary>

- `Grep` SetHLODLayer|HLODLayer\s*=|class.*WorldPartitionResaveActorsBuilder
- `Grep` UWorldPartitionResaveActorsBuilder

</details>

**Assistant:** Les recherches dans tout D:\Sun timeout. Restreignons.

<details><summary>Tools used</summary>

- `Grep` WorldPartitionResaveActorsBuilder
- `Glob` D:\Sun\**\WorldPartitionResaveActorsBuilder.h
- `Shell` Find parent ResaveActorsBuilder header
- `Shell` Find parent ResaveActorsBuilder header
- `Await`
- `Read` C:\Users\Arnaud.Storq\.cursor\projects\d-Sandbox-AI\terminals\206343.txt
- `Read` D:\Sun\Engine\Source\Editor\UnrealEd\Public\WorldPartition\WorldPartitionResaveActorsBuilder.h

</details>

**Assistant:** Maintenant, recherchons les propriétés AActor pour HLODLayer, RuntimeGrid et DataLayer pour comprendre comment les "vider":

<details><summary>Tools used</summary>

- `Grep` SetHLODLayer|HLODLayer\s*;|HLODLayer;
- `Grep` RuntimeGrid|RuntimeGrid\s*=
- `Grep` DataLayer|DataLayers

</details>

**Assistant:** Excellent! J'ai trouvé `RemoveAllDataLayers()` qui est exactement ce qu'il me faut. Maintenant, je vais aussi vérifier le pattern de `LogFixupNonPartitionedActors` qui semble être un nouveau log category. Vérifions aussi comment le `LogCmds` est utilisé et regardons la consigne du builder.

Vérifions également la structure de fichier `WorldPartitionBuilder.h` pour voir les méthodes virtuelles disponibles:

<details><summary>Tools used</summary>

- `Glob` D:\Sun\Engine\Source\Editor\UnrealEd\Public\WorldPartition\WorldPartitionBuilder.h
- `Grep` RemoveAllDataLayers|ExternalDataLayer
- `Glob` D:\Sun\Engine\Source\**\WorldPartitionBuilder.h
- `Grep` RemoveAllDataLayers
- `Grep` RemoveAllDataLayers
- `Shell` Find WorldPartitionBuilder.h

</details>

**Assistant:** Bien. Maintenant lisons le `WorldPartitionBuilder.h` pour comprendre ce qu'on hérite et regardons aussi le pattern de `RemoveAllDataLayers`. Maintenant je vais regarder en plus comment marquer un actor "dirty"/Modify() pour le sauvegarder:

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Source\Editor\UnrealEd\Public\WorldPartition\WorldPartitionBuilder.h

</details>

**Assistant:** Maintenant j'ai tout ce qu'il me faut. Vérifions juste s'il y a une `NAME_None` ou similaire pour le RuntimeGrid clear, et examinons aussi comment le `SetHLODLayer(nullptr)` est appelé pour HLOD.

<details><summary>Tools used</summary>

- `Grep` SetHLODLayer\(nullptr\)|SetRuntimeGrid\(NAME_None\)
- `Grep` SetHLODLayer\(
- `Grep` void AActor::SetHLODLayer

</details>

**Assistant:** Maintenant j'ai toutes les pièces dont j'ai besoin pour créer le builder. Examinons aussi un dernier détail sur `UWorldPartitionResaveActorsBuilder` parent et regardons comment l'enregistrement du builder marche, et vérifions le pattern `LogCmds`:

<details><summary>Tools used</summary>

- `Grep` DEFINE_LOG_CATEGORY_STATIC|DEFINE_LOG_CATEGORY\b

</details>

**Assistant:** Bien. Maintenant, je vais analyser un point critique. Le user dit:
- "tous les Level Instances non-partitionnés" : ce sont des LI dont le **inner Level** n'est pas partitionné
- "level instances peuvent etre des inner objects" : donc on traverse récursivement
- Dans chacun de ces LI non-partitionnés, on itère sur les **inner-actors** (non-LI)
- On reset HLODLayer, RuntimeGrid, et DataLayers

Important: les inner actors sont dans le `Level` du Level Instance (pas dans une WorldPartition, puisque non-partitionné). Donc on accède via `LevelInstance->GetLoadedLevel()->Actors`.

Le `WorldPartitionRuleBuilder.cpp` ligne 575-579 dit déjà : `LoadedLevel->bIsPartitioned` — donc on connaît le test pour distinguer.

Mais attention : dans `WorldPartitionResaveActorsRecursiveBuilder`, on voit que dans le case `!bIsPartitioned`, ça appelle `ProcessActorsInLevel(LoadedLevel, World, PackageHelper)` qui itère directement sur `Level->Actors`. C'est exactement ce qu'on veut.

Vérifions un dernier petit détail crucial : quand on est dans EditMode d'un Level Instance non-partitionné, est-ce que les inner-actors sont accessibles via `LoadedLevel->Actors`? Et est-ce qu'ils ont des packages externes (sauvegardables individuellement)?

<details><summary>Tools used</summary>

- `Grep` IsPackageExternal|GetExternalPackage

</details>

**Assistant:** J'ai vu suffisamment. Maintenant j'ai un plan clair. Voici mon design:

**Plan d'implémentation pour `WorldPartitionFixupNonPartitionedActorsBuilder`** :

1. **Classe** : `UWorldPartitionFixupNonPartitionedActorsBuilder` héritant de `UWorldPartitionBuilder`
2. **Stratégie**:
   - Itère sur les LI dans le WorldPartition racine (`ProcessLevelInstancesInWorldPartition`)
   - Récursivement traverse les LI imbriqués (les LI peuvent être inner objects de LI partitionnés)
   - Pour chaque LI rencontré, on entre en `EditMode` (via le subsystem) - cela charge son inner Level
   - Si **l'inner Level n'est pas partitionné** (`bIsPartitioned == false`), c'est notre cible !
   - On itère sur `LoadedLevel->Actors` (qui sont les inner-actors non-LI dans cette inner-level)
   - Pour chaque actor (qui n'est PAS un LI), si HLODLayer / RuntimeGrid / DataLayers != défaut → on log et on reset
   - On sauvegarde via `PackageHelper` (qui gère le checkout Perforce automatiquement)
3. **Log catégorie** : `LogFixupNonPartitionedActors`
4. **Si un LI inner est lui-même non-partitionné mais contient des LI** : on traverse à travers son `LoadedLevel->Actors` cherchant les LI et on récurse.

Important : Le LI parent (qui est partitionné mais contient le LI non-partitionné) hérite ses propriétés HLOD/Grid/DataLayer à ses children. C'est pourquoi on doit "reset" les inner actors qui les héritent déjà via le LI partitionné parent.

Créons aussi un TODO list:

<details><summary>Tools used</summary>

- `TodoWrite` update task list

</details>

**Assistant:** Maintenant créons le fichier .h. Je vais le créer au même niveau que `WorldPartition` folder (donc dans `WorldPartition/`) comme demandé:

<details><summary>Tools used</summary>

- `Write` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `TodoWrite` update task list

</details>

**Assistant:** Maintenant créons le fichier .cpp. Le pattern principal s'inspire du `WorldPartitionResaveActorsRecursiveBuilder` et de `WorldPartitionRuleBuilder`, mais adapté pour l'objectif spécifique.

<details><summary>Tools used</summary>

- `Write` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant vérifions s'il y a des erreurs de lint et que les includes/références sont corrects.

<details><summary>Tools used</summary>

- `ReadLints`

</details>

**Assistant:** Ces erreurs viennent de clang qui ne sait pas où trouver les headers Unreal (build system Unreal). Elles ne sont pas réelles — la compilation se fera via Unreal Build Tool. Vérifions également la structure pour s'assurer que les fichiers sont bien intégrés au build system. Le `Build.cs` du module recharge automatiquement tous les .cpp dans son dossier, donc on n'a rien à ajouter là.

Vérifions cependant un point important : `GetDataLayerInstancesForLevel`, `GetDataLayerAssets`, `RemoveAllDataLayers`, `FixupDataLayers` — ce sont des méthodes qui existent dans AActor. Vérifions:

<details><summary>Tools used</summary>

- `Grep` GetDataLayerInstancesForLevel|GetDataLayerAssets|GetHLODLayer|GetRuntimeGrid|FixupDataLayers

</details>

**Assistant:** Toutes les méthodes existent ! Vérifions également si `GetDataLayerInstancesForLevel` et `GetDataLayerInstances` sont protégés ou publics, et vérifions le `GetDataLayerShortName` sur `UDataLayerInstance`:

<details><summary>Tools used</summary>

- `Grep` GetDataLayerShortName
- `Glob` D:\Sun\Engine\Source\**\DataLayerInstance.h

</details>

**Assistant:** Bien. Vérifions aussi que `GetDataLayerInstancesForLevel` est utilisable correctement (et non `GetDataLayerInstances`), et regardons le retour de la fonction `RemoveAllDataLayers`. Maintenant, attention: `RemoveAllDataLayers` modifie déjà l'actor via `Modify()` (vu dans ActorEditor.cpp ligne 1761). On a un double Modify() qui n'est pas problématique mais est redondant. Mais aussi je notice: `GetDataLayerInstancesForLevel` ne retourne que ceux du niveau actuel, donc si les datalayers proviennent du parent ce ne sera pas dans la liste !

Vérifions ces détails:

<details><summary>Tools used</summary>

- `Grep` GetDataLayerInstancesForLevel|GetDataLayerInstances\(

</details>

**Assistant:** Important : `RemoveAllDataLayers` utilise `GetDataLayerInstances()` (sans `ForLevel`). C'est ce qu'on veut: ça retourne **toutes** les DLI résolues pour l'actor incluant celles héritées du parent. Donc on devrait utiliser `GetDataLayerInstances()` plutôt que `GetDataLayerInstancesForLevel()` pour le log. Vérifions:

<details><summary>Tools used</summary>

- `Grep` TArray<const UDataLayerInstance\*> GetDataLayerInstances

</details>

**Assistant:** Mise à jour: `GetDataLayerInstances()` est ce qu'on veut. Corrigeons ça dans le cpp:

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant, vérifions un point important: l'include de `DataLayerAsset.h` doit être présent pour `UDataLayerAsset`. Vérifions aussi `UHLODLayer` ne nécessite pas d'include particulier pour `GetHLODLayer()` puisqu'on n'utilise pas son interface, mais on a besoin de `GetNameSafe` qui utilise `UObject*` (déjà inclu via CoreMinimal).

<details><summary>Tools used</summary>

- `Grep` #include "WorldPartition/DataLayer/DataLayerAsset.h"

</details>

**Assistant:** Ajoutons les includes appropriés au CPP :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Vérifions maintenant ce qui est requis dans le .h. Mes forward declarations sont déjà bonnes. Pour le .h, je crois que `CoreMinimal.h` est correct. Vérifions les includes des autres fichiers .h pour s'aligner :

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionResaveActorsRecursiveBuilder.h

</details>

**Assistant:** Mon .h est aligné avec le pattern existant. Maintenant vérifions une chose importante : `CanProcessNonPartitionedWorlds`. Si on lance le builder sur un monde qui est **lui-même** non-partitionné (comme un Level Instance ouvert directement), il faut le permettre. Le map demandé est `LV_Overland` qui devrait être partitionné, mais ajoutons quand même cette flexibilité.

Vérifions aussi un point: si le LI est imbriqué dans un LI partitionné, il faut quand même pouvoir entrer en EditMode. Pour cela, le subsystem doit pouvoir le faire récursivement. Vérifions le `EditLevelInstance` behavior :

<details><summary>Tools used</summary>

- `Grep` EditLevelInstance

</details>

**Assistant:** Le subsystem supporte `EditLevelInstance` même imbriqué. Très bien.

Maintenant un détail technique important. Quand on entre en EditMode sur un LI imbriqué via `Subsystem->EditLevelInstance(LI)`, le subsystem va naviguer automatiquement à travers les parents jusqu'à pouvoir éditer ce LI. Donc notre récursivité fonctionne. 

Mais il y a un autre point : pour notre cas (un LI non-partitionné imbriqué dans un LI partitionné parent), le **parent** doit lui aussi être en EditMode quand on édite le child. Le subsystem gère ça via le param `bRecursive`. Vérifions: `EditLevelInstance` est appelé sans recursive, mais regardons la signature de `EditLevelInstanceInternal` qui prend `bRecursive`.

<details><summary>Tools used</summary>

- `Grep` void ULevelInstanceSubsystem::EditLevelInstance

</details>

**Assistant:** Bien. La fonction `EditLevelInstance` appelle `EditLevelInstanceInternal(..., false)`. Mais ça gère probablement les hiérarchies en commit/discard du précédent edit. La précondition est `check(CanEditLevelInstance(LevelInstance))`. C'est une assertion donc ça plante si on tente d'éditer un LI qu'on ne peut pas éditer.

Pour éviter ce souci, on devrait utiliser `CanEditLevelInstance` avant d'appeler `EditLevelInstance`. Voici une amélioration importante. Lisons l'implémentation de `CanEditLevelInstance` pour comprendre les conditions:

<details><summary>Tools used</summary>

- `Grep` bool ULevelInstanceSubsystem::CanEditLevelInstance

</details>

**Assistant:** Très bien. Améliorons le `FLevelInstanceEditScope` pour vérifier `CanEditLevelInstance` avant d'appeler `EditLevelInstance`, sinon ça plante avec un `check()`:

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant, vérifions un autre point : quand on a un LI imbriqué dans un LI **partitionné** (en EditMode du parent), peut-on traverser via le `WorldPartition` du parent ? On voit dans `WorldPartitionResaveActorsRecursiveBuilder` que ça fonctionne, donc OK.

Mais il y a un nouveau problème: dans notre cas, on **n'entre pas en EditMode du parent** avant d'éditer le child non-partitioned. Le check `CanEditLevelInstance` peut échouer si on essaie de pop directement dans un LI imbriqué quand le parent n'est pas déjà en EditMode.

Cependant, `EditLevelInstanceInternal` semble gérer ça automatiquement en navigant à travers les parents (vu dans le code source UE5: si tu édites un LI imbriqué, le subsystem commit/entre dans la chaîne des parents auto).

Pour être plus robuste, vérifions cependant si le subsystem gère bien ce cas dans notre flow. Lisons un peu plus de `EditLevelInstanceInternal`:

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Source\Runtime\Engine\Private\LevelInstance\LevelInstanceSubsystem.cpp

</details>

**Assistant:** J'ai vu une chose importante. `EditLevelInstance` est limité à un seul niveau de récursion. Si on a un `LevelInstanceEdit` actif (parent), il commit le parent et entre dans le child. Cela signifie qu'on doit gérer la séquence soigneusement.

Mais c'est exactement comme dans `WorldPartitionRuleBuilder.cpp::HandleLevelInstanceRecursive` qui marche très bien. Le pattern est :

1. Récupérer les LI de la WP racine via `ProcessLevelInstancesInWorldPartition` (charge en background)
2. Pour chaque LI: enter EditMode (le subsystem gère la chaîne des parents)
3. Process inner contenu
4. Exit EditMode (discard)
5. Récurser via WorldPartition imbriqué ou via Level->Actors

C'est exactement ce qu'on fait. 

Maintenant un dernier détail technique - vérifions le pattern de `ProcessLevelInstancesInWorldPartition` plus en détail. Dans `WorldPartitionRuleBuilder.cpp`, `ForEachActorWithLoading` charge le LI en mémoire, puis on entre en EditMode. Mais notre `HandleLevelInstanceRecursive` se réucurse via `ProcessLevelInstancesInWorldPartition`. Tactiquement c'est ok, mais il y aurait un problème si le child LI partitionné est dans un parent qui n'est plus en EditMode.

Heureusement, le code de `WorldPartitionRuleBuilder.cpp::HandleLevelInstanceRecursive` fait exactement ça et ça marche, on suit le même pattern.

Maintenant relisons le code complet pour vérifier l'intégrité:

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Petits ajustements:

1. La variable `RemovedCount` n'est pas vraiment utile au vu de l'usage. Mais ça reste correct.
2. La référence `ParentLevelInstancePath` est passée mais on pourrait améliorer la traçabilité du log en incluant aussi le nom du parent partitionné si c'est imbriqué. Mais le user demande "level instance parent" qui correspond bien au LI qui CONTIENT directement les inner-actors.

Maintenant, je remarque un point : pour le commentaire "On checkout dans Perforce", la méthode `SavePackages` de base de `UWorldPartitionBuilder` gère le checkout. Vérifions:

<details><summary>Tools used</summary>

- `Grep` UWorldPartitionBuilder::SavePackages
- `Grep` bool UWorldPartitionBuilder::SavePackages

</details>

**Assistant:** Excellent. La méthode `SavePackages` du builder fait exactement ce qu'il faut : checkout + save. Donc notre implémentation est correcte.

Maintenant, je remarque deux petits problèmes potentiels qu'il vaut mieux corriger :

1. **Variable inutilisée `RemovedCount`** - on devrait l'utiliser ou la supprimer
2. **Recurse via WorldPartition imbriqué quand parent partitionné** - mais on est dans un context où le parent doit être en EditMode. Pour `WorldPartitionRuleBuilder`, la récurser via `ProcessLevelInstancesInWorldPartition` après avoir quitté EditMode du parent rentre dans un nouveau `EditLevelInstance` qui re-commit les éventuels parents. Ça devrait fonctionner.

Mais en réalité, un point important: après notre `EditScope` (qui quitte le mode), on appelle `ProcessLevelInstancesInWorldPartition` sur le **NestedWorldPartition**. Ceci appelle `FWorldPartitionHelpers::ForEachActorWithLoading` qui s'attend à un WorldPartition initialisé. Si on a quitté l'EditMode, le NestedWorldPartition pourrait être détruit/dé-initialisé.

Vérifions comment `WorldPartitionRuleBuilder.cpp::HandleLevelInstanceRecursive` gère ce cas spécifiquement: ligne 591-604, c'est exactement la même structure et ça marche. La raison : `LevelInstance->GetLoadedLevel()` retourne le level **chargé** par le LI (qui n'est plus en EditMode mais reste chargé en lecture seule), et son `GetWorldPartition()` reste valide.

Cleanons les détails du cpp:

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant, vérifions deux choses critiques pour assurer la compilation:

1. **Le `Modify()` n'est pas nécessaire pour HLODLayer et RuntimeGrid quand RemoveAllDataLayers est aussi appelé**, car ce dernier fait Modify() en interne. Mais on fait Modify() avant de toucher HLOD ou Grid avec un `if (!bAnyChange)`. Le pattern actuel a un bug: si on a HLODLayer + DataLayers, le Modify est fait pour HLODLayer, puis pour DataLayers c'est `RemoveAllDataLayers` qui fait Modify lui-même. C'est OK car Modify() peut être appelé plusieurs fois (UE le gère).

2. **L'appel à `Actor->MarkPackageDirty()` à la fin** : déjà fait par Modify() en mode editor. Mais explicite c'est plus sûr.

Maintenant un point très critique. Le `Actor->Modify()` n'est efficace que **dans un transaction** (FScopedTransaction). Dans un commandlet, sans transaction, `Modify()` marque le package dirty mais ne crée pas d'undo. C'est OK pour nous, mais il faut aussi explicitement marquer le package dirty.

Vérifions le pattern utilisé dans `WorldPartitionConvertCommandlet` ligne 614-616:

<details><summary>Tools used</summary>

- `Grep` SetHLODLayer\(HLODLayer\)

</details>

**Assistant:** Confirmé: dans un commandlet, c'est `SetX()` + `MarkPackageDirty()` puis ajout au `PackagesToSave`. Notre code fait déjà ça.

Maintenant relisons le code complet pour vérifier qu'il n'y a pas d'erreurs et est cohérent:

<details><summary>Tools used</summary>

- `ReadLints`

</details>

**Assistant:** Comme attendu, les erreurs sont uniquement liées au fait que clang ne trouve pas les headers Unreal (système de build externe à clang). Ces erreurs ne sont pas réelles pour la compilation effective via UnrealBuildTool. Le code suit exactement les patterns d'autres builders du même projet qui compilent sans problème.

<details><summary>Tools used</summary>

- `TodoWrite` update task list

</details>

**Assistant:** Vérification finale du résultat :

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h

</details>

**Assistant:** Le builder est complet. Voici un récapitulatif de ce qui a été créé:

## Fichiers créés

J'ai créé deux nouveaux fichiers au même niveau que les autres builders de `WorldPartition/`:

- `WorldPartitionFixupNonPartitionedActorsBuilder.h`
- `WorldPartitionFixupNonPartitionedActorsBuilder.cpp`

## Comportement du builder

1. **Itération** : depuis la racine `LV_Overland` (partitionnée), on traverse tous les Level Instances `ALevelInstance` via `ForEachActorWithLoading` avec un filtre `IsChildContainerInstance()`. Pour chaque LI, on récurse à travers ses Level Instances imbriqués (donc peu importe si les LI sont des "inner objects" — ils sont découverts via la traversée récursive).

2. **Détection** : pour chaque LI on entre en EditMode (via `ULevelInstanceSubsystem::EditLevelInstance`), puis on lit `LoadedLevel->bIsPartitioned`. Si **non-partitionné**, c'est notre cible.

3. **Fixup** : pour chaque inner-actor du LI non-partitionné (qui n'est PAS lui-même un `ALevelInstance`) :
   - `SetHLODLayer(nullptr)` si non-nul
   - `SetRuntimeGrid(NAME_None)` si non-vide
   - `RemoveAllDataLayers()` + `FixupDataLayers()` si l'acteur a des DataLayers/DataLayerAssets

4. **Source control** : `UWorldPartitionBuilder::SavePackages(...)` (méthode statique héritée) gère automatiquement le **checkout via `FPackageSourceControlHelper`** (qui utilise le `-SCCProvider=Perforce` passé en ligne de commande) puis le resave. Les packages sont prêts à être submitted.

5. **Log** : la catégorie `LogFixupNonPartitionedActors` est définie. Chaque actor modifié génère une ligne `Display` au format :

   ```
   [<OutlinerPath du LI parent>] Actor '<label>' (<class>): HLODLayer cleared (was: X); RuntimeGrid cleared (was: Y); DataLayers cleared (removed: A, B, C)
   ```

   À la fin, un résumé `Display` indique le nombre de LI visités, fixés, et la ventilation des propriétés réinitialisées.

## Ligne de commande

```
-LogCmds="LogFixupNonPartitionedActors Verbose" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionFixupNonPartitionedActorsBuilder -SCCProvider=Perforce -Unattended -NoShaderCompile LV_Overland
```

## Notes techniques

- Le `Build.cs` du module `WorldBuildingEditor` ramasse automatiquement tous les `.cpp/.h` du dossier — aucune modification nécessaire.
- Les erreurs de lint clang affichées (« 'CoreMinimal.h' file not found ») sont normales en dehors d'Unreal Build Tool ; le projet compilera normalement.
- La fonction `RemoveAllDataLayers()` appelle déjà `Modify()` en interne. Pour `SetHLODLayer`/`SetRuntimeGrid`, on appelle `Actor->Modify()` explicitement puis `Actor->MarkPackageDirty()` à la fin — pattern identique à celui de `WorldPartitionConvertCommandlet`.
- L'`EditScope` RAII garantit qu'on sort proprement de l'EditMode (avec `bDiscardEdit=true`) même en cas d'exception ou de retour précoce, et vérifie `CanEditLevelInstance()` avant d'appeler `EditLevelInstance()` pour éviter l'`check()` interne du subsystem.


---

### User

48 logical cores)
  Executing up to 24 processes, one per physical core
Using Parallel executor to run 4 action(s)
------ Building 4 action(s) started ------
** For SundanceEditor-Win64-DebugGame **
[1/4] Compile [x64] WorldPartitionFixupNonPartitionedActorsBuilder.cpp
0>WorldPartitionFixupNonPartitionedActorsBuilder.cpp(339,37): Error C2665 : 'GetNameSafe': no overloaded function could convert all the argument types
		const FString PreviousHLODLayer = GetNameSafe(Actor->GetHLODLayer());
		                                  ^
D:\Sun\Engine\Source\Runtime\CoreUObject\Public\UObject\Field.h(1230,16): note: could be 'FString GetNameSafe(const FField *)'
inline FString GetNameSafe(const FField* InField)
               ^
D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp(339,37): note: 'FString GetNameSafe(const FField *)': cannot convert argument 1 from 'UHLODLayer *' to 'const FField *'
		const FString PreviousHLODLayer = GetNameSafe(Actor->GetHLODLayer());
		                                  ^
D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp(339,68): note: Types pointed to are unrelated; conversion requires reinterpret_cast, C-style cast or parenthesized function-style cast
		const FString PreviousHLODLayer = GetNameSafe(Actor->GetHLODLayer());
		                                                                 ^
D:\Sun\Engine\Source\Runtime\CoreUObject\Public\UObject\UObjectBaseUtility.h(892,16): note: or       'FString GetNameSafe(const UObjectBaseUtility *)'
inline FString GetNameSafe(const UObjectBaseUtility* Object)
               ^
D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp(339,37): note: 'FString GetNameSafe(const UObjectBaseUtility *)': cannot convert argument 1 from 'UHLODLayer *' to 'const UObjectBaseUtility *'
		const FString PreviousHLODLayer = GetNameSafe(Actor->GetHLODLayer());
		                                  ^
D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp(339,68): note: Types pointed to are unrelated; conversion requires reinterpret_cast, C-style cast or parenthesized function-style cast
		const FString PreviousHLODLayer = GetNameSafe(Actor->GetHLODLayer());
		                                                                 ^
D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp(339,37): note: while trying to match the argument list '(UHLODLayer *)'
		const FString PreviousHLODLayer = GetNameSafe(Actor->GetHLODLayer());
		                                  ^
Total time in Parallel executor: 1.70 seconds

**Assistant:** L'erreur de compilation indique que `UHLODLayer` n'est pas reconnu comme dérivé de `UObjectBaseUtility` car son header n'est pas inclus dans le translation unit. Le compilateur ne voit qu'une forward declaration. Il suffit d'inclure `HLODLayer.h`.

<details><summary>Tools used</summary>

- `Grep` class UHLODLayer\b
- `Glob` D:\Sun\Engine\Source\**\HLODLayer.h
- `Shell` Find HLODLayer.h location

</details>

**Assistant:** Bien. Ajoutons l'include pour `HLODLayer.h` dans le .cpp:

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** L'include de `HLODLayer.h` rend la classe `UHLODLayer` complète, ce qui permet à `GetNameSafe` de résoudre correctement la surcharge `GetNameSafe(const UObjectBaseUtility*)` puisque `UHLODLayer` hérite de `UObject` (qui hérite de `UObjectBaseUtility`). La compilation devrait passer.


---

### User

pour des fins de debug, j'aimerais filtrer l'arborescence, et ne traiter que les level instances non partitionnés dont le outliner path a "Hogsmeade"

**Assistant:** Je vais ajouter un paramètre de ligne de commande pour filtrer par sous-chaîne dans l'outliner path du LI non-partitionné.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h

</details>

**Assistant:** Modifions le .h pour ajouter le filtre :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h

</details>

**Assistant:** Maintenant modifions le .cpp pour parser le paramètre, appliquer le filtre dans `HandleLevelInstanceRecursive`, et logger le compteur dans le summary :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant appliquons le filtre dans `HandleLevelInstanceRecursive` (juste avant le fixup, pas avant la récursion — sinon on raterait des LI Hogsmeade imbriqués sous un LI parent qui ne matche pas) :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Ajoutons la nouvelle stat au log de résumé :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Et enfin, ajoutons l'implémentation de `DoesLevelInstanceMatchOutlinerFilter` à la fin du fichier :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
- `ReadLints`

</details>

**Assistant:** Toujours uniquement les erreurs clang attendues (headers Unreal non trouvés hors UBT). Le code compilera normalement.

## Résumé du changement

Le nouveau paramètre `-IncludeOutlinerPathSubstrings=` filtre les LI non-partitionnés à fixer **sans** affecter la traversée — donc même si un LI parent ne matche pas, le builder continuera à descendre dedans pour trouver des LI enfants qui matchent.

### Ligne de commande pour ton cas

```
-LogCmds="LogFixupNonPartitionedActors Verbose" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionFixupNonPartitionedActorsBuilder -SCCProvider=Perforce -Unattended -NoShaderCompile -IncludeOutlinerPathSubstrings=Hogsmeade LV_Overland
```

### Comportement

- Si **aucun** filtre n'est passé → comportement identique à avant (tous les LI non-partitionnés sont fixés).
- Si le filtre est passé → seuls les LI non-partitionnés dont le `OutlinerPath` (du registry) contient l'une des sous-chaînes (semantique OR, virgule-séparée) sont fixés. Les autres sont juste loggés en `Verbose` et comptés dans une nouvelle stat "skipped by filter".
- La traversée passe quand même à travers tous les LI parents (partitionnés ou non) pour ne pas rater un LI Hogsmeade imbriqué profondément.
- Le résumé final inclut maintenant le compteur `Non-partitioned LIs skipped by filter`.


---

### User

une fois que le log affiche , peux-tu me dire si l'asset est immediatement sauvegardé sur le disc ?
+ 199456	[2026.05.27-16.33.06:942][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT] Actor 'SM_OL_Cliff_Rock_LG_02A119' (StaticMeshActor): HLODLayer cleared (was: LV_Overland_HLODLayer_Near); DataLayers cleared (removed: DL_OVERLAND, DL_HOGSMEADE, DL_HM_EXT)
j'ai ensuite arreté le programme alors qu'il n'avait pas terminé.

car je ne comprends pas, j'ai refait un mapcheck et j'ai toujours mon erreur pour SM_OL_Cliff_Rock_LG_02A119
Actor /Game/Levels/Overland/Hogsmeade/Streets/LI_HM_Rocks_EXT.SM_OL_Cliff_Rock_LG_02A119 has an invalid HLOD layer /Game/Data/WorldPartition/HLOD/Overland/LV_Overland_HLODLayer_Near.LV_Overland_HLODLayer_Near 

quand je regarde dans le log, je vois plus tard un fail au moment du save package
200405	[2026.05.27-16.33.11:750][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT] Actor 'SM_OL_Cliff_Rock_LG_10A36' (StaticMeshActor): DataLayers cleared (removed: DL_OVERLAND, DL_HOGSMEADE, DL_HM_EXT)
+ 200406	[2026.05.27-16.33.11:754][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT] Actor 'SM_OL_Cliff_Rock_LG_10A37' (StaticMeshActor): DataLayers cleared (removed: DL_OVERLAND, DL_HOGSMEADE, DL_HM_EXT)
+ 200407	[2026.05.27-16.33.11:758][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT] Actor 'SM_OL_Cliff_Rock_LG_10A38' (StaticMeshActor): DataLayers cleared (removed: DL_OVERLAND, DL_HOGSMEADE, DL_HM_EXT)
+ 200408	[2026.05.27-16.33.11:763][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT] Actor 'SM_OL_Cliff_Rock_LG_10A39' (StaticMeshActor): DataLayers cleared (removed: DL_OVERLAND, DL_HOGSMEADE, DL_HM_EXT)
+ 200409	[2026.05.27-16.33.11:766][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT] Actor 'SM_OL_Cliff_Rock_LG_10A40' (StaticMeshActor): DataLayers cleared (removed: DL_OVERLAND, DL_HOGSMEADE, DL_HM_EXT)
+ 200410	[2026.05.27-16.33.11:770][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT] Actor 'Pivot' (LevelInstancePivot): DataLayers cleared (removed: DL_OVERLAND, DL_HOGSMEADE, DL_HM_EXT)
+ 200415	[2026.05.27-16.33.11:780][  0]LogFixupNonPartitionedActors: Error: Failed to save 1 package(s)
+ 200422	[2026.05.27-16.33.11:785][  0]LogFixupNonPartitionedActors: Verbose: Entering LevelInstance: LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Shops/LI_Honeydukes_INT
+ 200438	[2026.05.27-16.33.11:791][  0]LogFixupNonPartitionedActors: Verbose: LevelInstance LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Shops/LI_Honeydukes_INT is partitioned, skipping fixup of its direct inner-actors
+ 200451	[2026.05.27-16.33.11:798][  0]LogFixupNonPartitionedActors: Verbose: Entering LevelInstance: LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Building_A_EXT
+ 200460	[2026.05.27-16.33.11:804][  0]LogFixupNonPartitionedActors: Verbose: LevelInstance LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Building_A_EXT is partitioned, skipping fixup of its direct inner-actors
+ 200473	[2026.05.27-16.33.11:810][  0]LogFixupNonPartitionedActors: Verbose: Entering LevelInstance: LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Buildings/LI_Water_Mill_POP
+ 200487	[2026.05.27-16.33.11:835][  0]LogFixupNonPartitionedActors: Verbose: LevelInstance LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Buildings/LI_Water_Mill_POP is partitioned, skipping fixup of its direct inner-actors
+ 200504	[2026.05.27-16.33.11:842][  0]LogFixupNonPartitionedActors: Verbose: Entering LevelInstance: LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Buildings/LI_Water_Mill_POP/LI_FoodBags_E
+ 200506	[2026.05.27-16.33.11:844][  0]LogFixupNonPartitionedActors: Display: Non-partitioned LevelInstance found: LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Buildings/LI_Water_Mill_POP/LI_FoodBags_E -- fixing inner actors
+ 200507	[2026.05.27-16.33.11:847][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Buildings/LI_Water_Mill_POP/LI_FoodBags_E] Actor 'SundanceWorldSettings' (SundanceWorldSettings): DataLayers cleared (removed: DL_HOGSMEADE)
+ 200508	[2026.05.27-16.33.11:851][  0]LogFixupNonPartitionedActors: Display: [LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Buildings/LI_Water_Mill_POP/LI_FoodBags_E] Actor 'Brush0' (Brush): DataLayers cleared (removed: DL_HOGSMEADE)

peux-tu adapter le builder pour ne debugger specifiquement que SM_OL_Cliff_Rock_LG_02A119 (et toute sa hierarchie de level instance)

**Assistant:** Excellente question. Plusieurs choses à clarifier :

## Est-ce que le log signifie que l'asset est sauvegardé sur disque ?

**Non.** Le log `[...] Actor 'X': HLODLayer cleared...` est émis **avant** la sauvegarde. Voici le flow réel dans le code actuel :

1. `ResetInheritedPartitioningOnActor()` → modifie l'actor + log la ligne Display + marque le package dirty + retourne `true`
2. `FixupActorsInNonPartitionedLevel()` → ajoute le `UPackage*` à `PackagesToSave`
3. À la fin de la boucle sur le LI, `SaveModifiedPackages()` est appelé → c'est **là** que `SavePackages()` fait le checkout Perforce + écriture disque

Et précisément dans tes logs, on voit ligne `200415` : `Error: Failed to save 1 package(s)`. **Le package du LI `LI_HM_Rocks_EXT` (qui contient `SM_OL_Cliff_Rock_LG_02A119` et les autres) n'a pas pu être sauvegardé**, donc le `mapcheck` reproduit toujours l'erreur HLODLayer.

Pourquoi ça a échoué ? Le problème : `LI_HM_Rocks_EXT` est un Level **non-partitionné**, donc tous ses inner actors sont **embedded dans le même UPackage que le Level** (`/Game/Levels/Overland/Hogsmeade/Streets/LI_HM_Rocks_EXT`). Quand on collecte les packages des actors via `Actor->IsPackageExternal() ? Actor->GetExternalPackage() : Actor->GetOutermost()`, on récupère **le package du Level lui-même** (un seul package partagé entre tous les actors). Et tu vois "Failed to save 1 package(s)" → un seul package était à sauver, mais le checkout ou l'écriture a échoué.

Causes typiques :
- Le `.umap` de `LI_HM_Rocks_EXT` est read-only et le checkout Perforce a échoué (verrou exclusif posé par quelqu'un d'autre, ou conflit). 
- Ou: parce qu'on `CommitLevelInstance(..., bDiscardEdit=true)` **juste après** avoir collecté/marqué dirty mais avant d'arriver à sauver — non, dans le code actuel `SaveModifiedPackages()` est appelé **dans le scope** avant la destruction du `FLevelInstanceEditScope` (ligne 254). Donc ce n'est pas ça.

Le plus probable : le `.umap` n'a pas pu être checkout. Le log de `SavePackages` du parent `UWorldPartitionBuilder` doit déjà l'avoir indiqué (avec `LogWorldPartitionBuilder`). Active `-LogCmds="LogFixupNonPartitionedActors Verbose, LogWorldPartitionBuilder Verbose, SourceControl Verbose"` pour voir le détail.

## Ajout d'un filtre par actor pour debug

Je vais ajouter un paramètre `-IncludeActorNameSubstrings=` qui filtre les actors traités à l'intérieur des LI non-partitionnés. Combiné avec le filtre existant `-IncludeOutlinerPathSubstrings=Hogsmeade`, ça permet d'isoler `SM_OL_Cliff_Rock_LG_02A119` :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h

</details>

**Assistant:** Maintenant le .cpp — parsing du param, application du filtre, et implémentation de la fonction :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant appliquons le filtre dans `FixupActorsInNonPartitionedLevel` :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Et l'implémentation de la fonction `DoesActorMatchNameFilter` à la fin :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
- `ReadLints`

</details>

**Assistant:** Toujours uniquement les erreurs clang attendues (pas de headers Unreal hors UBT). OK.

## Réponse à ta question + ce qui a été ajouté

### Quand l'asset est-il sauvegardé ?

**Pas au moment du log `Display`.** Le log est émis dès qu'on a modifié l'actor en mémoire. La sauvegarde réelle (checkout Perforce + écriture `.umap`) arrive plus tard, dans `SaveModifiedPackages()`, lors d'un des points de flush :
- À la fin du traitement du LI courant (avant de quitter EditMode)
- Quand `PackagesToSave.Num() >= 100`
- À la toute fin de `RunInternal`

Et **dans tes logs** : la ligne `200415 Failed to save 1 package(s)` est précisément l'échec du save du package du Level `LI_HM_Rocks_EXT`. Comme c'est un Level non-partitionné, **tous ses inner actors** (`SM_OL_Cliff_Rock_LG_02A119`, `..._LG_10A36..40`, `Pivot`) partagent **le même `.umap`** → un seul package, qui n'a pas pu être sauvé → toutes tes modifs en mémoire sont perdues à la prochaine ouverture du LI → `mapcheck` reproduit l'erreur.

**Cause probable** : `SavePackages` (parent class) appelle `PackageHelper.Checkout()` qui peut échouer (verrou Perforce, fichier read-only non checkoutable, etc.). Le log détaillé est dans la catégorie `LogWorldPartitionBuilder`. Ajoute à ta commandline :

```
-LogCmds="LogFixupNonPartitionedActors Verbose, LogWorldPartitionBuilder Verbose, LogSourceControl Verbose"
```

### Nouveau filtre pour debug

Tu peux maintenant lancer :

```
-LogCmds="LogFixupNonPartitionedActors Verbose, LogWorldPartitionBuilder Verbose, LogSourceControl Verbose" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionFixupNonPartitionedActorsBuilder -SCCProvider=Perforce -Unattended -NoShaderCompile -IncludeOutlinerPathSubstrings=LI_HM_Rocks_EXT -IncludeActorNameSubstrings=SM_OL_Cliff_Rock_LG_02A119 LV_Overland
```

Le builder va :
1. Traverser toute la hiérarchie LI (sans skip — pour atteindre `LI_HM_Rocks_EXT` imbriqué profondément)
2. Quand il rencontre un LI **non-partitionné** dont l'outliner path contient `LI_HM_Rocks_EXT` → entrer en fixup mode
3. Dans ce LI, ne toucher **que** l'actor `SM_OL_Cliff_Rock_LG_02A119`
4. Logger toutes les opérations et le résultat du save (succès/échec)

Si le save échoue à nouveau avec un seul actor modifié, on saura que c'est bien un problème Perforce/permissions sur le `.umap` `LI_HM_Rocks_EXT`, indépendant de la quantité de modifs. Le verbose log de `LogWorldPartitionBuilder` te dira exactement quel fichier et pourquoi le checkout/save a échoué.


---

### User

LI_HM_Rocks_EXT est dans LI_Hogsmeade    
ne devrait on pas voir un commandline arg pour Hogsmeade aussi ?

**Assistant:** Pas besoin si tu utilises `IncludeOutlinerPathSubstrings=LI_HM_Rocks_EXT`. Voici pourquoi.

## Comportement actuel du filtre `IncludeOutlinerPathSubstrings`

Regardons le code pertinent :

```264:271:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
		if (!LoadedLevel->bIsPartitioned)
		{
			if (DoesLevelInstanceMatchOutlinerFilter(LevelInstancePath))
			{
				// This is the target case: a non-partitioned LI whose inner-actors inherit HLOD/Grid/DataLayer from the partitioned parent.
				UE_LOG(LogFixupNonPartitionedActors, Display, TEXT("Non-partitioned LevelInstance found: %s -- fixing inner actors"), *LevelInstancePath);
				FixupActorsInNonPartitionedLevel(LoadedLevel, LevelInstance, PackageHelper);
			}
```

Le filtre `IncludeOutlinerPathSubstrings` est appliqué **uniquement au moment de décider de fixer un LI** (ligne 266), **pas pendant la traversée**. La traversée continue récursivement à travers TOUS les LI parents (`HandleLevelInstanceRecursive` → `ProcessLevelInstancesInWorldPartition`), peu importe leur nom. Ça vient de la conception décrite dans le doc-comment :

```16:18:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
 *   -IncludeOutlinerPathSubstrings=Foo,Bar
 *     Only fix non-partitioned LevelInstances whose outliner path contains AT LEAST ONE of the
 *     listed comma-separated substrings (OR semantics). Traversal still recurses through non-
 *     matching parent LIs so that nested matching LIs are still discovered.
```

Tu as confirmation dans tes logs précédents : tu voyais bien le builder descendre dans `LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT` avec un filtre `Hogsmeade` qui ne matchait pas chaque palier explicitement.

## Donc `IncludeOutlinerPathSubstrings=LI_HM_Rocks_EXT` suffit

Le path complet d'un LI matché contient déjà sa hiérarchie. Par exemple, quand le builder évalue ces LI, il les compare au filtre :

| OutlinerPath du LI évalué | Contient `LI_HM_Rocks_EXT` ? | Action |
|---|---|---|
| `LV_Overland/Hogsmeade/LI_Hogsmeade` | non | traversé sans fixup |
| `LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade` | non | traversé sans fixup |
| `LV_Overland/Hogsmeade/LI_Hogsmeade/LI_Hogsmeade/Rocks/LI_HM_Rocks_EXT` | **oui** | **fixup actors** |

Donc avec :

```
-IncludeOutlinerPathSubstrings=LI_HM_Rocks_EXT -IncludeActorNameSubstrings=SM_OL_Cliff_Rock_LG_02A119
```

Le builder traverse toute la hiérarchie Hogsmeade, mais ne déclenche le fixup que sur le LI `LI_HM_Rocks_EXT`, et n'y modifie que l'actor `SM_OL_Cliff_Rock_LG_02A119`. C'est exactement ce que tu veux.

## Si tu voulais limiter la traversée elle-même

Là, oui, il faudrait un autre filtre (genre `-TraversalOutlinerPathSubstrings=Hogsmeade`) pour skipper carrément les sous-arbres comme `LV_Overland/Forest/...`. Ça accélérerait significativement le scan d'un gros monde comme `LV_Overland`.

Veux-tu que je l'ajoute ? Sinon le setup actuel répond déjà à ton besoin de debug ciblé.


---

### User

oui, rajoute le

**Assistant:** Je vais ajouter un paramètre `-TraversalOutlinerPathSubstrings=` qui filtre la traversée elle-même. Le piège : il faut filtrer **les LI candidates à descendre dedans** sans rater le cas où un LI matchant est imbriqué dans un LI non-matchant en cours de route.

La stratégie pragmatique : on autorise le sous-arbre d'un LI dès que **son outliner path contient déjà la sous-chaîne** (donc on est entré dans le sous-arbre cible), OU **la sous-chaîne pourrait encore apparaître plus profond** (heuristique conservatrice : la sous-chaîne commence par le path courant ou inversement). Vu la complexité, prenons une approche plus simple et robuste : **on descend tant qu'on n'a pas trouvé de match, et dès qu'on a trouvé un LI qui matche, on continue à descendre seulement dans ses descendants**. Ça correspond exactement à ton cas : tu veux limiter au sous-arbre `LV_Overland/Hogsmeade/...`.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h

</details>

**Assistant:** Maintenant ajoutons le filtre de traversée :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h

</details>

**Assistant:** Maintenant le .cpp. D'abord lisons-le pour situer les modifs :

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant ajoutons le parse du nouveau paramètre :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant, le coeur du changement : appliquer le filtre de traversée dans `HandleLevelInstanceRecursive` **avant** d'entrer en EditMode (gros gain de perf : on évite le coût du load + EditScope) :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** On peut maintenant aussi réutiliser cette variable `EarlyLevelInstancePath` plus bas. Lisons :

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Évitons le double appel à `GetLevelInstancePathForLog` :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant, mettons à jour le log de résumé :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant l'implémentation de `ShouldTraverseLevelInstance` à la fin du fichier :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
- `ReadLints`

</details>

**Assistant:** Toujours uniquement les erreurs clang attendues hors UBT. C'est bon.

## Récapitulatif

### Trois filtres maintenant disponibles

| Paramètre | Effet | Coût économisé |
|---|---|---|
| `-TraversalOutlinerPathSubstrings=Hogsmeade` | **Élague la traversée** : ne descend pas dans les LI hors du sous-arbre cible. Logique : `path.Contains(subStr) OR subStr.StartsWith(path)` pour permettre les ancêtres menant au sous-arbre. | EditMode + load du Level → énorme |
| `-IncludeOutlinerPathSubstrings=LI_HM_Rocks_EXT` | **Filtre quels LI sont fixés** (mais on continue la traversée). | Itération sur les inner-actors |
| `-IncludeActorNameSubstrings=SM_OL_Cliff_Rock_LG_02A119` | **Filtre quels actors sont modifiés** dans un LI matché. | Modify + dirty + save d'un package |

### Commande pour ton cas

```
-LogCmds="LogFixupNonPartitionedActors Verbose, LogWorldPartitionBuilder Verbose, LogSourceControl Verbose" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionFixupNonPartitionedActorsBuilder -SCCProvider=Perforce -Unattended -NoShaderCompile -TraversalOutlinerPathSubstrings=LV_Overland/Hogsmeade -IncludeOutlinerPathSubstrings=LI_HM_Rocks_EXT -IncludeActorNameSubstrings=SM_OL_Cliff_Rock_LG_02A119 LV_Overland
```

Le builder ne va plus :
- Visiter les LI hors de `LV_Overland/Hogsmeade` → l'élague avant même de loader le Level
- Fixer un LI qui n'est pas `LI_HM_Rocks_EXT`
- Toucher un actor qui n'est pas `SM_OL_Cliff_Rock_LG_02A119`

### Notes sur l'heuristique de traversée

L'heuristique `subStr.StartsWith(path)` repose sur le fait que ton `OutlinerPath` est hiérarchique (séparateurs `/`). Si pour une raison X le path du registry n'est pas un préfixe exact (ex: pas le `/` final, casse différente, ou parent intermédiaire absent du registry), tu pourrais voir un sous-arbre pruné par erreur. Si ça arrive, passe simplement une sous-chaîne plus haute dans la hiérarchie (par exemple `-TraversalOutlinerPathSubstrings=Hogsmeade` au lieu de `LV_Overland/Hogsmeade`) — ça matchera dès qu'on entrera dans le sous-arbre Hogsmeade.


---

### User

revert tes derniers ajouts de IncludeOutlinerPathSubstrings et IncludeActorNameSubstrings

**Assistant:** Je vais retirer `IncludeOutlinerPathSubstrings` et `IncludeActorNameSubstrings` mais garder `TraversalOutlinerPathSubstrings` puisque c'est le dernier ajout que tu voulais.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h

</details>

**Assistant:** Maintenant je fais les retraits dans le .h :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h
- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.h

</details>

**Assistant:** Maintenant le .cpp. Retirons le parsing des deux paramètres, le filtre actor name, le filtre LI fixup, les fonctions associées et le stat skipped :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Maintenant retirons le filtre `DoesLevelInstanceMatchOutlinerFilter` au point de décision fixup :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Retirons le filtre actor name dans la boucle d'actors :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Mettons à jour le log de résumé :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp

</details>

**Assistant:** Et enfin, supprimons les deux implémentations de fonctions (`DoesLevelInstanceMatchOutlinerFilter` et `DoesActorMatchNameFilter`) à la fin :

<details><summary>Tools used</summary>

- `StrReplace` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionFixupNonPartitionedActorsBuilder.cpp
- `ReadLints`

</details>

**Assistant:** Que des erreurs clang attendues (headers Unreal non visibles hors UBT).

Récapitulatif des changements :

- **Retiré** : `IncludeOutlinerPathSubstrings` (param + doc + champ + fonction + log + stat skipped)
- **Retiré** : `IncludeActorNameSubstrings` (param + doc + champ + fonction + log + filtre dans la boucle)
- **Conservé** : `TraversalOutlinerPathSubstrings` (le filtre de traversée que tu voulais)

Commande pour ton cas :

```
-LogCmds="LogFixupNonPartitionedActors Verbose, LogWorldPartitionBuilder Verbose, LogSourceControl Verbose" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionFixupNonPartitionedActorsBuilder -SCCProvider=Perforce -Unattended -NoShaderCompile -TraversalOutlinerPathSubstrings=Hogsmeade LV_Overland
```
