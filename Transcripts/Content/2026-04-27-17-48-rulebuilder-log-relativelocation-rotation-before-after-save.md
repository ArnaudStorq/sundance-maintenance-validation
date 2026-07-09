# Rulebuilder Log Relativelocation Rotation Before After Save

- Date: 2026-04-27 17:48
- Source transcript: `c1b3c318-909a-47ba-ab77-821ca0071369`

---

### User

pour chacun des acteurs traités dans D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp, je veux que tu log : les valeurs de RelationLocation et RelativeRotation AVANT le loading (depuis le package), puis une fois loadé , puis apres la sauvegarde. Identifie les acteurs avec les outliner paths

le relative location ou rotation pour un acteur vient de son brush component, exemple : 

// Update the BrushComponent RelativeLocation
			if (BrushComponent->GetRelativeLocation() != PivotTransform.GetLocation())
			{
				BrushComponent->SetRelativeLocation(FVector(PivotLocX, PivotLocY, PivotLocZ));
				bModified = true;
			}

**Assistant:** Examinant le fichier C++ pour comprendre le flux (chargement, sauvegarde) et où insérer les logs.

[REDACTED]

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.cpp

</details>

**Assistant:** Examinant l'API World Partition et le descripteur d'acteur pour obtenir les transformes avant chargement, et le header de la classe.

[REDACTED]

<details><summary>Tools used</summary>

- `Read` D:\Sun\Sundance\Source\WorldBuildingEditor\WorldPartition\WorldPartitionRuleBuilder.h
- `Grep` ForEachActorWithLoading|FWorldPartitionActorDescInstance

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` ForEachActorWithLoading
- `Grep` class FWorldPartitionActorDescInstance|GetLocalBounds|GetPivot|Brush

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Glob` **/WorldPartitionHelpers.h
- `Glob` **/WorldPartitionActorDescInstance*.h

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` ForEachActorWithLoading

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `SemanticSearch`

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` ActorDescInstance

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` GetLocalBounds|GetEditorBounds|GetTransform

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `WebSearch` Find API for pre-loaded actor desc transform in World Partition.

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` WorldPartitionActorDesc
- `Grep` WorldPartitionActorDesc

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Shell` Locate WorldPartitionActorDesc.h on D drive

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Shell` Find WorldPartitionActorDesc.h path

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Source\Runtime\Engine\Public\WorldPartition\WorldPartitionActorDesc.h
- `Grep` GetBounds|Relative|Brush|EditorBounds|RuntimeBounds

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Source\Runtime\Engine\Public\WorldPartition\WorldPartitionActorDesc.h
- `Read` D:\Sun\Engine\Source\Runtime\Engine\Public\WorldPartition\WorldPartitionActorDescInstance.h

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` Brush|RelativeLocation|FWorldPartitionComponentDesc

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` CreateComponentDesc|BrushComponentDesc|FWorldPartition

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` CreateComponentDesc
- `Glob` **/BrushComponent.h

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Source\Runtime\Engine\Classes\Components\BrushComponent.h
- `Grep` CreateComponentDesc|ComponentDesc

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` SceneComponentDesc|RelativeLocation|FWorldPartition.*ComponentDesc

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` CreateComponentDesc|FWorldPartitionSceneComponentDesc

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Read` D:\Sun\Engine\Source\Runtime\Engine\Private\Components\ActorComponent.cpp

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` CreateClassComponentDesc

</details>

**Assistant:** [REDACTED]

<details><summary>Tools used</summary>

- `Grep` CreateClassComponentDesc|FWorldPartition

</details>
