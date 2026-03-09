export default function HeroGlass() {
    return (
        <section className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/20 via-purple-400/10 to-pink-400/20" />
            <div className="relative mx-auto max-w-6xl px-6 py-20">
                <div className="rounded-3xl border border-white/10 bg-white/5 backdrop-blur-2xl shadow-2xl shadow-black/20 p-10 md:p-14">
                    <p className="text-sm text-white/70">AI EDU • Glass UI</p>
                    <h1 className="mt-4 text-4xl md:text-6xl font-semibold tracking-tight text-white">
                        Teach. Learn. Ship faster.
                    </h1>
                    <p className="mt-5 text-base md:text-lg text-white/75 max-w-2xl">
                        Premium glassmorphism experience with clean UX patterns. Built for modern SaaS education products.
                    </p>
                    <div className="mt-8 flex flex-col sm:flex-row gap-3">
                        <button className="rounded-xl px-5 py-3 bg-white/12 hover:bg-white/18 border border-white/15 backdrop-blur-md transition text-white">
                            Start Free
                        </button>
                        <button className="rounded-xl px-5 py-3 bg-black/20 hover:bg-black/30 border border-white/10 backdrop-blur-md transition text-white/90">
                            Watch Demo
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}
