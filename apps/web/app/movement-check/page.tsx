import { PublicMovementCheckPage } from "@/components/public-movement-check";
import { WorkspaceSwitcher } from "@/components/workspace-switcher";
import type { Metadata } from "next";
export const metadata: Metadata = { title: "Pre-Travel Animal Movement Check", description: "A synthetic, advisory-only movement check for animal owners, buyers, sellers, and transporters." };
export default function Page(){return <><header className="flex min-h-16 items-center justify-end border-b border-line bg-white px-4 sm:px-8"><WorkspaceSwitcher workspace="public"/></header><PublicMovementCheckPage/></>}
