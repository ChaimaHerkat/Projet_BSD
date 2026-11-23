import random
import unittest
from cryptobox import *


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

    def test_force_brute(self):
        res = cesar_force_brute(cesar_chiffrer("BONJOUR", 11))
        self.assertEqual(len(res), 25)
        self.assertIn((11, "BONJOUR"), res)

    def test_substitution(self):
        cle = "QWERTYUIOPASDFGHJKLZXCVBNM"
        self.assertEqual(substitution_chiffrer("ABC", cle), "QWE")
        self.assertEqual(substitution_dechiffrer("QWE", cle), "ABC")
        with self.assertRaises(ValueError):
            substitution_chiffrer("A", "ABC")
        with self.assertRaises(ValueError):
            substitution_chiffrer("A", "A" * 26)

    def test_transposition(self):
        self.assertEqual(transposition_chiffrer("BONJOUR", "CLE"), "BJRNUXOOX")
        self.assertEqual(transposition_dechiffrer("BJRNUXOOX", "CLE"), "BONJOURXX")

    def test_espaces_conserves_cesar(self):
        self.assertEqual(cesar_chiffrer("BONJOUR LE MONDE", 3), "ERQMRXU OH PRQGH")
        self.assertEqual(cesar_dechiffrer("ERQMRXU OH PRQGH", 3), "BONJOUR LE MONDE")
        self.assertEqual(cesar_chiffrer("Salut, ça va ? 2026", 1), "TBMVU, DB WB ? 2026")

    def test_espaces_conserves_substitution(self):
        cle = "QWERTYUIOPASDFGHJKLZXCVBNM"
        self.assertEqual(substitution_chiffrer("ABC DE", cle), "QWE RT")
        self.assertEqual(substitution_dechiffrer("QWE RT", cle), "ABC DE")

    def test_transposition_ignore_espaces(self):
        self.assertEqual(transposition_chiffrer("BON JOUR", "CLE"),
                         transposition_chiffrer("BONJOUR", "CLE"))

    def test_transposition_option_espaces(self):
        # sans option : espaces retirés (comportement du cours)
        self.assertEqual(transposition_chiffrer("BONJOUR CHAIMA", "CABA"), "OUAXJCMXNRIXBOHA")
        self.assertEqual(transposition_dechiffrer("OUAXJCMXNRIXBOHA", "CABA"), "BONJOURCHAIMAXXX")
        # avec option : l'espace est une case et revient à sa place
        c = transposition_chiffrer("BONJOUR CHAIMA", "CABA", garder_espaces=True)
        self.assertEqual(transposition_dechiffrer(c, "CABA", garder_espaces=True),
                         "BONJOUR CHAIMAXX")
        # espaces multiples / de bord réduits au chiffrement
        self.assertEqual(transposition_chiffrer("  BONJOUR   CHAIMA ", "CABA", True), c)

    def test_force_brute_conserve_espaces(self):
        res = cesar_force_brute(cesar_chiffrer("BONJOUR LE MONDE", 7))
        self.assertIn((7, "BONJOUR LE MONDE"), res)

    def test_meilleure_cle(self):
        for k in (1, 3, 11, 25):
            for phrase in ("BONJOUR", "Bonjour tout le monde", "WACH NE9RAW",
                           "Le chiffre de César est simple"):
                clair = preparer(phrase)
                self.assertEqual(cesar_meilleure_cle(cesar_chiffrer(phrase, k)),
                                 (k, clair))

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


if __name__ == "__main__":
    unittest.main()