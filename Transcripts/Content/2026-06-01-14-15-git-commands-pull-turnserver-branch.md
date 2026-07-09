# Git Commands Pull Turnserver Branch

- Date: 2026-06-01 14:15
- Source transcript: `6c04e883-06c4-4832-a63d-8b6282e16d89`

---

### User

git config --global core.protectNTFS false
git config --global core.longpaths true
git reset --hard
git clean -fd
git checkout -b Upgraded-TurnServer-2026 origin/Upgraded-TurnServer-2026

il manque git pull pour que tous les utilisateurs voient le commit ?

**Assistant:** Oui, exactement ! Après le `git checkout -b`, il faut faire un `git pull` pour récupérer les derniers commits de la branche distante. Mais en réalité, ça dépend de ce que tu veux faire.

Voici une explication des différents scénarios :

## Scénario 1 : Tu viens de créer la branche locale depuis origin

```powershell
git checkout -b Upgraded-TurnServer-2026 origin/Upgraded-TurnServer-2026
```

Ici, ta branche locale est **déjà synchronisée** avec `origin/Upgraded-TurnServer-2026` au moment du checkout. **Pas besoin de `git pull` immédiatement** sauf si quelqu'un a poussé entre-temps.

## Scénario 2 : Pour voir les nouveaux commits des autres

Pour récupérer les nouveaux commits poussés par d'autres utilisateurs :

```powershell
git fetch origin
git pull
```

Ou directement :

```powershell
git pull origin Upgraded-TurnServer-2026
```

## Scénario 3 : Pour que **les autres** voient TES commits

Ce n'est pas `git pull` qu'il faut, mais `git push` :

```powershell
git add .
git commit -m "ton message"
git push origin Upgraded-TurnServer-2026
```

## Workflow complet recommandé

```powershell
git config --global core.protectNTFS false
git config --global core.longpaths true

git fetch origin
git reset --hard
git clean -fd

git checkout -b Upgraded-TurnServer-2026 origin/Upgraded-TurnServer-2026

git pull
```

## Résumé rapide

| Commande | Rôle |
|----------|------|
| `git fetch` | Récupère les infos du remote (sans merger) |
| `git pull` | `fetch` + `merge` dans ta branche locale |
| `git push` | Envoie TES commits vers le remote pour que les autres les voient |

Donc :
- **`git pull`** → toi tu vois les commits des autres
- **`git push`** → les autres voient tes commits
