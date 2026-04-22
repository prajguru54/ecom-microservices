import type { CartItem } from "./cart";

export type Order = {
  id: string;
  createdAt: string;
  items: CartItem[];
  subtotal: number;
  shipping: number;
  total: number;
  customer: { name: string; email: string; address: string; city: string; zip: string };
};

const KEY = "atelier.orders.v1";

export function getOrders(): Order[] {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveOrder(order: Order) {
  const all = getOrders();
  all.unshift(order);
  localStorage.setItem(KEY, JSON.stringify(all));
}

export function getOrder(id: string) {
  return getOrders().find((o) => o.id === id);
}

export function newOrderId() {
  return "AT-" + Math.random().toString(36).slice(2, 8).toUpperCase();
}
