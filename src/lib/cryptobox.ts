// Port of cryptobox.py (CryptoBox brique 1): hand-written classical ciphers.
export const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

function sansAccents(texte: string): string {
  let t = texte.toUpperCase().replaceAll("Œ", "OE").replaceAll("Æ", "AE").replaceAll("ß", "SS");
  t = t.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  return t;
}
const isLetter = (c: string) => c >= "A" && c <= "Z";

export function normaliser(texte: string): string {
  return [...sansAccents(texte)].filter(isLetter).join("");
}
export function preparer(texte: string, garder = false): string {
  return garder ? sansAccents(texte) : normaliser(texte);
}
const mod = (n: number, m: number) => ((n % m) + m) % m;
function decaler(texte: string, k: number): string {
  return [...texte].map((c) => (isLetter(c) ? ALPHABET[mod(c.charCodeAt(0) - 65 + k, 26)] : c)).join("");
}

export const cesarChiffrer = (m: string, k: number, g = false) => decaler(preparer(m, g), k);
export const cesarDechiffrer = (c: string, k: number, g = false) => decaler(preparer(c, g), -k);
export function cesarForceBrute(c: string, g = false): [number, string][] {
  const p = preparer(c, g);
  return Array.from({ length: 25 }, (_, i) => [i + 1, cesarDechiffrer(p, i + 1, g)] as [number, string]);
}

const FREQ = [7.64, 0.9, 3.26, 3.67, 14.72, 1.07, 0.87, 0.74, 7.53, 0.61, 0.05, 5.46, 2.97, 7.1, 5.38, 3.02, 1.36, 6.55, 7.95, 7.24, 6.31, 1.63, 0.11, 0.43, 0.13, 0.33];
const LOG: Record<string, number> = Object.fromEntries([...ALPHABET].map((c, i) => [c, Math.log((FREQ[i] ?? 0.01) / 100)]));
const BIGRAMMES = new Set("ES EN LE DE RE NT ON ER TE EL AN SE ET LA OU UR IT TI AI NE ME OM UE AR RA QU CH".split(" "));
const MOTS = new Set(`LE LA LES UN UNE DES DU DE ET EN AU AUX CE CES SE SA SON SES MON MA MES TON TA TES
NOS VOS LEUR LEURS JE TU IL ELLE ON NOUS VOUS ILS ELLES MOI TOI LUI QUI QUE QUOI OU
DONT MAIS DONC OR NI CAR PAS NE PLUS TRES BIEN MAL SUR SOUS DANS PAR POUR AVEC SANS
CHEZ ENTRE VERS EST SONT ETRE AVOIR AI AS A AVONS AVEZ ONT SUIS ES SOMMES ETES FAIT
FAIRE DIT DIRE VA VAS VONT ALLER VOIR PEUT PEUX VEUX TOUT TOUS TOUTE TOUTES COMME SI
BONJOUR BONSOIR SALUT MERCI SALAM CRYPTAGE CLE MESSAGE SECRET TEXTE CHIFFRE CHIFFREMENT
CESAR MONDE AMI AMIS COURS ECOLE ETUDIANT PROFESSEUR UNIVERSITE ALGER ALGERIE
MOT MOTS PHRASE ATTAQUE DEMAIN AUJOURD HUI HIER SOIR MATIN NUIT JOUR VIE
THE AND OF TO IN IS IT YOU THAT HE WAS FOR ON ARE WITH AS HIS THEY BE AT ONE HAVE THIS
FROM OR HAD BY HELLO WORLD WORD NOT BUT WHAT ALL WERE WE WHEN YOUR CAN SAID THERE USE
WACH NE9RAW SAHA LABES KHOYA`.split(/\s+/));
const MOTS_SEG = [...MOTS].filter((m) => m.length >= 3 && /^[A-Z]+$/.test(m)).sort((a, b) => a.length - b.length);

function couverture(l: string): number {
  const best = new Array<number>(l.length + 1).fill(0);
  for (let i = 1; i <= l.length; i++) {
    best[i] = best[i - 1]!;
    for (const m of MOTS_SEG) if (m.length <= i && l.slice(i - m.length, i) === m) best[i] = Math.max(best[i]!, best[i - m.length]! + m.length);
  }
  return best[l.length]!;
}
export function score(texte: string): number {
  const l = [...texte].filter(isLetter).join("");
  if (!l) return 0;
  let s = ([...l].reduce((a, c) => a + (LOG[c] ?? 0), 0) / l.length) * 10;
  for (let i = 0; i < l.length - 1; i++) if (BIGRAMMES.has(l.slice(i, i + 2))) s += 0.5;
  let mot = "";
  for (const c of texte + " ") {
    if (isLetter(c)) mot += c;
    else { if (MOTS.has(mot)) s += 2 + mot.length; mot = ""; }
  }
  return s + 1.5 * couverture(l);
}
export const cesarForceBruteClassee = (c: string, g = false) =>
  cesarForceBrute(c, g).map(([k, t]) => ({ k, texte: t, score: score(t) })).sort((a, b) => b.score - a.score);

