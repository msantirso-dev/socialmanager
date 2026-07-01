"use client";

import { Building2 } from "lucide-react";
import { useCompanies } from "@/components/companies/companies-provider";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

interface CompanySelectorProps {
  className?: string;
}

export function CompanySelector({ className }: CompanySelectorProps) {
  const { companies, selected, setSelected, loading } = useCompanies();

  if (loading || !companies.length) return null;

  return (
    <div className={cn("space-y-1", className)}>
      <Label className="text-xs text-muted-foreground">Empresa activa</Label>
      <div className="relative">
        <Building2 className="pointer-events-none absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <select
          value={selected?.id ?? ""}
          onChange={(e) => {
            const company = companies.find((c) => c.id === e.target.value) ?? null;
            setSelected(company);
          }}
          className="flex h-9 w-full appearance-none rounded-md border border-input bg-background py-1 pl-8 pr-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {companies.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
