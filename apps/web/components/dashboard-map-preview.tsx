"use client";
import Link from "next/link";
import { useEffect,useState } from "react";
import { apiFetch,type Advisory,type Location,type Outbreak,type RouteAssessment } from "@/lib/api";
import { RouteRiskMap } from "@/components/route-risk-map";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";

export function DashboardMapPreview(){const[a,setA]=useState<Advisory|null>(null);const[r,setR]=useState<RouteAssessment|null>(null);const[l,setL]=useState<Location[]>([]);const[o,setO]=useState<Outbreak[]>([]);useEffect(()=>{Promise.all([apiFetch<Advisory[]>("/advisories"),apiFetch<Location[]>("/locations"),apiFetch<Outbreak[]>("/outbreaks")]).then(([ads,loc,out])=>{setA(ads[0]??null);setL(loc);setO(out);if(ads[0])apiFetch<RouteAssessment>("/routes/assess",{method:"POST",body:JSON.stringify({consignment_id:ads[0].consignment_id})}).then(setR)})},[]);if(!a)return <EmptyState title="No evaluated route yet" description="Evaluate a consignment to see its persisted route assessment here."/>;return <Card className="p-5 md:p-6"><div className="flex items-center justify-between"><div><p className="text-xs font-bold uppercase tracking-wider text-teal">Controlled risk map</p><h2 className="mt-2 font-display text-2xl font-semibold">Latest evaluated route</h2></div><Link href={`/advisories/${a.id}`} className="min-h-11 rounded-[10px] bg-teal px-4 py-3 text-sm font-bold text-white">View route assessment</Link></div>{r?<div className="mt-5"><RouteRiskMap assessment={r} locations={l} outbreaks={o}/><p className="mt-3 text-xs font-bold">Legend: Teal = fictional locations / safer route · Red = requested route / confirmed zone · Amber = suspected zone.</p></div>:<p className="mt-5 text-sm">Loading latest controlled route…</p>}</Card>}
