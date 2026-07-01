"use client";

import { useEffect, useState } from "react";
import { Calendar, Loader2, Plus, Send } from "lucide-react";
import { useCompanies } from "@/components/companies/companies-provider";
import { api, type Post } from "@/lib/domain-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-muted text-muted-foreground",
  scheduled: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  published: "bg-green-500/10 text-green-600 dark:text-green-400",
  failed: "bg-red-500/10 text-red-600 dark:text-red-400",
  publishing: "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400",
};

export default function CalendarPage() {
  const { selected } = useCompanies();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [caption, setCaption] = useState("");
  const [creating, setCreating] = useState(false);

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

  const createPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected) return;
    setCreating(true);
    try {
      await api.createPost({
        company_id: selected.id,
        type: "image",
        title: title.trim() || undefined,
        caption: caption.trim() || undefined,
      });
      setTitle("");
      setCaption("");
      setShowForm(false);
      load();
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="flex items-center gap-2 text-3xl font-bold">
          <Calendar className="h-8 w-8" /> Calendario
        </h1>
        {selected && (
          <Button onClick={() => setShowForm(!showForm)}>
            <Plus className="mr-2 h-4 w-4" /> Nueva publicación
          </Button>
        )}
      </div>

      {!selected && !loading && (
        <p className="text-muted-foreground">Seleccioná o creá una empresa para ver publicaciones.</p>
      )}

      {showForm && selected && (
        <Card className="mb-6">
          <CardHeader><CardTitle>Nueva publicación — {selected.name}</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={createPost} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="post-title">Título</Label>
                <Input id="post-title" value={title} onChange={(e) => setTitle(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="post-caption">Texto / caption</Label>
                <textarea
                  id="post-caption"
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  rows={4}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={creating}>{creating ? "Creando..." : "Crear borrador"}</Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancelar</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

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
        {!loading && selected && !posts.length && (
          <p className="text-muted-foreground">No hay publicaciones. Creá una con «Nueva publicación» o desde el generador IA.</p>
        )}
      </div>
    </div>
  );
}
