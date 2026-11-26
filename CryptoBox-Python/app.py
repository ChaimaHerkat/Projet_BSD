"""Interface Streamlit de CryptoBox.  Lancer : streamlit run app.py"""
import itertools
import random

import streamlit as st

import cryptobox as cb

st.set_page_config(page_title="CryptoBox", page_icon="🔐", layout="centered")
st.title("🔐 CryptoBox")
st.caption("Brique 1 : César, substitution, transposition par colonnes")


def tableau(donnees):
    """Affiche un tableau pleine largeur (compatible anciennes et nouvelles
    versions de Streamlit)."""
    try:
        st.dataframe(donnees, hide_index=True, width="stretch")
    except TypeError:
        st.dataframe(donnees, hide_index=True, use_container_width=True)


algo = st.sidebar.radio("Algorithme",
                        ["César", "Substitution", "Transposition", "Multi-couches"])
st.sidebar.info("Convention du projet : le texte est normalisé en majuscules A–Z, "
                "sans espaces ni accents. Tu peux cocher « Conserver les espaces » "
                "pour garder aussi espaces, ponctuation et chiffres.")

# ------------------------------------------------ Multi-couches (challenge)
if algo == "Multi-couches":
    st.subheader("Multi-couches : déchiffrement automatique")
    st.caption("Entre les couches dans l'ordre où on doit les RETIRER : "
               "l'étape 1 est la première à retirer (= la dernière couche "
               "appliquée au chiffrement). Pour une couche César, coche "
               "« k inconnu » : l'outil teste les 25 clés et garde celle qui "
               "donne un texte lisible.")

    chiffre_mc = st.text_area("Message intercepté", height=100,
                              placeholder="Ex : WMRQOPTPTPYP", key="mc_texte")
    garder_mc = st.checkbox("Conserver les espaces", value=False, key="mc_esp")
    nb = int(st.number_input("Nombre de couches", min_value=1, max_value=5,
                             value=3, step=1))

    couches = []  # (algorithme, clé) ; clé None = César à k inconnu
    for i in range(nb):
        st.markdown(f"**Étape {i + 1}** : couche à retirer " +
                    ("en premier" if i == 0 else f"en n°{i + 1}"))
        col1, col2 = st.columns([1, 2])
        type_ = col1.selectbox("Algorithme",
                               ["César", "Substitution", "Transposition"],
                               key=f"mc_algo_{i}")
        if type_ == "César":
            inconnu = col2.checkbox("k inconnu (force brute)", value=True,
                                    key=f"mc_inc_{i}")
            if inconnu:
                cle_i = None
            else:
                cle_i = int(col2.number_input("Clé k", value=3, step=1,
                                              key=f"mc_k_{i}"))
        elif type_ == "Substitution":
            cle_i = col2.text_input("Clé (alphabet de 26 lettres)",
                                    key=f"mc_cle_{i}")
        else:
            cle_i = col2.text_input("Mot-clé", key=f"mc_cle_{i}")
        couches.append((type_, cle_i))

    inconnues = [i for i, (t, c) in enumerate(couches)
                 if t == "César" and c is None]
    if len(inconnues) > 2:
        st.warning("Maximum 2 couches César à k inconnu (25 × 25 essais).")
        st.stop()

    def retirer(t, valeurs):
        """Retire les couches dans l'ordre saisi (étape 1, puis 2, ...)."""
        for i in range(len(couches)):
            type_i, cle_i = couches[i]
            if type_i == "César":
                k = cle_i if cle_i is not None else valeurs[i]
                t = cb.cesar_dechiffrer(t, k, garder_mc)
            elif type_i == "Substitution":
                t = cb.substitution_dechiffrer(t, cle_i, garder_mc)
            else:
                t = cb.transposition_dechiffrer(t, cle_i, garder_mc)
        return t

    if st.button("🔎 Déchiffrer / Force brute"):
        if not cb.normaliser(chiffre_mc):
            st.error("Saisis d'abord le message intercepté.")
            st.stop()
        resultats = []  # (description des k testés, texte obtenu)
        try:
            for ks in itertools.product(range(1, 26), repeat=len(inconnues)):
                valeurs = dict(zip(inconnues, ks))
                texte_i = retirer(chiffre_mc, valeurs)
                desc = ", ".join(f"étape {i + 1} : k = {k}"
                                 for i, k in valeurs.items()) or "—"
                resultats.append((desc, texte_i))
        except ValueError as e:
            st.error(str(e))
            st.stop()

        meilleur = max(resultats, key=lambda r: cb._score(r[1]))
        st.subheader("Résultat le plus lisible")
        if inconnues:
            st.success(meilleur[0])
        st.code(meilleur[1], language=None)
        st.caption(f"8 premières lettres : {meilleur[1][:8]}")
        if len(resultats) > 1:
            with st.expander(f"Les {len(resultats)} essais"):
                tableau([{"Clés testées": d, "Texte obtenu": t,
                          "": "✅ plus lisible" if t == meilleur[1] else ""}
                         for d, t in resultats])
    st.stop()

