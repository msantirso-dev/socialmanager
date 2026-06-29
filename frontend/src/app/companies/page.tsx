"use client";

import { Building2, Globe, Loader2 } from "lucide-react";
import { useCompanies } from "@/hooks/use-companies";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CompaniesPage() {
  const { companies, loading } = useCompanies();

  if (loading) return <div className="flex justify-center p-16"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="p-8">
      <h1 className="mb-6 text-3xl font-bold">Empresas</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {companies.map((c) => (
          <Card key={c.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-primary" />
                {c.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              {c.website && (
                <p className="flex items-center gap-1"><Globe className="h-4 w-4" />{c.website}</p>
              )}
              <p>Tono: {c.tone || "—"}</p>
              <p>Idioma: {c.language}</p>
              {c.brand_description && <p className="line-clamp-2">{c.brand_description}</p>}
            </CardContent>
          </Card>
        ))}
        {!companies.length && <p className="text-muted-foreground">No hay empresas. Usa el seed o regístrate.</p>}
      </div>
    </div>
  );
}
