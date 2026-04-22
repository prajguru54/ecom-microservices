export function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-border bg-secondary/40">
      <div className="container-page grid gap-10 py-14 text-sm md:grid-cols-4">
        <div>
          <div className="font-display text-2xl">Atelier<span className="text-accent">.</span></div>
          <p className="mt-3 max-w-xs text-muted-foreground">
            Considered objects for the modern home, sourced from independent makers.
          </p>
        </div>
        <div>
          <div className="mb-3 font-medium">Shop</div>
          <ul className="space-y-2 text-muted-foreground">
            <li>Chairs</li><li>Lighting</li><li>Tables</li><li>Objects</li>
          </ul>
        </div>
        <div>
          <div className="mb-3 font-medium">Studio</div>
          <ul className="space-y-2 text-muted-foreground">
            <li>About</li><li>Journal</li><li>Trade program</li>
          </ul>
        </div>
        <div>
          <div className="mb-3 font-medium">Support</div>
          <ul className="space-y-2 text-muted-foreground">
            <li>Shipping & returns</li><li>Care guide</li><li>Contact</li>
          </ul>
        </div>
      </div>
      <div className="container-page flex flex-col items-start justify-between gap-2 border-t border-border py-6 text-xs text-muted-foreground md:flex-row">
        <div>© {new Date().getFullYear()} Atelier Studio</div>
        <div>Crafted with care.</div>
      </div>
    </footer>
  );
}