modes = ["Chiffrer", "Déchiffrer"] + (["Force brute"] if algo == "César" else [])
mode = st.radio("Mode", modes, horizontal=True)

texte = st.text_area("Message" if mode == "Chiffrer" else "Texte chiffré",
                     height=120, placeholder="Saisissez votre texte ici…", key="texte")
garder_espaces = st.checkbox(
    "Conserver les espaces",
    value=False,
    help="Décoché (convention de l'énoncé) : espaces, ponctuation et accents sont "
         "retirés. Coché : ils sont conservés ; seules les lettres sont chiffrées "
         "(en transposition, chaque espace est une case du tableau).")

# texte réellement traité (visible pour comprendre la normalisation)
if algo == "Transposition":
    prepare = cb.preparer_transposition(texte, garder_espaces,
                                        nettoyer=(mode == "Chiffrer"))
else:
    prepare = cb.preparer(texte, garder_espaces)
if texte:
    st.caption(f"Texte pris en compte ({len(prepare)} caractères) : "
               f"`{prepare.replace(' ', '␣') or '—'}`")

# ------------------------------------------------------------- clés
cle = None
if algo == "César" and mode != "Force brute":
    cle = int(st.number_input("Clé k (entier quelconque)", value=3, step=1))
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
if not cb.normaliser(texte):  # aucune lettre à traiter
    st.stop()

# --- César : force brute (avec option : retirer aussi les autres couches)
if algo == "César" and mode == "Force brute":
    autres = st.checkbox(
        "Retirer aussi les couches suivantes (transposition / substitution)",
        help="Pour le challenge à plusieurs couches : pour chacune des 25 clés, "
             "on retire aussi les autres couches avant de juger si le texte "
             "est lisible.")
    ordre = ""
    mot = sub = ""
    if autres:
        ordre = st.selectbox("Ordre de retrait après César",
                             ["Transposition puis Substitution",
                              "Substitution puis Transposition"])
        mot = st.text_input("Mot-clé de transposition", "CAMION")
        sub = st.text_input("Clé de substitution",
                            "BIZHGQRESNOXJKMFLVDWYCPUAT")

    def candidat(k):
        """Texte obtenu pour la clé k, après retrait des couches suivantes."""
        t = cb.cesar_dechiffrer(texte, k, garder_espaces)
        if autres:
            if ordre.startswith("Transposition"):
                t = cb.transposition_dechiffrer(t, mot, garder_espaces)
                t = cb.substitution_dechiffrer(t, sub, garder_espaces)
            else:
                t = cb.substitution_dechiffrer(t, sub, garder_espaces)
                t = cb.transposition_dechiffrer(t, mot, garder_espaces)
        return t

    try:
        resultats = [(k, candidat(k)) for k in range(1, 26)]
    except ValueError as e:
        st.error(str(e))
        st.stop()

    meilleur_k, meilleur_texte = max(resultats, key=lambda kt: cb._score(kt[1]))
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
        st.subheader("Les 25 clés testées")
        tableau([{"Clé": k, "Texte possible": t,
                  "": "✅ plus probable" if k == meilleur_k else ""}
                 for k, t in resultats])
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
    resultat = f(texte, cle, garder_espaces)
except ValueError as e:
    st.error(str(e))
    st.stop()

st.subheader("Résultat")
st.code(resultat, language=None)

# ------------------------------------------------ visualisation par algo
if algo == "Substitution":
    with st.expander("Table de substitution"):
        tableau([dict(zip(cb.ALPHABET, cb.normaliser(cle)))])

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