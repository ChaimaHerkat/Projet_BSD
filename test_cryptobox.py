import random
import unittest
from cryptobox import *

CLE_QWERTY = "QWERTYUIOPASDFGHJKLZXCVBNM"


class TestExemplesEnonce(unittest.TestCase):
    """Les trois exemples donnés dans l'énoncé du projet."""

    def test_cesar(self):
        self.assertEqual(cesar_chiffrer("BONJOUR", 3), "ERQMRXU")
        self.assertEqual(cesar_dechiffrer("ERQMRXU", 3), "BONJOUR")

    def test_substitution(self):
        self.assertEqual(substitution_chiffrer("ATTAQUE", CLE_QWERTY), "QZZQJXT")
        self.assertEqual(substitution_dechiffrer("QZZQJXT", CLE_QWERTY), "ATTAQUE")

    def test_transposition(self):
        self.assertEqual(transposition_chiffrer("RENDEZVOUSAMIDI", "PORTE"),
                         "ESIEVMRZANOIDUD")
        self.assertEqual(transposition_dechiffrer("ESIEVMRZANOIDUD", "PORTE"),
                         "RENDEZVOUSAMIDI")


class TestCryptoBox(unittest.TestCase):
    def test_normaliser(self):
        self.assertEqual(normaliser("Été à Paris, 2026 !"), "ETEAPARIS")
        self.assertEqual(normaliser("Cœur"), "COEUR")

    def test_cesar(self):
        self.assertEqual(cesar_chiffrer("HELLO", 3), "KHOOR")
        self.assertEqual(cesar_chiffrer("XYZ", 3), "ABC")
        self.assertEqual(cesar_dechiffrer("KHOOR", 3), "HELLO")
        self.assertEqual(cesar_chiffrer("ABC", 0), "ABC")
        self.assertEqual(cesar_chiffrer("ABC", 29), cesar_chiffrer("ABC", 3))

    def test_cesar_cle_quelconque(self):
        self.assertEqual(cesar_chiffrer("ABC", -1), "ZAB")
        self.assertEqual(cesar_chiffrer("ABC", 10**12), cesar_chiffrer("ABC", 10**12 % 26))
        self.assertEqual(cesar_chiffrer("", 5), "")

    def test_force_brute(self):
        res = cesar_force_brute(cesar_chiffrer("BONJOUR", 11))
        self.assertEqual(len(res), 25)
        self.assertEqual([k for k, _ in res], list(range(1, 26)))
        self.assertIn((11, "BONJOUR"), res)

    def test_substitution(self):
        self.assertEqual(substitution_chiffrer("ABC", CLE_QWERTY), "QWE")
        self.assertEqual(substitution_dechiffrer("QWE", CLE_QWERTY), "ABC")
        with self.assertRaises(ValueError):
            substitution_chiffrer("A", "ABC")
        with self.assertRaises(ValueError):
            substitution_chiffrer("A", "A" * 26)

    def test_transposition(self):
        self.assertEqual(transposition_chiffrer("BONJOUR", "CLE"), "BJRNUXOOX")
        self.assertEqual(transposition_dechiffrer("BJRNUXOOX", "CLE"), "BONJOURXX")

    def test_transposition_cas_limites(self):
        self.assertEqual(transposition_chiffrer("", "CLE"), "")
        # mot-clé plus long que le message : tout est complété par des X
        self.assertEqual(len(transposition_chiffrer("AB", "MOTCLE")), 6)
        # mot-clé en minuscules / avec accents / espaces = même clé
        self.assertEqual(transposition_chiffrer("BONJOUR", "clé"),
                         transposition_chiffrer("BONJOUR", "CLE"))
        with self.assertRaises(ValueError):
            transposition_chiffrer("BONJOUR", "123")

    def test_convention_par_defaut_sans_espaces(self):
        # énoncé : A-Z uniquement, sans espaces ni accents
        self.assertEqual(cesar_chiffrer("Bonjour le monde !", 3), "ERQMRXUOHPRQGH")
        self.assertEqual(substitution_chiffrer("ABC DE", CLE_QWERTY), "QWERT")
        self.assertEqual(transposition_chiffrer("BON JOUR", "CLE"),
                         transposition_chiffrer("BONJOUR", "CLE"))

    def test_option_espaces_cesar(self):
        self.assertEqual(cesar_chiffrer("BONJOUR LE MONDE", 3, True), "ERQMRXU OH PRQGH")
        self.assertEqual(cesar_dechiffrer("ERQMRXU OH PRQGH", 3, True), "BONJOUR LE MONDE")
        self.assertEqual(cesar_chiffrer("Salut, ça va ? 2026", 1, True), "TBMVU, DB WB ? 2026")

    def test_option_espaces_substitution(self):
        self.assertEqual(substitution_chiffrer("ABC DE", CLE_QWERTY, True), "QWE RT")
        self.assertEqual(substitution_dechiffrer("QWE RT", CLE_QWERTY, True), "ABC DE")

    def test_option_espaces_transposition(self):
        self.assertEqual(transposition_chiffrer("BONJOUR CHAIMA", "CABA"), "OUAXJCMXNRIXBOHA")
        self.assertEqual(transposition_dechiffrer("OUAXJCMXNRIXBOHA", "CABA"), "BONJOURCHAIMAXXX")
        c = transposition_chiffrer("BONJOUR CHAIMA", "CABA", garder_espaces=True)
        self.assertEqual(transposition_dechiffrer(c, "CABA", garder_espaces=True),
                         "BONJOUR CHAIMAXX")
        self.assertEqual(transposition_chiffrer("  BONJOUR   CHAIMA ", "CABA", True), c)

    def test_force_brute_option_espaces(self):
        res = cesar_force_brute(cesar_chiffrer("BONJOUR LE MONDE", 7, True), True)
        self.assertIn((7, "BONJOUR LE MONDE"), res)

    def test_meilleure_cle(self):
        for k in (1, 3, 11, 25):
            for phrase in ("BONJOUR", "Bonjour tout le monde",
                           "Le chiffre de César est simple", "Attaque à l'aube"):
                for esp in (True, False):
                    clair = preparer(phrase, esp)
                    chiffre = cesar_chiffrer(phrase, k, esp)
                    self.assertEqual(cesar_meilleure_cle(chiffre, esp), (k, clair))

    def test_meilleure_cle_exemple_du_cours(self):
        # diapo : ZDFK QH9UDZ (k = 3) -> WACH NE9RAW (chiffre et chiffre gardés)
        self.assertEqual(cesar_meilleure_cle("ZDFK QH9UDZ", True), (3, "WACH NE9RAW"))

    def test_aller_retour_aleatoire(self):
        for _ in range(300):
            m = "".join(random.choice(ALPHABET) for _ in range(random.randint(0, 80)))
            k = random.randint(-50, 50)
            self.assertEqual(cesar_dechiffrer(cesar_chiffrer(m, k), k), m)
            cle = list(ALPHABET); random.shuffle(cle); cle = "".join(cle)
            self.assertEqual(substitution_dechiffrer(substitution_chiffrer(m, cle), cle), m)
            mot = "".join(random.choice(ALPHABET) for _ in range(random.randint(1, 9)))
            n = len(mot)
            attendu = m + "X" * (-len(m) % n)
            self.assertEqual(transposition_dechiffrer(transposition_chiffrer(m, mot), mot), attendu)
            # avec espaces : mots séparés par un seul espace
            mots = ["".join(random.choice(ALPHABET) for _ in range(random.randint(1, 6)))
                    for _ in range(random.randint(1, 6))]
            m2 = " ".join(mots)
            att2 = m2 + "X" * (-len(m2) % n)
            c2 = transposition_chiffrer(m2, mot, garder_espaces=True)
            self.assertEqual(transposition_dechiffrer(c2, mot, garder_espaces=True), att2)
            self.assertEqual(cesar_dechiffrer(cesar_chiffrer(m2, k, True), k, True), m2)
            self.assertEqual(substitution_dechiffrer(substitution_chiffrer(m2, cle, True), cle, True), m2)


if __name__ == "__main__":
    unittest.main()