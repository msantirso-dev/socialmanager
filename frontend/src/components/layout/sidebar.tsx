"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Building2, Calendar, LayoutDashboard, LogOut, MessageSquare, Share2, Sparkles, BarChart3,
} from "lucide-react";
import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/companies", label: "Empresas", icon: Building2 },
  { href: "/social", label: "Redes Sociales", icon: Share2 },
  { href: "/ai", label: "Generador IA", icon: Sparkles },
  { href: "/calendar", label: "Calendario", icon: Calendar },
  { href: "/metrics", label: "Métricas", icon: BarChart3 },
  { href: "/comments", label: "Comentarios", icon: MessageSquare },
];

const ROLE_LABELS: Record<string, string> = {
  admin: "Administrador", editor: "Editor", operator: "Operador", readonly: "Solo lectura",
};

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="hidden w-64 flex-col border-r bg-card md:flex">
      <div className="flex h-16 items-center border-b px-6">
        <Sparkles className="mr-2 h-6 w-6 text-primary" />
        <span className="text-lg font-bold">Social AI Manager</span>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href} className={cn(
            "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
            pathname === item.href ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          )}>
            <item.icon className="h-4 w-4" />{item.label}
          </Link>
        ))}
      </nav>
      <div className="border-t p-4">
        {user && (
          <div className="mb-3 space-y-1">
            <p className="truncate text-sm font-medium">{user.full_name}</p>
            <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            <p className="text-xs text-primary">{ROLE_LABELS[user.role] || user.role}</p>
          </div>
        )}
        <Button variant="outline" size="sm" className="w-full" onClick={() => logout()}>
          <LogOut className="mr-2 h-4 w-4" /> Cerrar sesión
        </Button>
      </div>
    </aside>
  );
}
