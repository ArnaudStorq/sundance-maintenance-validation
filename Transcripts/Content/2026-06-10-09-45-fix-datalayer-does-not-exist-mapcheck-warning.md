# Fix Datalayer Does Not Exist Mapcheck Warning

- Date: 2026-06-10 09:45
- Source transcript: `c6abda91-20bd-4854-acaf-5b151ab3e184`

---

### User

comment corriger ce warning dans les mapchecks 
LI_VAR_01 is assigned to DataLayer 'DL_M_VAR_01' that doesn't exist in the AWorldDataLayers. Please add this DataLayer to your level or remove it from the actor to avoid unexpected behavior. Fix It!

**Assistant:** Je vais d'abord vérifier le contexte du workspace pour mieux comprendre ce qui est disponible.

<details><summary>Tools used</summary>

- `Shell` List workspace contents
- `Shell` List workspace directory contents
- `Shell` List AI directory contents

</details>

**Assistant:** Le workspace semble vide. Pas de souci, je peux répondre à votre question sur ce warning d'Unreal Engine basé sur la connaissance du problème.

## Comprendre le warning

Ce warning des **Map Checks** d'Unreal Engine signifie qu'un acteur (`LI_VAR_01`) dans votre niveau est assigné à un **Data Layer** (`DL_M_VAR_01`) qui n'existe pas — ou plus — dans le `WorldDataLayers` de votre niveau (ou du World Partition).

Causes fréquentes :
- Le Data Layer a été supprimé/renommé après que des acteurs y aient été assignés.
- L'acteur a été copié/migré depuis un autre niveau qui contenait ce Data Layer.
- Le `WorldDataLayers` actor du niveau n'a pas été sauvegardé après la création du Data Layer.
- Référence à un Data Layer d'un sous-niveau / world non chargé.

## Solutions

### Solution 1 — Utiliser le "Fix It!" automatique (le plus simple)

Le message se termine par **« Fix It! »** parce que l'éditeur propose une correction automatique :

1. Ouvrez la fenêtre **Map Check** : `Build > Map Check` (ou `Window > Developer Tools > Map Check`).
2. Cliquez sur le lien **« Fix It! »** à la fin de la ligne du warning.
3. Cela va **retirer la référence au Data Layer manquant** sur l'acteur `LI_VAR_01`.
4. Sauvegardez l'acteur (ou le niveau).

C'est l'option recommandée si vous **n'avez plus besoin** du Data Layer `DL_M_VAR_01` sur cet acteur.

### Solution 2 — (Re)créer le Data Layer manquant

Si l'acteur **doit** rester dans ce Data Layer :

1. Ouvrez **Window > World Partition > Data Layers Outliner** (ou **Data Layers** selon la version d'UE).
2. Vérifiez la présence du `WorldDataLayers` dans l'Outliner (sinon il sera créé automatiquement).
3. Clic droit dans la fenêtre Data Layers > **Create New Data Layer** (Runtime ou Editor selon le besoin).
4. Nommez-le **exactement** `DL_M_VAR_01` (le nom doit correspondre à la référence — attention, c'est généralement le `DataLayer Asset` qui est référencé, donc créez/assignez l'asset portant ce nom dans `Content`, puis ajoutez-le au `WorldDataLayers` du niveau).
5. Sauvegardez le niveau.

> Note UE5 : depuis UE5, les Data Layers sont basés sur des **DataLayerAsset** (UAsset) qu'on instancie ensuite dans le `AWorldDataLayers` du niveau via une `DataLayerInstance`. Le nom `DL_M_VAR_01` peut donc référencer soit l'asset, soit l'instance — assurez-vous que l'asset existe **et** est ajouté au `WorldDataLayers` du niveau courant.

### Solution 3 — Retirer manuellement le Data Layer de l'acteur

1. Sélectionnez l'acteur `LI_VAR_01` dans l'Outliner.
2. Dans le **Details panel**, section **Data Layers**, retirez `DL_M_VAR_01`.
3. Sauvegardez l'acteur.

### Solution 4 — Cas du World Partition / sous-niveaux

Si vous travaillez avec **World Partition** ou des **Level Instances** :
- Vérifiez que le bon **niveau** est ouvert (le `WorldDataLayers` est par niveau).
- Si `LI_VAR_01` est dans un *Level Instance*, ouvrez ce sous-niveau et appliquez le fix dedans.
- Pensez à faire un **Build Data Layers** si la version d'UE l'exige.

## Recommandation

Dans 90 % des cas, le **« Fix It! »** intégré suffit — il nettoie proprement la référence orpheline. Ne créez un nouveau Data Layer que si la logique gameplay/streaming en dépend réellement.

Si vous me dites votre version d'Unreal Engine et le contexte (Data Layer supprimé volontairement ou non), je peux vous donner la procédure exacte adaptée.
