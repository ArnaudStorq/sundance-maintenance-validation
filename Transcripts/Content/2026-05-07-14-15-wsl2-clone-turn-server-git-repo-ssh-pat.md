# Wsl2 Clone Turn Server Git Repo Ssh Pat

- Date: 2026-05-07 14:15
- Source transcript: `f9a1b242-2dee-4734-9d2c-1c9b144d8a9c`

---

### User

j'ai mon instance de Linux Ubundu qui tourne sous WSL2 Linux.
Je veux pouvoir cloner et faire evoluer ce git repo : https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4# 
Dis-moi les etapes.

**Assistant:** Je vais te guider pour cloner et travailler avec ce repo Git d'entreprise (`github.wbgames.com`) depuis ton WSL2 Ubuntu. Comme c'est un GitHub Enterprise interne (pas github.com public), il y a quelques particularités.

## Étapes complètes

### 1. Préparer ton WSL2 Ubuntu

Ouvre ton terminal WSL2 et installe les outils nécessaires :

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl openssh-client build-essential
```

Vérifie que Git est bien installé :

```bash
git --version
```

### 2. Configurer ton identité Git

Utilise ton email WB Games (celui associé à ton compte GitHub Enterprise) :

```bash
git config --global user.name "Prénom Nom"
git config --global user.email "[email protected]"
git config --global init.defaultBranch main
```

### 3. Configurer l'authentification

Tu as **deux options**. Je recommande **SSH** (plus simple à long terme) :

#### Option A — SSH (recommandé)

Génère une clé SSH dans WSL :

```bash
ssh-keygen -t ed25519 -C "[email protected]"
```

Appuie sur Entrée pour accepter l'emplacement par défaut (`~/.ssh/id_ed25519`) et choisis une passphrase (ou laisse vide).

Démarre l'agent SSH et ajoute la clé :

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Affiche ta clé publique pour la copier :

```bash
cat ~/.ssh/id_ed25519.pub
```

Ajoute cette clé sur GitHub Enterprise :
1. Va sur `https://github.wbgames.com/settings/keys`
2. Clique sur **New SSH key**
3. Colle la clé et donne-lui un nom (ex: "WSL2 Ubuntu")

Teste la connexion :

```bash
ssh -T [email protected]
```

Tu devrais voir un message comme `Hi <username>! You've successfully authenticated...`

#### Option B — HTTPS avec Personal Access Token (PAT)

1. Va sur `https://github.wbgames.com/settings/tokens`
2. Génère un token avec le scope `repo`
3. Configure le credential helper :

```bash
git config --global credential.helper store
```

Au premier `git clone`, Git te demandera ton username et ton **token** (à utiliser à la place du mot de passe).

### 4. Cloner le repo

Crée un dossier de travail et clone :

```bash
mkdir -p ~/projects && cd ~/projects
```

**Avec SSH :**

```bash
git clone [email protected]:WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
```

**Avec HTTPS :**

```bash
git clone https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
```

Puis entre dans le dossier :

```bash
cd Mercury-TURN-server-for-UE4
```

### 5. Workflow pour faire évoluer le repo

Crée une branche pour tes modifications :

```bash
git checkout -b feature/ma-modification
```

Travaille sur les fichiers, puis :

```bash
git status                              # voir ce qui a changé
git add .                               # stager les changements
git commit -m "Description claire"      # committer
git push -u origin feature/ma-modification   # pousser la branche
```

Ensuite, sur l'interface web GitHub Enterprise, ouvre une **Pull Request** depuis ta branche vers `main` (ou `develop`, selon la convention du projet).

Pour rester à jour avec la branche principale :

```bash
git checkout main
git pull
git checkout feature/ma-modification
git rebase main      # ou: git merge main
```

### 6. Conseils spécifiques à WSL2

