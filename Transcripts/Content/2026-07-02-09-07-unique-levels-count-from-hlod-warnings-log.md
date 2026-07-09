# Unique Levels Count From Hlod Warnings Log

- Date: 2026-07-02 09:07
- Source transcript: `59d15194-c77c-4ec9-99cd-d18f0316b45b`

---

### User

donne moi la liste les Levels unique (et le nombre d'occurences) trouvés dans ce log :
D:\Sandbox\HLODLayerWarnings_Thursday.txt

**Assistant:** I need to read through the file and identify how many distinct Level values are present.

<details><summary>Tools used</summary>

- `Read` D:\Sandbox\HLODLayerWarnings_Thursday.txt

</details>

**Assistant:** Je vais extraire les niveaux avec PowerShell et compter les occurrences.

I'll use PowerShell to extract the level names and count how many times each one appears.

<details><summary>Tools used</summary>

- `Shell` Extract and count unique levels from log

</details>

**Assistant:** Voici les **18 Levels uniques** trouvés dans le log, triés par nombre d'occurrences :

| Occurrences | Level |
|---:|---|
| 350 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Poachers_Crate_PuffskeinFur` |
| 243 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_DragonClaw` |
| 204 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_UnicornHorn_B` |
| 123 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_UnicornHorn_A` |
| 99 | `/Game/Environment/LevelAssemblies/Rocks/Cluster/LA_Rock_Cluster_Pine_Small_A` |
| 88 | `/Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Entrance` |
| 47 | `/Game/Environment/Population/Camp/LI_Camp_Storage_B` |
| 29 | `/Game/Levels/Overland/Ruins/Castle_Saints/LI_Castle_Brath_Walls_B` |
| 28 | `/Game/Environment/Population/Camp/LI_Camp_Furnace_A` |
| 17 | `/Game/Experimental/Levels/Vault/Vault_Resource_Platforming_01/LI_Resource_Horklump_01` |
| 12 | `/Game/Environment/Population/Camp/LI_Camp_Storage_G` |
| 6 | `/Game/Levels/Overland/Ruins/Castle_Saints/LI_Castle_Brath_Annex_A` |
| 3 | `/Game/Environment/Road/LevelActors/Scatter_Meshes/LA_Central_Mound_02` |
| 2 | `/Game/Experimental/Levels/Vault/Vault_Resource_Cave_MoonStone_01/LI_Vault_Resource_Cave_Moon_A` |
| 2 | `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Manor_Blockout` |
| 1 | `/Game/Experimental/Levels/Vault/Vault_Academic_Rune_01/LI_Vault_Academic_Rune_01` |
| 1 | `/Game/Experimental/Levels/Overland/Ruins/LI_HV_A02_Ruins_Redcaps` |
| 1 | `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Cottage_Blockout` |

**Total : 18 levels uniques**, pour **1256 lignes** de warnings au total.

I'm looking at the results now—there are 18 distinct levels total.
