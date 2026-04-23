/**
 * Catalog HTTP client. Base URL: VITE_CATALOG_BASE_URL (see frontend/.env.example).
 */
import { z } from "zod";

const categoryResponseSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable().optional(),
  parent_id: z.number().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type CategoryResponse = z.infer<typeof categoryResponseSchema>;

const productResponseSchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable().optional(),
  price: z.union([z.string(), z.number()]).transform((v) => (typeof v === "string" ? parseFloat(v) : v)),
  category_id: z.number(),
  is_active: z.boolean(),
  created_at: z.string(),
  updated_at: z.string(),
  category: categoryResponseSchema.nullable().optional(),
});

export type ProductResponse = z.infer<typeof productResponseSchema>;

function isAbsoluteUrl(value: string): boolean {
  return value.startsWith("http://") || value.startsWith("https://");
}

function resolveCatalogBaseUrl(): { baseUrl: string; requiresAbsoluteOutput: boolean } {
  const rawPublic = import.meta.env.VITE_CATALOG_BASE_URL;
  const publicBase = rawPublic === undefined ? "" : String(rawPublic).trim();
  const isServerRuntime = typeof window === "undefined";

  if (!isServerRuntime) {
    if (!publicBase) {
      throw new Error(
        "VITE_CATALOG_BASE_URL is not set. Copy frontend/.env.example to frontend/.env and set it.",
      );
    }
    return {
      baseUrl: publicBase.replace(/\/$/, ""),
      requiresAbsoluteOutput: false,
    };
  }

  const rawServer = import.meta.env.VITE_CATALOG_SERVER_URL;
  const serverBase = rawServer === undefined ? "" : String(rawServer).trim();
  if (serverBase) {
    if (!isAbsoluteUrl(serverBase)) {
      throw new Error("VITE_CATALOG_SERVER_URL must be an absolute URL in server runtime.");
    }
    return {
      baseUrl: serverBase.replace(/\/$/, ""),
      requiresAbsoluteOutput: true,
    };
  }

  if (publicBase && isAbsoluteUrl(publicBase)) {
    return {
      baseUrl: publicBase.replace(/\/$/, ""),
      requiresAbsoluteOutput: true,
    };
  }

  throw new Error(
    "Server runtime needs absolute catalog URL. Set VITE_CATALOG_SERVER_URL (for example http://127.0.0.1:8004 or http://gateway-service:8003/api).",
  );
}

function buildUrl(path: string, searchParams?: Record<string, string | number | boolean | undefined>) {
  const { baseUrl, requiresAbsoluteOutput } = resolveCatalogBaseUrl();
  const pathname = path.startsWith("/") ? path : `/${path}`;
  const absoluteBase = isAbsoluteUrl(baseUrl);
  const origin = typeof window !== "undefined" ? window.location.origin : "http://localhost";
  const prefix = baseUrl.startsWith("/") || absoluteBase ? baseUrl : `/${baseUrl}`;
  const full = absoluteBase ? `${baseUrl}${pathname}` : `${origin}${prefix}${pathname}`;
  const url = new URL(full);
  if (searchParams) {
    for (const [k, v] of Object.entries(searchParams)) {
      if (v !== undefined) url.searchParams.set(k, String(v));
    }
  }
  if (requiresAbsoluteOutput || absoluteBase) {
    return url.toString();
  }
  return `${url.pathname}${url.search}`;
}

async function parseJson<T>(res: Response, schema: z.ZodType<T>): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Catalog API ${res.status}: ${text.slice(0, 200)}`);
  }
  const data: unknown = await res.json();
  return schema.parse(data);
}

const categoryListSchema = z.array(categoryResponseSchema);
const productListSchema = z.array(productResponseSchema);

export async function fetchCategories(): Promise<CategoryResponse[]> {
  const url = buildUrl("/categories/");
  const res = await fetch(url);
  return parseJson(res, categoryListSchema);
}

export async function fetchRootCategories(): Promise<CategoryResponse[]> {
  const url = buildUrl("/categories/root");
  const res = await fetch(url);
  return parseJson(res, categoryListSchema);
}

export type FetchProductsParams = {
  skip?: number;
  limit?: number;
  search?: string;
  categoryId?: number;
  activeOnly?: boolean;
};

export async function fetchProducts(params: FetchProductsParams = {}): Promise<ProductResponse[]> {
  const url = buildUrl("/products/", {
    skip: params.skip ?? 0,
    limit: params.limit ?? 100,
    search: params.search?.trim() || undefined,
    category_id: params.categoryId,
    active_only: params.activeOnly ?? true,
  });
  const res = await fetch(url);
  return parseJson(res, productListSchema);
}

export async function fetchProduct(id: number): Promise<ProductResponse> {
  const url = buildUrl(`/products/${id}`);
  const res = await fetch(url);
  return parseJson(res, productResponseSchema);
}

export async function fetchProductsByCategory(
  categoryId: number,
  opts: { limit?: number; skip?: number; activeOnly?: boolean } = {},
): Promise<ProductResponse[]> {
  const url = buildUrl("/products/", {
    category_id: categoryId,
    skip: opts.skip ?? 0,
    limit: opts.limit ?? 100,
    active_only: opts.activeOnly ?? true,
  });
  const res = await fetch(url);
  return parseJson(res, productListSchema);
}
