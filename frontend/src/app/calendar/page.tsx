"use client";

import { useEffect, useState } from "react";
import { Calendar, Loader2, Send } from "lucide-react";
import { useCompanies } from "@/hooks/use-companies";
import { api, type Post } from "@/lib/domain-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-500/10 text-gray-600",
  scheduled: "bg-blue-500/10 text-blue-600",
  published: "bg-green-500/10 text-green-600",
  failed: "bg-red-500/10 text-red-600",
  publishing: "bg-yellow-500/10 text-yellow-600",
};

export default function CalendarPage() {
  const { selected } = useCompanies();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    if (!selected) return;
    setLoading(true);
    api.posts(selected.id).then(setPosts).finally(() => setLoading(false));
  };

  useEffect(load, [selected?.id]);

  const publish = async (id: string) => {
    await api.publishPost(id);
    load();
  };

  return (
    <div className="p-8">
      <h1 className="mb-6 flex items-center gap-2 text-3xl font-bold"><Calendar className="h-8 w-8" /> Calendario</h1>
      {loading && <Loader2 className="animate-spin" />}
      <div className="space-y-3">
        {posts.map((p) => (
          <Card key={p.id}>
            <CardHeader className="flex flex-row items-center justify-between py-3">
              <CardTitle className="text-base">{p.title || p.caption?.slice(0, 60) || "Sin título"}</CardTitle>
              <span className={`rounded-full px-2 py-1 text-xs font-medium ${STATUS_COLORS[p.status] || ""}`}>{p.status}</span>
            </CardHeader>
            <CardContent className="flex items-center justify-between pb-3">
              <div className="text-sm text-muted-foreground">
                {p.scheduled_at ? new Date(p.scheduled_at).toLocaleString("es") : "Sin programar"} · {p.type}
              </div>
              {(p.status === "draft" || p.status === "scheduled" || p.status === "failed") && (
                <Button size="sm" onClick={() => publish(p.id)}><Send className="mr-1 h-3 w-3" /> Publicar</Button>
              )}
            </CardContent>
          </Card>
        ))}
        {!loading && !posts.length && <p className="text-muted-foreground">No hay publicaciones. Créalas desde el generador IA.</p>}
      </div>
    </div>
  );
}
