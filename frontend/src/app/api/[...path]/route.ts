import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

function getBackendUrl(): string {
  const url =
    process.env.BACKEND_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000";
  return url.replace(/\/$/, "");
}

const HOP_BY_HOP = new Set(["connection", "keep-alive", "transfer-encoding", "upgrade", "host"]);

async function proxyRequest(request: NextRequest, path: string[]) {
  const targetUrl = `${getBackendUrl()}/api/${path.join("/")}${request.nextUrl.search}`;

  const headers = new Headers();
  request.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) {
      headers.set(key, value);
    }
  });

  let body: ArrayBuffer | undefined;
  if (request.method !== "GET" && request.method !== "HEAD") {
    body = await request.arrayBuffer();
  }

  let response: Response;
  try {
    response = await fetch(targetUrl, {
      method: request.method,
      headers,
      body,
      redirect: "manual",
    });
  } catch {
    return NextResponse.json(
      { detail: "No se pudo conectar con el backend. Verificá BACKEND_INTERNAL_URL en Coolify." },
      { status: 502 }
    );
  }

  const responseHeaders = new Headers();
  response.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) {
      responseHeaders.set(key, value);
    }
  });

  return new NextResponse(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

type RouteContext = { params: Promise<{ path: string[] }> };

async function handler(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
export const OPTIONS = handler;
export const HEAD = handler;
