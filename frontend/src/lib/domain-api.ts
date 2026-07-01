import { apiFetch } from "./api";

export interface Company {
  id: string;
  name: string;
  website?: string;
  brand_description?: string;
  tone?: string;
  language: string;
}

export interface SocialAccount {
  id: string;
  company_id: string;
  network: string;
  username?: string;
  display_name?: string;
  is_connected: boolean;
}

export interface Post {
  id: string;
  company_id: string;
  type: string;
  status: string;
  title?: string;
  caption?: string;
  hashtags?: string[];
  scheduled_at?: string;
  published_at?: string;
  media_urls?: string[];
}

export interface Dashboard {
  scheduled_posts: number;
  published_posts: number;
  failed_posts: number;
  pending_comments: number;
  total_engagement: number;
  total_reach: number;
  ai_calls: number;
  ai_cost: number;
  credits_balance: number;
  followers: number;
  upcoming_posts: Post[];
}

export interface Comment {
  id: string;
  post_id: string;
  author_username?: string;
  text: string;
  status: string;
  reply_text?: string;
}

export const api = {
  companies: () => apiFetch<Company[]>("/api/v1/companies"),
  createCompany: (data: Partial<Company> & { name: string }) =>
    apiFetch<Company>("/api/v1/companies", { method: "POST", body: JSON.stringify(data) }),
  updateCompany: (id: string, data: Partial<Company>) =>
    apiFetch<Company>(`/api/v1/companies/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteCompany: (id: string) => apiFetch<{ message: string }>(`/api/v1/companies/${id}`, { method: "DELETE" }),
  dashboard: () => apiFetch<Dashboard>("/api/v1/dashboard"),
  metrics: (companyId?: string) => apiFetch<{ posts: unknown[]; totals: Record<string, number> }>(`/api/v1/metrics${companyId ? `?company_id=${companyId}` : ""}`),
  socialAccounts: (companyId: string) => apiFetch<SocialAccount[]>(`/api/v1/social/accounts?company_id=${companyId}`),
  instagramConnect: (companyId: string) => apiFetch<{ oauth_url: string }>(`/api/v1/social/instagram/connect?company_id=${companyId}`),
  posts: (companyId?: string) => apiFetch<Post[]>(`/api/v1/posts${companyId ? `?company_id=${companyId}` : ""}`),
  createPost: (data: unknown) => apiFetch<Post>("/api/v1/posts", { method: "POST", body: JSON.stringify(data) }),
  publishPost: (id: string) => apiFetch<Post>(`/api/v1/posts/${id}/publish`, { method: "POST" }),
  generateContent: (data: unknown) => apiFetch<Record<string, unknown>>("/api/v1/ai/generate/content", { method: "POST", body: JSON.stringify(data) }),
  generateImage: (data: unknown) => apiFetch<{ url: string; asset_id: string }>("/api/v1/ai/generate/image", { method: "POST", body: JSON.stringify(data) }),
  comments: () => apiFetch<Comment[]>("/api/v1/comments"),
  replyComment: (id: string, message: string, useAi = false) =>
    apiFetch<Comment>(`/api/v1/comments/${id}/reply`, { method: "POST", body: JSON.stringify({ message, use_ai: useAi }) }),
};
