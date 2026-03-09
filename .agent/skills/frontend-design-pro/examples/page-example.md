# Page Example — Glassmorphism Landing

Bu dosya, `NavbarGlass`, `HeroGlass`, `PricingGlass` bileşenlerini bir sayfada nasıl birleştireceğini gösterir.

> Not: Aşağıdaki örnekler Next.js App Router (app/) ile uyumludur.
> React/Vite kullanıyorsan aynı bileşenleri `App.tsx` içinde de benzer şekilde render edebilirsin.

---

## 1) Next.js (App Router) örneği

### `app/page.tsx`

```tsx
import NavbarGlass from "../components/NavbarGlass";
import HeroGlass from "../components/HeroGlass";
import PricingGlass from "../components/PricingGlass";

export default function Page() {
  return (
    <main className="min-h-screen bg-black text-white">
      <NavbarGlass />
      <HeroGlass />

      <section id="features" className="mx-auto max-w-6xl px-6 py-16">
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl shadow-black/20 p-6">
          <h2 className="text-2xl font-semibold">Features</h2>
          <p className="mt-2 text-white/70">
            Add your FeaturesGlass.tsx here if available.
          </p>
        </div>
      </section>

      <section id="pricing">
        <PricingGlass />
      </section>

      <section id="faq" className="mx-auto max-w-6xl px-6 py-16">
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl shadow-black/20 p-6">
          <h2 className="text-2xl font-semibold">FAQ</h2>
          <div className="mt-4 space-y-3 text-white/75">
            <div className="rounded-xl border border-white/10 bg-black/20 p-4">
              <p className="font-medium text-white">How does this work?</p>
              <p className="mt-1 text-white/70">
                It’s a glassmorphism UI template designed for SaaS landing pages.
              </p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/20 p-4">
              <p className="font-medium text-white">Is it performance friendly?</p>
              <p className="mt-1 text-white/70">
                Blur and shadows are intentionally kept moderate.
              </p>
            </div>
          </div>
        </div>
      </section>

      <footer className="mx-auto max-w-6xl px-6 pb-12">
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl shadow-black/20 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <p className="text-white font-semibold">AI EDU</p>
            <p className="text-white/60 text-sm mt-1">Premium glass UI for education SaaS.</p>
          </div>
          <a
            href="#"
            className="inline-flex rounded-xl px-4 py-2 text-sm text-white bg-white/12 hover:bg-white/18 border border-white/15 backdrop-blur-md transition"
          >
            Get started
          </a>
        </div>
      </footer>
    </main>
  );
}
