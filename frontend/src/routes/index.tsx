import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { z } from "zod";
import { zodValidator, fallback } from "@tanstack/zod-adapter";
import { Search, X } from "lucide-react";
import { CATEGORIES, PRODUCTS, type Category } from "@/lib/products";
import { ProductCard } from "@/components/ProductCard";

const searchSchema = z.object({
  cat: fallback(z.string(), "all").default("all"),
  q: fallback(z.string(), "").default(""),
});

export const Route = createFileRoute("/")({
  validateSearch: zodValidator(searchSchema),
  head: () => ({
    meta: [
      { title: "Shop — Atelier" },
      { name: "description", content: "Browse furniture, lighting, and objects." },
    ],
  }),
  component: Index,
});

function Index() {
  const { cat, q } = Route.useSearch();
  const navigate = Route.useNavigate();
  const [query, setQuery] = useState(q);

  const filtered = useMemo(() => {
    const term = q.trim().toLowerCase();
    return PRODUCTS.filter((p) => {
      if (cat !== "all" && p.category !== cat) return false;
      if (!term) return true;
      return (
        p.name.toLowerCase().includes(term) ||
        p.tagline.toLowerCase().includes(term) ||
        p.material.toLowerCase().includes(term)
      );
    });
  }, [cat, q]);

  return (
    <>
      {/* Hero */}
      <section className="container-page pt-12 pb-10 md:pt-20 md:pb-16">
        <div className="grid items-end gap-8 md:grid-cols-12">
          <div className="md:col-span-8">
            <div className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
              Spring Edit · 2026
            </div>
            <h1 className="mt-4 font-display text-5xl leading-[1.05] text-balance md:text-7xl">
              Objects shaped by hand,<br />
              <span className="italic text-accent">chosen with care.</span>
            </h1>
          </div>
          <p className="text-muted-foreground md:col-span-4 md:text-right">
            A small, rotating collection of furniture, lighting, and ceramics from independent
            European studios. Shipped worldwide.
          </p>
        </div>
      </section>

      {/* Filters */}
      <section className="container-page sticky top-16 z-30 -mt-2 border-b border-border bg-background/85 py-4 backdrop-blur">
        <div className="flex flex-col items-start justify-between gap-3 md:flex-row md:items-center">
          <div className="flex flex-wrap gap-1.5">
            {CATEGORIES.map((c) => {
              const active = cat === c.id;
              return (
                <Link
                  key={c.id}
                  to="/"
                  search={(prev: { cat: string; q: string }) => ({ ...prev, cat: c.id })}
                  className={
                    "rounded-full border px-3.5 py-1.5 text-sm transition " +
                    (active
                      ? "border-foreground bg-foreground text-background"
                      : "border-border text-muted-foreground hover:border-foreground/40 hover:text-foreground")
                  }
                >
                  {c.label}
                </Link>
              );
            })}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              navigate({ search: (prev: { cat: string; q: string }) => ({ ...prev, q: query }) });
            }}
            className="flex w-full items-center gap-2 rounded-full border border-border bg-background px-3.5 py-1.5 md:w-72"
          >
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search the collection"
              className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
            />
            {query && (
              <button
                type="button"
                onClick={() => {
                  setQuery("");
                  navigate({ search: (prev: { cat: string; q: string }) => ({ ...prev, q: "" }) });
                }}
                className="text-muted-foreground hover:text-foreground"
                aria-label="Clear"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </form>
        </div>
      </section>

      {/* Grid */}
      <section className="container-page py-12">
        {filtered.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border py-24 text-center">
            <h3 className="font-display text-2xl">Nothing matches.</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Try clearing your filters or searching another term.
            </p>
            <Link
              to="/"
              search={{ cat: "all", q: "" }}
              className="mt-6 inline-flex rounded-full border border-border px-4 py-2 text-sm hover:border-foreground/40"
            >
              Reset filters
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-x-6 gap-y-12 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filtered.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}
      </section>
    </>
  );
}

// Type narrowing helper for typescript on filter ids
export type _Cat = Category;
