# Miro Plugin Usage And Board Invite

- Date: 2026-07-07 11:03
- Source transcript: `38a5b926-d881-4ec1-85a9-749938f7f7cd`

---

### User

Show me how the Miro plugin works

**Assistant:** You just installed the **Miro** plugin, which gives me secure access to your Miro boards to read context, create diagrams, and generate content. Here's what it includes.

## Commands (invoke with `/`)
- **`/browse`** — List and explore items on a Miro board
- **`/diagram`** — Create a diagram on a board from a text description
- **`/doc`** — Create a Google Docs-style document on a board
- **`/summarize`** — Generate documentation or a summary from a board's contents
- **`/table`** — Create a table on a board with specified columns

## Skill
- **`miro-mcp`** — Teaches me how to use the Miro tools effectively (diagrams, docs, tables, extracting board context). I'll pull this in automatically when you ask me to work with Miro, or you can invoke it with `/`.

## MCP Server
- **`miro`** — The underlying connection that powers all of the above, letting me read board data and create items directly.

Let me check whether the server needs authentication.

I should give the user an overview of the Miro plugin they just installed, then look into the STATUS.md file to check on the authentication setup.

<details><summary>Tools used</summary>

- `Glob` **/miro*/**/STATUS.md

</details>

**Assistant:** I'll broaden my search approach.

<details><summary>Tools used</summary>

- `Glob` **/STATUS.md
- `GetMcpTools`

</details>

**Assistant:** The `miro` MCP server needs authentication before I can use any of its tools. Let me start that for you.

I need to set up authentication with the MCP server.

<details><summary>Tools used</summary>

- `CallMcpTool` Authenticate the Miro MCP server

</details>

**Assistant:** Authentication succeeded — the Miro server is now connected and ready.

## You're all set
Here's how to start using it:

- **Explore a board:** `/browse` (I'll list the items and layout so you know what's there)
- **Create a diagram:** `/diagram` — e.g. "a flowchart of our login flow"
- **Add a document:** `/doc` — draft notes, specs, or summaries as a doc on the board
- **Summarize a board:** `/summarize` — turn board contents into written documentation
- **Build a table:** `/table` — e.g. "a table with columns Task, Owner, Status"

You can also just describe what you want in plain language (e.g. *"add a diagram of our CI pipeline to my Miro board"*) and I'll use the right tool automatically. Most actions need a board URL or ID, so have that handy — or run `/browse` to point me at the right one.

What would you like to do first?


---

### User

/browse

**Assistant:** I'd be happy to browse a Miro board for you, but I need to know which board. Could you paste the **Miro board URL**? It looks something like:

```
https://miro.com/app/board/uXjV...=
```

Optionally, you can also tell me if you want to filter by a specific item type:
- `frame`, `sticky_note`, `card`, `shape`, `text`, `image`, `document`, or `embed`

For example: `https://miro.com/app/board/abc123= sticky_note` to see only sticky notes.

The user ran the `/browse` command without providing a URL, so I need to ask them for the board link they want to browse.


---

### User

est-ce qu'un link est ok ? https://miro.com/app/live-embed/uXjVGDLdwP4=/?embedMode=view_only_without_ui&moveToViewport=3658%2C-4356%2C6704%2C3517&embedId=518528592692

**Assistant:** Bonne question ! Ce lien est un lien **"live-embed"** (destiné à l'intégration/affichage en lecture seule), pas l'URL standard d'un board. L'identifiant du board (`uXjVGDLdwP4=`) est toutefois présent, donc je peux essayer de l'utiliser. Le format idéal ressemble plutôt à :

```
https://miro.com/app/board/uXjVGDLdwP4=
```

Laissez-moi vérifier les outils disponibles puis tester l'accès au board.

The user is asking in French about a link, which appears to be a Miro board embed URL. I'm extracting the board ID and checking what tools I have available to access it.

<details><summary>Tools used</summary>

- `GetMcpTools`
- `Grep` "tool":
- `Read` C:\Users\Arnaud.Storq\.cursor\projects\d-Sandbox-AI\agent-tools\03aab281-99ce-45ac-b23c-9297abdd86e1.txt

</details>

**Assistant:** Je teste l'accès au board en reconstruisant l'URL standard à partir de l'identifiant.

<details><summary>Tools used</summary>

- `CallMcpTool` List items on the Miro board

</details>

**Assistant:** L'accès a été refusé avec cet identifiant. Essayons avec l'URL complète telle que vous l'avez fournie.

I'm trying the full live-embed URL instead.

<details><summary>Tools used</summary>

- `CallMcpTool` List items using the live-embed URL

</details>

**Assistant:** Voici le verdict :

## Réponse courte
**Non, ce lien ne fonctionne pas tel quel** — pour deux raisons :

1. **Mauvais format d'URL.** C'est un lien `live-embed` (fait pour intégrer un board en lecture seule dans une page web). Les outils Miro attendent l'URL standard d'un board : `https://miro.com/app/board/...`

2. **Accès refusé.** J'ai reconstruit l'URL standard à partir de l'identifiant (`uXjVGDLdwP4=`) et tenté d'y accéder → réponse : **« Board access denied »**. Le compte Miro connecté ici n'a donc pas les droits sur ce board (board privé, autre organisation, ou partagé uniquement via ce lien d'intégration public).

