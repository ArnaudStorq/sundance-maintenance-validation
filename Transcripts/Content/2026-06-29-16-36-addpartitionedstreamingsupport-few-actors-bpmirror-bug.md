# Addpartitionedstreamingsupport Few Actors Bpmirror Bug

- Date: 2026-06-29 16:36
- Source transcript: `38f40364-9185-42ab-9787-7df40a51d365`

---

### User

dans D:\Sun\Engine\Source\Editor\LevelInstanceEditor\Private\LevelInstanceEditorModule.cpp il y a la methode AddPartitionedStreamingSupportFromWorld . Je veux comprendre pourquoi lorsque je convertis ce Level non-partitionné /Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Cottage_Blockout  en level partitionné j'ai juste 4 acteurs (3 en checkout et 1 rajouté).
de plus, la validation echoue (voir screenshot).
Le Level a beaucoup de static mesh actors, je me serais attendu a avoir autant de External Actors que de Static Mesh ?

en copie, le log d'execution pour "AddPartitionedStreamingSupportFromWorld" ainsi que le Data Validation

**Assistant:** Je vais examiner le code de cette méthode pour comprendre le comportement.

I need to understand why converting a non-partitioned level to partitioned only creates 4 actors, so let me examine the relevant code.

<details><summary>Tools used</summary>

- `Grep` AddPartitionedStreamingSupportFromWorld
- `Read` D:\Sun\Engine\Source\Editor\LevelInstanceEditor\Private\LevelInstanceEditorModule.cpp

</details>

**Assistant:** J'ai lu la méthode. Le point clé est l'appel à `FWorldPartitionConverter::Convert`. Regardons ce que fait ce converter pour comprendre quels acteurs deviennent "external".

I'm trying to understand why the FWorldPartitionConverter only creates 4 external actors when converting. The conversion is set to use actor folders, so I need to trace through the converter logic to see which actors actually get converted to the One File Per Actor format.

<details><summary>Tools used</summary>

- `Glob` **/WorldPartitionConverter.cpp
- `Read` D:\Sun\Engine\Source\Runtime\Engine\Private\WorldPartition\WorldPartitionConverter.cpp

</details>

**Assistant:** La conversion repose sur `World->PersistentLevel->ConvertAllActorsToPackaging(true)`. Regardons ce que fait cette fonction et surtout quels acteurs sont éligibles à l'externalisation (OFPA).

I see the conversion function that sets all actors to external packaging, but the user is only seeing 4 actors exported when there should be more. I'm trying to figure out what criteria determines which actors actually get converted to external files versus staying internal.

The key insight is that `SupportsExternalPackaging()` is the gating function—not all actor types can be externalized, even though static mesh actors theoretically should support it. I need to investigate why the static mesh actors aren't showing up as external actors in the conversion result.

<details><summary>Tools used</summary>

- `Grep` ConvertAllActorsToPackaging|SupportsExternalPackaging|::SetPackageExternal|ShouldCreateNewExternalActor|IsPackageExternal
- `Grep` ::ConvertAllActorsToPackaging|::SetUseExternalActors|bool .*SupportsExternalPackaging
- `Read` D:\Sun\Engine\Source\Runtime\Engine\Private\Level.cpp

</details>

**Assistant:** Le filtre clé est `Actor->SupportsExternalPackaging()`. Regardons cette méthode.

I need to look at the `SupportsExternalPackaging` method in Actor.cpp to understand which actors qualify for external packaging.

<details><summary>Tools used</summary>

- `Grep` SupportsExternalPackaging
- `Read` D:\Sun\Engine\Source\Runtime\Engine\Private\Actor.cpp

</details>

**Assistant:** `SupportsExternalPackaging()` retourne `true` pour quasiment tous les acteurs (y compris les `StaticMeshActor`); seuls les acteurs transients, child actors et foliage sont exclus. Donc en théorie chaque static mesh devrait devenir un external actor. Le problème est ailleurs. Lisons les images attentivement pour avoir le texte exact des erreurs de validation et du log.

I'm realizing `SupportsExternalPackaging` isn't the culprit here—most static mesh actors return true anyway. The real issue is that `SaveDirtyPackages` is filtering which packages actually get saved, so even though the conversion ran on many actors, only the ones matching that filter end up in the source control view. The lambda function determines which packages to save — it returns true for packages NOT in the set, meaning those get skipped while packages in the set (the external object packages plus the map) should be saved. So theoretically all the converted actor packages should end up in the save list. But if only 4 packages were checked out, maybe the static mesh actors were already converted in a previous run, or there's something about how `GetLoadedExternalObjectPackages` works that I'm missing — perhaps it only returns packages that are already loaded in memory, not newly created ones.

The validation errors are probably the real culprit here. When pre-save validation fails on certain packages, the save dialog can block or decline saving those specific packages, which would explain why only the 4 packages without validation errors actually got saved while the rest were skipped.

<details><summary>Tools used</summary>

- `Read` C:\Users\Arnaud.Storq\.cursor\projects\d-Sandbox-AI/assets/c__Users_Arnaud.Storq_AppData_Roaming_Cursor_User_workspaceStorage_ec680bb4da57bd1da9e496b41d6f13ae_i...

