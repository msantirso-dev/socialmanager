"use client";

import { useState } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { useCompanies } from "@/components/companies/companies-provider";
import { api } from "@/lib/domain-api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function AIPage() {
  const { selected, loading: companiesLoading } = useCompanies();
  const [concept, setConcept] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState("");

  const generate = async () => {
    if (!selected || !concept) return;
    setLoading(true);
    try {
      const data = await api.generateContent({
        company_id: selected.id,
        concept,
        text_provider: "anthropic",
      });
      setResult(data);
    } catch (e) {
      setResult({ error: String(e) });
    } finally {
      setLoading(false);
    }
  };

  const generateImg = async () => {
    if (!selected || !result?.image_prompt) return;
    setLoading(true);
    try {
      const data = await api.generateImage({
        company_id: selected.id,
        prompt: String(result.image_prompt),
        provider: "openai",
      });
      setImageUrl(data.url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8">
      <h1 className="mb-6 text-3xl font-bold">Generador IA</h1>
      {!companiesLoading && !selected && (
        <p className="mb-6 text-muted-foreground">Creá o seleccioná una empresa en el menú lateral para generar contenido.</p>
      )}
      <Card className="mb-6">
        <CardHeader><CardTitle>Concepto</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Describe tu idea de contenido</Label>
            <Input value={concept} onChange={(e) => setConcept(e.target.value)} placeholder="Promocionar un sistema de domótica premium..." className="mt-2" />
          </div>
          <Button onClick={generate} disabled={loading || !selected}>
            {loading ? <Loader2 className="mr-2 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
            Generar contenido
          </Button>
        </CardContent>
      </Card>
      {result && !result.error && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card><CardHeader><CardTitle>Título</CardTitle></CardHeader><CardContent>{String(result.title)}</CardContent></Card>
          <Card><CardHeader><CardTitle>Texto</CardTitle></CardHeader><CardContent className="whitespace-pre-wrap">{String(result.text)}</CardContent></Card>
          <Card><CardHeader><CardTitle>Hashtags</CardTitle></CardHeader><CardContent>{(result.hashtags as string[])?.join(" ")}</CardContent></Card>
          <Card><CardHeader><CardTitle>CTA</CardTitle></CardHeader><CardContent>{String(result.cta)}</CardContent></Card>
          <Card className="md:col-span-2">
            <CardHeader><CardTitle>Prompt imagen</CardTitle></CardHeader>
            <CardContent>
              <p className="mb-2 text-sm">{String(result.image_prompt)}</p>
              <Button size="sm" onClick={generateImg} disabled={loading}>Generar imagen</Button>
              {imageUrl && <img src={imageUrl} alt="Generated" className="mt-4 max-w-md rounded-lg" />}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
