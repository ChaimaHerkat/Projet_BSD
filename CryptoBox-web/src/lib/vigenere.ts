// Vigenère + casseur, sans bibliothèque. À placer dans src/lib/ (ou à la suite de cryptobox.ts).

const A = 65;

/** Majuscules + accents retirés. Espaces, chiffres, ponctuation restent tels quels. */
export function normaliserVig(texte: string): string {
  return texte.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toUpperCase();
}

const estLettre = (c: string) => c >= "A" && c <= "Z";

function decaler(texte: string, cle: string, signe: 1 | -1): string {
  const k = [...normaliserVig(cle)].filter(estLettre).map((c) => c.charCodeAt(0) - A);
  if (k.length === 0) throw new Error("La clé doit contenir au moins une lettre.");
  let i = 0;
  let sortie = "";
  for (const c of normaliserVig(texte)) {
    if (estLettre(c)) {
      const decalage = k[i % k.length] ?? 0;
      sortie += String.fromCharCode((((c.charCodeAt(0) - A + signe * decalage) % 26) + 26) % 26 + A);
      i++; // la clé n'avance que sur les lettres
    } else {
      sortie += c; // recopié tel quel
    }
  }
  return sortie;
}

export const vigenereChiffrer = (texte: string, cle: string) => decaler(texte, cle, 1);
export const vigenereDechiffrer = (texte: string, cle: string) => decaler(texte, cle, -1);

/** Retrouve la clé de longueur L : lettre la plus fréquente de chaque colonne = un E chiffré. */
export function casserVigenere(texte: string, L: number): string {
  const t = [...normaliserVig(texte)].filter(estLettre).join("");
  let cle = "";
  for (let j = 0; j < L; j++) {
    const freq = new Array(26).fill(0);
    for (let p = j; p < t.length; p += L) freq[t.charCodeAt(p) - A]++;
    if (Math.max(...freq) === 0) throw new Error("Texte trop court pour cette longueur de clé.");
    const plusFrequente = freq.indexOf(Math.max(...freq));
    cle += String.fromCharCode(((plusFrequente - 4 + 26) % 26) + A); // 4 = rang de E
  }
  return cle;
}