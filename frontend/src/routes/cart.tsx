import { createFileRoute, Link } from "@tanstack/react-router";
import { Minus, Plus, X, ShoppingBag } from "lucide-react";
import { useCart } from "@/store/cart";
import { formatPrice } from "@/lib/products";

export const Route = createFileRoute("/cart")({
  head: () => ({ meta: [{ title: "Cart — Atelier" }] }),
  component: CartPage,
});

function CartPage() {
  const { items, setQty, remove, subtotal, count } = useCart();
  const shipping = subtotal > 500 || subtotal === 0 ? 0 : 25;
  const total = subtotal + shipping;

  if (count === 0) {
    return (
      <div className="container-page py-24">
        <div className="mx-auto max-w-md text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <ShoppingBag className="h-6 w-6 text-muted-foreground" />
          </div>
          <h1 className="mt-6 font-display text-4xl">Your cart is empty</h1>
          <p className="mt-2 text-muted-foreground">
            Start with something small — a vessel, a bowl, a piece of light.
          </p>
          <Link
            to="/"
            className="mt-8 inline-flex rounded-full bg-foreground px-6 py-3 text-sm text-background hover:bg-foreground/90"
          >
            Browse the shop
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container-page py-12 md:py-16">
      <h1 className="font-display text-4xl md:text-5xl">Your cart</h1>
      <div className="mt-10 grid gap-12 lg:grid-cols-12">
        <ul className="divide-y divide-border lg:col-span-8">
          {items.map(({ product, qty }) => (
            <li key={product.id} className="flex gap-4 py-6 md:gap-6">
              <Link to="/product/$id" params={{ id: product.id }} className="shrink-0">
                <img
                  src={product.image}
                  alt={product.name}
                  className="h-28 w-24 rounded-md object-cover md:h-36 md:w-32"
                />
              </Link>
              <div className="flex flex-1 flex-col">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <Link
                      to="/product/$id"
                      params={{ id: product.id }}
                      className="font-display text-xl hover:text-accent"
                    >
                      {product.name}
                    </Link>
                    <div className="text-sm text-muted-foreground">{product.tagline}</div>
                  </div>
                  <div className="text-sm tabular-nums">{formatPrice(product.price * qty)}</div>
                </div>

                <div className="mt-auto flex items-center justify-between pt-4">
                  <div className="inline-flex items-center rounded-full border border-border">
                    <button
                      onClick={() => setQty(product.id, qty - 1)}
                      className="p-2 text-muted-foreground hover:text-foreground"
                      aria-label="Decrease"
                    >
                      <Minus className="h-3.5 w-3.5" />
                    </button>
                    <span className="w-8 text-center text-sm tabular-nums">{qty}</span>
                    <button
                      onClick={() => setQty(product.id, qty + 1)}
                      className="p-2 text-muted-foreground hover:text-foreground"
                      aria-label="Increase"
                    >
                      <Plus className="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <button
                    onClick={() => remove(product.id)}
                    className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-destructive"
                  >
                    <X className="h-3.5 w-3.5" /> Remove
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>

        <aside className="lg:col-span-4">
          <div className="rounded-lg border border-border bg-card p-6 shadow-soft">
            <h2 className="font-display text-2xl">Summary</h2>
            <dl className="mt-6 space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Subtotal</dt>
                <dd className="tabular-nums">{formatPrice(subtotal)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Shipping</dt>
                <dd className="tabular-nums">
                  {shipping === 0 ? "Free" : formatPrice(shipping)}
                </dd>
              </div>
              <div className="border-t border-border pt-3 flex justify-between text-base">
                <dt>Total</dt>
                <dd className="tabular-nums font-medium">{formatPrice(total)}</dd>
              </div>
            </dl>
            <Link
              to="/checkout"
              className="mt-6 flex w-full items-center justify-center rounded-full bg-foreground px-6 py-3 text-sm text-background hover:bg-foreground/90"
            >
              Checkout
            </Link>
            <Link
              to="/"
              className="mt-3 flex w-full items-center justify-center rounded-full border border-border px-6 py-3 text-sm hover:border-foreground/40"
            >
              Continue shopping
            </Link>
          </div>
        </aside>
      </div>
    </div>
  );
}
