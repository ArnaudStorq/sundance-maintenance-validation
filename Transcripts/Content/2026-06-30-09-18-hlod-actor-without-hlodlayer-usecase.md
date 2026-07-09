# Hlod Actor Without Hlodlayer Usecase

- Date: 2026-06-30 09:18
- Source transcript: `4f6fa566-9cea-4f64-8918-901ceec52eec`

---

### User

quel est l'interet dans UE pour un acteur d'est un HLOD mais sans avoir de HLODLayer ? decrit moi le use-case

**Assistant:** Bonne question, et la réponse dépend de la **version d'UE et du système HLOD** utilisé. Je pars du principe que tu parles du **HLOD de World Partition** (UE5), car c'est là que la distinction « HLOD relevant » vs « HLOD Layer assigné » est la plus parlante.

## Les deux réglages distincts sur un acteur

Il faut bien séparer deux propriétés qui n'ont rien à voir :

1. **`Is Spatially Loaded` / HLOD relevant** (`bEnableAutoLODGeneration`) → est-ce que l'acteur participe au système HLOD ?
2. **`HLOD Layer`** (`UHLODLayer*`) → dans *quel* layer son proxy va être généré, et *comment* (Instancing, Merged Mesh, Simplified Mesh, Approximated Mesh…).

Un acteur peut donc être « HLOD » (pertinent pour la génération) tout en ayant `HLOD Layer = None`. Ce n'est pas une contradiction.

## Ce que veut dire `HLOD Layer = None`

Quand un acteur est HLOD-relevant mais n'a **pas** de HLODLayer explicite, le builder de génération HLOD applique une règle de **fallback** :

- **Si le monde a un Default HLOD Layer** (défini dans les World Partition Settings) → l'acteur est intégré dans **ce layer par défaut**.
- **Si aucun default n'existe** → aucun proxy n'est généré pour cet acteur : il sera simplement *streamé/déchargé* à distance, sans représentation lointaine.

## Les use-cases concrets

**1. Le cas le plus fréquent : workflow par défaut (héritage global)**

Sur un open world, 90 % de tes static meshes doivent finir dans le même HLOD « générique » (un merge/simplify standard). Plutôt que d'assigner manuellement un layer à des milliers d'acteurs :

- tu définis **un Default HLOD Layer** au niveau du monde,
- tu laisses tous les acteurs « ordinaires » avec `HLOD Layer = None`.

Ils héritent automatiquement du layer par défaut. Tu ne réserves l'assignation explicite d'un HLODLayer **que** pour les acteurs spéciaux : un bâtiment héros qui mérite un Approximated Mesh, de la végétation qui doit rester en Instancing, un objet avec une draw distance différente, etc. → maintenance énormément simplifiée.

**2. L'acteur participe au cell loading mais ne doit PAS avoir de proxy lointain**

Si tu veux qu'un acteur soit géré par World Partition (chargé/déchargé selon la grille) mais qu'il **disparaisse purement et simplement** au-delà de la loading range — sans coût de génération ni de rendu d'un proxy — tu le laisses HLOD-relevant avec `None` **et** sans default applicable. Typique pour :
- petits props / clutter de gameplay sans intérêt visuel à distance,
- objets dynamiques ou interactifs,
- éléments dont un proxy mergé n'apporterait rien (trop petits pour être vus de loin).

**3. Souplesse de pipeline / itération**

Laisser `None` permet de **changer la stratégie HLOD globalement** en modifiant juste le Default HLOD Layer du monde, sans rééditer chaque acteur. Pratique en début de projet quand la stratégie HLOD n'est pas figée.

## En résumé

Être « HLOD » sans HLODLayer n'est pas un oubli : c'est le mécanisme d'**héritage du layer par défaut** du monde. L'intérêt est double — un **workflow par défaut sans micro-gestion** (chaque acteur n'a pas besoin de son propre layer), et la possibilité d'avoir des acteurs **gérés par World Partition mais volontairement sans proxy lointain** quand aucun default ne s'applique.

Tu es bien sur World Partition (UE5), ou plutôt sur l'ancien système HLOD (volumes + ALODActor d'UE4) ? La réponse au fallback change légèrement selon le cas.

