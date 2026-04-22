import { Link, useRouterState } from "@tanstack/react-router";
import { ShoppingBag, Search } from "lucide-react";
import { useCart } from "@/store/cart";

const NAV = [
  { to: "/", label: "Shop" },
  { to: "/orders", label: "Orders" },
];

export function SiteHeader() {
  const { count } = useCart();
  const { location } = useRouterState();

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="container-page flex h-16 items-center justify-between gap-6">
        <Link to="/" className="font-display text-2xl tracking-tight">
          Atelier<span className="text-accent">.</span>
        </Link>

        <nav className="hidden items-center gap-8 text-sm md:flex">
          {NAV.map((n) => {
            const active =
              n.to === "/" ? location.pathname === "/" : location.pathname.startsWith(n.to);
            return (
              <Link
                key={n.to}
                to={n.to}
                className={
                  "transition-colors hover:text-foreground " +
                  (active ? "text-foreground" : "text-muted-foreground")
                }
              >
                {n.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            to="/"
            search={{ q: "" }}
            className="hidden items-center gap-2 rounded-full border border-border px-3 py-1.5 text-xs text-muted-foreground hover:border-foreground/40 sm:flex"
          >
            <Search className="h-3.5 w-3.5" /> Search
          </Link>
          <Link
            to="/cart"
            className="relative inline-flex h-10 w-10 items-center justify-center rounded-full hover:bg-muted"
            aria-label="Cart"
          >
            <ShoppingBag className="h-[18px] w-[18px]" />
            {count > 0 && (
              <span className="absolute -right-0.5 -top-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded-full bg-accent px-1 text-[10px] font-medium text-accent-foreground">
                {count}
              </span>
            )}
          </Link>
        </div>
      </div>
    </header>
  );
}
