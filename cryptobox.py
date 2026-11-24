#!/usr/bin/env python3
"""CryptoBox - brique 1 : César, substitution, transposition par colonnes.

Aucune bibliothèque de cryptographie : tout est codé à la main.

Convention de l'énoncé (comportement par défaut) :
  lettres majuscules A-Z uniquement, sans espaces ni accents.
  Tout texte saisi est donc normalisé d'abord : 'Été à Paris !' -> 'ETEAPARIS'.

Option garder_espaces=True (les trois algorithmes) :
  les espaces, la ponctuation et les chiffres sont conservés (accents retirés,
  tout en majuscules). César/substitution les laissent à leur place ;
  en transposition ce sont des cases du tableau qui reviennent à leur
  place au déchiffrement.
"""
import argparse
import math
import sys
import unicodedata

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


# ---------------------------------------------------------------- outils
def _sans_accents(texte):
    """Majuscules + accents retirés, tout le reste est conservé.
    'Été à Paris !' -> 'ETE A PARIS !'"""
    for avant, apres in (("Œ", "OE"), ("Æ", "AE"), ("ß", "SS")):
        texte = texte.upper().replace(avant, apres)
    texte = unicodedata.normalize("NFD", texte)  # É -> E + accent combinant
    return "".join(c for c in texte if not unicodedata.combining(c))


def normaliser(texte):
    """Format de l'énoncé : majuscules A-Z seulement.
    'Été à Paris !' -> 'ETEAPARIS'."""
    return "".join(c for c in _sans_accents(texte) if "A" <= c <= "Z")


def preparer(texte, garder_espaces=False):
    """Texte prêt pour César / substitution.
    Par défaut : A-Z seulement. Avec garder_espaces : on garde espaces,
    ponctuation et chiffres (seules les lettres seront chiffrées)."""
    return _sans_accents(texte) if garder_espaces else normaliser(texte)


def _decaler(texte, k):
    """Décale les lettres A-Z de k places ; tout le reste est laissé tel quel."""
    return "".join(ALPHABET[(ord(c) - 65 + k) % 26] if "A" <= c <= "Z" else c
                   for c in texte)


# ---------------------------------------------------------------- César
def cesar_chiffrer(message, k, garder_espaces=False):
    """C = (M + k) mod 26   (k : n'importe quel entier)"""
    return _decaler(preparer(message, garder_espaces), k)


def cesar_dechiffrer(chiffre, k, garder_espaces=False):
    """M = (C - k) mod 26"""
    return _decaler(preparer(chiffre, garder_espaces), -k)


def cesar_force_brute(chiffre, garder_espaces=False):
    """Teste les 25 clés (1 à 25). Renvoie une liste de (clé, texte clair possible)."""
    chiffre = preparer(chiffre, garder_espaces)
    return [(k, cesar_dechiffrer(chiffre, k, garder_espaces)) for k in range(1, 26)]


# --- choix automatique de la clé la plus plausible (force brute lisible)
# Fréquences des lettres en français (en %).
_FREQ_FR = dict(zip(ALPHABET, [
    7.64, 0.90, 3.26, 3.67, 14.72, 1.07, 0.87, 0.74, 7.53, 0.61, 0.05, 5.46, 2.97,
    7.10, 5.38, 3.02, 1.36, 6.55, 7.95, 7.24, 6.31, 1.63, 0.11, 0.43, 0.13, 0.33]))
_LOG_FR = {c: math.log(f / 100) for c, f in _FREQ_FR.items()}

_BIGRAMMES = ("ES EN LE DE RE NT ON ER TE EL AN SE ET LA OU UR IT TI AI NE "
              "ME OM UE AR RA QU CH").split()

_MOTS = set("""
LE LA LES UN UNE DES DU DE ET EN AU AUX CE CES SE SA SON SES MON MA MES TON TA TES
NOS VOS LEUR LEURS JE TU IL ELLE ON NOUS VOUS ILS ELLES MOI TOI LUI QUI QUE QUOI OU
DONT MAIS DONC OR NI CAR PAS NE PLUS TRES BIEN MAL SUR SOUS DANS PAR POUR AVEC SANS
CHEZ ENTRE VERS EST SONT ETRE AVOIR AI AS A AVONS AVEZ ONT SUIS ES SOMMES ETES FAIT
FAIRE DIT DIRE VA VAS VONT ALLER VOIR PEUT PEUX VEUX TOUT TOUS TOUTE TOUTES COMME SI
BONJOUR BONSOIR SALUT MERCI SALAM CRYPTAGE CLE MESSAGE SECRET TEXTE CHIFFRE CHIFFREMENT
CESAR MONDE AMI AMIS COURS ECOLE ETUDIANT PROFESSEUR UNIVERSITE ALGER ALGERIE
MOT MOTS PHRASE ATTAQUE DEMAIN AUJOURD HUI HIER SOIR MATIN NUIT JOUR VIE
THE AND OF TO IN IS IT YOU THAT HE WAS FOR ON ARE WITH AS HIS THEY BE AT ONE HAVE THIS
FROM OR HAD BY HELLO WORLD WORD NOT BUT WHAT ALL WERE WE WHEN YOUR CAN SAID THERE USE
WACH NE9RAW SAHA LABES KHOYA
""".split())

