import { describe, it, expect } from "vitest";
import * as C from "./cryptobox";

describe("cryptobox (exemples de l'énoncé)", () => {
  it("César BONJOUR k=3", () => expect(C.cesarChiffrer("BONJOUR", 3)).toBe("ERQMRXU"));
  it("Substitution ATTAQUE", () => expect(C.substitutionChiffrer("ATTAQUE", "QWERTYUIOPASDFGHJKLZXCVBNM")).toBe("QZZQJXT"));
  it("Transposition PORTE", () => expect(C.transpositionChiffrer("RENDEZVOUSAMIDI", "PORTE")).toBe("ESIEVMRZANOIDUD"));
  it("Transposition inverse", () => expect(C.transpositionDechiffrer("ESIEVMRZANOIDUD", "PORTE")).toBe("RENDEZVOUSAMIDI"));
  it("Normalisation", () => expect(C.normaliser("Été à Paris !")).toBe("ETEAPARIS"));
  it("Force brute trouve k=3", () => expect(C.cesarForceBruteClassee("ERQMRXU")[0]?.k).toBe(3));
});

describe("multi-couches", () => {
  // Chiffré construit dans l'ordre inverse du retrait : transposition en
  // premier, puis César k=3 appliqué par-dessus.
  const transposé = C.transpositionChiffrer("RENDEZVOUSAMIDI", "PORTE");
  const aRetirer: C.Couche[] = [
    { type: "cesar", k: null },
    { type: "transposition", motcle: "PORTE" },
  ];

  it("retire les couches dans l'ordre saisi", () => {
    const chiffre = C.cesarChiffrer(transposé, 3);
    const essais = C.multiForceBrute(chiffre, aRetirer);
    expect(essais[0]?.texte).toBe("RENDEZVOUSAMIDI");
    expect(essais[0]?.cles).toBe("étape 1 : k = 3");
  });

  it("teste les 25 clés d'une couche César inconnue", () => {
    const essais = C.multiForceBrute(C.cesarChiffrer(transposé, 3), aRetirer);
    expect(essais).toHaveLength(25);
    expect(new Set(essais.map((e) => e.cles))).toHaveLength(25);
  });

  it("accepte 2 couches César inconnues (625 essais) et refuse la 3e", () => {
    const deux: C.Couche[] = [{ type: "cesar", k: null }, { type: "cesar", k: null }];
    expect(C.multiForceBrute("XK", deux)).toHaveLength(625);
    const trois: C.Couche[] = [{ type: "cesar", k: null }, { type: "cesar", k: null }, { type: "cesar", k: null }];
    expect(() => C.multiForceBrute("XK", trois)).toThrow("Maximum 2 couches César à k inconnu");
  });

  it("refuse un message sans lettre", () => {
    expect(() => C.multiForceBrute("123 !?", [{ type: "cesar", k: 3 }])).toThrow("Saisis d'abord le message intercepté.");
  });

  it("une couche à clé connue n'a qu'un seul essai, décrit par « — »", () => {
    const essais = C.multiForceBrute("ERQMRXU", [{ type: "cesar", k: 3 }]);
    expect(essais).toHaveLength(1);
    expect(essais[0]?.cles).toBe("—");
    expect(essais[0]?.texte).toBe("BONJOUR");
  });

  it("signale une transposition dont la longueur ne colle pas", () => {
    const couche: C.Couche[] = [{ type: "transposition", motcle: "PORTE" }];
    expect(() => C.multiForceBrute("ABC", couche)).toThrow("non multiple de la longueur du mot-clé");
  });
});
