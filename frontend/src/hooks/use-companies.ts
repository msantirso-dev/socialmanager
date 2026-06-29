"use client";

import { useEffect, useState } from "react";
import { api, type Company } from "@/lib/domain-api";

export function useCompanies() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Company | null>(null);

  useEffect(() => {
    api.companies()
      .then((c) => {
        setCompanies(c);
        if (c.length) setSelected(c[0]);
      })
      .catch(() => setCompanies([]))
      .finally(() => setLoading(false));
  }, []);

  return { companies, selected, setSelected, loading };
}
