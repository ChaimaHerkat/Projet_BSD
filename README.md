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
