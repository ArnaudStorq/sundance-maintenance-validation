@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  Traitement WorldPartitionRuleBuilder pour une liste de LI
REM ============================================================

REM --- A adapter selon votre installation ---------------------
REM Chemin vers l'executable (UnrealEditor-Cmd.exe) et le .uproject
set "EDITOR_CMD=D:\Sun\Engine\Binaries\Win64\UnrealEditor-Win64-DebugGame.exe"
set "UPROJECT=D:\Sun\Sundance\Sundance.uproject"

REM Arguments communs (contenant le marqueur <NOM_DU_LI>)
set "ARGS=-LogCmds=\"Global none,LogWorldPartitionRules display,LogWorldPartitionRuleBuilder display,LogWorldPartitionBuilder warning,LogCommandletPackageHelper error\" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionRuleBuilder -DataLayerRules -HLODLayerRules -RuntimeGridRules -ContainOutlinerPathSubstrings=\"\" -DiscardOutlinerPathSubstrings=\"\" -BuildMachine -Unattended <NOM_DU_LI>"

REM --- Liste des Level Instances a traiter --------------------
set LI_LIST=^
 LI_Crate_Poachers_DragonClaw^
 LI_Crate_Poachers_UnicornHorn_B^
 LI_Crate_Poachers_UnicornHorn_A^
 LI_Resource_Horklump_01^
 LI_Castle_Brath_Annex_A^
 LI_COG_Manor_Blockout^
 LI_HV_A02_Ruins_Redcaps^
 LI_Dun_COG_01_Entrance^
 LI_Hamlets_GransHouse_EXT_Rock_A^
 LI_Hamlets_GransHouse_EXT_Rock_B^
 LI_Hamlets_GransHouse_EXT_Rock_C^
 LI_Camp_StorageLarge_E^
 LI_Camp_WoodenBox_A^
 LI_COG_Cottage_Blockout

REM --- Boucle de traitement -----------------------------------
for %%L in (%LI_LIST%) do (
    echo.
    echo ============================================================
    echo  Traitement de : %%L
    echo ============================================================

    REM Remplace <NOM_DU_LI> par le nom du LI courant
    set "CURRENT_ARGS=!ARGS:<NOM_DU_LI>=%%L!"

    echo "%EDITOR_CMD%" "%UPROJECT%" !CURRENT_ARGS!
    "%EDITOR_CMD%" "%UPROJECT%" !CURRENT_ARGS!

    if errorlevel 1 (
        echo [ERREUR] Le traitement de %%L a echoue ^(code !errorlevel!^).
    ) else (
        echo [OK] %%L traite avec succes.
    )
)

echo.
echo ============================================================
echo  Traitement termine.
echo ============================================================

endlocal
pause
