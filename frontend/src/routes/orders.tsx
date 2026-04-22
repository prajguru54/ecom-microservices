import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { getOrders, type Order } from "@/store/orders";
import { formatPrice } from "@/lib/products";

export const Route = createFileRoute("/orders")({
  head: () => ({ meta: [{ title: "Orders — Atelier" }] }),
  component: OrdersPage,
});

function OrdersPage() {
  const [orders, setOrders] = useState<Order[] | null>(null);

  useEffect(() => {
    setOrders(getOrders());
  }, []);

  return (
    <div className="container-page py-12 md:py-16">
      <h1 className="font-display text-4xl md:text-5xl">Orders</h1>
      <p className="mt-2 text-muted-foreground">A record of everything you've placed.</p>

      <div className="mt-10">
        {orders === null ? (
          <div className="space-y-4">
            {[0, 1].map((i) => (
              <div key={i} className="h-24 animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        ) : orders.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border py-20 text-center">
            <h3 className="font-display text-2xl">No orders yet</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              When you place an order, it will appear here.
            </p>
            <Link
              to="/"
              className="mt-6 inline-flex rounded-full bg-foreground px-5 py-2.5 text-sm text-background hover:bg-foreground/90"
            >
              Start shopping
            </Link>
          </div>
        ) : (
          <ul className="divide-y divide-border rounded-lg border border-border bg-card">
            {orders.map((o) => (
              <li key={o.id}>
                <Link
                  to="/orders/$id"
                  params={{ id: o.id }}
                  className="flex items-center justify-between gap-4 p-5 hover:bg-muted/40"
                >
                  <div>
                    <div className="font-mono text-sm">{o.id}</div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(o.createdAt).toLocaleDateString(undefined, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}{" "}
                      · {o.items.length} item{o.items.length > 1 ? "s" : ""}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="tabular-nums">{formatPrice(o.total)}</div>
                    <div className="text-xs text-moss">Confirmed</div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
