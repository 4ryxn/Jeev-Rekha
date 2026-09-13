"use client";
import { useState } from "react";
import { RegisterConsignmentForm } from "@/components/register-consignment-form";
import { RegisterSymptomReportForm } from "@/components/register-symptom-report-form";
import { TargetI18nProvider, useTargetLocale } from "@/components/target-i18n";
export function RegisterOperationsForm(){return <TargetI18nProvider><RegisterOperationsContent /></TargetI18nProvider>}
function RegisterOperationsContent(){const[type,setType]=useState<"consignment"|"symptoms">("consignment");const {locale}=useTargetLocale();return <div><div className="mb-6 flex gap-2"><button className={`rounded px-4 py-2 ${type==="consignment"?"bg-teal text-white":"bg-paper"}`} onClick={()=>setType("consignment")}>{locale==="hi"?"पशु खेप":"Consignment"}</button><button className={`rounded px-4 py-2 ${type==="symptoms"?"bg-teal text-white":"bg-paper"}`} onClick={()=>setType("symptoms")}>{locale==="hi"?"लक्षण / मृत्यु की रिपोर्ट":"Report Symptoms / Mortality"}</button></div>{type==="consignment"?<RegisterConsignmentForm/>:<RegisterSymptomReportForm/>}</div>}
