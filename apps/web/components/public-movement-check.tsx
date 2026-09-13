"use client";

import { CheckCircle2, CircleHelp, ShieldAlert, TriangleAlert } from "lucide-react";
import Link from "next/link";
import { cloneElement, isValidElement, useEffect, useState, type ReactNode } from "react";
import { apiFetch, type Location, type PublicMovementCheck, type RiskState } from "@/lib/api";
import { LanguageToggle, TargetI18nProvider, useTargetLocale } from "@/components/target-i18n";

type Language = "en" | "hi";
type Details = { origin: string; destination: string; species: string; count: string };

const copy = {
  en: {
    title: "Jeev Rekha — Pre-Travel Animal Movement Check",
    owners: "For animal owners, buyers, sellers and transporters",
    origin: "Origin", destination: "Destination", species: "Species", specifySpecies: "Specify species",
    selectOrigin: "Select origin", selectDestination: "Select destination", enterAnimalCount: "Enter animal count", enterVehicleReference: "Enter vehicle reference", selectVaccinationEvidence: "Select vaccination evidence",
    selectSpecies: "Select species", cattle: "Cattle", buffalo: "Buffalo", goat: "Goat", sheep: "Sheep", pig: "Pig", poultry: "Poultry", other: "Other",
    count: "Approximate animal count", vehicle: "Vehicle reference", vaccination: "Vaccination evidence (optional)",
    check: "Check movement advisory", workspace: "Operations workspace", print: "Print advisory slip", demo: "Synthetic demonstration · Pre-travel advisory", slip: "Jeev Rekha — Pre-Travel Advisory Slip · Synthetic demonstration", animals: "animals", verified: "Verified", declared: "Declared", unknown: "Unknown",
    meaning: "What this means", action: "What to do now", coverage: "Information coverage",
    offline: "A current movement advisory needs connectivity. Please use a connected veterinary centre.",
    disclaimer: "This is a pre-travel advisory. An authorised veterinary official makes the final decision.",
    required: "Please complete the required movement details.",
    statuses: { green: "Lower risk with sufficient information", amber: "Precaution required", red: "High-risk exposure identified", grey: "Information is insufficient" },
    actions: { green: "Keep the movement reference and seek veterinary advice if local conditions change.", amber: "Verify available evidence and seek veterinary advice before travel.", red: "Do not proceed until authorised veterinary guidance is obtained.", grey: "Request current field verification before travel." },
  },
  hi: {
    title: "जीव रेखा — यात्रा-पूर्व पशु आवागमन जाँच",
    owners: "पशु मालिकों, खरीदारों, विक्रेताओं और परिवहनकर्ताओं के लिए",
    origin: "प्रस्थान स्थान", destination: "गंतव्य", species: "प्रजाति", specifySpecies: "प्रजाति लिखें",
    selectOrigin: "प्रस्थान स्थान चुनें", selectDestination: "गंतव्य चुनें", enterAnimalCount: "पशु संख्या दर्ज करें", enterVehicleReference: "वाहन संदर्भ दर्ज करें", selectVaccinationEvidence: "टीकाकरण प्रमाण चुनें",
    selectSpecies: "प्रजाति चुनें", cattle: "गाय/बैल", buffalo: "भैंस", goat: "बकरी", sheep: "भेड़", pig: "सूअर", poultry: "कुक्कुट", other: "अन्य",
    count: "अनुमानित पशु संख्या", vehicle: "वाहन संदर्भ", vaccination: "टीकाकरण प्रमाण (वैकल्पिक)",
    check: "आवागमन सलाह जाँचें", workspace: "संचालन कार्यक्षेत्र", print: "सलाह पर्ची प्रिंट करें", demo: "कृत्रिम प्रदर्शन · यात्रा-पूर्व सलाह", slip: "जीव रेखा — यात्रा-पूर्व सलाह पर्ची · कृत्रिम प्रदर्शन", animals: "पशु", verified: "सत्यापित", declared: "घोषित", unknown: "अज्ञात",
    meaning: "इसका क्या अर्थ है", action: "अब क्या करें", coverage: "जानकारी कवरेज",
    offline: "वर्तमान आवागमन सलाह के लिए कनेक्टिविटी आवश्यक है। कृपया जुड़े हुए पशु चिकित्सा केंद्र का उपयोग करें।",
    disclaimer: "यह यात्रा-पूर्व सलाह है। अंतिम निर्णय अधिकृत पशु चिकित्सा अधिकारी लेते हैं।",
    required: "कृपया आवश्यक आवागमन विवरण पूरा करें।",
    statuses: { green: "पर्याप्त जानकारी के साथ कम जोखिम", amber: "सावधानी आवश्यक", red: "उच्च-जोखिम संपर्क की पहचान", grey: "जानकारी अपर्याप्त है" },
    actions: { green: "आवागमन संदर्भ रखें और स्थानीय स्थिति बदलने पर पशु चिकित्सा सलाह लें।", amber: "उपलब्ध प्रमाण सत्यापित करें और यात्रा से पहले पशु चिकित्सा सलाह लें।", red: "अधिकृत पशु चिकित्सा मार्गदर्शन मिलने तक आगे न बढ़ें।", grey: "यात्रा से पहले वर्तमान क्षेत्रीय सत्यापन का अनुरोध करें।" },
  },
} as const;