L'utilisateur pose une question conceptuelle sur Unreal Engine concernant les HLOD sans HLODLayer associée. Je dois expliquer le cas d'usage et répondre en français. Je réfléchis à la façon dont les HLOD fonctionnent dans le système World Partition d'UE5, où les acteurs peuvent être marqués comme HLOD même sans couche HLOD explicite. So when an actor is marked as HLOD-relevant but has no HLODLayer assigned, it falls back to the world's default HLOD layer defined in the World Partition settings. This is a straightforward way to include actors in HLOD generation without manually assigning each one to a specific layer—they just use the project's default behavior. The real use case would be for actors that don't need special HLOD treatment and can work fine with whatever the default layer provides. The HLOD builder checks each actor's HLODLayer property — if it's set, that layer is used; otherwise it falls back to the world's default HLOD layer from World Settings. If neither exists, the actor generates no HLOD proxy and simply loads/unloads spatially without any distant representation. This second scenario is useful for small, non-visually-significant objects like clutter or gameplay props that don't need proxies at distance. I'm planning to structure the answer around these two properties and their interaction with World Partition's HLOD system.


---

### User

ue5

**Assistant:** Parfait, donc tout ce que j'ai décrit s'applique : en UE5 c'est le **HLOD de World Partition** qui gère ça. Je précise quelques points spécifiques UE5 pour bien fermer le sujet.

## Le fallback en UE5

En UE5, sur ton acteur tu as la catégorie **World Partition / HLOD** avec :

- **`Is Spatially Loaded`** → l'acteur est géré par la grille World Partition (chargé/déchargé par cellule).
- **`HLOD Layer`** → le layer (et donc la méthode de build) utilisé pour son proxy.

Quand `HLOD Layer = None`, le builder regarde le **Default HLOD Layer** défini sur la **World Partition Setup** (accessible via les *World Settings* → catégorie *World Partition*, ou directement sur le `Runtime Hash` de la grille). C'est ce default qui est appliqué.

## Le détail important en UE5 : la hiérarchie de layers

En UE5, les `HLODLayer` ont une propriété **`Parent HLOD Layer`**. C'est ce qui permet le **HLOD de HLOD** :

- HLOD0 (mesh mergé d'une cellule) → agrégé dans HLOD1 → etc.

Un acteur avec `HLOD Layer = None` rejoint le default, qui est en général **le premier niveau de la chaîne**. Tu n'assignes un layer explicite que quand tu veux **sortir un acteur de cette chaîne par défaut** (autre méthode de build, autre draw distance, ou l'isoler dans sa propre branche).

## Les use-cases UE5, confirmés

1. **Workflow par défaut** → tu définis un Default HLOD Layer sur la grille, et la majorité de tes acteurs restent en `None` : ils héritent automatiquement. Zéro micro-gestion sur des milliers d'acteurs.

2. **Acteur streamé mais sans proxy lointain** → HLOD-relevant + `None` + aucun default applicable = l'acteur disparaît proprement au-delà de la loading range, sans coût de génération/rendu d'un proxy. Idéal pour le petit clutter de gameplay.

3. **Itération de stratégie** → tu changes la méthode HLOD globale en touchant juste le Default Layer de la grille, sans rééditer chaque acteur.

En clair : en UE5, un acteur « HLOD » sans HLODLayer **n'est jamais exclu du système** — il bascule simplement sur le **Default HLOD Layer de la grille World Partition**. L'absence de layer explicite, c'est le mode « j'hérite du comportement global ».

The user confirmed they're using UE5, so my explanation about World Partition and HLOD systems is directly applicable. I should refine my answer with UE5-specific details while keeping it concise since I've already provided the comprehensive breakdown.
