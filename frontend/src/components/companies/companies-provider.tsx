"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, type Company } from "@/lib/domain-api";

interface CompanyInput {
  name: string;
  website?: string;
  brand_description?: string;
  tone?: string;
  language?: string;
}

interface CompaniesContextValue {
  companies: Company[];
  selected: Company | null;
  setSelected: (c: Company | null) => void;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  createCompany: (data: CompanyInput) => Promise<Company>;
  updateCompany: (id: string, data: Partial<CompanyInput>) => Promise<Company>;
  deleteCompany: (id: string) => Promise<void>;
}

const CompaniesContext = createContext<CompaniesContextValue | null>(null);

const STORAGE_KEY = "sam_selected_company";

export function CompaniesProvider({ children }: { children: React.ReactNode }) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selected, setSelectedState] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const setSelected = useCallback((company: Company | null) => {
    setSelectedState(company);
    if (company) localStorage.setItem(STORAGE_KEY, company.id);
    else localStorage.removeItem(STORAGE_KEY);
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await api.companies();
      setCompanies(list);
      const savedId = localStorage.getItem(STORAGE_KEY);
      const saved = savedId ? list.find((c) => c.id === savedId) : null;
      setSelectedState(saved ?? list[0] ?? null);
      if ((saved ?? list[0]) && !saved && list[0]) {
        localStorage.setItem(STORAGE_KEY, list[0].id);
      }
    } catch (e) {
      setCompanies([]);
      setSelectedState(null);
      setError(e instanceof Error ? e.message : "Error al cargar empresas");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const createCompany = async (data: CompanyInput) => {
    const created = await api.createCompany(data);
    await refresh();
    setSelected(created);
    return created;
  };

  const updateCompany = async (id: string, data: Partial<CompanyInput>) => {
    const updated = await api.updateCompany(id, data);
    await refresh();
    return updated;
  };

  const deleteCompany = async (id: string) => {
    await api.deleteCompany(id);
    if (selected?.id === id) localStorage.removeItem(STORAGE_KEY);
    await refresh();
  };

  return (
    <CompaniesContext.Provider
      value={{ companies, selected, setSelected, loading, error, refresh, createCompany, updateCompany, deleteCompany }}
    >
      {children}
    </CompaniesContext.Provider>
  );
}

export function useCompanies() {
  const ctx = useContext(CompaniesContext);
  if (!ctx) throw new Error("useCompanies must be used within CompaniesProvider");
  return ctx;
}
