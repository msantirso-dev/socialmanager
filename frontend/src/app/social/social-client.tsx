"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Instagram, Loader2, RefreshCw } from "lucide-react";
import { useCompanies } from "@/hooks/use-companies";
import { api, type SocialAccount } from "@/lib/domain-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function SocialPageInner() {
  const { selected, loading: cl } = useCompanies();
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [loading, setLoading] = useState(false);
  const params = useSearchParams();
  const connected = params.get("connected");
  const error = params.get("error");

  const load = () => {
    if (!selected) return;
    setLoading(true);
    api.socialAccounts(selected.id).then(setAccounts).finally(() => setLoading(false));
  };

  useEffect(load, [selected?.id]);

  const connect = async () => {
    if (!selected) return;
    const { oauth_url } = await api.instagramConnect(selected.id);
    window.location.href = oauth_url;
  };

  const ig = accounts.find((a) => a.network === "instagram");

  return (
    <div className="p-8">
      <h1 className="mb-6 text-3xl font-bold">Redes Sociales</h1>
      {connected && <div className="mb-4 rounded-md bg-green-500/10 p-3 text-green-700">Instagram conectado correctamente</div>}
      {error && <div className="mb-4 rounded-md bg-destructive/10 p-3 text-destructive">{error}</div>}
      {(cl || loading) && <Loader2 className="animate-spin" />}
      {selected && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Instagram className="h-5 w-5" /> Instagram</CardTitle>
            <CardDescription>Empresa: {selected.name}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {ig?.is_connected ? (
              <div>
                <p className="font-medium">@{ig.username}</p>
                <p className="text-sm text-muted-foreground">{ig.display_name}</p>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" onClick={load}><RefreshCw className="mr-1 h-4 w-4" /> Actualizar</Button>
                </div>
              </div>
            ) : (
              <Button onClick={connect}><Instagram className="mr-2 h-4 w-4" /> Conectar Instagram</Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
