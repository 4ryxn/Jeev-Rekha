"use client";

import { useEffect, useState } from "react";

export type DataContext = "demo_seed" | "pilot_entered" | "all";
export const DATA_CONTEXT_KEY = "jeevrekha-data-context";
export const dataContextLabel = (context: DataContext) => context === "demo_seed" ? "Demo data" : context === "pilot_entered" ? "Pilot records" : "All records";
export const dataContextDescription = (context: DataContext) => context === "demo_seed" ? "Controlled fictional SIH demonstration records" : context === "pilot_entered" ? "Records manually entered by the local operations team" : "Both sources shown with visible source badges";
export function readDataContext(): DataContext { if (typeof window === "undefined") return "demo_seed"; const value = window.localStorage.getItem(DATA_CONTEXT_KEY); return value === "pilot_entered" || value === "all" ? value : "demo_seed"; }
export function setDataContext(context: DataContext) { window.localStorage.setItem(DATA_CONTEXT_KEY, context); window.dispatchEvent(new Event("jeevrekha-data-context-change")); }
export function sourcePath(path: string, context: DataContext) { return context === "all" ? path : `${path}${path.includes("?") ? "&" : "?"}source=${context}`; }
export function useDataContext() { const [context, setContext] = useState<DataContext>("demo_seed"); useEffect(() => { const refresh = () => setContext(readDataContext()); refresh(); window.addEventListener("jeevrekha-data-context-change", refresh); return () => window.removeEventListener("jeevrekha-data-context-change", refresh); }, []); return { context, setContext: (next: DataContext) => { setDataContext(next); setContext(next); } }; }
