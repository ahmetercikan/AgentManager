type NavItem = { label: string; href: string };

const nav: NavItem[] = [
    { label: "Features", href: "#features" },
    { label: "Pricing", href: "#pricing" },
    { label: "FAQ", href: "#faq" }
];

export default function NavbarGlass() {
    return (
        <header className="sticky top-0 z-50">
            <div className="mx-auto max-w-6xl px-6 pt-5">
                <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl shadow-2xl shadow-black/20">
                    <div className="flex items-center justify-between px-4 py-3 md:px-5">
                        {/* Brand */}
                        <a href="#" className="flex items-center gap-2 text-white">
                            <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-white/12 bg-white/8 backdrop-blur-md">
                                <span className="text-sm font-semibold">AI</span>
                            </span>
                            <span className="text-sm md:text-base font-semibold tracking-tight">
                                AI EDU
                            </span>
                        </a>

                        {/* Desktop nav */}
                        <nav className="hidden md:flex items-center gap-2">
                            {nav.map((item) => (
                                <a
                                    key={item.href}
                                    href={item.href}
                                    className="rounded-xl px-3 py-2 text-sm text-white/75 hover:text-white hover:bg-white/8 border border-transparent hover:border-white/10 transition"
                                >
                                    {item.label}
                                </a>
                            ))}
                        </nav>

                        {/* Actions */}
                        <div className="flex items-center gap-2">
                            <a
                                href="#"
                                className="hidden sm:inline-flex rounded-xl px-4 py-2 text-sm text-white/85 hover:text-white bg-black/20 hover:bg-black/30 border border-white/10 backdrop-blur-md transition"
                            >
                                Sign in
                            </a>
                            <a
                                href="#"
                                className="inline-flex rounded-xl px-4 py-2 text-sm text-white bg-white/12 hover:bg-white/18 border border-white/15 backdrop-blur-md transition"
                            >
                                Start free
                            </a>
                        </div>
                    </div>

                    {/* Mobile quick links (simple, no menu state) */}
                    <div className="md:hidden border-t border-white/10 px-4 py-2">
                        <div className="flex items-center gap-2 overflow-x-auto">
                            {nav.map((item) => (
                                <a
                                    key={item.href}
                                    href={item.href}
                                    className="whitespace-nowrap rounded-xl px-3 py-2 text-sm text-white/75 hover:text-white hover:bg-white/8 border border-transparent hover:border-white/10 transition"
                                >
                                    {item.label}
                                </a>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}
