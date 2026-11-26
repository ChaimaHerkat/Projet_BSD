import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Copy, Dices, KeyRound, Lock, LockOpen, ShieldCheck, Shuffle, Columns3, Search, Layers, Plus, X } from "lucide-react";
import { toast } from "sonner";
import { Toaster } from "@/components/ui/sonner";
import * as C from "@/lib/cryptobox";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CryptoBox — Chiffrement classique" },
      { name: "description", content: "Chiffrez et déchiffrez avec César, substitution, transposition et multi-couches, plus force brute automatique." },
      { property: "og:title", content: "CryptoBox — Chiffrement classique" },
      { property: "og:description", content: "César, substitution, transposition par colonnes, multi-couches et force brute, dans le navigateur." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

type Algo = "cesar" | "substitution" | "transposition" | "multi";
type Mode = "chiffrer" | "dechiffrer" | "brute";

const ALGOS: { id: Algo; label: string; desc: string; icon: typeof Lock }[] = [
  { id: "cesar", label: "César", desc: "C = (M + k) mod 26", icon: KeyRound },
  { id: "substitution", label: "Substitution", desc: "Alphabet de 26 lettres", icon: Shuffle },
  { id: "transposition", label: "Transposition", desc: "Colonnes par mot-clé", icon: Columns3 },
  { id: "multi", label: "Multi-couches", desc: "Couches enchaînées", icon: Layers },
];

function Index() {
  const [algo, setAlgo] = useState<Algo>("cesar");
  const [mode, setMode] = useState<Mode>("chiffrer");
  const [texte, setTexte] = useState("BONJOUR");
  const [garder, setGarder] = useState(false);
  const [k, setK] = useState(3);
  const [cleSub, setCleSub] = useState("QWERTYUIOPASDFGHJKLZXCVBNM");
  const [mot, setMot] = useState("PORTE");
  const [tout, setTout] = useState(false);

  const effectiveMode: Mode = algo !== "cesar" && mode === "brute" ? "chiffrer" : mode;

  const { resultat, erreur, brute } = useMemo(() => {
    try {
      if (algo === "cesar") {
        if (effectiveMode === "brute") return { resultat: "", erreur: "", brute: C.cesarForceBruteClassee(texte, garder) };
        return { resultat: effectiveMode === "chiffrer" ? C.cesarChiffrer(texte, k, garder) : C.cesarDechiffrer(texte, k, garder), erreur: "", brute: null };
      }
      if (algo === "substitution")
        return { resultat: effectiveMode === "chiffrer" ? C.substitutionChiffrer(texte, cleSub, garder) : C.substitutionDechiffrer(texte, cleSub, garder), erreur: "", brute: null };
      return { resultat: effectiveMode === "chiffrer" ? C.transpositionChiffrer(texte, mot, garder) : C.transpositionDechiffrer(texte, mot, garder), erreur: "", brute: null };
    } catch (e) {
      return { resultat: "", erreur: (e as Error).message, brute: null };
    }
  }, [algo, effectiveMode, texte, garder, k, cleSub, mot]);

  const prepare = C.preparer(texte, garder);
  const copier = (t: string) => { navigator.clipboard.writeText(t); toast.success("Copié dans le presse-papiers"); };

  const modes: { id: Mode; label: string; icon: typeof Lock }[] = [
    { id: "chiffrer", label: "Chiffrer", icon: Lock },
    { id: "dechiffrer", label: "Déchiffrer", icon: LockOpen },
    ...(algo === "cesar" ? [{ id: "brute" as Mode, label: "Force brute", icon: Search }] : []),
  ];

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:py-14">
      <Toaster />
      <header className="mb-10 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 font-mono text-xs text-muted-foreground">
            <ShieldCheck className="h-3.5 w-3.5 text-primary" /> Aucune bibliothèque crypto · tout est codé à la main
          </div>
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            Crypto<span className="text-primary">Box</span>
          </h1>
          <p className="mt-2 max-w-xl text-muted-foreground">Chiffrement classique : César, substitution, transposition par colonnes et challenge multi-couches.</p>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <aside className="space-y-2">
          <p className="mb-3 font-mono text-xs uppercase tracking-widest text-muted-foreground">Algorithme</p>
          {ALGOS.map((a) => {
            const Icon = a.icon;
            const active = algo === a.id;
            return (
              <button key={a.id} onClick={() => setAlgo(a.id)}
                className={`flex w-full items-center gap-3 rounded-xl border p-3 text-left transition-all ${active ? "border-primary/60 bg-accent shadow-glow" : "border-border bg-card/60 hover:border-primary/30 hover:bg-card"}`}>
                <span className={`grid h-9 w-9 place-items-center rounded-lg ${active ? "bg-primary text-primary-foreground" : "bg-secondary text-muted-foreground"}`}><Icon className="h-4 w-4" /></span>
                <span>
                  <span className="block font-semibold">{a.label}</span>
                  <span className="block font-mono text-xs text-muted-foreground">{a.desc}</span>
                </span>
              </button>
            );
          })}
          <div className="mt-6 rounded-xl border border-border bg-card/40 p-4 text-sm text-muted-foreground">
            Le texte est normalisé en majuscules A–Z, sans espaces ni accents. <span className="font-mono text-foreground">Été à Paris !</span> → <span className="font-mono text-primary">ETEAPARIS</span>
          </div>
        </aside>

        <main className="space-y-6">
          {algo === "multi" ? (
            <MultiCouches />
          ) : (
            <>
              <section className="rounded-2xl border border-border bg-card/80 p-6 backdrop-blur">
                <div className="mb-5 inline-flex rounded-lg border border-border bg-secondary p-1">
                  {modes.map((m) => {
                    const Icon = m.icon;
                    return (
                      <button key={m.id} onClick={() => setMode(m.id)}
                        className={`flex items-center gap-2 rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${effectiveMode === m.id ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"}`}>
                        <Icon className="h-4 w-4" /> {m.label}
                      </button>
                    );
                  })}
                </div>

                <label className="mb-2 block text-sm font-medium">{effectiveMode === "chiffrer" ? "Message" : "Texte chiffré"}</label>
                <textarea value={texte} onChange={(e) => setTexte(e.target.value)} rows={4}
                  className="w-full resize-y rounded-xl border border-input bg-background/60 p-4 font-mono text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-ring/30" />
                <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
                  <span className="font-mono">Pris en compte ({prepare.length}) : {prepare.slice(0, 60)}{prepare.length > 60 ? "…" : ""}</span>
                  <label className="flex cursor-pointer items-center gap-2">
                    <input type="checkbox" checked={garder} onChange={(e) => setGarder(e.target.checked)} className="accent-primary" />
                    Conserver les espaces et la ponctuation
                  </label>
                </div>

                {effectiveMode !== "brute" && (
                  <div className="mt-5">
                    {algo === "cesar" && (
                      <Field label="Clé k">
                        <input type="number" value={k} onChange={(e) => setK(parseInt(e.target.value || "0", 10))} className="input-field w-32" />
                      </Field>
                    )}
                    {algo === "substitution" && (
                      <Field label="Clé (26 lettres)">
                        <div className="flex gap-2">
                          <input value={cleSub} onChange={(e) => setCleSub(e.target.value.toUpperCase())} className="input-field flex-1 tracking-widest" />
                          <button onClick={() => setCleSub(C.cleAleatoire())} className="btn-ghost"><Dices className="h-4 w-4" /> Aléatoire</button>
                        </div>
                      </Field>
                    )}
                    {algo === "transposition" && (
                      <Field label="Mot-clé">
                        <input value={mot} onChange={(e) => setMot(e.target.value.toUpperCase())} className="input-field w-60 tracking-widest" />
                      </Field>
                    )}
                  </div>
                )}
              </section>

              {effectiveMode !== "brute" ? (
                <section className="rounded-2xl border border-primary/30 bg-card/80 p-6 shadow-glow">
                  <div className="mb-3 flex items-center justify-between">
                    <p className="font-mono text-xs uppercase tracking-widest text-primary">Résultat</p>
                    {resultat && <button onClick={() => copier(resultat)} className="btn-ghost"><Copy className="h-4 w-4" /> Copier</button>}
                  </div>
                  {erreur ? <p className="text-sm text-destructive">{erreur}</p> :
                    <p className="break-all font-mono text-2xl font-semibold tracking-wider">{resultat || <span className="text-muted-foreground">—</span>}</p>}
                  {algo === "transposition" && !erreur && <Grille texte={effectiveMode === "chiffrer" ? C.preparer(texte, garder) : resultat} mot={mot} />}
                </section>
              ) : brute && (
                <section className="rounded-2xl border border-primary/30 bg-card/80 p-6 shadow-glow">
                  <p className="mb-2 font-mono text-xs uppercase tracking-widest text-primary">Clé la plus probable</p>
                  {brute[0] && (
                    <div className="flex flex-wrap items-baseline gap-4">
                      <span className="rounded-lg bg-primary px-3 py-1 font-mono text-lg font-bold text-primary-foreground">k = {brute[0].k}</span>
                      <span className="break-all font-mono text-2xl font-semibold">{brute[0].texte}</span>
                    </div>
                  )}
                  <button onClick={() => setTout(!tout)} className="btn-ghost mt-5">{tout ? "Masquer" : "Voir"} les 25 clés testées</button>
                  {tout && (
                    <div className="mt-4 grid gap-1.5 sm:grid-cols-2">
                      {brute.map((b, i) => (
                        <div key={b.k} className={`flex gap-3 rounded-lg border px-3 py-2 font-mono text-sm ${i === 0 ? "border-primary/50 bg-accent" : "border-border bg-background/40"}`}>
                          <span className="w-10 shrink-0 text-muted-foreground">k={b.k}</span>
                          <span className="truncate">{b.texte}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              )}
            </>
          )}
        </main>
      </div>
      <footer className="mt-14 text-center font-mono text-xs text-muted-foreground">CryptoBox · Brique 1</footer>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div><label className="mb-2 block text-sm font-medium">{label}</label>{children}</div>;
}

// ------------------------------------------------------------- Multi-couches
const TYPES: { id: C.Couche["type"]; label: string }[] = [
  { id: "cesar", label: "César" },
  { id: "substitution", label: "Substitution" },
  { id: "transposition", label: "Transposition" },
];

function nouvelleCouche(type: C.Couche["type"]): C.Couche {
  if (type === "cesar") return { type: "cesar", k: null };
  if (type === "substitution") return { type: "substitution", cle: "QWERTYUIOPASDFGHJKLZXCVBNM" };
  return { type: "transposition", motcle: "PORTE" };
}

function MultiCouches() {
  const [texte, setTexte] = useState("ASVAJKRTXMNVYEY");
  const [garder, setGarder] = useState(false);
  const [couches, setCouches] = useState<C.Couche[]>([
    { type: "cesar", k: null },
    { type: "transposition", motcle: "PORTE" },
    { type: "substitution", cle: "QWERTYUIOPASDFGHJKLZXCVBNM" },
  ]);
  const [essais, setEssais] = useState<C.EssaiMulti[] | null>(null);
  const [erreur, setErreur] = useState("");
  const [tout, setTout] = useState(false);

  const inconnues = C.couchesInconnues(couches);
  const nbEssais = 25 ** inconnues.length;
  const blocage = inconnues.length > 2;

  const setNb = (n: number) =>
    setCouches((cs) => (n > cs.length ? [...cs, ...Array.from({ length: n - cs.length }, () => nouvelleCouche("cesar"))] : cs.slice(0, n)));
  const majCouche = (i: number, c: C.Couche) => setCouches((cs) => cs.map((x, j) => (j === i ? c : x)));
  const supprCouche = (i: number) => setCouches((cs) => cs.filter((_, j) => j !== i));

  const lancer = () => {
    try {
      setEssais(C.multiForceBrute(texte, couches, garder));
      setErreur("");
      setTout(false);
    } catch (e) {
      setEssais(null);
      setErreur((e as Error).message);
    }
  };

  const meilleur = essais?.[0];

  return (
    <>
      <section className="rounded-2xl border border-border bg-card/80 p-6 backdrop-blur">
        <p className="mb-1 font-semibold">Déchiffrement automatique</p>
        <p className="mb-5 text-sm text-muted-foreground">
          Entre les couches dans l'ordre où on doit les <span className="text-foreground">retirer</span> : l'étape 1 est la première à retirer,
          c'est-à-dire la dernière couche appliquée au chiffrement. Pour une couche César, coche « k inconnu » : l'outil teste les 25 clés.
        </p>

        <label className="mb-2 block text-sm font-medium">Message intercepté</label>
        <textarea value={texte} onChange={(e) => setTexte(e.target.value)} rows={3} placeholder="Ex : ASVAJKRTXMNVYEY"
          className="w-full resize-y rounded-xl border border-input bg-background/60 p-4 font-mono text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-ring/30" />
        <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs text-muted-foreground">
          <span className="font-mono">Pris en compte ({C.preparer(texte, garder).length})</span>
          <label className="flex cursor-pointer items-center gap-2">
            <input type="checkbox" checked={garder} onChange={(e) => setGarder(e.target.checked)} className="accent-primary" />
            Conserver les espaces et la ponctuation
          </label>
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <span className="text-sm font-medium">Nombre de couches</span>
          <div className="inline-flex rounded-lg border border-border bg-secondary p-1">
            {[1, 2, 3, 4, 5].map((n) => (
              <button key={n} onClick={() => setNb(n)}
                className={`h-8 w-8 rounded-md font-mono text-sm transition-colors ${couches.length === n ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground"}`}>
                {n}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-4 space-y-3">
          {couches.map((c, i) => (
            <div key={i} className="rounded-xl border border-border bg-background/40 p-4">
              <div className="mb-3 flex items-center justify-between gap-2">
                <p className="font-mono text-xs uppercase tracking-widest text-primary">
                  Étape {i + 1} <span className="normal-case text-muted-foreground">· à retirer {i === 0 ? "en premier" : `en n°${i + 1}`}</span>
                </p>
                {couches.length > 1 && (
                  <button onClick={() => supprCouche(i)} aria-label={`Retirer l'étape ${i + 1}`}
                    className="rounded-md p-1 text-muted-foreground transition hover:border-destructive/50 hover:text-destructive">
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>

              <div className="flex flex-wrap items-end gap-4">
                <Field label="Algorithme">
                  <select value={c.type} onChange={(e) => majCouche(i, nouvelleCouche(e.target.value as C.Couche["type"]))} className="input-field min-w-44">
                    {TYPES.map((t) => <option key={t.id} value={t.id}>{t.label}</option>)}
                  </select>
                </Field>

                {c.type === "cesar" && (
                  <>
                    <label className="flex cursor-pointer items-center gap-2 pb-2 text-sm">
                      <input type="checkbox" checked={c.k === null} onChange={(e) => majCouche(i, { type: "cesar", k: e.target.checked ? null : 3 })} className="accent-primary" />
                      k inconnu (force brute)
                    </label>
                    {c.k !== null && (
                      <Field label="Clé k">
                        <input type="number" value={c.k} onChange={(e) => majCouche(i, { type: "cesar", k: parseInt(e.target.value || "0", 10) })} className="input-field w-24" />
                      </Field>
                    )}
                  </>
                )}

                {c.type === "substitution" && (
                  <div className="min-w-72 flex-1">
                    <Field label="Clé (alphabet de 26 lettres)">
                      <div className="flex gap-2">
                        <input value={c.cle} onChange={(e) => majCouche(i, { type: "substitution", cle: e.target.value.toUpperCase() })} className="input-field flex-1 tracking-widest" />
                        <button onClick={() => majCouche(i, { type: "substitution", cle: C.cleAleatoire() })} className="btn-ghost"><Dices className="h-4 w-4" /></button>
                      </div>
                    </Field>
                  </div>
                )}

                {c.type === "transposition" && (
                  <Field label="Mot-clé">
                    <input value={c.motcle} onChange={(e) => majCouche(i, { type: "transposition", motcle: e.target.value.toUpperCase() })} className="input-field w-48 tracking-widest" />
                  </Field>
                )}
              </div>
            </div>
          ))}
        </div>

        {couches.length < 5 && (
          <button onClick={() => setNb(couches.length + 1)} className="btn-ghost mt-3"><Plus className="h-4 w-4" /> Ajouter une couche</button>
        )}

        <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
          <p className="font-mono text-xs text-muted-foreground">
            {blocage ? "Trop de clés inconnues" : inconnues.length ? `${nbEssais} essais à tester (${inconnues.length === 2 ? "25 × 25" : "25"})` : "Aucune clé inconnue : 1 seul déchiffrement"}
          </p>
          <button onClick={lancer} disabled={blocage}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40">
            <Search className="h-4 w-4" /> Déchiffrer / Force brute
          </button>
        </div>

        {blocage && <p className="mt-3 text-sm text-destructive">Maximum 2 couches César à k inconnu (25 × 25 essais).</p>}
      </section>

      {erreur && (
        <section className="rounded-2xl border border-destructive/40 bg-card/80 p-6">
          <p className="text-sm text-destructive">{erreur}</p>
        </section>
      )}

      {meilleur && (
        <section className="rounded-2xl border border-primary/30 bg-card/80 p-6 shadow-glow">
          <div className="mb-3 flex items-center justify-between">
            <p className="font-mono text-xs uppercase tracking-widest text-primary">Résultat le plus lisible</p>
            <button onClick={() => { navigator.clipboard.writeText(meilleur.texte); toast.success("Copié dans le presse-papiers"); }} className="btn-ghost"><Copy className="h-4 w-4" /> Copier</button>
          </div>
          {inconnues.length > 0 && (
            <p className="mb-2 inline-block rounded-lg bg-primary px-3 py-1 font-mono text-sm font-bold text-primary-foreground">{meilleur.cles}</p>
          )}
          <p className="break-all font-mono text-2xl font-semibold tracking-wider">{meilleur.texte || <span className="text-muted-foreground">—</span>}</p>
          <p className="mt-2 font-mono text-xs text-muted-foreground">8 premières lettres : {meilleur.texte.slice(0, 8) || "—"}</p>

          {essais && essais.length > 1 && (
            <>
              <button onClick={() => setTout(!tout)} className="btn-ghost mt-5">{tout ? "Masquer" : "Voir"} les {essais.length} essais</button>
              {tout && (
                <div className="mt-4 space-y-1.5">
                  {essais.slice(0, 50).map((e, i) => (
                    <div key={i} className={`flex flex-wrap gap-3 rounded-lg border px-3 py-2 font-mono text-sm ${i === 0 ? "border-primary/50 bg-accent" : "border-border bg-background/40"}`}>
                      <span className="w-40 shrink-0 truncate text-muted-foreground">{e.cles}</span>
                      <span className="truncate">{e.texte}</span>
                    </div>
                  ))}
                  {essais.length > 50 && <p className="pt-1 font-mono text-xs text-muted-foreground">50 premiers essais sur {essais.length}, triés du plus lisible au moins lisible.</p>}
                </div>
              )}
            </>
          )}
        </section>
      )}
    </>
  );
}

function Grille({ texte, mot }: { texte: string; mot: string }) {
  const m = C.normaliser(mot);
  if (!m || !texte) return null;
  let ordre: number[];
  try { ordre = C.ordreColonnes(m); } catch { return null; }
  const n = m.length;
  const t = texte + "X".repeat((n - (texte.length % n)) % n);
  const lignes = Array.from({ length: t.length / n }, (_, r) => t.slice(r * n, r * n + n));
  if (lignes.length > 12) return null;
  return (
    <div className="mt-6 overflow-x-auto">
      <p className="mb-2 text-xs text-muted-foreground">Grille (entre parenthèses : ordre de lecture des colonnes)</p>
      <table className="font-mono text-sm">
        <thead><tr>{[...m].map((c, i) => <th key={i} className="px-3 py-1 text-primary">{c}<span className="ml-1 text-xs text-muted-foreground">({ordre.indexOf(i) + 1})</span></th>)}</tr></thead>
        <tbody>{lignes.map((l, r) => <tr key={r}>{[...l].map((c, i) => <td key={i} className="border border-border px-3 py-1 text-center">{c}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}
