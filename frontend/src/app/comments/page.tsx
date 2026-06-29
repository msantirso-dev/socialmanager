"use client";

import { useEffect, useState } from "react";
import { Bot, Loader2, MessageSquare, Send } from "lucide-react";
import { api, type Comment } from "@/lib/domain-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function CommentsPage() {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [replies, setReplies] = useState<Record<string, string>>({});

  const load = () => api.comments().then(setComments).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const reply = async (id: string, useAi = false) => {
    await api.replyComment(id, replies[id] || "", useAi);
    load();
  };

  return (
    <div className="p-8">
      <h1 className="mb-6 flex items-center gap-2 text-3xl font-bold"><MessageSquare className="h-8 w-8" /> Comentarios</h1>
      {loading && <Loader2 className="animate-spin" />}
      <div className="space-y-3">
        {comments.map((c) => (
          <Card key={c.id}>
            <CardHeader className="py-3">
              <CardTitle className="text-sm">@{c.author_username || "usuario"} · {c.status}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-3">{c.text}</p>
              {c.reply_text ? (
                <p className="text-sm text-muted-foreground">Respuesta: {c.reply_text}</p>
              ) : c.status === "pending" && (
                <div className="flex gap-2">
                  <Input placeholder="Tu respuesta..." value={replies[c.id] || ""} onChange={(e) => setReplies({ ...replies, [c.id]: e.target.value })} />
                  <Button size="sm" onClick={() => reply(c.id)}><Send className="h-4 w-4" /></Button>
                  <Button size="sm" variant="outline" onClick={() => reply(c.id, true)}><Bot className="h-4 w-4" /></Button>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
        {!loading && !comments.length && <p className="text-muted-foreground">No hay comentarios pendientes.</p>}
      </div>
    </div>
  );
}
