"use client";
import { useState } from "react";
import { RegisterConsignmentForm } from "@/components/register-consignment-form";
import { RegisterSymptomReportForm } from "@/components/register-symptom-report-form";
export function RegisterOperationsForm(){const[type,setType]=useState<"consignment"|"symptoms">("consignment");return <div><div className="mb-6 flex gap-2"><button className={`rounded px-4 py-2 ${type==="consignment"?"bg-teal text-white":"bg-paper"}`} onClick={()=>setType("consignment")}>Consignment</button><button className={`rounded px-4 py-2 ${type==="symptoms"?"bg-teal text-white":"bg-paper"}`} onClick={()=>setType("symptoms")}>Report Symptoms / Mortality</button></div>{type==="consignment"?<RegisterConsignmentForm/>:<RegisterSymptomReportForm/>}</div>}