# Mots d'au moins 3 lettres, pour repérer des mots collés (texte sans espaces).
_MOTS_SEG = sorted((m for m in _MOTS if len(m) >= 3 and m.isalpha()), key=len)


def _couverture(lettres):
    """Nombre maximal de lettres couvertes par des mots connus mis bout à bout
    (découpage d'un texte sans espaces en mots du dictionnaire)."""
    meilleur = [0] * (len(lettres) + 1)
    for i in range(1, len(lettres) + 1):
        meilleur[i] = meilleur[i - 1]
        for m in _MOTS_SEG:
            if len(m) <= i and lettres[i - len(m):i] == m:
                meilleur[i] = max(meilleur[i], meilleur[i - len(m)] + len(m))
    return meilleur[-1]


def _score(texte):
    """Plus le score est élevé, plus le texte ressemble à du français lisible."""
    lettres = "".join(c for c in texte if "A" <= c <= "Z")
    if not lettres:
        return 0.0
    # 1) vraisemblance des fréquences de lettres (moyenne par lettre)
    score = sum(_LOG_FR[c] for c in lettres) / len(lettres) * 10
    # 2) bigrammes fréquents en français
    for i in range(len(lettres) - 1):
        if lettres[i:i + 2] in _BIGRAMMES:
            score += 0.5
    # 3) mots reconnus (le signal le plus fort)
    mot = ""
    for c in texte + " ":
        if "A" <= c <= "Z":
            mot += c
        else:
            if mot in _MOTS:
                score += 2 + len(mot)
            mot = ""
    # 4) texte collé sans espaces : mots connus mis bout à bout
    score += 1.5 * _couverture(lettres)
    return score


def cesar_meilleure_cle(chiffre, garder_espaces=False):
    """Renvoie (k, texte clair) pour la clé qui donne le texte le plus lisible."""
    return max(cesar_force_brute(chiffre, garder_espaces),
               key=lambda kt: _score(kt[1]))


def cesar_force_brute_classee(chiffre, garder_espaces=False):
    """Les 25 candidats triés du plus lisible au moins lisible."""
    return sorted(cesar_force_brute(chiffre, garder_espaces),
                  key=lambda kt: -_score(kt[1]))


# --------------------------------------------------------- Substitution
def verifier_cle_substitution(cle):
    cle = normaliser(cle)
    if len(cle) != 26 or set(cle) != set(ALPHABET):
        raise ValueError("La clé doit contenir les 26 lettres de l'alphabet, "
                         "chacune une seule fois.")
    return cle


def _substituer(texte, table, garder_espaces):
    return "".join(table.get(c, c) for c in preparer(texte, garder_espaces))


def substitution_chiffrer(message, cle, garder_espaces=False):
    """A -> 1re lettre de la clé, B -> 2e, etc."""
    cle = verifier_cle_substitution(cle)
    return _substituer(message, dict(zip(ALPHABET, cle)), garder_espaces)


def substitution_dechiffrer(chiffre, cle, garder_espaces=False):
    cle = verifier_cle_substitution(cle)
    return _substituer(chiffre, dict(zip(cle, ALPHABET)), garder_espaces)  # table inverse


# --------------------------------------------------------- Transposition
def _ordre_colonnes(motcle):
    """Indices des colonnes dans l'ordre alphabétique du mot-clé.
    Lettres répétées : celle de gauche passe en premier."""
    motcle = normaliser(motcle)
    if not motcle:
        raise ValueError("Le mot-clé doit contenir au moins une lettre.")
    return sorted(range(len(motcle)), key=lambda i: (motcle[i], i))


