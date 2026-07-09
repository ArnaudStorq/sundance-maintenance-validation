# Replace Getactorfolderdesc With Getpath

- Date: 2026-05-26 13:08
- Source transcript: `535c5a5f-ba37-4482-8693-47ef12ead1ef`

---

### User

j'ai ce code. remplace l'utilisation de FActorFolderDescsContext::GetActorFolderDesc par FActorFolderDesc::GetPath

void UWorldPartitionFixupActorFoldersBuilder::FindDuplicatePaths(const TArray<FActorFolderEntry>& AllFolders, TArray<FDuplicatedActorFolderEntry>& OutDuplicates) const
{
// First, we create a map LevelPackage<>TArray<ActorFolderEntry>
// (in other words, we regroup ActorFolders by Levels)
TMap<FString, TArray<const FActorFolderEntry*>> LevelToEntries;
for (const FActorFolderEntry& ActorFolderEntry : AllFolders)
{
LevelToEntries.FindOrAdd(ActorFolderEntry.OuterLevelPackage).Add(&ActorFolderEntry);
}

// Then for each Levels...
for (auto& LevelToEntryPair : LevelToEntries)
{
// Retrieve the list of Actor Folders in this level
const TArray<const FActorFolderEntry*>& ActorFolderEntries = LevelToEntryPair.Value;

// Per-Level FActorFolderDescsContext used by BuildFolderPath
TOptional<FActorFolderDescsContext> BuildFolderPathLevelContext;

// Create a map FolderPath<>TArray<FActorFolderEntry*> to find duplicated paths
TMap<FString, TArray<const FActorFolderEntry*>> PathGroups;
for (const FActorFolderEntry* ActorFolderEntry: ActorFolderEntries)
{
if (ActorFolderEntry->bIsDeleted)
{
// Skip deleted Actor Folder
continue;
}

const FString FolderPath = BuildFolderPath(*ActorFolderEntry, BuildFolderPathLevelContext);
if (FolderPath.IsEmpty())
{
// Skip wrong paths
continue;
}

// Add this Actor Folder Entry to the group of the corresponding path
PathGroups.FindOrAdd(FolderPath).Add(ActorFolderEntry);
}

for (auto& PathGroupPair : PathGroups)
{
const FString FolderPath = PathGroupPair.Key;
TArray<const FActorFolderEntry*>& PathActorFolderEntries = PathGroupPair.Value;

// 0 or 1 Actor Folder found for a path? Good, it means no multiple GUIDs for the same path, so let's skip it (no duplicates found)
if (PathActorFolderEntries.Num() <= 1)
{
continue;
}

// Let's sort by FolderGuid to guarantee determinism (we want the same entry to be chosen as the "replacing" one across different runs)
PathActorFolderEntries.Sort([](const FActorFolderEntry& A, const FActorFolderEntry& B)
{
return A.FolderGuid.ToString().Compare(B.FolderGuid.ToString(), ESearchCase::CaseSensitive) < 0;
});

//
const FActorFolderEntry* ReplacingEntry = PathActorFolderEntries[0];
for (int32 ActorFolderIndex = 1; ActorFolderIndex < PathActorFolderEntries.Num(); ++ActorFolderIndex)
{
FDuplicatedActorFolderEntry DuplicatedActorFolderEntry;
DuplicatedActorFolderEntry.Folder = *PathActorFolderEntries[ActorFolderIndex];
DuplicatedActorFolderEntry.ReplacingGuid = ReplacingEntry->FolderGuid;
DuplicatedActorFolderEntry.ResolvedPath = FolderPath;
OutDuplicates.Add(MoveTemp(DuplicatedActorFolderEntry));
}
}
}
}

FString UWorldPartitionFixupActorFoldersBuilder::BuildFolderPath(const FActorFolderEntry& Entry, TOptional<FActorFolderDescsContext>& BuildFolderPathLevelContext) const
{
if (!BuildFolderPathLevelContext.IsSet())
{
const FActorFolderDesc ActorFolderDesc = UActorFolder::GetAssetRegistryInfoFromPackage(Entry.PackageName);
BuildFolderPathLevelContext.Emplace(ActorFolderDesc);
}

const FActorFolderDesc* EntryDesc = BuildFolderPathLevelContext->GetActorFolderDesc(Entry.FolderGuid);
if (EntryDesc == nullptr)
{
return FString();
}
return EntryDesc->GetPath();
}

**Assistant:** Je vais analyser le code pour comprendre la structure actuelle et faire le remplacement demandé.

