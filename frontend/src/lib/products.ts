import type { ProductResponse } from "@/lib/catalogApi";

/** Display slug derived from catalog category name (filters / related products). */
export type CategorySlug = string;

export type Product = {
  id: string;
  name: string;
  tagline: string;
  description: string;
  price: number;
  category: CategorySlug;
  image: string;
  material: string;
  inStock: boolean;
};

export function categoryNameToSlug(name: string): CategorySlug {
  const s = name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return s || "misc";
}

function placeholderImage(productId: number, seed: string) {
  return `https://picsum.photos/seed/${encodeURIComponent(`catalog-${productId}-${seed}`)}/900/1125`;
}

/** Map catalog API product to the UI Product shape (tagline/image/material are placeholders until API adds fields). */
export function mapProductResponseToProduct(p: ProductResponse): Product {
  const desc = p.description?.trim() ?? "";
  const firstLine = (desc.split(/\n+/)[0] ?? "").trim();
  const tagline =
    firstLine.length > 120 ? `${firstLine.slice(0, 117)}…` : firstLine || p.name;
  const catName = p.category?.name ?? "";
  const slug = categoryNameToSlug(catName || "misc");

  return {
    id: String(p.id),
    name: p.name,
    tagline,
    description: desc || "No description yet.",
    price: Number.isFinite(p.price) ? p.price : 0,
    category: slug,
    image: placeholderImage(p.id, slug),
    material: "—",
    inStock: p.is_active,
  };
}

export const formatPrice = (amount: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