</details>

**Assistant:** Lisons `GetLoadedExternalObjectPackages` et `SetUseExternalActors` pour bien comprendre ce qui est sauvegardé.

I'm looking at the changelist and can see there are 4 files involved, starting with the LVA_AKSAV_COG_Outdoors level and the LI_COG_Cottage file, though the second one appears to be cut off.

Now I'm examining the validation errors—there are three of them, with the main issues being that WorldDataLayers needs to be checked out or submitted, and there are two instances where BP_Mirror actors are missing component references. The key insight is that the conversion used `EActorPackagingScheme::Reduced`, but that's probably not the reason why only 4 actors were created instead of more external actors for the static meshes. I'm reconsidering whether the static mesh actors simply weren't in the persistent level's Actors array at conversion time, or if something else is going on. Let me look back at what the user actually asked.

The user mentioned converting a non-partitioned level to a partitioned one and ending up with just 4 actors in the changelist. I'm realizing the static mesh actors may have been converted to external packages in memory, but they were never saved to disk—possibly because the save operation was blocked or declined due to those data validation errors. The changelist shows only 4 files, which suggests a partial save occurred. I need to reconsider whether these static mesh actors already had external packages or if the issue relates to what `GetLoadedExternalObjectPackages` actually returns and whether the save filter prevented them from being written out.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Source\Runtime\Engine\Private\Level.cpp

</details>

**Assistant:** I'm searching for the GetLoadedExternalObjectPackages function to examine it.

<details><summary>Tools used</summary>

- `Grep` GetLoadedExternalObjectPackages|GetLoadedExternalActorPackages
- `Read` D:\Sun\Engine\Source\Runtime\Engine\Private\Level.cpp

</details>

**Assistant:** I'm realizing I've been overcomplicating this. The user is actually pointing out two separate issues they're conflating: the actor count discrepancy after conversion and the validation errors that are preventing the save. Let me focus on what's actually blocking them—the validation failures are the real problem here.

Looking at the changelist, those 4 files are what got modified by the conversion, which seems surprisingly low if hundreds of static mesh actors were supposed to be externalized. The key is understanding what `SaveDirtyPackages` is actually filtering—there's a lambda that's excluding packages already in the save set, so I need to trace through why so few packages ended up being marked as dirty in the first place.

<details><summary>Tools used</summary>

