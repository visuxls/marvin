const MARVIN_API_URL =
  process.env.MARVIN_API_URL ??
  process.env.NEXT_PUBLIC_MARVIN_API_URL ??
  "http://127.0.0.1:7932";

const PASSTHROUGH_RESPONSE_HEADERS = [
  "content-type",
  "cache-control",
  "x-vercel-ai-ui-message-stream",
] as const;

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function proxyToMarvin(request: Request, path: string[]) {
  const subpath = path.join("/");
  const url = new URL(`/api/${subpath}`, MARVIN_API_URL);
  url.search = new URL(request.url).search;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("content-type", contentType);
  }

  const init: RequestInit & { duplex?: "half" } = {
    method: request.method,
    headers,
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
    init.duplex = "half";
  }

  const upstream = await fetch(url, init);
  const responseHeaders = new Headers();

  for (const name of PASSTHROUGH_RESPONSE_HEADERS) {
    const value = upstream.headers.get(name);
    if (value) {
      responseHeaders.set(name, value);
    }
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export const dynamic = "force-dynamic";

async function proxyHandler(request: Request, context: RouteContext) {
  const { path } = await context.params;
  return proxyToMarvin(request, path);
}

export const GET = proxyHandler;
export const POST = proxyHandler;
export const PATCH = proxyHandler;
export const DELETE = proxyHandler;

export async function OPTIONS() {
  return new Response(null, { status: 200 });
}
