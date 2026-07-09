@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM  WorldPartitionRuleBuilder processing for a list of LIs
REM ============================================================

REM --- Adjust to match your installation ----------------------
REM Path to the executable (UnrealEditor-Cmd.exe) and the .uproject
set "EDITOR_CMD=D:\Sun\Engine\Binaries\Win64\UnrealEditor-Win64-DebugGame.exe"
set "UPROJECT=D:\Sun\Sundance\Sundance.uproject"

REM Shared arguments (containing the <LI_NAME> placeholder)
set "ARGS=-LogCmds=\"Global none,LogWorldPartitionRules display,LogWorldPartitionRuleBuilder display,LogWorldPartitionBuilder warning,LogCommandletPackageHelper error\" -run=WorldPartitionBuilderCommandlet -Builder=WorldPartitionRuleBuilder -DataLayerRules -HLODLayerRules -RuntimeGridRules -ContainOutlinerPathSubstrings=\"\" -DiscardOutlinerPathSubstrings=\"\" -BuildMachine -Unattended <LI_NAME>"

REM --- List of Level Instances to process ---------------------
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

REM --- Processing loop -----------------------------------------
for %%L in (%LI_LIST%) do (
    echo.
    echo ============================================================
    echo  Processing: %%L
    echo ============================================================

    REM Replace <LI_NAME> with the name of the current LI
    set "CURRENT_ARGS=!ARGS:<LI_NAME>=%%L!"

    echo "%EDITOR_CMD%" "%UPROJECT%" !CURRENT_ARGS!
    "%EDITOR_CMD%" "%UPROJECT%" !CURRENT_ARGS!

    if errorlevel 1 (
        echo [ERROR] Processing of %%L failed ^(code !errorlevel!^).
    ) else (
        echo [OK] %%L processed successfully.
    )
)

echo.
echo ============================================================
echo  Processing complete.
echo ============================================================

endlocal
pause