<details><summary>Tools used</summary>

- `Glob` **/WorldPartitionFixupActorFoldersBuilder*
- `Glob` **/*FixupActorFolders*
- `Grep` FindDuplicatePaths

</details>

**Assistant:** Le fichier n'est pas dans le workspace. Je vais analyser le code que vous avez fourni directement.

En regardant le code, voici la situation actuelle:

```cpp
const FActorFolderDesc* EntryDesc = BuildFolderPathLevelContext->GetActorFolderDesc(Entry.FolderGuid);
if (EntryDesc == nullptr)
{
    return FString();
}
return EntryDesc->GetPath();
```

`FActorFolderDescsContext::GetActorFolderDesc(FolderGuid)` retourne un `FActorFolderDesc*` à partir d'un `FGuid`, puis on appelle `GetPath()` dessus.

La signature de `FActorFolderDesc::GetPath` est probablement différente — elle prend probablement directement le contexte et le guid pour résoudre le chemin (probablement parce que `GetPath` doit remonter la hiérarchie des parents via le contexte).

Vérifions la signature attendue:

<details><summary>Tools used</summary>

- `WebSearch` FActorFolderDesc GetPath FActorFolderDescsContext Unreal Engine
- `WebSearch` "FActorFolderDesc::GetPath" "FActorFolderDescsContext" Unreal source

</details>

**Assistant:** Cherchons directement la signature dans le code source d'Unreal:

<details><summary>Tools used</summary>

- `WebFetch` https://github.com/EpicGames/UnrealEngine/blob/release/Engine/Source/Runtime/Engine/Public/ActorFolder.h
- `WebSearch` "FActorFolderDesc" "GetPath" "FActorFolderDescsContext&" github source

</details>

**Assistant:** Cherchons sur GitHub directement:

<details><summary>Tools used</summary>

- `WebFetch` https://github.com/search?q=%22FActorFolderDesc%22+%22GetPath%22+%22FActorFolderDescsContext%22&type=code
- `WebFetch` https://github.com/chenyong2github/UnrealEngine/blob/c865e168/Engine/Source/Runtime/Engine/Public/ActorFolder.h
- `WebFetch` https://github.com/chenyong2github/UnrealEngine/raw/c865e168/Engine/Source/Runtime/Engine/Public/ActorFolderDesc.h

</details>

**Assistant:** Maintenant je regarde l'implémentation pour voir comment GetPath fonctionne et confirmer la nouvelle signature:

<details><summary>Tools used</summary>

- `WebFetch` https://github.com/chenyong2github/UnrealEngine/raw/c865e168/Engine/Source/Runtime/Engine/Private/ActorFolderDesc.cpp

</details>

**Assistant:** Parfait, j'ai maintenant toute l'information nécessaire. Voici ce que j'ai compris:

**Signatures existantes:**
- `FActorFolderDescsContext::GetActorFolderDesc(const FGuid& InFolderGuid)` → retourne un `const FActorFolderDesc*` à partir d'un GUID.
- `FActorFolderDesc::GetPath() const` → retourne le chemin complet du folder en remontant la hiérarchie via un `FActorFolderDescsContext` créé en interne.

**Point important:** `FActorFolderDesc::GetPath()` crée son propre `FActorFolderDescsContext` à chaque appel (qui re-scanne l'asset registry). C'est donc coûteux. Dans le code actuel, le `BuildFolderPathLevelContext` est conservé entre les itérations pour mutualiser ce coût par niveau.

Je vais maintenant faire le remplacement demandé. Il faut faire attention à ce que la mutualisation du contexte par niveau soit perdue avec la nouvelle approche (puisque `GetPath()` crée son propre contexte). Mais comme c'est ce que vous avez explicitement demandé, je remplace l'utilisation comme requis.

Voici le code modifié:

```cpp
void UWorldPartitionFixupActorFoldersBuilder::FindDuplicatePaths(const TArray<FActorFolderEntry>& AllFolders, TArray<FDuplicatedActorFolderEntry>& OutDuplicates) const
{
	// First, we create a map LevelPackage<>TArray<ActorFolderEntry>
	// (in other words, we regroup ActorFolders by Levels)
	TMap<FString, TArray<const FActorFolderEntry*>> LevelToEntries;
	for (const FActorFolderEntry& ActorFolderEntry : AllFolders)
	{
		LevelToEntries.FindOrAdd(ActorFolderEntry.OuterLevelPackage).Add(&ActorFolderEntry);
	}

	// Then for each Levels...
	for (auto& LevelToEntryPair : LevelToEntries)
	{
		// Retrieve the list of Actor Folders in this level
		const TArray<const FActorFolderEntry*>& ActorFolderEntries = LevelToEntryPair.Value;

		// Create a map FolderPath<>TArray<FActorFolderEntry*> to find duplicated paths
		TMap<FString, TArray<const FActorFolderEntry*>> PathGroups;
		for (const FActorFolderEntry* ActorFolderEntry : ActorFolderEntries)
		{
			if (ActorFolderEntry->bIsDeleted)
			{
				// Skip deleted Actor Folder
				continue;
			}

			const FString FolderPath = BuildFolderPath(*ActorFolderEntry);
			if (FolderPath.IsEmpty())
			{
				// Skip wrong paths
				continue;
			}

			// Add this Actor Folder Entry to the group of the corresponding path
			PathGroups.FindOrAdd(FolderPath).Add(ActorFolderEntry);
		}

		for (auto& PathGroupPair : PathGroups)
		{
			const FString FolderPath = PathGroupPair.Key;
			TArray<const FActorFolderEntry*>& PathActorFolderEntries = PathGroupPair.Value;

			// 0 or 1 Actor Folder found for a path? Good, it means no multiple GUIDs for the same path, so let's skip it (no duplicates found)
			if (PathActorFolderEntries.Num() <= 1)
			{
				continue;
			}

			// Let's sort by FolderGuid to guarantee determinism (we want the same entry to be chosen as the "replacing" one across different runs)
			PathActorFolderEntries.Sort([](const FActorFolderEntry& A, const FActorFolderEntry& B)
			{
				return A.FolderGuid.ToString().Compare(B.FolderGuid.ToString(), ESearchCase::CaseSensitive) < 0;
			});

			//
			const FActorFolderEntry* ReplacingEntry = PathActorFolderEntries[0];
			for (int32 ActorFolderIndex = 1; ActorFolderIndex < PathActorFolderEntries.Num(); ++ActorFolderIndex)
			{
				FDuplicatedActorFolderEntry DuplicatedActorFolderEntry;
				DuplicatedActorFolderEntry.Folder = *PathActorFolderEntries[ActorFolderIndex];
				DuplicatedActorFolderEntry.ReplacingGuid = ReplacingEntry->FolderGuid;
				DuplicatedActorFolderEntry.ResolvedPath = FolderPath;
				OutDuplicates.Add(MoveTemp(DuplicatedActorFolderEntry));
			}
		}
	}
}

FString UWorldPartitionFixupActorFoldersBuilder::BuildFolderPath(const FActorFolderEntry& Entry) const
{
	const FActorFolderDesc ActorFolderDesc = UActorFolder::GetAssetRegistryInfoFromPackage(Entry.PackageName);
	if (ActorFolderDesc.GetFolderGuid() != Entry.FolderGuid)
	{
		return FString();
	}
	return ActorFolderDesc.GetPath();
}
```

### Résumé des changements

1. **`BuildFolderPath`** : la signature ne prend plus le paramètre `TOptional<FActorFolderDescsContext>& BuildFolderPathLevelContext`. La méthode :
   - Récupère directement le `FActorFolderDesc` du package via `UActorFolder::GetAssetRegistryInfoFromPackage(Entry.PackageName)`.
   - Vérifie que le GUID correspond bien à celui de l'entrée (équivalent du `GetActorFolderDesc(Entry.FolderGuid) == nullptr` qui servait à valider l'existence).
   - Appelle directement `FActorFolderDesc::GetPath()` sur le desc, qui s'occupe lui-même de remonter la hiérarchie en interne.

2. **`FindDuplicatePaths`** : suppression de la déclaration `TOptional<FActorFolderDescsContext> BuildFolderPathLevelContext;` et de son passage à `BuildFolderPath`.

### Attention - impact sur les performances

`FActorFolderDesc::GetPath()` instancie en interne un nouveau `FActorFolderDescsContext` à chaque appel, ce qui déclenche un scan de l'AssetRegistry. L'ancienne version mutualisait ce contexte par niveau (`BuildFolderPathLevelContext` créé une seule fois par `Level`), alors que la nouvelle version va le recréer pour chaque entrée. Si vous avez beaucoup de folders dans un même level, cela peut significativement ralentir le builder. Si la performance pose problème, il faudrait songer à exposer une variante de `GetPath()` qui accepte un `FActorFolderDescsContext` externe.
