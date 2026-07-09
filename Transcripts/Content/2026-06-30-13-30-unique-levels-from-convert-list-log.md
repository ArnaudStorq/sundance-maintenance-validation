# Unique Levels From Convert List Log

- Date: 2026-06-30 13:30
- Source transcript: `e6292e5a-0365-4efa-abc9-6b4bb6aab950`

---

### User

dans moi la liste unique des levels referencés dans C:\Users\Arnaud.Storq\Downloads\list levels restant a convertir_tuesday.txt
par exemple pour une ligne [2026.06.30-12.19.36:906][832]LogAvaStreamingGeneration: Verbose: Skipped RuntimeGrid override ('None' -> 'SmallGrid') for actor 'SM_LON_DA_Crate_01_Books_BLK9' in level '/Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Entrance': rule 'DA_SmallGrid_Rules' cannot use HLOD layer 'LV_Overland_HLODLayer_Near' on that partition
je veux /Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Entrance suivi du nombre d'occurences

**Assistant:** Je vais analyser le fichier pour extraire la liste unique des levels avec leur nombre d'occurrences.

I need to extract the unique levels from the file along with how many times each one appears, so I'm looking for all instances of the pattern `in level '...'` and pulling out what's inside those quotes.

<details><summary>Tools used</summary>

- `Shell` Extract unique levels with occurrence counts

</details>

**Assistant:** Le quoting pose problème. Je vais écrire un petit script.

I'll switch to writing a script file to handle this more cleanly.

<details><summary>Tools used</summary>

- `Write` d:\Sandbox\AI\extract_levels.ps1
- `Shell` Run the level extraction script

</details>

**Assistant:** Voici la liste unique des levels référencés (via `in level '...'`), avec le nombre d'occurrences, triée par fréquence décroissante :

| Occurrences | Level |
|---|---|
| 2598 | `/Game/Levels/Overland/Hogsmeade/Bridges/LI_GEN_Bridge_B` |
| 736 | `/Game/Levels/Overland/Hogsmeade/Bridges/LI_GEN_Bridge_A` |
| 361 | `/Game/Levels/Overland/Hogsmeade/Bridges/LI_GEN_Bridge_C_B` |
| 350 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Poachers_Crate_PuffskeinFur` |
| 243 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_DragonClaw` |
| 212 | `/Game/Levels/Overland/Hogsmeade/Bridges/LI_GEN_Bridge_C` |
| 204 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_UnicornHorn_B` |
| 123 | `/Game/Levels/Overland/Camps/Poacher/Meshes/LI_Crate_Poachers_UnicornHorn_A` |
| 99 | `/Game/Environment/LevelAssemblies/Rocks/Cluster/LA_Rock_Cluster_Pine_Small_A` |
| 88 | `/Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Entrance` |
| 47 | `/Game/Environment/Population/Camp/LI_Camp_Storage_B` |
| 32 | `/Game/Environment/Nature/Mounds_Woodland/LevelAssemblies/LA_Mound_Woodland_A01` |
| 29 | `/Game/Levels/Overland/Ruins/Castle_Saints/LI_Castle_Brath_Walls_B` |
| 28 | `/Game/Environment/Population/Camp/LI_Camp_Furnace_A` |
| 17 | `/Game/Experimental/Levels/Vault/Vault_Resource_Platforming_01/LI_Resource_Horklump_01` |
| 12 | `/Game/Environment/Population/Camp/LI_Camp_Storage_G` |
| 6 | `/Game/Levels/Overland/Ruins/Castle_Saints/LI_Castle_Brath_Annex_A` |
| 4 | `/Game/Experimental/Levels/Vault/Vault_Resource_Cave_MoonStone_01/LI_Vault_Resource_Cave_Moon_01` |
| 3 | `/Game/Environment/Road/LevelActors/Scatter_Meshes/LA_Central_Mound_02` |
| 2 | `/Game/Experimental/Levels/Vault/Vault_Resource_Cave_MoonStone_01/LI_Vault_Resource_Cave_Moon_A` |
| 2 | `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Manor_Blockout` |
| 1 | `/Game/Experimental/Levels/Vault/Vault_Academic_Rune_01/LI_Vault_Academic_Rune_01` |
| 1 | `/Game/Experimental/Levels/Overland/Ruins/LI_HV_A02_Ruins_Redcaps` |
| 1 | `/Game/Experimental/Levels/Overland/COG_Mission/LI_COG_Cottage_Blockout` |

**24 levels uniques** au total. Je supprime le script temporaire.

Now I'm organizing the script and getting ready to show the results.

<details><summary>Tools used</summary>

- `Delete` d:\Sandbox\AI\extract_levels.ps1

</details>

**Assistant:** Pour ton exemple, `/Game/Levels/Dungeons/COG_01_Dungeon/LI_Dun_COG_01_Entrance` apparaît **88 fois**.
