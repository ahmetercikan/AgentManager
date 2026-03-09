const tiers = [
    { name: "Starter", price: "$19", desc: "For solo learners", perks: ["Core lessons", "Community", "Basic templates"] },
    { name: "Pro", price: "$49", desc: "For teams", perks: ["Everything in Starter", "Team seats", "Advanced templates"] },
    { name: "Elite", price: "$99", desc: "For orgs", perks: ["Everything in Pro", "SSO", "Dedicated support"] }
];

export default function PricingGlass() {
    return (
        <section className="relative mx-auto max-w-6xl px-6 py-16">
            <div className="text-center">
                <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">Pricing</h2>
                <p className="mt-3 text-white/70">Simple tiers with glass UI cards.</p>
            </div>

            <div className="mt-10 grid gap-5 md:grid-cols-3">
                {tiers.map((t) => (
                    <div key={t.name} className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl shadow-black/20 p-6">
                        <div className="flex items-baseline justify-between">
                            <h3 className="text-xl font-semibold text-white">{t.name}</h3>
                            <span className="text-2xl font-semibold text-white">{t.price}</span>
                        </div>
                        <p className="mt-2 text-white/70">{t.desc}</p>
                        <ul className="mt-5 space-y-2 text-white/75">
                            {t.perks.map((p) => (
                                <li key={p} className="flex gap-2">
                                    <span className="text-white/60">•</span>
                                    <span>{p}</span>
                                </li>
                            ))}
                        </ul>
                        <button className="mt-6 w-full rounded-xl px-5 py-3 bg-white/12 hover:bg-white/18 border border-white/15 backdrop-blur-md transition text-white">
                            Choose {t.name}
                        </button>
                    </div>
                ))}
            </div>
        </section>
    );
}