export function verifierCleSubstitution(cle: string): string {
  const c = normaliser(cle);
  if (c.length !== 26 || new Set(c).size !== 26) throw new Error("La clé doit contenir les 26 lettres de l'alphabet, chacune une seule fois.");
  return c;
}
export function substitutionChiffrer(m: string, cle: string, g = false) {
  const c = verifierCleSubstitution(cle);
  return [...preparer(m, g)].map((x) => (isLetter(x) ? c[x.charCodeAt(0) - 65] : x)).join("");
}
export function substitutionDechiffrer(ch: string, cle: string, g = false) {
  const c = verifierCleSubstitution(cle);
  return [...preparer(ch, g)].map((x) => (isLetter(x) ? ALPHABET[c.indexOf(x)] : x)).join("");
}
export function cleAleatoire(): string {
  const a = [...ALPHABET];
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j]!, a[i]!]; }
  return a.join("");
}

export function ordreColonnes(motcle: string): number[] {
  const m = normaliser(motcle);
  if (!m) throw new Error("Le mot-clé doit contenir au moins une lettre.");
  return Array.from({ length: m.length }, (_, i) => i).sort((a, b) => (m[a]! < m[b]! ? -1 : m[a]! > m[b]! ? 1 : a - b));
}
function preparerTransposition(t: string, g: boolean, nettoyer: boolean) {
  if (!g) return normaliser(t);
  const s = [...sansAccents(t)].map((c) => (/\s/.test(c) ? " " : c)).join("");
  return nettoyer ? s.split(" ").filter(Boolean).join(" ") : s;
}
export function transpositionChiffrer(m: string, motcle: string, g = false) {
  let msg = preparerTransposition(m, g, true);
  const n = normaliser(motcle).length;
  const ordre = ordreColonnes(motcle);
  if (msg.length % n) msg += "X".repeat(n - (msg.length % n));
  return ordre.map((col) => [...msg].filter((_, i) => i % n === col).join("")).join("");
}
export function transpositionDechiffrer(ch: string, motcle: string, g = false) {
  const c = preparerTransposition(ch, g, false);
  const n = normaliser(motcle).length;
  const ordre = ordreColonnes(motcle);
  if (c.length % n) throw new Error(`Longueur du chiffré (${c.length}) non multiple de la longueur du mot-clé (${n}).`);
  const lignes = c.length / n;
  const cols: string[] = new Array(n).fill("");
  ordre.forEach((col, rang) => (cols[col] = c.slice(rang * lignes, (rang + 1) * lignes)));
  let out = "";
  for (let r = 0; r < lignes; r++) for (let k = 0; k < n; k++) out += cols[k]![r];
  return out;
}

// ============= Multi-couches (challenge) =============
// Une couche = un algorithme + sa clé. Pour César, k === null laisse la clé
// inconnue : la force brute testera les 25 valeurs de cette couche.
export type Couche =
  | { type: "cesar"; k: number | null }
  | { type: "substitution"; cle: string }
  | { type: "transposition"; motcle: string };

export interface EssaiMulti {
  /** Description des clés testées, ex. « étape 1 : k = 3, étape 3 : k = 7 ». */
  cles: string;
  texte: string;
  score: number;
}

/** Indices des couches César dont la clé est laissée inconnue. */
export function couchesInconnues(couches: Couche[]): number[] {
  return couches.map((c, i) => (c.type === "cesar" && c.k === null ? i : -1)).filter((i) => i >= 0);
}

/** Retire les couches dans l'ordre saisi (étape 1 en premier, puis 2, ...). */
export function retirerCouches(chiffre: string, couches: Couche[], kInconnus: Record<number, number>, garder = false): string {
  let t = chiffre;
  couches.forEach((c, i) => {
    if (c.type === "cesar") t = cesarDechiffrer(t, c.k ?? kInconnus[i] ?? 0, garder);
    else if (c.type === "substitution") t = substitutionDechiffrer(t, c.cle, garder);
    else t = transpositionDechiffrer(t, c.motcle, garder);
  });
  return t;
}

const descriptionCles = (inconnues: number[], valeurs: Record<number, number>) =>
  inconnues.map((i) => `étape ${i + 1} : k = ${valeurs[i]}`).join(", ") || "—";

/**
 * Force brute multi-couches : teste toutes les combinaisons des clés César
 * inconnues (25 par couche), retire les couches dans l'ordre saisi, puis juge
 * la lisibilité de chaque texte obtenu. Les essais sont triés du plus lisible
 * au moins lisible.
 */
export function multiForceBrute(chiffre: string, couches: Couche[], garder = false): EssaiMulti[] {
  if (!normaliser(chiffre)) throw new Error("Saisis d'abord le message intercepté.");
  const inconnues = couchesInconnues(couches);
  if (inconnues.length > 2) throw new Error("Maximum 2 couches César à k inconnu (25 × 25 essais).");

  const total = 25 ** inconnues.length;
  const essais: EssaiMulti[] = [];
  for (let n = 0; n < total; n++) {
    const valeurs: Record<number, number> = {};
    let reste = n;
    for (const i of inconnues) {
      valeurs[i] = (reste % 25) + 1;
      reste = Math.floor(reste / 25);
    }
    const texte = retirerCouches(chiffre, couches, valeurs, garder);
    essais.push({ cles: descriptionCles(inconnues, valeurs), texte, score: score(texte) });
  }
  return essais.sort((a, b) => b.score - a.score);
}
