"use client";
import { apiFetch, type Location } from "@/lib/api";
import { offlineDb } from "@/lib/offline-queue";
export async function loadLocationReferences(): Promise<Location[]> { try { const locations=await apiFetch<Location[]>("/locations",{cache:"no-store"}); if(locations.length<2)throw new Error("Location references are incomplete"); await offlineDb.locationReferences.bulkPut(locations); return locations; } catch { const locations=await offlineDb.locationReferences.orderBy("name").toArray() as Location[]; if(locations.length<2)throw new Error("Connect once to load local location references before offline registration."); return locations; } }
