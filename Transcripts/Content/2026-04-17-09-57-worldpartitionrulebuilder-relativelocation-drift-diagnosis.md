# Worldpartitionrulebuilder Relativelocation Drift Diagnosis

- Date: 2026-04-17 09:57
- Source transcript: `83abcd27-28c7-4c46-b918-9a69067451c7`

---

### User

es-tu disponible ?


---

### User

es-tu dispo ?


---

### User

es-tu dispo >

**Assistant:** Oui, je suis disponible. Dis-moi ce sur quoi tu veux travailler.

[REDACTED]


---

### User

Tu trouveras dans le fichier  C:\Users\Arnaud.Storq\Downloads\FRIDAY_OK.log le resultat du processing de UWorldPartitionRuleBuilder (D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp) avec bActivateBug = false

Tu trouveras dans le fichier  C:\Users\Arnaud.Storq\Downloads\FRIDAY_KO.log le resultat du processing de UWorldPartitionRuleBuilder (D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp) avec bActivateBug = true

Explique moi pourquoi avec bActivateBug = true on a les messages "Found different RelativeLocation/RelativeRotation for actor" qui s'affichent, aide-moi a trouver le probleme.

**Assistant:** Examinant les journaux et le code source pour expliquer la différence.

[REDACTED]

<details><summary>Tools used</summary>

- `Read` C:\Users\Arnaud.Storq\Downloads\FRIDAY_OK.log
- `Read` C:\Users\Arnaud.Storq\Downloads\FRIDAY_KO.log
- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp

</details>

**Assistant:** Cherchant dans les journaux les messages pertinents et le contexte.

[REDACTED]

<details><summary>Tools used</summary>

- `Grep` Found different RelativeLocation
- `Grep` Found different RelativeLocation
- `Grep` LI_Hogwarts|Ravenclaw

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Read` C:\Users\Arnaud.Storq\Downloads\FRIDAY_KO.log
- `Read` C:\Users\Arnaud.Storq\Downloads\FRIDAY_OK.log

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` Saved [0-9]+ dirty packages
- `Grep` Saved [0-9]+ dirty packages

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` Saved [0-9]+ dirty packages

</details>

**Assistant:** Voici ce qui se passe, d’après le code et les deux logs.

## Ce que fait vraiment le message

`CheckActorTransformsFromDisk()` (appelée depuis `SaveModifiedPackages`) compare :

1. **« Current »** : l’acteur **déjà en mémoire**, tel qu’il est dans l’éditeur au moment du save.
2. **« Original »** : le même acteur rechargé **seul** depuis le `.uasset` dans un package temporaire (load isolé).

Les deux utilisent `RootComponent->GetRelativeLocation()` / `GetRelativeRotation()`.

## Ce que montrent tes logs (KO)

Exemple typique :

- **Current** : coordonnées très grandes (ex. `X=10341 Y=-74973 Z=4330`) — typique d’un repère **monde / chaîne de parents** du niveau parent.
- **Original** : valeurs plus « petites » (ex. `X=-11499 Y=2209 Z=124`) — cohérent avec ce qui est **sérialisé** dans le package externe pour le sous-niveau partitionné.

Les écarts de rotation du type ~30° entre Current et Original vont aussi dans le sens d’une **composition avec la transform du Level Instance** (ou un repère différent), pas d’une petite dérive numérique.

Donc le message ne dit pas forcément « le save a cassé la transform » ; il dit surtout : **« la transform relative lue en mémoire ne correspond pas à celle qu’on obtient en rechargeant le même fichier tout seul »**.

## Lien avec le Level Instance en mode édition

Dans `HandleLevelInstanceRecursive`, `SaveModifiedPackages` est appelée **à l’intérieur** du scope qui a fait `EditLevelInstance` :

```572:607:D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp
	{
		const FLevelInstanceEditScope EditScope(Subsystem, LevelInstance);
		// ...
		ProcessActorsInWorldPartition(InnerWorldPartition, World, PackageHelper);
		// Save any package changes before processing nested level instances
		SaveModifiedPackages(PackageHelper);
	}
```

Tant que ce mode édition est actif, la scène des acteurs **internes** au LI n’est pas la même que celle d’un acteur chargé **isolément** depuis son `.uasset`. Du coup, comparer `GetRelativeLocation` / `GetRelativeRotation` live vs reload isolé est **souvent une comparaison entre deux repères** — d’où les gros écarts que tu vois.

## Pourquoi `bActivateBug = true` fait apparaître les messages et pas l’autre run

Ce n’est pas que Hogwarts « invente » une autre logique de transform pour Hogsmeade ; c’est surtout que **le run KO modifie et sauvegarde beaucoup plus de packages** que le run OK.

- **KO** : au moins `Saved 11 dirty packages` puis `Saved 20 dirty packages` → `CheckActorTransformsFromDisk` s’exécute sur ces lots et tombe sur des acteurs LI_Hogsmeade / etc.
- **OK** : une seule ligne du type **`Saved 2 dirty packages`** dans tout le log → presque aucun passage dans cette vérif avec des acteurs « sensibles », donc **aucun** `Found different RelativeLocation/RelativeRotation`.

En activant `LI_Hogwarts` / `LI_RavenclawTower_INT`, tu fais énormément de travail en plus, donc beaucoup plus d’acteurs marqués dirty et beaucoup plus d’appels à `SaveModifiedPackages` **pendant** des sessions `EditLevelInstance` — ce qui **révèle** le problème de la comparaison, qui était déjà conceptuellement biaisée.

## Piste de correction (côté outil, pas côté données)

- **Ne pas** appeler `CheckActorTransformsFromDisk` tant qu’un LI est encore en mode édition ; en sortir du scope (ou reporter save + check après `CommitLevelInstance`).
- Ou comparer quelque chose d’invariant : par ex. transform **monde** des deux côtés, ou données du **descriptor** World Partition plutôt que le reload isolé du package.
- Ou ignorer / filtrer les acteurs dont le monde / le conteneur est un LI actuellement ouvert en édition.

En résumé : les messages viennent d’une **vérif qui mélange deux contextes de chargement** (édition de Level Instance vs asset isolé), et `bActivateBug = true` augmente fortement le volume de saves qui passent dans cette vérif, donc tu les vois partout dans le log KO.

[REDACTED]
