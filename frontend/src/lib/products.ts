export type Category = "chairs" | "lighting" | "tables" | "objects";

export type Product = {
  id: string;
  name: string;
  tagline: string;
  description: string;
  price: number;
  category: Category;
  image: string;
  material: string;
  inStock: boolean;
};

const img = (seed: string) =>
  `https://images.unsplash.com/${seed}?auto=format&fit=crop&w=900&q=80`;

export const PRODUCTS: Product[] = [
  {
    id: "halden-lounge",
    name: "Halden Lounge",
    tagline: "Sculpted oak lounge chair",
    description:
      "A study in restraint. The Halden lounge is hand-shaped from solid white oak with a vegetable-tanned leather sling, designed to soften with use.",
    price: 1480,
    category: "chairs",
    image: img("photo-1567538096630-e0c55bd6374c"),
    material: "Solid oak, vegetable-tanned leather",
    inStock: true,
  },
  {
    id: "noor-pendant",
    name: "Noor Pendant",
    tagline: "Hand-blown glass pendant",
    description:
      "Mouth-blown in a small Murano studio, the Noor pendant casts a warm, diffused glow ideal for dining tables and entryways.",
    price: 620,
    category: "lighting",
    image: img("photo-1513506003901-1e6a229e2d15"),
    material: "Hand-blown glass, brushed brass",
    inStock: true,
  },
  {
    id: "atlas-table",
    name: "Atlas Dining Table",
    tagline: "Travertine pedestal table",
    description:
      "Carved from a single block of Italian travertine, Atlas anchors a room with quiet weight. Seats six comfortably.",
    price: 3200,
    category: "tables",
    image: img("photo-1493663284031-b7e3aefcae8e"),
    material: "Italian travertine",
    inStock: true,
  },
  {
    id: "mira-vase",
    name: "Mira Vessel",
    tagline: "Wheel-thrown stoneware",
    description:
      "Each Mira vessel is wheel-thrown and finished with a dolomite glaze that develops subtle variation in the kiln.",
    price: 145,
    category: "objects",
    image: img("photo-1578500494198-246f612d3b3d"),
    material: "Stoneware, dolomite glaze",
    inStock: true,
  },
  {
    id: "ines-chair",
    name: "Ines Side Chair",
    tagline: "Caned beech side chair",
    description:
      "A modern reading of a continental classic. Steam-bent beech frame with hand-woven cane seat.",
    price: 540,
    category: "chairs",
    image: img("photo-1592078615290-033ee584e267"),
    material: "Beech, natural cane",
    inStock: true,
  },
  {
    id: "ode-floor-lamp",
    name: "Ode Floor Lamp",
    tagline: "Linen-shaded floor lamp",
    description:
      "A sculptural floor lamp with a hand-stitched linen shade and a slender blackened-steel stem.",
    price: 890,
    category: "lighting",
    image: img("photo-1507473885765-e6ed057f782c"),
    material: "Linen, blackened steel",
    inStock: false,
  },
  {
    id: "sora-coffee",
    name: "Sora Coffee Table",
    tagline: "Burl walnut coffee table",
    description:
      "A low, generous coffee table cut from a single walnut burl and finished with hardwax oil.",
    price: 1980,
    category: "tables",
    image: img("photo-1533090481720-856c6e3c1fdc"),
    material: "Walnut burl, hardwax oil",
    inStock: true,
  },
  {
    id: "kaja-bowl",
    name: "Kaja Serving Bowl",
    tagline: "Turned ash bowl",
    description:
      "Hand-turned from a single piece of European ash, finished with food-safe oil. Each bowl is unique.",
    price: 220,
    category: "objects",
    image: img("photo-1578749556568-bc2c40e68b61"),
    material: "European ash",
    inStock: true,
  },
];

export const CATEGORIES: { id: Category | "all"; label: string }[] = [
  { id: "all", label: "All" },
  { id: "chairs", label: "Chairs" },
  { id: "lighting", label: "Lighting" },
  { id: "tables", label: "Tables" },
  { id: "objects", label: "Objects" },
];

export const formatPrice = (cents: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(cents);

export const getProduct = (id: string) => PRODUCTS.find((p) => p.id === id);
