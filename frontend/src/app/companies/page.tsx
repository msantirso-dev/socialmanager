"use client";

import { useState } from "react";
import { Building2, Globe, Loader2, Pencil, Plus, Trash2 } from "lucide-react";
import { useAuth } from "@/components/auth/auth-provider";
import { useCompanies } from "@/components/companies/companies-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError } from "@/lib/api";

const EMPTY_FORM = { name: "", website: "", brand_description: "", tone: "professional", language: "es" };

export default function CompaniesPage() {
  const { user } = useAuth();
  const { companies, loading, error, createCompany, updateCompany, deleteCompany } = useCompanies();
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");

  const isAdmin = user?.role === "admin";
  const canEdit = isAdmin || user?.role === "editor";

  const openCreate = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setFormError("");
    setShowForm(true);
  };

  const openEdit = (c: (typeof companies)[0]) => {
    setEditingId(c.id);
    setForm({
      name: c.name,
      website: c.website ?? "",
      brand_description: c.brand_description ?? "",
      tone: c.tone ?? "professional",
      language: c.language ?? "es",
    });
    setFormError("");
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return;
    setSaving(true);
    setFormError("");
    try {
      const payload = {
        name: form.name.trim(),
        website: form.website.trim() || undefined,
        brand_description: form.brand_description.trim() || undefined,
        tone: form.tone.trim() || undefined,
        language: form.language.trim() || "es",
      };
      if (editingId) {
        await updateCompany(editingId, payload);
      } else {
        await createCompany(payload);
      }
      setShowForm(false);
      setForm(EMPTY_FORM);
      setEditingId(null);
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`¿Eliminar la empresa "${name}"? Se borrarán también sus posts y cuentas sociales.`)) return;
    try {
      await deleteCompany(id);
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Error al eliminar");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center p-16">
        <Loader2 className="animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-3xl font-bold">Empresas</h1>
        {isAdmin && (
          <Button onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" /> Nueva empresa
          </Button>
        )}
      </div>

      {error && <div className="mb-4 rounded-md bg-destructive/10 p-3 text-sm text-destructive">{error}</div>}

      {showForm && (isAdmin || editingId) && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>{editingId ? "Editar empresa" : "Nueva empresa"}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2">
              {formError && (
                <div className="md:col-span-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive">{formError}</div>
              )}
              <div className="space-y-2">
                <Label htmlFor="name">Nombre *</Label>
                <Input id="name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="website">Sitio web</Label>
                <Input id="website" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} placeholder="https://..." />
              </div>
              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="description">Descripción de marca</Label>
                <textarea
                  id="description"
                  value={form.brand_description}
                  onChange={(e) => setForm({ ...form, brand_description: e.target.value })}
                  rows={3}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tone">Tono</Label>
                <Input id="tone" value={form.tone} onChange={(e) => setForm({ ...form, tone: e.target.value })} placeholder="professional, casual..." />
              </div>
              <div className="space-y-2">
                <Label htmlFor="language">Idioma</Label>
                <Input id="language" value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })} placeholder="es" />
              </div>
              <div className="flex gap-2 md:col-span-2">
                <Button type="submit" disabled={saving}>{saving ? "Guardando..." : editingId ? "Guardar cambios" : "Crear empresa"}</Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancelar</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {companies.map((c) => (
          <Card key={c.id}>
            <CardHeader className="flex flex-row items-start justify-between space-y-0">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Building2 className="h-5 w-5 text-primary" />
                {c.name}
              </CardTitle>
              {canEdit && (
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEdit(c)} aria-label="Editar">
                    <Pencil className="h-4 w-4" />
                  </Button>
                  {isAdmin && (
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => handleDelete(c.id, c.name)} aria-label="Eliminar">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              )}
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              {c.website && (
                <p className="flex items-center gap-1"><Globe className="h-4 w-4" />{c.website}</p>
              )}
              <p>Tono: {c.tone || "—"}</p>
              <p>Idioma: {c.language}</p>
              {c.brand_description && <p className="line-clamp-3">{c.brand_description}</p>}
            </CardContent>
          </Card>
        ))}
        {!companies.length && (
          <p className="text-muted-foreground md:col-span-3">
            No hay empresas.{isAdmin ? " Creá la primera con el botón «Nueva empresa»." : " Contactá a un administrador."}
          </p>
        )}
      </div>
    </div>
  );
}
