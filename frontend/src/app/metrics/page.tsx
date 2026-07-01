"use client";

import { useEffect, useState } from "react";
import { BarChart3, Loader2 } from "lucide-react";
import { useCompanies } from "@/components/companies/companies-provider";
import { api } from "@/lib/domain-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function MetricsPage() {
  const { selected } = useCompanies();
  const [data, setData] = useState<{ posts: Array<Record<string, unknown>>; totals: Record<string, number> } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.metrics(selected?.id).then(setData).catch(() => setData(null)).finally(() => setLoading(false));
  }, [selected?.id]);

  if (loading) return <div className="flex justify-center p-16"><Loader2 className="animate-spin" /></div>;

  return (
    <div className="p-8">
      <h1 className="mb-6 flex items-center gap-2 text-3xl font-bold"><BarChart3 className="h-8 w-8" /> Métricas</h1>
      {data && (
        <>
          <div className="mb-6 grid gap-4 md:grid-cols-3">
            <Card><CardHeader><CardTitle className="text-sm">Likes</CardTitle></CardHeader><CardContent className="text-2xl font-bold">{data.totals.likes}</CardContent></Card>
            <Card><CardHeader><CardTitle className="text-sm">Comentarios</CardTitle></CardHeader><CardContent className="text-2xl font-bold">{data.totals.comments}</CardContent></Card>
            <Card><CardHeader><CardTitle className="text-sm">Alcance</CardTitle></CardHeader><CardContent className="text-2xl font-bold">{data.totals.reach}</CardContent></Card>
          </div>
          <div className="space-y-2">
            {data.posts.map((p) => (
              <Card key={String(p.post_id)}>
                <CardContent className="flex justify-between py-3 text-sm">
                  <span>{String(p.title || p.post_id)}</span>
                  <span className="text-muted-foreground">❤ {String(p.likes)} · 💬 {String(p.comments)} · 👁 {String(p.reach)}</span>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
