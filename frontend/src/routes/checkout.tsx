import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { useCart } from "@/store/cart";
import { formatPrice } from "@/lib/products";
import { newOrderId, saveOrder } from "@/store/orders";

export const Route = createFileRoute("/checkout")({
  head: () => ({ meta: [{ title: "Checkout — Atelier" }] }),
  component: CheckoutPage,
});

function CheckoutPage() {
  const { items, subtotal, clear, count } = useCart();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    address: "",
    city: "",
    zip: "",
  });
  const shipping = subtotal > 500 ? 0 : 25;
  const total = subtotal + shipping;

  if (count === 0) {
    return (
      <div className="container-page py-24 text-center">
        <h1 className="font-display text-3xl">Nothing to check out</h1>
        <Link to="/" className="mt-4 inline-block text-accent underline">Browse the shop</Link>
      </div>
    );
  }

  const update = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    await new Promise((r) => setTimeout(r, 900));
    const id = newOrderId();
    saveOrder({
      id,
      createdAt: new Date().toISOString(),
      items,
      subtotal,
      shipping,
      total,
      customer: form,
    });
    clear();
    toast.success("Order placed", { description: `Confirmation ${id}` });
    navigate({ to: "/orders/$id", params: { id } });
  };

  const Field = ({
    label,
    name,
    type = "text",
    required = true,
  }: {
    label: string;
    name: keyof typeof form;
    type?: string;
    required?: boolean;
  }) => (
    <label className="block">
      <span className="text-xs uppercase tracking-wider text-muted-foreground">{label}</span>
      <input
        type={type}
        required={required}
        value={form[name]}
        onChange={update(name)}
        className="mt-1.5 w-full rounded-md border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-foreground"
      />
    </label>
  );

  return (
    <div className="container-page py-12 md:py-16">
      <h1 className="font-display text-4xl md:text-5xl">Checkout</h1>
      <form onSubmit={onSubmit} className="mt-10 grid gap-12 lg:grid-cols-12">
        <div className="space-y-8 lg:col-span-7">
          <section>
            <h2 className="font-display text-xl">Contact</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Field label="Full name" name="name" />
              <Field label="Email" name="email" type="email" />
            </div>
          </section>
          <section>
            <h2 className="font-display text-xl">Shipping</h2>
            <div className="mt-4 grid gap-4">
              <Field label="Address" name="address" />
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="City" name="city" />
                <Field label="Postal code" name="zip" />
              </div>
            </div>
          </section>
        </div>

        <aside className="lg:col-span-5">
          <div className="rounded-lg border border-border bg-card p-6 shadow-soft">
            <h2 className="font-display text-xl">Order</h2>
            <ul className="mt-4 divide-y divide-border">
              {items.map(({ product, qty }) => (
                <li key={product.id} className="flex items-center gap-3 py-3">
                  <img src={product.image} alt="" className="h-14 w-12 rounded object-cover" />
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
                <dd className="tabular-nums">{formatPrice(subtotal)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Shipping</dt>
                <dd className="tabular-nums">{shipping === 0 ? "Free" : formatPrice(shipping)}</dd>
              </div>
              <div className="flex justify-between border-t border-border pt-2 text-base">
                <dt>Total</dt>
                <dd className="tabular-nums font-medium">{formatPrice(total)}</dd>
              </div>
            </dl>
            <button
              type="submit"
              disabled={submitting}
              className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-full bg-foreground px-6 py-3 text-sm text-background hover:bg-foreground/90 disabled:opacity-60"
            >
              {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
              {submitting ? "Placing order..." : "Place order"}
            </button>
            <p className="mt-3 text-center text-xs text-muted-foreground">
              This is a demo. No payment will be charged.
            </p>
          </div>
        </aside>
      </form>
    </div>
  );
}
