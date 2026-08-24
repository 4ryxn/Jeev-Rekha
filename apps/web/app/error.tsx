"use client";
import { RouteError } from "@/components/ui/route-feedback";

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) { return <RouteError label="Operations workspace" reset={reset} />; }