const icons: { [key in RiskState]: typeof CheckCircle2 } = { green: CheckCircle2, amber: TriangleAlert, red: ShieldAlert, grey: CircleHelp };
const movementCheckControlClass = "h-16 w-full appearance-auto rounded-xl border border-line bg-white px-4 py-0 text-base leading-6 text-ink";

export function PublicMovementCheckPage() {
  return <TargetI18nProvider><PublicMovementCheckContent /></TargetI18nProvider>;
}

function PublicMovementCheckContent() {
  const { locale: language } = useTargetLocale();
  const [locations, setLocations] = useState<Location[]>([]);
  const [result, setResult] = useState<PublicMovementCheck | null>(null);
  const [details, setDetails] = useState<Details | null>(null);
  const [error, setError] = useState("");
  const [online, setOnline] = useState(true);
  const [loading, setLoading] = useState(false);
  const [isOtherSpecies, setIsOtherSpecies] = useState(false);
  const t = copy[language];

  useEffect(() => {
    setOnline(navigator.onLine);
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    apiFetch<Location[]>("/locations?source=demo_seed").then(setLocations).catch(() => setError(copy[language].offline));
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); };
  }, [language]);

  async function submit(form: HTMLFormElement) {
    if (!online) { setError(t.offline); return; }
    const data = new FormData(form);
    const selectedSpecies = String(data.get("species"));
    const species = selectedSpecies === "Other" ? String(data.get("other_species") || "").trim() : selectedSpecies;
    const origin = locations.find((item) => item.id === Number(data.get("origin")));
    const destination = locations.find((item) => item.id === Number(data.get("destination")));
    setLoading(true); setError("");
    try {
      const vehicleReference = String(data.get("vehicle") || "").trim();
      if (!vehicleReference) {
        throw new Error(t.required);
      }
      const payload = {
        origin_location_id: Number(data.get("origin")), destination_location_id: Number(data.get("destination")),
        species, approximate_animal_count: Number(data.get("count")),
        vehicle_reference: vehicleReference, vaccination_evidence: String(data.get("vaccination") || "") || null,
      };
      setResult(await apiFetch<PublicMovementCheck>("/public/movement-check", { method: "POST", body: JSON.stringify(payload) }));
      setDetails({ origin: origin?.name ?? "", destination: destination?.name ?? "", species: payload.species, count: String(payload.approximate_animal_count) });
    } catch (reason) { setError(reason instanceof Error ? reason.message : t.required); } finally { setLoading(false); }
  }

  return (
    <main className="min-h-screen bg-paper px-4 py-6 sm:px-8">
      <div className="mx-auto max-w-4xl">
        <header className="flex flex-col gap-4 border-b border-line pb-6 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[.14em] text-teal">{t.demo}</p>
            <h1 className="mt-3 font-display text-3xl font-semibold leading-tight text-ink sm:text-5xl">{t.title}</h1>
            <p className="mt-3 text-sm leading-6 text-slate-700">{t.disclaimer}</p>
          </div>
          <LanguageToggle />
        </header>
        <p className="mt-6 w-full rounded-xl border border-line bg-white p-4 font-semibold">{t.owners}</p>
        <form onSubmit={(event) => { event.preventDefault(); submit(event.currentTarget); }} className="mt-6 rounded-xl border border-line bg-white p-5 shadow-sm sm:p-7">
          <div className="grid gap-5 md:grid-cols-2">
            <Field label={t.origin}><select required name="origin" defaultValue=""><option value="" disabled>{t.selectOrigin}</option>{locations.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}</select></Field>
            <Field label={t.destination}><select required name="destination" defaultValue=""><option value="" disabled>{t.selectDestination}</option>{locations.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}</select></Field>
            <Field label={t.species}>
              <select required name="species" defaultValue="" onChange={(event) => setIsOtherSpecies(event.target.value === "Other")}>
                <option value="" disabled>{t.selectSpecies}</option>
                <option value="Cattle">{t.cattle}</option><option value="Buffalo">{t.buffalo}</option><option value="Goat">{t.goat}</option>
                <option value="Sheep">{t.sheep}</option><option value="Pig">{t.pig}</option><option value="Poultry">{t.poultry}</option><option value="Other">{t.other}</option>
              </select>
            </Field>
            {isOtherSpecies && <Field label={t.specifySpecies}><input required name="other_species" /></Field>}
            <Field label={t.count}><input required name="count" type="number" min="1" placeholder={t.enterAnimalCount} /></Field>
            <Field label={t.vehicle}><input required name="vehicle" placeholder={t.enterVehicleReference} /></Field>
            <Field label={t.vaccination}><select name="vaccination" defaultValue=""><option value="" disabled>{t.selectVaccinationEvidence}</option><option value="verified">{t.verified}</option><option value="declared">{t.declared}</option><option value="unknown">{t.unknown}</option></select></Field>
          </div>
          {error && <p role="alert" className="mt-5 rounded-lg bg-[#FDECEC] p-4 text-sm font-semibold text-risk-red">{error}</p>}
          <button disabled={loading || !locations.length} className="mt-6 min-h-14 w-full rounded-xl bg-teal px-5 text-lg font-bold text-white disabled:opacity-60">{loading ? "…" : t.check}</button>
        </form>
        {result && details && <Result result={result} details={details} t={t} />}
        <footer className="mt-8 flex flex-wrap gap-4 text-sm font-bold"><Link className="text-teal underline" href="/">{t.workspace}</Link><span>{t.disclaimer}</span></footer>
      </div>
    </main>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  const control = isValidElement<{ className?: string }>(children)
    ? cloneElement(children, { className: `${movementCheckControlClass} ${children.props.className ?? ""}` })
    : children;
  return <label className="block text-base font-bold text-ink"><span>{label}</span><span className="mt-2 block">{control}</span></label>;
}