def preparer_transposition(texte, garder_espaces=False, nettoyer=True):
    """Texte tel qu'il est placé dans la grille de transposition.
    - garder_espaces=False : lettres A-Z seulement (énoncé).
    - garder_espaces=True  : espaces, ponctuation et chiffres sont des cases.
      Avec nettoyer=True (chiffrement) les blancs multiples/de bord sont
      réduits ; avec nettoyer=False (déchiffrement) on ne touche à rien."""
    if not garder_espaces:
        return normaliser(texte)
    texte = "".join(" " if c.isspace() else c for c in _sans_accents(texte))
    return " ".join(texte.split()) if nettoyer else texte


def transposition_chiffrer(message, motcle, garder_espaces=False):
    message = preparer_transposition(message, garder_espaces, nettoyer=True)
    n = len(normaliser(motcle))
    ordre = _ordre_colonnes(motcle)
    if len(message) % n:
        message += "X" * (n - len(message) % n)  # complète la dernière ligne
    return "".join(message[col::n] for col in ordre)  # colonne = 1 caractère sur n


def transposition_dechiffrer(chiffre, motcle, garder_espaces=False):
    """Attention : les X de remplissage restent à la fin (ils sont
    indiscernables de vrais X). Sans garder_espaces, les espaces d'origine
    ne reviennent pas (ils ont été retirés au chiffrement)."""
    chiffre = preparer_transposition(chiffre, garder_espaces, nettoyer=False)
    n = len(normaliser(motcle))
    ordre = _ordre_colonnes(motcle)
    if len(chiffre) % n:
        raise ValueError(f"Longueur du chiffré ({len(chiffre)}) non multiple "
                         f"de la longueur du mot-clé ({n})."
                         + (" (les espaces comptent comme des caractères)"
                            if garder_espaces else ""))
    lignes = len(chiffre) // n
    colonnes = [""] * n
    for rang, col in enumerate(ordre):  # le rang-ième bloc appartient à la colonne col
        colonnes[col] = chiffre[rang * lignes:(rang + 1) * lignes]
    return "".join(colonnes[c][r] for r in range(lignes) for c in range(n))


# ------------------------------------------------------------------ CLI
def _lire_message(arg):
    return arg if arg is not None else sys.stdin.read()


def _parser():
    p = argparse.ArgumentParser(prog="cryptobox",
                                description="CryptoBox - brique 1")
    sub = p.add_subparsers(dest="algo", required=True)
    aide_esp = ("garder espaces, ponctuation et chiffres "
                "(par défaut : lettres A-Z seulement)")

    c = sub.add_parser("cesar", help="chiffre de César")
    c.add_argument("action", choices=["chiffrer", "dechiffrer", "brute"])
    c.add_argument("texte", nargs="?")
    c.add_argument("-k", "--cle", type=int, help="décalage (entier quelconque)")
    c.add_argument("--tous", action="store_true",
                   help="avec 'brute' : afficher les 25 clés (sinon la plus lisible)")
    c.add_argument("--espaces", action="store_true", help=aide_esp)

    s = sub.add_parser("substitution", help="substitution monoalphabétique")
    s.add_argument("action", choices=["chiffrer", "dechiffrer"])
    s.add_argument("texte", nargs="?")
    s.add_argument("-k", "--cle", required=True, help="alphabet de 26 lettres")
    s.add_argument("--espaces", action="store_true", help=aide_esp)

    t = sub.add_parser("transposition", help="transposition par colonnes")
    t.add_argument("action", choices=["chiffrer", "dechiffrer"])
    t.add_argument("texte", nargs="?")
    t.add_argument("-k", "--cle", required=True, help="mot-clé")
    t.add_argument("--espaces", action="store_true", help=aide_esp)
    return p


def main(argv=None):
    a = _parser().parse_args(argv)
    texte = _lire_message(a.texte)
    try:
        if a.algo == "cesar":
            if a.action == "brute":
                if a.tous:
                    for k, t in cesar_force_brute(texte, a.espaces):
                        print(f"{k:2d}  {t}")
                else:
                    k, t = cesar_meilleure_cle(texte, a.espaces)
                    print(f"k = {k} : {t}")
                return 0
            if a.cle is None:
                raise ValueError("L'option -k est requise.")
            f = cesar_chiffrer if a.action == "chiffrer" else cesar_dechiffrer
            print(f(texte, a.cle, a.espaces))
        else:
            fonctions = {
                ("substitution", "chiffrer"): substitution_chiffrer,
                ("substitution", "dechiffrer"): substitution_dechiffrer,
                ("transposition", "chiffrer"): transposition_chiffrer,
                ("transposition", "dechiffrer"): transposition_dechiffrer,
            }
            print(fonctions[(a.algo, a.action)](texte, a.cle, a.espaces))
    except ValueError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())