## Ce qu'il faut pour que ça marche
- Ouvrez le board dans Miro et copiez l'URL depuis la barre d'adresse (elle ressemble à `https://miro.com/app/board/uXjVGDLdwP4=`), **ou**
- Utilisez le bouton **Share** du board pour obtenir un lien de partage, **et**
- Assurez-vous que le board est accessible par le **compte Miro authentifié** ici (invitez ce compte, ou partagez le board avec accès « anyone with the link »).

Un lien d'intégration `view_only_without_ui` ne suffit pas : l'API a besoin d'un board auquel votre compte a réellement accès.

Voulez-vous que je vérifie quel compte Miro est actuellement connecté (via `user_who_am_i`) pour confirmer avec quels droits je travaille ?

The live-embed URL format is invalid, and reconstructing the board ID results in an access denial error. This suggests the board exists but the current account lacks permission to view it, so I should let the user know about this access restriction.


---

### User

comment inviter ce compte

**Assistant:** Bonne idée — pour inviter le bon compte, il faut d'abord savoir **quel compte Miro est connecté** ici. Je vérifie.

I need to check which account is currently connected by looking at the user_who_am_i information before I can help with the invitation process.

<details><summary>Tools used</summary>

- `CallMcpTool` Check the connected Miro account

</details>

**Assistant:** Le compte connecté ne renvoie que des identifiants techniques (pas d'e-mail visible) :

- **User ID :** `3458764514604156126`
- **Team ID :** `3074457362315368070`
- **Org ID :** `3074457346138850490`

C'est le compte Miro que vous avez utilisé lors de l'authentification du plugin (l'e-mail est celui avec lequel vous vous êtes connecté à Miro). Voici les deux façons de lui donner accès au board.

## Option A — Partager par lien (le plus simple)
1. Ouvrez le board dans Miro.
2. Cliquez sur **Share** (bouton bleu, en haut à droite).
3. Dans la section d'accès par lien, réglez **« Anyone with the link »** sur **Can view** (ou **Can edit**).
4. Copiez ce lien → il aura le format `https://miro.com/app/board/uXjVGDLdwP4=`.
5. Donnez-moi cette URL et je pourrai lire le board.

> C'est la méthode recommandée si vous n'êtes pas sûr de l'e-mail exact du compte connecté.

## Option B — Inviter le compte nominativement
1. Ouvrez le board → **Share**.
2. Dans le champ **« Add members / Invite »**, saisissez l'**adresse e-mail du compte Miro** que vous avez utilisé pour authentifier le plugin.
3. Choisissez le niveau d'accès (**Can view** ou **Can edit**).
4. Cliquez sur **Invite / Send**.
5. Une fois l'invitation acceptée, je pourrai accéder au board avec l'URL standard.

## Points importants
- Le board doit appartenir (ou être partagé avec) la **même organisation/équipe** que le compte connecté, sinon l'accès restera refusé même après invitation, selon les règles de votre entreprise.
- Un lien `live-embed` (comme celui de départ) ne suffit **jamais** : il faut un vrai partage de board.

Souhaitez-vous que je reste prêt à retester dès que vous aurez ajusté le partage ? Il vous suffit de me recoller l'URL standard du board.

The API only returns user IDs, not email addresses, so I can't retrieve that information directly. I should focus on explaining how to invite collaborators and share the board in Miro instead.