function Result({ result, details, t }: { result: PublicMovementCheck; details: Details; t: (typeof copy)[Language] }) {
  const Icon = icons[result.risk_state];
  return <section className="mt-6 rounded-xl border-2 border-ink bg-white p-6 sm:p-8"><p className="text-xs font-bold uppercase tracking-[.14em] text-teal">{t.slip}</p><div className="mt-4 flex gap-4"><Icon className="shrink-0 text-teal" size={36} aria-hidden="true" /><div><p className="text-sm font-bold uppercase tracking-wider">{result.risk_state.toUpperCase()}</p><h2 className="mt-1 font-display text-3xl font-semibold">{t.statuses[result.risk_state]}</h2></div></div><p className="mt-5 text-sm font-semibold">{details.origin} → {details.destination} · {details.species} · {details.count} {t.animals}</p><div className="mt-6 grid gap-5 md:grid-cols-2"><div><h3 className="font-bold">{t.meaning}</h3><p className="mt-2 text-sm leading-6">{t.statuses[result.risk_state]}</p><p className="mt-3 text-sm">{t.coverage}: {result.evidence_coverage_score}/100 · {result.information_coverage}</p></div><div><h3 className="font-bold">{t.action}</h3><p className="mt-2 text-sm leading-6">{t.actions[result.risk_state]}</p></div></div><p className="mt-5 text-xs text-slate-600">{new Date(result.generated_at).toLocaleString()}</p><p className="mt-4 rounded-lg bg-paper p-4 text-sm font-semibold">{t.disclaimer}</p><button onClick={() => window.print()} className="mt-5 min-h-11 rounded-lg border border-ink px-4 font-bold">{t.print}</button></section>;
}
