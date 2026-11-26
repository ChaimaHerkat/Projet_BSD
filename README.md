<<<<<<< HEAD
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
=======
# CryptoBox — brique 1

Outil de chiffrement classique codé à la main (aucune bibliothèque de cryptographie) :

- **César** : chiffrer, déchiffrer, force brute (teste les 25 clés)
- **Substitution** : chiffrer, déchiffrer avec une clé de 26 lettres
- **Transposition par colonnes** : chiffrer, déchiffrer avec un mot-clé

## Convention

Par défaut, tout texte est normalisé en **majuscules A–Z, sans espaces ni accents**
(`Été à Paris !` → `ETEAPARIS`). L'option « Conserver les espaces »
(`--espaces` en ligne de commande) garde aussi espaces, ponctuation et chiffres.

- César : `C = (M + k) mod 26` (k entier quelconque)
- Substitution : A → 1re lettre de la clé, B → 2e, etc.
- Transposition : message écrit en lignes sous le mot-clé (dernière ligne complétée
  par des `X`), colonnes lues dans l'ordre alphabétique des lettres du mot-clé
  (lettres répétées : celle de gauche d'abord).

Exemples de l'énoncé :

| Algorithme | Entrée | Clé | Sortie |
|---|---|---|---|
| César | `BONJOUR` | k = 3 | `ERQMRXU` |
| Substitution | `ATTAQUE` | `QWERTYUIOPASDFGHJKLZXCVBNM` | `QZZQJXT` |
| Transposition | `RENDEZVOUSAMIDI` | `PORTE` | `ESIEVMRZANOIDUD` |

## Installation

```
pip install -r requirements.txt
```

## Interface web (Streamlit)

```
streamlit run app.py
```

En force brute, la clé la plus lisible est affichée d'abord ; le bouton
« Afficher tous les k » montre les 25 clés testées.

## Ligne de commande

```
python cryptobox.py cesar chiffrer "Bonjour" -k 3
python cryptobox.py cesar brute ERQMRXU            # clé la plus lisible
python cryptobox.py cesar brute ERQMRXU --tous     # les 25 clés
python cryptobox.py substitution chiffrer ATTAQUE -k QWERTYUIOPASDFGHJKLZXCVBNM
python cryptobox.py transposition chiffrer RENDEZVOUSAMIDI -k PORTE
python cryptobox.py transposition dechiffrer ESIEVMRZANOIDUD -k PORTE
```

Ajouter `--espaces` pour garder espaces et ponctuation.

## Tests

```
python -m unittest -v
```

## Limites connues

- Au déchiffrement de la transposition, les `X` de remplissage restent à la fin
  (ils sont indiscernables de vrais `X`).
- Le choix automatique de la clé en force brute s'appuie sur des statistiques du
  français : il peut se tromper sur un texte très court ou composé de noms propres ;
  le tableau des 25 clés reste disponible.
>>>>>>> 34cb967899d93074073e7b4c27b848fce2614f27
