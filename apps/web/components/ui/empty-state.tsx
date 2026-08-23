import { Construction } from "lucide-react";

export function EmptyState({ title, description }: { title: string; description: string }) {
  return <section className="rounded-xl border border-dashed border-line bg-white px-6 py-16 text-center">
    <Construction className="mx-auto text-teal" size={32} aria-hidden="true" />
    <h2 className="mt-4 font-display text-2xl font-semibold tracking-tight">{title}</h2>
    <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-600">{description}</p>
  </section>;
}
