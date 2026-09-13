"use client";

import { NextIntlClientProvider } from "next-intl";
import { createContext, useContext, useState, type ReactNode } from "react";

export type TargetLocale = "en" | "hi";
const LocaleContext = createContext<{ locale: TargetLocale; setLocale: (locale: TargetLocale) => void } | null>(null);
const messages = { en: { language: { label: "Language" } }, hi: { language: { label: "भाषा" } } };

export function TargetI18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<TargetLocale>("en");
  return <LocaleContext.Provider value={{ locale, setLocale }}><NextIntlClientProvider locale={locale} messages={messages[locale]}>{children}</NextIntlClientProvider></LocaleContext.Provider>;
}

export function useTargetLocale() {
  const value = useContext(LocaleContext);
  if (!value) throw new Error("Target i18n components must be inside TargetI18nProvider.");
  return value;
}

export function LanguageToggle() {
  const { locale, setLocale } = useTargetLocale();
  return <div className="flex gap-2" aria-label="Language"><button type="button" onClick={() => setLocale("en")} aria-pressed={locale === "en"} className={`min-h-11 rounded-lg border px-3 font-bold ${locale === "en" ? "border-teal bg-teal text-white" : "border-line bg-white"}`}>English</button><button type="button" onClick={() => setLocale("hi")} aria-pressed={locale === "hi"} className={`min-h-11 rounded-lg border px-3 font-bold ${locale === "hi" ? "border-teal bg-teal text-white" : "border-line bg-white"}`}>हिन्दी</button></div>;
}