- **Travaille dans le filesystem Linux** (`~/projects/...`) et **pas** dans `/mnt/c/...` — les performances Git sont 10x meilleures.
- Si le repo contient des fichiers volumineux (binaires UE4), vérifie s'il utilise **Git LFS** :

```bash
sudo apt install -y git-lfs
git lfs install
```

Si le repo a un `.gitattributes` avec des règles LFS, le clone récupèrera automatiquement les fichiers LFS.

- Pour ouvrir le projet dans VS Code depuis WSL :

```bash
code .
```

### Points à valider avant de commencer

- As-tu déjà accès à `github.wbgames.com` (compte actif, VPN si requis hors bureau) ?
- Le repo a-t-il une convention particulière (CONTRIBUTING.md, branche `develop` au lieu de `main`, etc.) ? À vérifier dans le README une fois cloné.

Dis-moi quelle option d'authentification tu préfères (SSH ou HTTPS) et où tu bloques, je peux t'aider sur l'étape suivante.


---

### User

je veux utiliser le HTTPS avec PAT (j'ai créé un token)

arnaudstorq@MTLWKS20850:~/dev$ git clone https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
Cloning into 'Mercury-TURN-server-for-UE4'...
Username for 'https://github.wbgames.com': ArnaudStorq
Password for 'https://ArnaudStorq@github.wbgames.com':
remote: Password authentication is not available for Git operations.
remote: You must use a personal access token or SSH key.
remote: See https://github.wbgames.com/settings/tokens or https://github.wbgames.com/settings/ssh
fatal: unable to access 'https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git/': The requested URL returned error: 403
arnaudstorq@MTLWKS20850:~/dev$ git clone https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git

**Assistant:** Le message est clair : tu as bien tapé ton **mot de passe**, mais GitHub Enterprise n'accepte plus l'authentification par mot de passe. Il faut **coller ton PAT à la place du mot de passe**.

## Solution

Relance la commande :

```bash
git clone https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
```

Quand il demande :
- **Username** : `ArnaudStorq` (ton username GitHub)
- **Password** : **colle ton PAT** (le token `ghp_...` ou similaire que tu as généré), **PAS ton mot de passe**

> Astuce WSL/PowerShell : pour coller dans le terminal WSL, fais clic droit (ou `Ctrl+Shift+V`). Le token ne s'affichera pas pendant que tu le colles, c'est normal — tape Entrée après.

## Pour ne pas avoir à le retaper à chaque fois

Configure le credential helper **avant** de cloner (ou après, peu importe) :

### Option 1 — Stockage en clair (simple, mais le token est lisible dans `~/.git-credentials`)

```bash
git config --global credential.helper store
```

Au prochain clone, il te demandera username + PAT une seule fois, puis les sauvegardera.

### Option 2 — Cache temporaire en mémoire (plus sûr)

```bash
git config --global credential.helper 'cache --timeout=28800'
```

Le token reste en mémoire 8 heures après chaque utilisation.

### Option 3 — Utiliser le Windows Credential Manager depuis WSL (recommandé)

C'est l'option la plus propre : ton PAT est stocké de façon sécurisée dans le gestionnaire d'identifiants Windows et partagé entre Windows et WSL.

```bash
git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager.exe"
```

> Prérequis : avoir Git for Windows installé côté Windows (qui inclut Git Credential Manager). Si le chemin ci-dessus n'existe pas, vérifie où GCM est installé avec `ls /mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager*`.

## Alternative : embarquer le token dans l'URL (déconseillé)

Tu peux aussi cloner directement avec :

```bash
git clone https://ArnaudStorq:<TON_PAT>@github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
```

Mais le token apparaîtra dans `.git/config` en clair — à éviter.

## Récapitulatif rapide

1. Configure le helper (option 1 par défaut) :
   ```bash
   git config --global credential.helper store
   ```
2. Clone à nouveau :
   ```bash
   git clone https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
   ```
3. Username = `ArnaudStorq`, Password = **ton PAT**.

Dis-moi si ça passe ou si tu as un nouveau message d'erreur.


---

### User

arnaudstorq@MTLWKS20850:~/dev$ git clone https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
Cloning into 'Mercury-TURN-server-for-UE4'...
Username for 'https://github.wbgames.com': ArnaudStorq
Password for 'https://ArnaudStorq@github.wbgames.com':
remote: Write access to repository not granted.
fatal: unable to access 'https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git/': The requested URL returned error: 403
arnaudstorq@MTLWKS20850:~/dev$

**Assistant:** Bonne nouvelle : ton **PAT fonctionne** (l'authentification a réussi). Le problème est différent maintenant — c'est une question de **permissions** sur le repo.

## Ce que dit l'erreur

```
remote: Write access to repository not granted.
```

GitHub Enterprise refuse l'accès parce que ton compte n'a **pas les droits** sur ce repo. Deux causes possibles :

### Cause 1 — Ton PAT n'a pas les bons scopes

Quand tu as créé ton token, il faut au minimum cocher le scope **`repo`** (qui inclut `repo:status`, `repo_deployment`, `public_repo`, etc.).

**Vérifie ici :** `https://github.wbgames.com/settings/tokens`

Regarde ton token et confirme que la case **`repo`** (Full control of private repositories) est cochée. Si non, supprime-le et régénère-en un nouveau avec ce scope.

> Note : le message "Write access not granted" est trompeur — même pour un simple `git clone` (lecture seule), GitHub Enterprise vérifie que le token a le scope `repo` pour les repos privés.

### Cause 2 — Ton compte n'a pas accès au repo

Ton utilisateur `ArnaudStorq` doit être :
- **Membre** de l'organisation `WB-Games-Montreal`, **ET**
- **Collaborateur** du repo `Mercury-TURN-server-for-UE4` (au minimum en lecture)

**Pour vérifier :**
1. Va sur `https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4` dans ton navigateur **avec ton compte connecté**.
2. Si tu vois une page **404** ou "You don't have access" → tu n'es pas dans la liste des collaborateurs.
3. Si tu vois le repo et son contenu → c'est seulement un problème de scope du PAT.

### Cause 3 (moins probable) — SSO non autorisé pour le token

Certaines orgs GitHub Enterprise utilisent **SAML SSO**. Dans ce cas, après avoir créé ton PAT, il faut explicitement **autoriser le token pour l'organisation** :

1. Va sur `https://github.wbgames.com/settings/tokens`
2. À côté de ton token, clique sur **Configure SSO**
3. Autorise-le pour l'org `WB-Games-Montreal`

## Plan d'action

1. **Ouvre le repo dans ton navigateur** : [https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4](https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4)
   - Tu vois le code → passe à l'étape 2
   - Tu vois "Not Found" / "no access" → demande à un admin du repo de t'ajouter comme collaborateur
2. **Vérifie ton PAT** : `https://github.wbgames.com/settings/tokens` → scope `repo` coché + bouton **"Configure SSO"** activé pour `WB-Games-Montreal` si présent.
3. **Relance le clone** :
   ```bash
   git clone https://github.wbgames.com/WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
   ```

## Dis-moi

- Est-ce que tu peux voir le repo dans ton navigateur quand tu es connecté ?
- Quels scopes as-tu coché en créant le PAT ?
- Y a-t-il un bouton "Configure SSO" / "Enable SSO" à côté de ton token dans la page des tokens ?

Avec ces 3 infos, on identifiera la cause exacte.


---

### User

aide moi a creer une clé ssh pour pouvoir cloner git@github.wbgames.com:WB-Games-Montreal/Mercury-TURN-server-for-UE4.git

**Assistant:** Parfait, on passe au SSH. Voici les étapes complètes dans ton WSL2 Ubuntu.

## 1. Vérifier si tu as déjà une clé SSH

```bash
ls -al ~/.ssh
```

Si tu vois déjà `id_ed25519` et `id_ed25519.pub`, tu peux sauter à l'**étape 3**. Sinon, on en crée une.

## 2. Générer une nouvelle clé SSH

```bash
ssh-keygen -t ed25519 -C "[email protected]"
```

> Remplace `[email protected]` par l'email associé à ton compte `github.wbgames.com`.

À chaque question :
- **`Enter file in which to save the key`** → appuie simplement sur **Entrée** (accepte le chemin par défaut `~/.ssh/id_ed25519`)
- **`Enter passphrase`** → soit tu mets une passphrase (plus sécurisé, te sera redemandée à l'utilisation), soit tu laisses vide en appuyant sur Entrée (plus pratique)
- **`Enter same passphrase again`** → confirme

Tu devrais voir quelque chose comme :
```
Your identification has been saved in /home/arnaudstorq/.ssh/id_ed25519
Your public key has been saved in /home/arnaudstorq/.ssh/id_ed25519.pub
```

## 3. Démarrer l'agent SSH et ajouter la clé

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Si tu as mis une passphrase, il te la demandera ici.

## 4. Copier ta clé publique

Affiche-la pour pouvoir la copier :

```bash
cat ~/.ssh/id_ed25519.pub
```

Tu verras une ligne qui ressemble à :
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... [email protected]
```

**Sélectionne et copie toute cette ligne** (du `ssh-ed25519` jusqu'à la fin de l'email).

> Astuce WSL : pour copier le contenu directement dans le presse-papiers Windows :
> ```bash
> cat ~/.ssh/id_ed25519.pub | clip.exe
> ```

## 5. Ajouter la clé sur GitHub Enterprise

1. Va sur **`https://github.wbgames.com/settings/keys`** dans ton navigateur (connecté avec ton compte WB).
2. Clique sur **`New SSH key`** (ou `Add SSH key`).
3. Remplis :
   - **Title** : un nom descriptif, ex: `WSL2 Ubuntu - MTLWKS20850`
   - **Key type** : `Authentication Key`
   - **Key** : colle la clé publique que tu as copiée
4. Clique sur **`Add SSH key`** (il te redemandera peut-être ton mot de passe GitHub pour confirmer).

> Si l'organisation `WB-Games-Montreal` utilise **SAML SSO**, après avoir ajouté la clé, tu verras un bouton **`Configure SSO`** à côté → clique dessus et autorise-la pour `WB-Games-Montreal`.

## 6. Tester la connexion SSH

```bash
ssh -T [email protected]
```

À la première connexion, tu auras :
```
The authenticity of host 'github.wbgames.com (...)' can't be established.
ED25519 key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Tape **`yes`** et Entrée.

Si tout est bon, tu verras :
```
Hi ArnaudStorq! You've successfully authenticated, but GitHub does not provide shell access.
```

> Note : le message **`does not provide shell access`** est **normal** — c'est le succès attendu.

## 7. Cloner le repo en SSH

```bash
cd ~/dev
git clone [email protected]:WB-Games-Montreal/Mercury-TURN-server-for-UE4.git
```

Si le clone démarre (`Cloning into 'Mercury-TURN-server-for-UE4'...` puis téléchargement des objets), c'est gagné.

## En cas de problème

Voici les erreurs les plus courantes et leur cause :

| Erreur | Cause probable |
|---|---|
| `Permission denied (publickey)` | La clé n'est pas (ou mal) ajoutée sur GitHub, ou pas chargée dans l'agent SSH |
| `Could not resolve hostname github.wbgames.com` | DNS / VPN — il te faut peut-être être connecté au VPN WB |
| `ERROR: The `WB-Games-Montreal' organization has enabled or enforced SAML SSO` | Il faut cliquer sur "Configure SSO" sur la page des clés et autoriser pour l'org |
| Clone démarre mais : `remote: Repository not found` | Ton compte n'est pas collaborateur du repo (à demander à l'admin) |

## Bonus : éviter de relancer `ssh-add` à chaque session WSL

Ajoute ces lignes à la fin de ton `~/.bashrc` :

```bash
if [ -z "$SSH_AUTH_SOCK" ]; then
   eval "$(ssh-agent -s)" > /dev/null
   ssh-add ~/.ssh/id_ed25519 2>/dev/null
fi
```

Puis recharge :

```bash
source ~/.bashrc
```

---

Lance les étapes 1 à 6 et dis-moi à quelle étape tu en es ou si tu as un message d'erreur — je te débloque.


---

### User

dans wsl2, comment installer vs code et github desktop dans WSL2 ubuntu linux

**Assistant:** Bonne question — mais il y a une nuance importante à comprendre avant. Voici la situation pour chacun.

## VS Code — **ne s'installe PAS dans WSL2**

C'est contre-intuitif, mais **VS Code s'installe sur Windows**, et il se connecte ensuite à WSL2 via une extension. C'est l'architecture officielle Microsoft, et ça marche très bien.

### Étapes

#### 1. Installer VS Code sur Windows (pas dans WSL)

Sur Windows, télécharge et installe depuis : [https://code.visualstudio.com/](https://code.visualstudio.com/)

Lors de l'installation, **coche bien** :
- ☑ Add to PATH
- ☑ Register Code as an editor for supported file types

#### 2. Installer l'extension WSL

Dans VS Code (sous Windows) :
1. Ouvre la barre des extensions (`Ctrl+Shift+X`)
2. Cherche **`WSL`** (publié par Microsoft)
3. Clique **Install**

#### 3. Lancer VS Code depuis WSL

Dans ton terminal WSL2 Ubuntu, va dans ton repo :

```bash
cd ~/dev/Mercury-TURN-server-for-UE4
code .
```

À la première utilisation, VS Code installe automatiquement un petit "VS Code Server" côté Linux. Ensuite, l'UI tourne sur Windows mais tout le code (terminal intégré, extensions, debugger, Git, Node, Python...) **s'exécute dans Ubuntu**.

Tu sauras que tu es bien en mode WSL quand tu verras en bas à gauche de VS Code :

```
WSL: Ubuntu
```

> **Pourquoi ne pas installer VS Code DANS Ubuntu WSL ?**
> Techniquement c'est possible (`sudo apt install code`), mais ça force VS Code à tourner via WSLg en mode "GUI Linux", ce qui est plus lent, moins intégré, et perd la majorité des bénéfices. **Ne le fais pas.** L'approche officielle "Windows + extension WSL" est celle recommandée par Microsoft.

#### 4. (Optionnel) Extensions utiles à installer côté WSL

Une fois connecté en `WSL: Ubuntu`, installe par exemple :
- **GitLens** — historique Git enrichi
- **Git Graph** — visualisation graphique de l'historique
- **C/C++** (Microsoft) — si tu touches au code C++ d'UE4

VS Code te demandera "Install in WSL: Ubuntu" pour chacune — clique oui.

---

## GitHub Desktop — **ne supporte pas GitHub Enterprise wbgames.com de façon native, et pas Linux officiellement**

Là il y a deux problèmes :

### Problème 1 — GitHub Desktop n'a pas de version Linux officielle

[github.com/desktop/desktop](https://github.com/desktop/desktop) ne distribue que pour **Windows et macOS**. Il existe un fork communautaire ([shiftkey/desktop](https://github.com/shiftkey/desktop)) qui fournit des `.deb` pour Linux, mais ce n'est **pas officiel** et c'est moins maintenu.

### Problème 2 — Même installé, GitHub Desktop est limité avec GitHub Enterprise

GitHub Desktop est **conçu d'abord pour github.com**. Ajouter `github.wbgames.com` est possible (Préférences → Comptes → "Sign in to GitHub Enterprise"), mais certaines fonctionnalités (PR, gestion d'issues) sont parfois capricieuses selon la version d'Enterprise utilisée par WB.

### Mes recommandations concrètes

**Option A — La meilleure (mon conseil)** : utilise **GitHub Desktop sur Windows directement** (pas dans WSL).

1. Télécharge depuis [https://desktop.github.com/](https://desktop.github.com/)
2. Installe-le sur Windows
3. **File → Options → Accounts → Sign in to GitHub Enterprise** → renseigne `github.wbgames.com`
4. Pour cloner : **File → Clone repository** → onglet "URL" → colle l'URL HTTPS du repo
5. **Important** : clone-le dans un dossier WSL pour garder de bonnes performances Git, par exemple : `\\wsl$\Ubuntu\home\arnaudstorq\dev\Mercury-TURN-server-for-UE4`

> Tu peux accéder au filesystem WSL depuis l'explorateur Windows via `\\wsl$\Ubuntu\` ou via le raccourci "Linux" dans le panneau gauche. GitHub Desktop sait travailler avec ces chemins, et tes commandes `git` dans WSL travailleront aussi sur le même dossier.

**Option B — Alternative GUI dans WSL/Windows** :

Si tu veux vraiment une interface graphique multi-plateforme et bien intégrée à GitHub Enterprise, regarde plutôt :
- **GitKraken** (gratuit pour usage personnel, payant pour pro) — excellent support GitHub Enterprise
- **SourceTree** (gratuit, Atlassian) — Windows uniquement
- **Lazygit** (TUI dans le terminal) — `sudo apt install lazygit` dans WSL, marche très bien
- **L'onglet Source Control de VS Code** + extensions GitLens & Git Graph — c'est honnêtement souvent suffisant et c'est ce que beaucoup de devs utilisent au final

---

## Mon setup recommandé pour ton cas (WB Games + WSL2 + Mercury TURN)

```
┌─────────────────────────────────────────┐
│            Windows                      │
│  ┌────────────┐    ┌──────────────────┐ │
│  │  VS Code   │    │ GitHub Desktop   │ │
│  │ + ext. WSL │    │ (Enterprise OK)  │ │
│  └─────┬──────┘    └────────┬─────────┘ │
│        │                    │           │
│  ─ ─ ─ │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│ ─ ─ ─ ─ ─ │
│        ▼                    ▼           │
│  ┌─────────────────────────────────────┐│
│  │  WSL2 Ubuntu                        ││
│  │  ~/dev/Mercury-TURN-server-for-UE4  ││
│  │  (git, ssh, build tools)            ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### Étapes concrètes

1. ✅ Tu as déjà SSH configuré (étapes précédentes) — donc le clone marchera pour Git en ligne de commande.
2. **Installe VS Code sur Windows** + extension **WSL**.
3. Dans WSL : `cd ~/dev/Mercury-TURN-server-for-UE4 && code .` → tu codes dans VS Code, terminal intégré WSL, Git intégré WSL.
4. **Optionnel** : installe **GitHub Desktop sur Windows**, configure le compte Enterprise, et pointe-le vers le même dossier `\\wsl$\Ubuntu\home\arnaudstorq\dev\Mercury-TURN-server-for-UE4` si tu veux la GUI pour gérer commits/PRs.

---

Dis-moi par quoi tu veux commencer (VS Code en premier je suppose ?) et si tu veux que je te guide sur l'installation de l'extension WSL ou la config de GitHub Desktop pour Enterprise.


---

### User

si je veux changer de branch dans le repo git a partir de vscode, estce que c'est "rebase branch" qu'il faut utiliser ?

**Assistant:** Non, surtout pas ! `Rebase branch` fait quelque chose de complètement différent (et potentiellement destructeur si mal utilisé). Pour **simplement changer de branche**, c'est une autre commande.

## Pour changer de branche dans VS Code

### Méthode 1 — Le plus rapide : la barre de statut (recommandé)

En **bas à gauche** de VS Code, tu vois un nom de branche avec une petite icône de fork :

```
WSL: Ubuntu  |  ⎇ main  |  0↓ 0↑
```

1. **Clique sur `⎇ main`** (ou le nom de la branche actuelle)
2. Une palette s'ouvre en haut listant toutes les branches (locales et distantes)
3. Tape pour filtrer ou choisis dans la liste
4. **Clique sur la branche** → VS Code fait `git checkout` automatiquement

### Méthode 2 — Via la palette de commandes

1. `Ctrl+Shift+P` (palette de commandes)
2. Tape **`Git: Checkout to...`**
3. Sélectionne la branche

> C'est exactement la même action que la méthode 1.

### Méthode 3 — Via le panneau Source Control

1. `Ctrl+Shift+G` (ouvre le panneau Source Control)
2. Clique sur **`...`** (menu en haut du panneau) → **`Checkout to...`**

---

## Le vocabulaire Git dans VS Code

Voici ce que fait chaque commande pour que tu ne te trompes pas :

| Commande VS Code | Commande Git équivalente | Ce que ça fait |
|---|---|---|
| **Checkout to...** | `git checkout <branche>` | ✅ **Change de branche** (ce que tu veux) |
| **Create Branch...** | `git checkout -b <nouvelle>` | Crée une nouvelle branche **et** s'y déplace |
| **Switch Branch** | `git switch <branche>` | Change de branche (alternative moderne) |
| **Pull** | `git pull` | Récupère les nouveaux commits depuis le remote |
| **Push** | `git push` | Envoie tes commits locaux vers le remote |
| **Sync** | `git pull` + `git push` | Combo des deux |
| **Merge Branch...** | `git merge <branche>` | Fusionne une autre branche **dans** la branche courante |
| **Rebase Branch...** | `git rebase <branche>` | ⚠️ Réécrit l'historique de la branche courante (avancé) |

## C'est quoi `Rebase Branch...` exactement (et pourquoi pas le confondre) ?

Imagine cette situation :

```
main:        A---B---C
                  \
ma-branche:        D---E
```

Tu es sur `ma-branche` et tu fais **`Rebase Branch... → main`** :

```
main:        A---B---C
                      \
ma-branche:            D'---E'
```

Ça **prend tes commits `D` et `E`** et les **réapplique par-dessus le dernier état de `main`** (`C`). Les commits originaux `D` et `E` sont remplacés par `D'` et `E'` (mêmes changements, mais nouveaux SHA).

**C'est utile** quand tu veux mettre à jour ta branche feature avec les derniers changements de `main`, sans créer un commit de merge.

**Mais c'est dangereux** parce que :
- Ça **réécrit l'historique** de ta branche
- Si la branche est déjà partagée (poussée), il faudra un `git push --force-with-lease`, ce qui peut écraser le travail des autres
- Sur certains repos, le rebase est interdit par convention

> **Règle d'or pour débuter** : utilise `Merge Branch...` au lieu de `Rebase Branch...` tant que tu n'es pas à l'aise avec les implications. Et pour **changer de branche**, c'est **`Checkout to...`** point final.

---

## Workflow typique

```
1. Cliquer ⎇ main en bas à gauche
2. Choisir "Create new branch..." → "feature/ma-modification"
   → VS Code te met automatiquement sur la nouvelle branche
3. Tu codes, tu commits via le panneau Source Control (Ctrl+Shift+G)
4. Tu pushes via Sync ou le bouton ↑
5. Pour revenir à main : cliquer ⎇ feature/... → choisir "main"
```

---

Donc pour répondre directement à ta question : **`Checkout to...`** est la bonne commande pour changer de branche. Ne touche pas à `Rebase Branch...` pour l'instant — c'est un outil pour plus tard quand tu maîtriseras bien le workflow Git de base.


---

### User

comment faire switch branch depuis vscode

**Assistant:** Voici les **3 méthodes** pour switcher de branche dans VS Code, de la plus rapide à la plus complète.

## Méthode 1 — La barre de statut (la plus rapide)

C'est la méthode quotidienne, en 2 clics.

1. Regarde **en bas à gauche** de VS Code, tu vois quelque chose comme :

   ```
   WSL: Ubuntu   ⎇ main   0↓ 0↑
   ```

2. **Clique sur le nom de la branche** (`⎇ main`)
3. Une palette s'ouvre en haut avec :
   - 🆕 **Create new branch...**
   - 🆕 **Create new branch from...**
   - La liste de **toutes tes branches** (locales et remote)
4. **Tape pour filtrer** ou clique directement sur la branche voulue
5. ✅ VS Code fait le switch automatiquement

> Si tu ne vois pas le nom de la branche en bas, c'est que tu n'es pas dans un dossier qui est un repo Git, ou que VS Code ne l'a pas encore détecté.

## Méthode 2 — La palette de commandes

Pratique si tu as les mains sur le clavier.

1. **`Ctrl+Shift+P`** (ouvre la palette de commandes)
2. Tape **`checkout`**
3. Sélectionne **`Git: Checkout to...`**
4. Choisis ta branche dans la liste

## Méthode 3 — Le panneau Source Control

1. **`Ctrl+Shift+G`** (ouvre Source Control dans la barre latérale)
2. Clique sur l'icône **`...`** (More Actions, en haut du panneau)
3. **`Checkout to...`**
4. Choisis ta branche

---

## Cas spécifiques

### Tu veux switcher vers une **branche distante** (pas encore en local)

Si la branche existe sur le remote mais pas encore chez toi, fais d'abord :

1. **`Ctrl+Shift+P`** → **`Git: Fetch`** (récupère la liste des branches remote)
2. Puis utilise une des 3 méthodes ci-dessus → la branche apparaîtra avec le préfixe `origin/...`
3. Sélectionne-la → VS Code crée automatiquement une branche locale qui la suit

### Tu veux **créer une nouvelle branche** et y switcher

1. Clique sur **`⎇ <branche>`** en bas à gauche
2. Choisis **`Create new branch...`** (en haut de la liste)
3. Tape le nom (ex: `feature/ma-modification`)
4. Entrée → tu es sur la nouvelle branche

### Tu as des **changements non commités** au moment du switch

VS Code essaie de garder tes changements avec toi sur la nouvelle branche. **Mais** :
- Si les fichiers modifiés entrent en conflit avec la branche cible → VS Code refuse le switch et affiche une erreur
- Solution : commit tes changements, ou stash-les (**`Ctrl+Shift+P`** → **`Git: Stash`**)

---

## Récap visuel

```
   ┌─ Barre de statut VS Code (en bas) ─────────────────┐
   │                                                    │
   │  WSL: Ubuntu  ⎇ main  0↓ 0↑   Ln 12, Col 4   UTF-8│
   │               └─┬─┘                                │
   │                 └──── CLIQUE ICI                   │
   └────────────────────────────────────────────────────┘
                     │
                     ▼
   ┌─ Palette qui s'ouvre en haut ──────────────────────┐
   │  Select a branch to checkout                        │
   │  ─────────────────────────────────────             │
   │   + Create new branch...                            │
   │   + Create new branch from...                       │
   │  ─────────────────────────────────────             │
   │   ⎇ main                                            │
   │   ⎇ develop                                         │
   │   ⎇ feature/turn-server-config                      │
   │   ⎇ origin/hotfix-1.2                              │
   └────────────────────────────────────────────────────┘
```

---

**TL;DR** : clique sur **`⎇ main`** en bas à gauche → choisis ta branche → c'est fait.

Si tu ne vois pas l'icône de branche en bas à gauche, dis-le-moi avec une capture ou décris ce que tu vois — il peut y avoir un souci de détection du repo Git.
