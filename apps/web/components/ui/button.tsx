import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "primary" | "secondary" | "quiet";
};

const styles = {
  primary: "bg-teal text-white hover:bg-[#0b625c]",
  secondary: "border border-ink/20 bg-white text-ink hover:border-ink/50",
  quiet: "text-ink hover:bg-ink/5",
};

export function Button({ children, className = "", variant = "primary", ...props }: ButtonProps) {
  return (
    <button className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-[10px] px-4 text-sm font-semibold ${styles[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
