import type { ReactNode } from "react";

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description: string; action?: ReactNode }) {
  return <header className="flex flex-col gap-5 border-b border-line pb-7 lg:flex-row lg:items-end lg:justify-between">
    <div className="max-w-3xl">
      {eyebrow && <p className="mb-3 text-xs font-bold uppercase tracking-[0.16em] text-teal">{eyebrow}</p>}
      <h1 className="font-display text-4xl font-semibold leading-none tracking-[-0.05em] text-ink md:text-5xl">{title}</h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">{description}</p>
    </div>
    {action}
  </header>;
}
