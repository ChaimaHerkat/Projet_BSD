"""Interface Streamlit de CryptoBox.  Lancer : streamlit run app.py"""
import random

import streamlit as st

import cryptobox as cb

st.set_page_config(page_title="CryptoBox", page_icon="🔐", layout="centered")
st.title("🔐 CryptoBox")
st.caption("Brique 1 : César, substitution, transposition par colonnes")

algo = st.sidebar.radio("Algorithme", ["César", "Substitution", "Transposition"])
if algo == "Transposition":
    st.sidebar.info("La transposition travaille sur les lettres A–Z (sans accents). "
                    "Les espaces sont retirés, sauf si tu coches « Conserver les espaces ».")
else:
    st.sidebar.info("Les espaces, la ponctuation et les chiffres sont conservés ; "
                    "seules les lettres sont chiffrées (accents retirés).")

modes = ["Chiffrer", "Déchiffrer"] + (["Force brute"] if algo == "César" else [])
mode = st.radio("Mode", modes, horizontal=True)

texte = st.text_area("Message" if mode == "Chiffrer" else "Texte chiffré",
                     height=120, placeholder="Saisissez votre texte ici…", key="texte")
norm = cb.normaliser(texte)

garder_espaces = False
if algo == "Transposition":
    garder_espaces = st.checkbox(
        "Conserver les espaces", value=False,
        help="Coché : l'espace est une case du tableau et revient à sa place au "
             "déchiffrement. Décoché : les espaces sont retirés.")
    prepare = cb.preparer_transposition(texte, garder_espaces,
                                        nettoyer=(mode == "Chiffrer"))
    if texte:
        affiche = prepare.replace(" ", "␣")
        st.caption(f"Texte pris en compte ({len(prepare)} caractères"
                   f"{', espaces inclus' if garder_espaces else ''}) : "
                   f"`{affiche or '—'}`")

# ------------------------------------------------------------- clés
cle = None
if algo == "César" and mode != "Force brute":
    cle = st.slider("Clé k", 0, 25, 3)
elif algo == "Substitution":
    if "cle_sub" not in st.session_state:
        st.session_state.cle_sub = "QWERTYUIOPASDFGHJKLZXCVBNM"
    if st.button("🎲 Générer une clé aléatoire"):
        lettres = list(cb.ALPHABET)
        random.shuffle(lettres)
        st.session_state.cle_sub = "".join(lettres)
    cle = st.text_input("Clé (alphabet de 26 lettres)", key="cle_sub")
elif algo == "Transposition":
    cle = st.text_input("Mot-clé", value="CLE")

# --------------------------------------------------------- traitement
if not norm:  # aucune lettre à traiter
    st.stop()

# --- César : force brute -> on affiche d'abord la clé la plus lisible
if algo == "César" and mode == "Force brute":
    meilleur_k, meilleur_texte = cb.cesar_meilleure_cle(texte)
    st.subheader("Clé la plus probable")
    st.success(f"k = {meilleur_k}")
    st.code(meilleur_texte, language=None)

    if "tous_k" not in st.session_state:
        st.session_state.tous_k = False

    def _basculer():
        st.session_state.tous_k = not st.session_state.tous_k

    st.button("Masquer les autres clés" if st.session_state.tous_k
              else "Afficher tous les k", on_click=_basculer)

    if st.session_state.tous_k:
        st.subheader("Les 25 clés possibles")
        st.dataframe(
            [{"Clé": k, "Texte possible": t,
              "": "✅ plus probable" if k == meilleur_k else ""}
             for k, t in cb.cesar_force_brute(texte)],
            hide_index=True, width='stretch')
    st.stop()

try:
    if algo == "César":
        f = cb.cesar_chiffrer if mode == "Chiffrer" else cb.cesar_dechiffrer
    elif algo == "Substitution":
        f = (cb.substitution_chiffrer if mode == "Chiffrer"
             else cb.substitution_dechiffrer)
    else:
        f = (cb.transposition_chiffrer if mode == "Chiffrer"
             else cb.transposition_dechiffrer)
        f = lambda t, c, _f=f: _f(t, c, garder_espaces)
    resultat = f(texte, cle)
except ValueError as e:
    st.error(str(e))
    st.stop()

st.subheader("Résultat")
st.code(resultat, language=None)

# ------------------------------------------------ visualisation par algo
if algo == "Substitution":
    with st.expander("Table de substitution"):
        st.dataframe([dict(zip(cb.ALPHABET, cb.normaliser(cle))),],
                     hide_index=True, width='stretch')

if algo == "Transposition":
    mot = cb.normaliser(cle)
    n = len(mot)
    ordre = cb._ordre_colonnes(mot)
    numeros = {col: rang + 1 for rang, col in enumerate(ordre)}
    if mode == "Chiffrer":
        grille_txt = prepare + "X" * (-len(prepare) % n)
    else:
        grille_txt = resultat
    grille_txt = grille_txt.replace(" ", "␣")  # espace visible dans la grille
    lignes = [grille_txt[i:i + n] for i in range(0, len(grille_txt), n)]
    with st.expander("Grille de transposition", expanded=True):
        colonnes_nom = [f"{mot[i]} ({numeros[i]})" for i in range(n)]
        st.dataframe([dict(zip(colonnes_nom, l)) for l in lignes], hide_index=True)
        st.caption("Entre parenthèses : l'ordre de lecture des colonnes."
                   + (" ␣ = espace." if garder_espaces else ""))