import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useState } from "react";
import { Minus, Plus, Check } from "lucide-react";
import { toast } from "sonner";
import { fetchProduct, fetchProductsByCategory } from "@/lib/catalogApi";
import { formatPrice, mapProductResponseToProduct } from "@/lib/products";
import { useCart } from "@/store/cart";
import { ProductCard } from "@/components/ProductCard";

export const Route = createFileRoute("/product/$id")({
  loader: async ({ params }) => {
    const id = Number(params.id);
    if (!Number.isInteger(id) || id < 1) throw notFound();
    try {
      const raw = await fetchProduct(id);
      const product = mapProductResponseToProduct(raw);
      const categoryId = raw.category_id;
      let relatedRaw: Awaited<ReturnType<typeof fetchProductsByCategory>> = [];
      try {
        relatedRaw = await fetchProductsByCategory(categoryId, { limit: 12 });
      } catch {
        relatedRaw = [];
      }
      const related = relatedRaw
        .filter((p) => p.id !== id)
        .slice(0, 3)
        .map(mapProductResponseToProduct);
      return { product, related };
    } catch {
      throw notFound();
    }
  },
  head: ({ loaderData }) =>
    loaderData
      ? {
          meta: [
            { title: `${loaderData.product.name} — Atelier` },
            { name: "description", content: loaderData.product.tagline },
            { property: "og:title", content: loaderData.product.name },
            { property: "og:description", content: loaderData.product.tagline },
            { property: "og:image", content: loaderData.product.image },
          ],
        }
      : {},
  notFoundComponent: () => (
    <div className="container-page py-24 text-center">
      <h1 className="font-display text-4xl">Product not found</h1>
      <Link to="/" className="mt-4 inline-block text-accent underline">
        Return to shop
      </Link>
    </div>
  ),
  component: ProductPage,
});

function ProductPage() {
  const { product, related } = Route.useLoaderData();
  const { add } = useCart();
  const [qty, setQty] = useState(1);

  return (
    <>
      <div className="container-page pt-6 text-xs text-muted-foreground">
        <Link to="/" className="hover:text-foreground">
          Shop
        </Link>
        <span className="mx-2">/</span>
        <span className="text-foreground">{product.name}</span>
      </div>

      <article className="container-page grid gap-10 py-8 md:grid-cols-12 md:gap-16 md:py-12">
        <div className="md:col-span-7">
          <div className="overflow-hidden rounded-md bg-muted">
            <img
              src={product.image}
              alt={product.name}
              className="aspect-[4/5] w-full object-cover"
            />
          </div>
        </div>

        <div className="md:col-span-5 md:sticky md:top-24 md:self-start">
          <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
            {product.category}
          </div>
          <h1 className="mt-3 font-display text-4xl md:text-5xl">{product.name}</h1>
          <p className="mt-2 text-muted-foreground">{product.tagline}</p>
          <div className="mt-6 text-2xl tabular-nums">{formatPrice(product.price)}</div>

          <p className="mt-8 leading-relaxed text-foreground/80">{product.description}</p>

          <dl className="mt-8 space-y-2 border-t border-border pt-6 text-sm">
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Material</dt>
              <dd>{product.material}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Lead time</dt>
              <dd>2–3 weeks</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Shipping</dt>
              <dd>Worldwide</dd>
            </div>
          </dl>

          <div className="mt-8 flex items-center gap-3">
            <div className="inline-flex items-center rounded-full border border-border">
              <button
                onClick={() => setQty((q) => Math.max(1, q - 1))}
                className="p-2.5 text-muted-foreground hover:text-foreground"
                aria-label="Decrease"
              >
                <Minus className="h-4 w-4" />
              </button>
              <span className="w-8 text-center text-sm tabular-nums">{qty}</span>
              <button
                onClick={() => setQty((q) => q + 1)}
                className="p-2.5 text-muted-foreground hover:text-foreground"
                aria-label="Increase"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
            <button
              disabled={!product.inStock}
              onClick={() => {
                add(product, qty);
                toast.success(`${product.name} added to cart`, {
                  description: `${qty} × ${formatPrice(product.price)}`,
                });
              }}
              className="flex-1 rounded-full bg-foreground px-6 py-3 text-sm text-background transition hover:bg-foreground/90 disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground"
            >
              {product.inStock ? "Add to cart" : "Sold out"}
            </button>
          </div>

          <div className="mt-6 flex items-center gap-2 text-xs text-muted-foreground">
            <Check className="h-3.5 w-3.5 text-moss" />
            Free shipping on orders over $500
          </div>
        </div>
      </article>

      {related.length > 0 && (
        <section className="container-page border-t border-border py-16">
          <h2 className="font-display text-3xl">You may also like</h2>
          <div className="mt-8 grid gap-x-6 gap-y-12 sm:grid-cols-2 lg:grid-cols-3">
            {related.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}
    </>
  );
}
