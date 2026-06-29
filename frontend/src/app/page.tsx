"use client";

import { useEffect, useState } from "react";
import {
  Activity, Bot, Calendar, Globe, Heart, MessageSquare, Send, Sparkles, Users,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api, type Dashboard } from "@/lib/domain-api";
import { useAuth } from "@/components/auth/auth-provider";

export default function HomePage() {
  const { user } = useAuth();
  const [dash, setDash] = useState<Dashboard | null>(null);

  useEffect(() => {
    api.dashboard().then(setDash).catch(() => setDash(null));
  }, []);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">Bienvenido, {user?.full_name}</p>
      </div>

      {dash ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm">Programadas</CardTitle><Calendar className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{dash.scheduled_posts}</div></CardContent></Card>
            <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm">Publicadas</CardTitle><Send className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{dash.published_posts}</div></CardContent></Card>
            <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm">Engagement</CardTitle><Heart className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{dash.total_engagement}</div></CardContent></Card>
            <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm">Seguidores</CardTitle><Users className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{dash.followers}</div></CardContent></Card>
            <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm">Alcance</CardTitle><Globe className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{dash.total_reach}</div></CardContent></Card>
            <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm">Comentarios pend.</CardTitle><MessageSquare className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{dash.pending_comments}</div></CardContent></Card>
            <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm">Llamadas IA</CardTitle><Bot className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{dash.ai_calls}</div><p className="text-xs text-muted-foreground">${dash.ai_cost.toFixed(2)}</p></CardContent></Card>
            <Card><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm">Créditos</CardTitle><Sparkles className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{dash.credits_balance}</div></CardContent></Card>
          </div>

          {dash.upcoming_posts.length > 0 && (
            <Card className="mt-8">
              <CardHeader><CardTitle>Próximas publicaciones</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {dash.upcoming_posts.map((p) => (
                  <div key={p.id} className="flex justify-between text-sm">
                    <span>{p.title || p.caption?.slice(0, 50)}</span>
                    <span className="text-muted-foreground">{p.scheduled_at ? new Date(p.scheduled_at).toLocaleString("es") : "—"}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </>
      ) : (
        <Card><CardContent className="flex items-center gap-2 p-6"><Activity className="h-5 w-5 animate-pulse" /> Cargando dashboard...</CardContent></Card>
      )}
    </div>
  );
}
