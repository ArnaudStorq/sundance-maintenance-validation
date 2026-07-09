# Gamelift Server Sdk Min Version Amazon Linux 2023

- Date: 2026-05-29 13:19
- Source transcript: `5f78a882-330e-4bcd-8f32-279c9cd11271`

---

### User

quelle est la version minimale du gamelift server sdk a utiliser pour amazoin linux 2023 ?

**Assistant:** Je vais chercher cette information sur le web pour vous donner une réponse précise et à jour.

<details><summary>Tools used</summary>

- `WebSearch` Finding the minimum GameLift Server SDK version compatible with Amazon Linux 2023

</details>

**Assistant:** Voici la réponse :

## Version minimale du GameLift Server SDK pour Amazon Linux 2023

**Server SDK 5.x** est la version minimale requise pour Amazon Linux 2023 (AL2023). Les versions 4.x et antérieures ne sont **pas supportées** sur AL2023.

### Détails selon votre cas d'usage

| Configuration | Version minimale du SDK |
|---|---|
| **Cas général (AL2023, instances x86)** | SDK 5.0 |
| **C++ ou C# sur instances Graviton (ARM)** | SDK **5.1.1** ou plus récent |
| **Go sur instances Graviton (ARM)** | SDK 5.0 ou plus récent |

### Points importants à noter

- AL2023 est **uniquement** supporté à partir du Server SDK V5 — il n'y a pas de rétrocompatibilité avec le SDK V4.
- Si vous utilisez actuellement le SDK 4.x sur AL2, vous devez d'abord migrer votre build vers le SDK 5.x **avant** de déployer sur AL2023.
- Amazon Linux 2 (AL2) atteint sa fin de support le **30 juin 2026**, donc la migration vers AL2023 + SDK 5.x est fortement recommandée.

### Liens utiles

- [Documentation officielle - Get Amazon GameLift Servers development tools](https://docs.aws.amazon.com/gameliftservers/latest/developerguide/gamelift-supported.html)
- [Guide de migration SDK V4 → V5](https://docs.aws.amazon.com/gameliftservers/latest/developerguide/reference-serversdk5-migration.html)
- [FAQ AL2 GameLift](https://aws.amazon.com/gamelift/faq/al2/)
