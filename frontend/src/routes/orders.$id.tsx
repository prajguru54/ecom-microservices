import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Check } from "lucide-react";
import { getOrder, type Order } from "@/store/orders";
import { formatPrice } from "@/lib/products";

export const Route = createFileRoute("/orders/$id")({
  head: ({ params }) => ({ meta: [{ title: `Order ${params.id} — Atelier` }] }),
  component: OrderDetail,
});

function OrderDetail() {
  const { id } = Route.useParams();
  const [state, setState] = useState<{ loading: boolean; order: Order | undefined }>({
    loading: true,
    order: undefined,
  });

  useEffect(() => {
    setState({ loading: false, order: getOrder(id) });
  }, [id]);

  if (state.loading) {
    return (
      <div className="container-page py-16">
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="mt-8 h-64 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  if (!state.order) {
    return (
      <div className="container-page py-24 text-center">
        <h1 className="font-display text-3xl">Order not found</h1>
        <Link to="/orders" className="mt-4 inline-block text-accent underline">
          View all orders
        </Link>
      </div>
    );
  }

  const order = state.order;

  return (
    <div className="container-page py-12 md:py-16">
      <div className="mx-auto max-w-2xl">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-moss/15 text-moss">
            <Check className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">
              Order confirmed
            </div>
            <div className="font-mono text-sm">{order.id}</div>
          </div>
        </div>

        <h1 className="mt-8 font-display text-4xl md:text-5xl text-balance">
          Thank you, {order.customer.name.split(" ")[0] || "friend"}.
        </h1>
        <p className="mt-3 text-muted-foreground">
          We've received your order and sent a confirmation to{" "}
          <span className="text-foreground">{order.customer.email}</span>. Expect a shipping
          update within 2–3 business days.
        </p>

        <div className="mt-10 rounded-lg border border-border bg-card p-6">
          <h2 className="font-display text-xl">Items</h2>
          <ul className="mt-4 divide-y divide-border">
            {order.items.map(({ product, qty }) => (
              <li key={product.id} className="flex items-center gap-4 py-4">
                <img src={product.image} alt="" className="h-16 w-14 rounded object-cover" />
                <div className="flex-1">
                  <div className="text-sm">{product.name}</div>
                  <div className="text-xs text-muted-foreground">Qty {qty}</div>
                </div>
                <div className="text-sm tabular-nums">
                  {formatPrice(product.price * qty)}
                </div>
              </li>
            ))}
          </ul>

          <dl className="mt-4 space-y-2 border-t border-border pt-4 text-sm">
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Subtotal</dt>
              <dd className="tabular-nums">{formatPrice(order.subtotal)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Shipping</dt>
              <dd className="tabular-nums">
                {order.shipping === 0 ? "Free" : formatPrice(order.shipping)}
              </dd>
            </div>
            <div className="flex justify-between border-t border-border pt-2 text-base">
              <dt>Total</dt>
              <dd className="tabular-nums font-medium">{formatPrice(order.total)}</dd>
            </div>
          </dl>
        </div>

        <div className="mt-6 grid gap-6 rounded-lg border border-border bg-card p-6 sm:grid-cols-2 text-sm">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">Ship to</div>
            <div className="mt-2">{order.customer.name}</div>
            <div className="text-muted-foreground">{order.customer.address}</div>
            <div className="text-muted-foreground">
              {order.customer.city}, {order.customer.zip}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">Status</div>
            <div className="mt-2 text-moss">Confirmed · preparing for shipment</div>
          </div>
        </div>

        <div className="mt-10 flex gap-3">
          <Link
            to="/"
            className="inline-flex rounded-full bg-foreground px-5 py-2.5 text-sm text-background hover:bg-foreground/90"
          >
            Continue shopping
          </Link>
          <Link
            to="/orders"
            className="inline-flex rounded-full border border-border px-5 py-2.5 text-sm hover:border-foreground/40"
          >
            All orders
          </Link>
        </div>
      </div>
    </div>
  );
}
