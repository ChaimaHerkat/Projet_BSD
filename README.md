# CryptoBox — version web

Chiffrement classique (César, substitution, transposition par colonnes,
multi-couches) refait en TypeScript / React à partir de la version Python
(`cryptobox.py` + `app.py`). Aucune bibliothèque de cryptographie : toute la
logique des chiffres est écrite à la main.

## Lancer le projet

```sh
npm install        # ou: bun install
npm run dev        # puis ouvrir http://localhost:8080
```

Autres commandes :

```sh
npm run test       # les tests des chiffres (13 tests)
npm run build      # build de production
npm run lint       # ESLint
```

## Où se trouve quoi

| Fichier | Rôle |
| --- | --- |
| `src/lib/cryptobox.ts` | Toute la logique : normalisation, César, substitution, transposition, score de lisibilité, force brute multi-couches. Fonctions pures, sans interface. |
| `src/lib/cryptobox.test.ts` | Tests : exemples de l'énoncé + multi-couches (ordre de retrait, nombre d'essais, limites). |
| `src/routes/index.tsx` | L'écran unique de l'application : barre de gauche (algorithme), modes, résultat, grille de transposition, panneau Multi-couches. |
| `src/routes/__root.tsx` | Structure de la page, polices, métadonnées. |
| `src/styles.css` | Thème sombre, couleurs, ombres (Tailwind CSS v4). |

## Les quatre algorithmes

- **César** — `C = (M + k) mod 26`, avec force brute classée par score.
- **Substitution** — clé = alphabet de 26 lettres, chacune une seule fois.
- **Transposition** — colonnes lues dans l'ordre alphabétique du mot-clé,
  padding avec des `X`.
- **Multi-couches** — on indique les couches dans l'ordre où elles doivent être
  retirées (étape 1 = dernière couche appliquée). Pour une couche César, cocher
  « k inconnu » teste les 25 clés. Maximum 2 couches à clé inconnue
  (25 × 25 = 625 essais), et chaque essai est classé par lisibilité.

## Normalisation

Le texte est mis en majuscules, sans accents, sans espaces ni ponctuation :
`Été à Paris !` → `ETEAPARIS`. La case « Conserver les espaces et la
ponctuation » garde la mise en forme quand c'est possible.