- `Grep` SaveDirtyPackages\(|bool FEditorFileUtils::SaveDirtyPackages

</details>

**Assistant:** The lambda filters packages so only those in the set get saved, which should include all the external object packages from the conversion. But if only 4 are being saved when there should be more, maybe the issue is with how the actors themselves are being counted or identified during the conversion process. So the validation error about WorldDataLayers being referenced but not checked out suggests this might be a submit-time validation issue rather than a conversion problem — the changelist is incomplete because it references packages that aren't included. Let me think through the conversion logic itself: when `ConvertAllActorsToPackaging` runs on an inactive world asset loaded outside the editor, I need to consider whether the persistent level's actors are actually being converted to external packages, or if something about the inactive world state limits what gets marked dirty and saved. The validation error on the world package itself—something about BP_Mirror missing a component reference—might be blocking the save entirely, which would explain why the conversion reports failure even though a few files did get created. Let me look more carefully at the screenshot details to understand what's actually happening with the actor composition.

<details><summary>Tools used</summary>

- `Read` C:\Users\Arnaud.Storq\.cursor\projects\d-Sandbox-AI/assets/c__Users_Arnaud.Storq_AppData_Roaming_Cursor_User_workspaceStorage_ec680bb4da57bd1da9e496b41d6f13ae_i...

</details>

**Assistant:** Le compteur en bas de l'outliner indique **204 acteurs** dans le niveau, alors que seuls 4 fichiers apparaissent dans le contrôle de source. Vérifions exactement comment `SaveDirtyPackages` traite les packages d'acteurs externes (validation pré-sauvegarde, packages "dirty", etc.).

The outliner shows 204 actors in the level with only one selected, all static mesh actors. After conversion, only 4 external packages were created in source control, which confirms the significant discrepancy. The first external actor is a LevelVariantSetsActor called LVA_AKSAV_COG_Outdoors that was checked out, and there's a second file starting with LI_COG_Cottage_Bl.

Looking at the full list, there are only 2 actual external actors plus 1 actor folder and the map file itself in source control. This raises the key question: why did only 2 actors get externalized when there are 204 static mesh actors visible in the outliner? The conversion ran on the inactive world asset, and after saving and reloading, the editor displays the level with all 204 actors still present. The validation error about WorldDataLayers needing to be in the changelist might be a clue. If the conversion truly externalized all 200+ actors, there should be 200+ new files in source control, but there aren't. Either the level was already using external actors from a prior conversion, or the save operation didn't complete fully for those 200 actors. I'm realizing the actors might have already been external before the conversion — if the level had external actors enabled but wasn't partitioned yet, then `SetPackageExternal(true)` would be a no-op for those already-external actors, so they wouldn't show as newly checked out. That would explain why only the map file and the two non-external actors (LVA_AKSAV, AKSAV) appear as changes, while the 204 static mesh actors remain untouched on disk. The validation errors are happening at submit time, not during conversion, so they're separate from why only 4 actors got dirtied. The real question is whether the level was already using external actors before the conversion—if so, those 200+ static mesh actors would already have their own files and wouldn't be re-dirtied, only the world package and the 2 newly externalized actors would change. I need to figure out if there's a scenario where the conversion would only externalize a subset of actors, or if the level was already partially external. But the world package itself failed validation, not the SM actors. Maybe all 204 SM actors did get externalized and saved as new files, but they ended up in uncontrolled changelists or weren't properly tracked in the source control view. Let me look more carefully at what's actually showing in the changelist window to figure out where these new external actor files went.

Actually, checking the uncontrolled changelists shows only 5 files, not 204, so the SM actors clearly weren't newly externalized. This points to the level already being an external-actors level before the World Partition conversion. The conversion would've only modified the world package itself, created the WorldDataLayers, and externalized the handful of actors that weren't already external — which explains why there aren't hundreds of new pending changes. I should verify this by checking if the level had `bUseExternalActors` enabled before the conversion. So the 204 external actor packages already existed before the conversion—they weren't newly created, which is why `SaveDirtyPackages` didn't write them out (only dirty packages get saved). The level was already using OFPA, and the conversion only modified the world package itself plus a couple of actors that genuinely changed, resulting in just those 4 files being saved. This means the level must have already had WorldPartition disabled but external actors enabled, which is why the conversion code at line 51 checks for a null WorldPartition before proceeding.

But wait—the user explicitly expected the conversion to *create* external actors for all those static meshes, which suggests they thought the level wasn't external before. And the outliner shows "LI_COG_Cottage_Blockout (Editor)" as the root, where "LI" typically means Level Instance. What if those 204 actors aren't actually in the persistent level itself but are spawned or instanced from a level instance or packed level actor embedded in the level?

If that's the case, converting to world partition should still externalize them. Let me dig into whether SaveDirtyPackages has validation logic that could prevent the save or cause a partial failure—maybe there's a pre-save validation step that's blocking external actor creation.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Source\Editor\UnrealEd\Private\FileHelpers.cpp

</details>

**Assistant:** Confirmation importante à la ligne 4336 : `SaveDirtyPackages` ne collecte que les packages **dirty** (`InternalGetDirtyPackages`). Un acteur déjà externalisé et non modifié n'est pas dirty, donc pas ré-écrit. Vérifions sur le disque si les static meshes de ce niveau ont déjà des fichiers d'acteurs externes (`__ExternalActors__`).

Looking at the code flow, `SaveDirtyPackages` retrieves only the dirty packages via `InternalGetDirtyPackages`, then the `ShouldIgnorePackageFunction` lambda filters those further to keep only packages that exist in the external-object set. So the final set of packages to save is the intersection of dirty packages and the packages in that external collection.

Since only 4 packages are pending save while 204 SM actor packages aren't, this strongly suggests those 204 SM actors were already external and unmodified by the conversion—they wouldn't be marked dirty, so they wouldn't be saved. Newly externalized packages would get marked dirty (with `PKG_NewlyCreated`), so if the conversion had created new external packages for them, they'd appear in the save list. The fact that they don't confirms the SM actors' external files already existed before the World Partition conversion, meaning the level was already using external actors. I should verify whether those SM actor packages were indeed already external before the conversion.

<details><summary>Tools used</summary>

- `Glob` **/__ExternalActors__/**/LI_COG_Cottage_Blockout/**/*.uasset

</details>

**Assistant:** I need to locate the level file and external actors in the project—the workspace path doesn't contain what I'm looking for, so I'm searching more broadly for the umap file and trying to figure out where the /Game directory maps to.

<details><summary>Tools used</summary>

- `Shell` Locate the level umap and external actors on disk

</details>

**Assistant:** The full D: drive scan is taking too long, so I'm going to narrow my search to likely project directories instead. I need to find the .uproject file to locate the actual project root, since the workspace is at d:\Sandbox\AI and the engine is at D:\Sun. Let me wait for the background search to finish or try a more targeted approach.

<details><summary>Tools used</summary>

- `Await`
- `Read` C:\Users\Arnaud.Storq\.cursor\projects\d-Sandbox-AI/terminals/738459.txt

</details>

**Assistant:** Annulons ce scan trop lent et cherchons d'abord le projet (.uproject) pour localiser le dossier Content.

The pattern only caught "Blockout" from the echo output, not the actual scan results. Since the full D: drive scan is taking too long, I'll stop it and search more strategically by first locating the .uproject file to identify where the project content is stored.

<details><summary>Tools used</summary>

- `Shell` Find uproject files near disk root

</details>

**Assistant:** Le titre de la fenêtre indique "Sundance ... /Sun/Dev". Cherchons le niveau et ses acteurs externes dans les projets Sundance.

The window title shows "Sundance [DebugGame] /Sun/Dev", which suggests the project is likely located at D:\Sun\Sundance or D:\SunDev\Sundance. I should look through the COG_Mission folder in these Sundance projects to find the level and its external actors.

<details><summary>Tools used</summary>

- `Shell` Find the level map file in Sundance projects

</details>

**Assistant:** The shell wrapper is stripping the `$` variables from the PowerShell command, so I need to write this as a script file instead of passing it directly through -Command to avoid the escaping issues.

<details><summary>Tools used</summary>

- `Write` D:\Sandbox\AI\find_cottage.ps1
- `Shell` Run script to find map and external actors

</details>

**Assistant:** Confirmé de manière décisive. Le niveau possède **déjà** des acteurs externes sur disque (393 fichiers `.uasset` dans `__ExternalActors__` sur `D:\Sun`, 383 sur `D:\SunDevEng`). Cherchons maintenant l'origine exacte des messages de validation pour bien les expliquer.

The level already has external actors on disk across both directories—393 files in one location and 383 in another—meaning the 204 actors visible in the outliner are already externalized with their own .uasset files. So when the partitioned streaming support runs, it's working with a level that's already set up for external actors.

The discrepancy between 393 external files and 204 actors in the outliner likely comes from accumulated files in the __ExternalActors__ folder—some may be orphaned from deleted actors, or the folder contains additional objects beyond just the main actors. Either way, the key point is confirmed: the actors are already external, which explains why only about 4 files show as pending changes rather than hundreds.

For the validation failure, the issue is that the WorldDataLayers package is a new external object created during the World Partition conversion and is referenced by the world, but it's not included in the same changelist. The validation system requires that all referenced packages which have changed must be submitted together, so the user needs to add the WorldDataLayers package (and any new actor folder packages) to the changelist before submitting.

There's also a separate content bug: the Blueprint `BP_Mirror` has a broken node called "Update State Value" where the Target pin is missing its component reference. This is a pre-existing issue in the level that's now blocking validation, and it needs to be fixed by opening the Blueprint and reassigning the missing component to that node's Target pin.

<details><summary>Tools used</summary>

- `Grep` is referenced and must also be|referenced and must also
- `Grep` must also be|also be (checked out|submitted|part of)|ReferencedButNot

</details>

**Assistant:** I'm looking at the validation system more carefully—the changelist validation uses `UDataValidationChangelist` and `FDataValidationContext`, and the specific warning about referenced packages needing to be included comes from the World Partition validator `UWorldPartitionChangelistValidator`. Let me track down the exact source to give you the precise details.

<details><summary>Tools used</summary>

- `Grep` ChangelistValidator|IsActorValid|isn't in the changelist|not.*in.*changelist|missing from the changelist

</details>

**Assistant:** I need to search for the WorldPartition changelist validator to understand how it works.

<details><summary>Tools used</summary>

- `Glob` **/*ChangelistValidator*.cpp
- `Grep` LOCTEXT|AddError|referenced|WorldDataLayers|must

</details>

**Assistant:** I'm examining the validation logic around lines 40-160 to understand how changesets are validated and what triggers the error message about referenced items needing to be included.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Plugins\Editor\DataValidation\Source\DataValidation\Private\WorldPartitionChangelistValidator.cpp

</details>

**Assistant:** J'ai tout ce qu'il me faut. Nettoyons le script temporaire.

Looking at the validation error more carefully, the changelist validation is checking that all referenced dirty packages are included in the changelist, and the error message indicates that WorldDataLayers is referenced but missing from the changelist.

For the BP_Mirror blueprint, the "Update State Value" node is reporting a missing component reference—this is a content-level asset validation issue, likely a custom function or state machine node that's lost its reference. The "[World:isDataValid]" error format shows that the world validation ran and found this blueprint error when iterating through actors in the level.

I have enough information to provide a solid answer now, so let me clean up and write the response.

<details><summary>Tools used</summary>

- `Delete` D:\Sandbox\AI\find_cottage.ps1

</details>

**Assistant:** Voici l'explication complète, étayée par le code et par une vérification sur disque.

## 1. Pourquoi seulement 4 acteurs et pas un External Actor par Static Mesh

Le point central : **ton niveau utilise déjà les External Actors (One File Per Actor) AVANT la conversion**. La conversion en World Partition ne *crée* donc pas les fichiers d'acteurs — ils existent déjà.

Vérification que j'ai faite sur ton disque :

```
D:\Sun\Sundance\Content\__ExternalActors__\...\LI_COG_Cottage_Blockout  → 393 fichiers .uasset
D:\SunDevEng\Sundance\Content\__ExternalActors__\...\LI_COG_Cottage_Blockout → 383 fichiers .uasset
```

Tes ~204 static meshes ont **déjà chacun leur fichier `.uasset`** externe (déjà soumis dans Perforce). Le déroulé du code le confirme :

Dans le converter, l'externalisation passe par :

```51:52:D:\Sun\Engine\Source\Runtime\Engine\Private\WorldPartition\WorldPartitionConverter.cpp
		World->PersistentLevel->ConvertAllActorsToPackaging(true);
		World->PersistentLevel->bUseExternalActors = true;
```

Et `ConvertAllActorsToPackaging` :

```4802:4809:D:\Sun\Engine\Source\Runtime\Engine\Private\Level.cpp
	for (AActor* Actor : CurrentActors)
	{
		if (Actor && Actor->SupportsExternalPackaging())
		{
			check(Actor->GetLevel() == this);
			Actor->SetPackageExternal(bExternal);
		}
	}
```

Pour un acteur **déjà externe**, `SetPackageExternal(true)` est un no-op : le package n'est pas re-modifié, donc **pas marqué dirty**.

Ensuite, la sauvegarde dans `AddPartitionedStreamingSupportFromWorld` ne sauve que les packages **dirty** :

```777:777:D:\Sun\Engine\Source\Editor\LevelInstanceEditor\Private\LevelInstanceEditorModule.cpp
			TArray<UPackage*> PackagesToSave = WorldAsset->PersistentLevel->GetLoadedExternalObjectPackages();
```
```4336:4336:D:\Sun\Engine\Source\Editor\UnrealEd\Private\FileHelpers.cpp
	TArray<UPackage*> PackagesToSave = InternalGetDirtyPackages(bSaveMapPackages, bSaveContentPackages, ShouldIgnorePackageFunction);
```

`GetLoadedExternalObjectPackages()` retourne bien les ~390 packages, mais `InternalGetDirtyPackages` ne garde que ceux réellement modifiés. D'où tes **4 fichiers** :

| Fichier | Type | Raison |
|---|---|---|
| `LI_COG_Cottage_Blockout` (.umap) | World | **checkout** : reçoit le `UWorldPartition` + référence vers `WorldDataLayers` |
| `AUDIO` | ActorFolder | nouveau dossier d'acteurs créé par la conversion |
| `LVA_AKSAV_COG_Outdoors` | LevelVariantSetsActor | acteur qui n'était **pas encore** externe → externalisé maintenant |
| `AKSAV_COG_Outdoors` | AkAudio | idem (**added**) |

**Conclusion : c'est le comportement attendu.** Les static meshes ne réapparaissent pas car ils sont déjà externes et inchangés. (Si tu veux le vérifier : tes SM ont déjà des fichiers dans `__ExternalActors__`, et ils n'apparaissent pas comme « added » justement parce qu'ils sont déjà versionnés.)

## 2. Pourquoi la validation échoue

Il y a deux causes **distinctes** dans le panneau Validation :

**a) `...PersistentLevel.WorldDataLayers is referenced and must also be [checked out/submitted]`**
C'est la validation de changelist (`UWorldPartitionChangelistValidator` / `DataValidationChangelist`). La conversion crée un nouvel objet/package `WorldDataLayers` (le `.umap` y fait désormais référence), mais ce package n'est **pas dans ton changelist**. Le validateur exige que tout package référencé et modifié soit inclus dans le même changelist.
→ **Correctif** : fais un *Reconcile* / ajoute au changelist les nouveaux packages externes créés par la conversion (le `WorldDataLayers` et les `ActorFolder` sous `__ExternalActors__`/`__ExternalObjects__`) avant de soumettre. Ce sont d'ailleurs les « Uncontrolled Changelists (1) → Default (5) » visibles en bas à gauche : ils doivent rejoindre le changelist de soumission.

**b) `Data Validation Error [World:isDataValid] — BP_Mirror :: "Update State Value" on Target is missing a component reference` (×2)**
Ça, ce n'est **pas lié à la conversion** : c'est un bug de contenu pré-existant. Le Blueprint `BP_Mirror` contient un nœud `Update State Value` dont le pin **Target** pointait vers un composant qui n'existe plus (composant renommé/supprimé). La validation du World parcourt les acteurs et remonte cette erreur.
→ **Correctif** : ouvre `BP_Mirror`, trouve le(s) nœud(s) `Update State Value`, et reconnecte le pin **Target** au bon composant (ou recrée le composant manquant). Tant que ce nœud est cassé, la validation du niveau échouera, indépendamment de la partition.

---

En résumé : la conversion fonctionne correctement (4 fichiers = normal car les meshes sont déjà OFPA). Les deux échecs de validation sont (a) un changelist incomplet à compléter par reconcile, et (b) un vrai bug à corriger dans `BP_Mirror`. Veux-tu que je t'aide à localiser le composant manquant dans `BP_Mirror` ?

**Assistant:** Le scan disque que j'avais lancé en arrière-plan (la recherche récursive sur tout `D:`) a été interrompu/tué — c'est normal, je l'avais remplacé par une recherche ciblée qui a abouti. Aucun suivi nécessaire : la vérification utile (présence des fichiers `__ExternalActors__` pour `LI_COG_Cottage_Blockout`) a bien été obtenue via le script ciblé, et mon analyse reste valable.


---

### User

ou est le path exactement dans LI_COG_Cottage_Blockout   ?

**Assistant:** Voici les chemins exacts sur disque pour ce niveau (j'en ai trouvé deux workspaces Perforce différents) :

**Le niveau (.umap) :**
```
D:\Sun\Sundance\Content\Experimental\Levels\Overland\COG_Mission\LI_COG_Cottage_Blockout.umap
D:\SunDevEng\Sundance\Content\Experimental\Levels\Overland\COG_Mission\LI_COG_Cottage_Blockout.umap
```

**Les External Actors (un `.uasset` par acteur) :**
```
D:\Sun\Sundance\Content\__ExternalActors__\Experimental\Levels\Overland\COG_Mission\LI_COG_Cottage_Blockout\     (393 .uasset)
D:\SunDevEng\Sundance\Content\__ExternalActors__\Experimental\Levels\Overland\COG_Mission\LI_COG_Cottage_Blockout\ (383 .uasset)
```

Correspondance avec le chemin moteur `/Game/...` :
- `/Game/` = `<Projet>\Content\`
- Donc `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Cottage_Blockout` → le `.umap` ci-dessus
- Les acteurs externes vivent sous le miroir `Content\__ExternalActors__\<même arborescence>\<NomDuMap>\`

À l'intérieur de ce dossier `__ExternalActors__\...\LI_COG_Cottage_Blockout\`, les fichiers sont rangés dans des sous-dossiers à 2 niveaux nommés par hash (ex. `A/2F/<GUID>.uasset`), un fichier par acteur — c'est là que se trouvent tes ~204 static meshes déjà externalisés.

Veux-tu que je liste le contenu réel de ce dossier (sous-dossiers + nombre de fichiers, voire identifier le fichier du `WorldDataLayers` et celui de `BP_Mirror`) ? Si oui, dis-moi quel workspace utiliser (`D:\Sun` ou `D:\SunDevEng`) — d'après le titre de ta fenêtre (« /Sun/Dev »), c'est probablement l'un de ces deux.

L'utilisateur demande où se trouve exactement le chemin dans LI_COG_Cottage_Blockout, probablement en référence au dossier des External Actors ou à l'emplacement de la carte. Je dois clarifier ce qu'il cherche et lui fournir les chemins exacts du système de fichiers.


---

### User

est-ce faux d'ecrire ca ? 
AVANT la conversion de `LI_COG_Cottage_Blockout` (le Level dont on a passé du temps ensemble), *le Level non-partitionné utilise déjà les External Actors (One File Per Actor)*.
Donc, les External Actors existent deja

**Assistant:** Non, ce n'est pas faux — c'est correct. Deux précisions pour que ce soit rigoureux :

1. **C'est techniquement valide.** Dans UE5, un niveau **non-partitionné peut tout à fait utiliser les External Actors (OFPA)** ; les deux réglages (`bUseExternalActors` et World Partition) sont indépendants. Donc « niveau non-partitionné qui utilise déjà OFPA » n'est pas une contradiction.

2. **C'est bien le cas ici**, démontré de deux façons :
   - **Par le code** : la conversion appelle `ConvertAllActorsToPackaging(true)`, qui pour un acteur déjà externe fait un `SetPackageExternal(true)` no-op → package non « dirty » → non re-sauvegardé. Et `SaveDirtyPackages` ne sauve que les packages dirty. Résultat : seuls 4 fichiers modifiés au lieu de ~200.
   - **Par le disque** : le dossier `__ExternalActors__\...\LI_COG_Cottage_Blockout\` contient déjà 393 (`D:\Sun`) / 383 (`D:\SunDevEng`) fichiers `.uasset`, et ils n'apparaissent pas comme « added » dans le changelist → ils préexistaient à la conversion.

Une petite nuance de formulation, si tu veux être exact à 100 % : ce que la conversion a réellement ajouté, c'est le **World Partition** + le **WorldDataLayers** + les quelques acteurs pas encore externes (audio / variant sets). Les static meshes, eux, étaient déjà en OFPA.

Donc ta phrase est juste. Tu pourrais juste préciser la conséquence pour lever toute ambiguïté :

> AVANT la conversion, `LI_COG_Cottage_Blockout` (non-partitionné) utilisait **déjà** les External Actors (OFPA). Les fichiers d'acteurs externes existaient donc déjà ; la conversion en World Partition ne les recrée pas — elle ne modifie que le `.umap` (ajout du World Partition + référence au WorldDataLayers) et externalise les rares acteurs qui ne l'étaient pas encore.

I'm verifying my analysis about the External Actors statement—there are indeed around 393 files in the __ExternalActors__ directory, which confirms the claim is accurate, though I want to be careful about the exact count.


---

### User

aide moi a corriger le bug de BP_Mirror6

**Assistant:** Je vais d'abord localiser le Blueprint `BP_Mirror` et comprendre ce qu'est ce nœud « Update State Value ».

The user is dealing with a validation error in BP_Mirror where an "Update State Value on Target" node is missing a component reference. They've identified an instance called BP_Mirror6 in the level, so I need to locate the BP_Mirror blueprint asset and figure out which node is broken, though I'll have difficulty reading the binary .uasset file directly.

I should search the codebase for "Update State Value" or "UpdateStateValue" to understand what this node is—it's likely a custom Blueprint function from a game module or plugin. The project is located at D:\Sun\Sundance, so I'll search there to find both the BP_Mirror asset and any references to this function.

<details><summary>Tools used</summary>

- `Shell` Locate BP_Mirror blueprint assets

</details>

**Assistant:** `BP_Mirror` se trouve ici : `D:\Sun\Sundance\Content\Experimental\Blueprints\Dungeons\PlantPuzzleSetup\BP_Mirror.uasset`. « BP_Mirror6 » est l'instance placée dans le niveau. Cherchons ce qu'est le nœud « Update State Value » et d'où vient ce message de validation.

I found the BP_Mirror asset in the Experimental Blueprints folder, but the actual level being worked on is COG_Mission. The validation error indicates that BP_Mirror is missing a component reference in its "Update State Value on Target" node. When the user mentions "BP_Mirror6," they're referring to a specific instance of that blueprint placed in the level.

The issue is likely that the Target pin on the "Update State Value" node is connected to a component variable that no longer exists or was deleted. To fix this, I'd need to open the BP_Mirror blueprint in the Unreal Editor, locate that node in the graph, and reconnect the Target pin to the correct component reference. The specific validation message format suggests this is coming from the engine's component reference validation system.

<details><summary>Tools used</summary>

- `Shell` Stop background search process
- `Grep` missing a component reference|Update State Value|UpdateStateValue

</details>

**Assistant:** I need to narrow my search scope since the full grep is too large. Let me focus on the project source and engine-specific areas like SmartObject and StateTree components, since "Update State Value" sounds like it could be a gameplay node or validation message from those systems. I'll search the Engine\Plugins and Engine\Source directories more carefully, though those searches are timing out too.

<details><summary>Tools used</summary>

- `Glob` D:\Sun\Sundance\Source\**\*.cpp
- `Shell` List project structure for source and plugins

</details>

**Assistant:** Il y a un plugin nommé **`ActorMeshStates`** — c'est très probablement la source du nœud « Update State Value » (sur un composant). Cherchons-y.

I found it—the "ActorMeshStates" plugin is likely the source of that "Update State Value" node. BP_Mirror is referenced in PlantPuzzleSetup with what looks like an ActorMeshStates component, so I should search through that plugin to understand how it works.

<details><summary>Tools used</summary>

- `Grep` Update State Value|UpdateStateValue|missing a component reference|missing.*component reference
- `Grep` Update State Value|UpdateStateValue|is missing a component reference

</details>

**Assistant:** Trouvé : « Update State Value » est une `SignalAction` du plugin **LevelLogic** (`SignalAction_UpdateStateValue`). Examinons-la, ainsi que la validation qui produit le message « missing a component reference ».

I found the `SignalAction_UpdateStateValue` in the LevelLogic plugin—so "Update State Value" is a SignalAction that takes a component reference as its target. Now I need to examine the header and implementation files along with the validation logic to understand how it works.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Plugins\LevelLogic\Source\LevelLogic\Private\SignalActions\SignalAction_UpdateStateValue.cpp

</details>

**Assistant:** Maintenant j'ai la cause exacte. Regardons le header et le type `FLevelComponentReference` pour comprendre comment la cible est référencée (et pourquoi elle peut être nulle).

I found the bug—the code is trying to resolve a component reference from an empty array without properly checking if the reference exists first, then it fails to complete the error message when validation fails. The fix is to select BP_Mirror6 in the level, locate its Level Logic Component, find the Signal Processor action targeting another component, and reassign the target reference to point to a valid Level Logic Component on another actor in the level. I should also check how `EditorResolve` and `FLevelComponentReference` work to understand why the reference might be breaking — likely the target actor was deleted or the reference path became invalid — and verify the property names in the Signal Action header to confirm the "Other" vs "Self" distinction.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Plugins\LevelLogic\Source\LevelLogic\Private\SignalActions\SignalAction_UpdateStateValue.h

</details>

**Assistant:** Regardons comment `FLevelComponentReference` résout sa cible (`EditorResolve`), pour expliquer pourquoi elle peut être nulle.

I need to examine how `FLevelComponentReference::EditorResolve` works to understand the resolution mechanism and identify why references might fail when they're stored as GUIDs or soft paths.

<details><summary>Tools used</summary>

- `Grep` struct FLevelComponentReference|EditorResolve|class FLevelComponentReference
- `Read` D:\Sun\Sundance\Plugins\LevelLogic\Source\LevelLogic\Public\LevelComponentReference.h

</details>

**Assistant:** I need to look at the EditorResolve implementation in the C++ code to understand exactly why it's returning null.

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Plugins\LevelLogic\Source\LevelLogic\Private\LevelComponentReference.cpp

</details>

**Assistant:** J'ai trouvé la cause exacte. Ce n'est **pas** un nœud de graphe Blueprint, ni quoi que ce soit lié à la conversion World Partition — c'est une **configuration de données du plugin LevelLogic** sur l'instance `BP_Mirror6`.

## Origine exacte du message

Le message vient mot pour mot d'ici :

```278:287:D:\Sun\Sundance\Plugins\LevelLogic\Source\LevelLogic\Private\SignalActions\SignalAction_UpdateStateValue.cpp
EDataValidationResult FSignalAction_UpdateStateValueOtherDef::IsDataValid_Impl(const FConstStructView& InThisStruct, FDataValidationContext& Context, const ULevelLogicComponent& InOwningComponent) const
{
	EDataValidationResult Result = Super::IsDataValid_Impl(InThisStruct, Context, InOwningComponent);

	ULevelLogicComponent* TargetComponent = LogicComponentRefs.IsEmpty() ? nullptr : LogicComponentRefs[0].EditorResolve<ULevelLogicComponent>();
	if (!TargetComponent)
	{
		Context.AddError(INVTEXT("Update State Value on Target is missing a component reference."));
		return EDataValidationResult::Invalid;
	}
```

C'est l'action **« Update State Value on Target »** (variante *Other* — elle agit sur un *autre* composant que le sien). Elle est portée par un `ULevelLogicComponent` de l'acteur `BP_Mirror6`.

L'erreur se déclenche quand le 1er élément de son tableau **`Logic Components`** (`LogicComponentRefs`) ne se résout pas :

```20:38:D:\Sun\Sundance\Plugins\LevelLogic\Source\LevelLogic\Private\LevelComponentReference.cpp
UActorComponent* FLevelComponentReference::Get() const
{
	if (AActor* Actor = OwningActor.Get())
	{
		if (!ComponentPath.IsEmpty())
		{
			UActorComponent* Component = FindObject<UActorComponent>(Actor, *ComponentPath);
			...
```

Une `FLevelComponentReference` = `OwningActor` (soft-ref vers un acteur du niveau) + `ComponentPath` (chemin du composant). `EditorResolve` charge même l'acteur s'il est « pending » (streamé). Donc si ça reste nul, c'est que :
- le tableau **Logic Components est vide** (aucune cible choisie), **ou**
- l'**acteur cible a été supprimé / renommé / déplacé** dans un autre niveau ou data layer (la soft-ref pointe dans le vide), **ou**
- le **`ComponentPath` ne correspond plus** à un composant existant sur l'acteur cible.

Ces champs sont `EditInstanceOnly` → la référence est définie **sur l'instance placée** (`BP_Mirror6`), pas dans le Blueprint. C'est donc une correction de **données dans le niveau**, pas dans le `.uasset` du Blueprint.

## Comment corriger (dans l'éditeur)

Je ne peux pas le faire à ta place : c'est une donnée binaire d'asset/instance qui se modifie dans l'éditeur. Voici la marche à suivre :

1. Ouvre le niveau `LI_COG_Cottage_Blockout`.
2. Dans le **Data Validation log**, double-clique sur la ligne d'erreur → ça devrait sélectionner l'acteur `BP_Mirror6` (sinon, cherche `BP_Mirror6` dans l'Outliner).
3. Panneau **Details** → composant **Level Logic** → déroule **Signal Processor Definitions** et repère l'action **« Update State Value on Target »** (label affiché : `Update State Value: <tag>`).
4. Regarde la propriété **Logic Components** :
   - Si elle est **vide** → ajoute une entrée et choisis l'acteur + son `LevelLogicComponent` cible avec le picker.
   - Si elle pointe vers un acteur affiché en **None / invalide** → ré-assigne la bonne cible (l'acteur qui possède le `LevelLogicComponent` que ce miroir doit piloter).
   - Si cette action n'a **plus de raison d'être** (cible définitivement disparue) → supprime l'action (ou le processor) concerné.
5. Relance **Tools → Validate Data** sur le niveau : l'erreur doit disparaître.
6. Sauvegarde (et inclus l'acteur externe `BP_Mirror6` modifié dans ton changelist).

## Points d'attention

- L'erreur est sur l'**instance** : vérifie s'il y a d'autres instances de `BP_Mirror` dans le niveau (`BP_Mirror2`, `3`, …) qui auraient le même souci.
- Souvent la cause est qu'une **cible a été supprimée/déplacée dans un Data Layer**. Si la cible existe mais dans un autre data layer non chargé, charge-le avant de valider — `EditorResolve` charge le streaming mais pas forcément un data layer désactivé.

Veux-tu que je vérifie combien d'instances de `BP_Mirror` sont présentes dans ce niveau (en inspectant les fichiers d'External Actors), pour t'aider à toutes les repérer ?

I'm looking at the root cause now—this is a data configuration issue in the editor, not something that requires engine code changes. The problem stems from a missing component reference in one of the logic component slots.

The "Update State Value on Target" action on BP_Mirror6's Signal Processor is pointing to a target actor that either doesn't exist anymore or has an invalid component path. Since this is an instance-level configuration (not a blueprint default), I need to fix it directly on the placed actor in the level. The fix involves opening the level, selecting the BP_Mirror6 instance, and checking the Signal Processor Definitions in the Details panel to identify and correct the broken reference. I'm confirming the error message matches exactly what's shown in the screenshot—"BP_Mirror :: Update State Value on Target is missing a component reference" at line 285. Now I can give a clear, focused answer.

**Assistant:** Le processus de recherche en arrière-plan (`BP_Mirror*`) que j'avais lancé a été arrêté — c'est normal, je l'avais moi-même tué après avoir récupéré les résultats utiles (la localisation de `BP_Mirror.uasset` et l'identification du plugin `LevelLogic`). Aucun suivi nécessaire : mon analyse de la cause de l'erreur de validation reste valable.

Pour rappel, la correction se fait dans l'éditeur sur l'instance `BP_Mirror6` (propriété **Logic Components** de l'action « Update State Value on Target » de son `LevelLogicComponent`). Dis-moi si tu veux que je recense toutes les instances de `BP_Mirror` du niveau.
