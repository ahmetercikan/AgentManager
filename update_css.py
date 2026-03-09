import re

with open('monitor/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Eski CSS'i yeni glassmorphism CSS ile değiştir
new_css = """
    <style>
        :root {
            /* SaaS / Teknoloji Paleti - frontend-design-pro/resources/tokens.json'a dayalı */
            --glass-primary: #6366F1;       /* Indigo */
            --glass-primary-hover: #8B5CF6; /* Violet */
            --glass-bg-dark: #000000;       /* Siyah arka plan */
            --glass-bg-light: #F8FAFC;      /* Açık arka plan */
            --glass-accent-cyan: #06B6D4;   /* Cyan vurgu */
            --glass-accent-green: #10B981;  /* Yeşil vurgu */
            --glass-text: #E2E8F0;          /* Açık metin (dark mode) */
            --glass-text-muted: #94A3B8;    /* Soluk metin */
            
            /* Glassmorphism Surface Tokens */
            --glass-surface: rgba(255,255,255,0.06);     /* bg-white/6 */
            --glass-surface-hover: rgba(255,255,255,0.10); /* hover:bg-white/10 */
            --glass-border: rgba(255,255,255,0.12);      /* border-white/12 */
            --glass-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); /* shadow-black/25 */
            --glass-shadow-soft: 0 20px 25px -5px rgba(0,0,0,0.15), 0 8px 10px -6px rgba(0,0,0,0.15); /* soft shadow */
            
            --radius-card: 1.5rem;   /* 24px */
            --radius-button: 1rem;   /* 16px */
            --transition-speed: 200ms;
        }

        /* ===== RESET & ACCESSIBILITY ===== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        *:focus-visible {
            outline: 2px solid var(--glass-primary);
            outline-offset: 2px;
        }

        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        }

        /* ===== GLOBAL STYLES ===== */
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--glass-bg-dark);
            color: var(--glass-text);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            /* Gradient Backdrop */
            background-image:
                radial-gradient(ellipse at 20% 50%, rgba(34,211,238,0.20) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 30%, rgba(192,132,252,0.10) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 70%, rgba(244,114,182,0.20) 0%, transparent 50%);
            background-attachment: fixed;
            min-height: 100vh;
        }

        /* ===== TOP ANNOUNCEMENT BANNER ===== */
        .top-banner {
            background-color: rgba(99,102,241,0.1);
            border-bottom: 1px solid var(--glass-border);
            padding: 10px 20px;
            text-align: center;
            font-size: 0.85rem;
            color: #E2E8F0;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }

        .top-banner span {
            font-weight: 600;
            color: #C7D2FE;
        }

        /* ===== HEADER / NAVBAR ===== */
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 75px;
            position: sticky;
            top: 0;
            z-index: 1000;
            
            /* Glassmorphism Header */
            background: rgba(0,0,0,0.40);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--glass-border);
            padding: 0 5%;
        }

        .header-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            font-size: 1.3rem;
            color: #ffffff;
            text-decoration: none;
            letter-spacing: -0.025em; /* tracking-tight */
            transition: opacity var(--transition-speed);
        }

        .header-logo:hover {
            opacity: 0.8;
        }

        .header-logo svg {
            color: var(--glass-primary);
        }

        .nav-links {
            display: flex;
            gap: 24px;
            align-items: center;
        }

        .nav-links a:not(.btn-header-download) {
            text-decoration: none;
            color: var(--glass-text-muted);
            font-size: 0.95rem;
            font-weight: 500;
            transition: color var(--transition-speed);
        }

        .nav-links a:not(.btn-header-download):hover {
            color: #ffffff;
        }

        .btn-header-download {
            background: rgba(255,255,255,0.08); /* bg-white/8 */
            border: 1px solid var(--glass-border);
            padding: 8px 20px;
            border-radius: var(--radius-button);
            font-weight: 500;
            color: #ffffff;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all var(--transition-speed);
            backdrop-filter: blur(12px);
        }

        .btn-header-download:hover {
            background: rgba(255,255,255,0.12); /* hover:bg-white/12 */
            border-color: rgba(255,255,255,0.20);
        }

        /* ===== HERO SECTION ===== */
        .hero {
            text-align: center;
            padding: 70px 20px 50px;
            max-width: 1000px;
            margin: 0 auto;
        }

        .hero h1 {
            font-size: 3.75rem; /* text-6xl */
            font-weight: 600;   /* font-semibold */
            letter-spacing: -0.025em; /* tracking-tight */
            line-height: 1;
            margin-bottom: 24px;
            color: #ffffff;
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.25rem; /* text-4xl */
            }
        }

        .hero p {
            font-size: 1.125rem; /* text-lg */
            color: var(--glass-text-muted);
            max-width: 750px;
            margin: 0 auto 40px;
            font-weight: 400;
        }

        /* ===== TABS ===== */
        .tabs-container {
            background: rgba(0,0,0,0.20);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-top: 1px solid var(--glass-border);
            border-bottom: 1px solid var(--glass-border);
            padding: 0 5%;
            position: sticky;
            top: 75px;
            z-index: 999;
        }

        .tabs {
            display: flex;
            gap: 40px;
            justify-content: center;
            overflow-x: auto;
            /* Scrollbar hiding for neat look */
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        .tabs::-webkit-scrollbar {
            display: none;
        }

        .tab {
            padding: 20px 0;
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--glass-text-muted);
            cursor: pointer;
            position: relative;
            transition: color var(--transition-speed);
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .tab svg {
            width: 18px;
            height: 18px;
            stroke-width: 2.2;
            color: var(--glass-text-muted);
            transition: color var(--transition-speed);
        }

        .tab:hover {
            color: #ffffff;
        }
        .tab:hover svg {
            color: #ffffff;
        }

        .tab.active {
            color: #ffffff;
        }

        .tab.active svg {
            color: var(--glass-accent-cyan);
        }

        .tab.active::after {
            content: '';
            position: absolute;
            bottom: -1px;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--glass-primary), var(--glass-accent-cyan));
            border-radius: 2px 2px 0 0;
        }

        /* ===== CONTENT AREAS ===== */
        .main-content {
            background-color: transparent;
            padding: 50px 5%;
            min-height: 600px;
        }

        .page-content {
            display: none;
        }

        .page-content.active {
            display: block;
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .section-title {
            font-size: 1.875rem; /* text-3xl */
            font-weight: 600;
            letter-spacing: -0.025em;
            margin-bottom: 12px;
            text-align: center;
            color: #ffffff;
        }

        .section-subtitle {
            font-size: 1rem;
            color: var(--glass-text-muted);
            text-align: center;
            margin-bottom: 40px;
        }

        /* ===== BUTTONS ===== */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 12px 20px;
            border-radius: var(--radius-button);
            font-weight: 500;
            font-size: 0.95rem;
            cursor: pointer;
            text-decoration: none;
            transition: all var(--transition-speed);
            border: 1px solid transparent;
            gap: 8px;
        }

        /* Glass Primary Button (from snippets) */
        .btn-primary {
            background: rgba(255,255,255,0.10); /* bg-white/10 */
            border: 1px solid rgba(255,255,255,0.15); /* border-white/15 */
            backdrop-filter: blur(12px); /* backdrop-blur-md */
            -webkit-backdrop-filter: blur(12px);
            color: #ffffff;
        }

        .btn-primary:hover:not(:disabled) {
            background: rgba(255,255,255,0.15); /* hover:bg-white/15 */
            transform: translateY(-1px);
        }

        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Secondary Glass Button */
        .btn-outline {
            background: rgba(0,0,0,0.20); /* bg-black/20 */
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            color: rgba(255,255,255,0.90);
        }

        .btn-outline:hover {
            background: rgba(0,0,0,0.30); /* hover:bg-black/30 */
            color: #ffffff;
        }

        /* ===== UTILITY: GLASS SURFACE (Cards) ===== */
        .glass-surface {
            background: var(--glass-surface);
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--glass-shadow);
            border-radius: var(--radius-card);
        }

        /* ===== DOMAIN CARDS ===== */
        .domain-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px;
            max-width: 1200px;
            margin: 0 auto 40px;
        }

        .domain-card {
            background: var(--glass-surface);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-card);
            padding: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: left;
            position: relative;
            display: flex;
            flex-direction: column;
            gap: 15px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--glass-shadow);
        }

        .domain-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255,255,255,0.25);
            background: var(--glass-surface-hover);
        }

        .domain-card .icon-container {
            width: 48px;
            height: 48px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--glass-text);
            margin-bottom: 5px;
            transition: all var(--transition-speed);
            font-size: 1.5rem;
        }

        .domain-card:hover .icon-container {
            background: var(--glass-primary);
            color: #ffffff;
            border-color: var(--glass-primary);
        }

        .domain-card.selected {
            border-color: var(--glass-primary);
            background: rgba(99,102,241,0.15); /* Tint of primary */
        }

        .domain-card.selected .icon-container {
            background: var(--glass-primary);
            color: #ffffff;
            border-color: var(--glass-primary);
        }

        .domain-name {
            font-size: 1.25rem;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: -0.025em;
        }

        .domain-desc {
            font-size: 0.95rem;
            color: var(--glass-text-muted);
            line-height: 1.6;
        }

        .domain-meta {
            margin-top: auto;
            font-size: 0.8rem;
            font-weight: 500;
            color: rgba(255,255,255,0.5);
            display: flex;
            align-items: center;
            gap: 15px;
        }

        /* ===== BUILDER / CARD UI ===== */
        .builder-layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .card {
            background: var(--glass-surface);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-card);
            overflow: hidden;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--glass-shadow);
        }

        .card-header {
            padding: 16px 24px;
            font-weight: 600;
            border-bottom: 1px solid var(--glass-border);
            background: rgba(255,255,255,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
            color: #ffffff;
        }

        .card-body {
            padding: 24px;
        }

        /* Inputs within cards */
        input.agent-input, select.agent-input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            color: #ffffff;
            font-size: 0.95rem;
            margin-bottom: 16px;
            outline: none;
            transition: border-color var(--transition-speed);
        }

        input.agent-input:focus, select.agent-input:focus {
            border-color: var(--glass-primary);
        }
        
        select.agent-input option {
            background-color: #1e1e1e;
            color: #fff;
        }

        textarea.agent-input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            color: #ffffff;
            font-size: 0.95rem;
            margin-bottom: 16px;
            outline: none;
            min-height: 100px;
            resize: vertical;
        }
        textarea.agent-input:focus {
            border-color: var(--glass-primary);
        }

        /* ===== CHIPS ===== */
        .agent-chip {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            border: 1px solid var(--glass-border);
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            margin-bottom: 12px;
            transition: all var(--transition-speed);
            color: #ffffff;
        }

        .agent-chip:hover {
            border-color: rgba(255,255,255,0.25);
            background: rgba(255,255,255,0.06);
        }

        .agent-chip.in-team {
            background: rgba(16, 185, 129, 0.1); /* Green tint */
            border-color: rgba(16, 185, 129, 0.3);
        }

        .agent-info {
            flex: 1;
        }
        .agent-info strong {
            display: block;
            font-size: 0.95rem;
            font-weight: 500;
        }
        .agent-info small {
            color: var(--glass-text-muted);
            font-size: 0.8rem;
        }

        /* ===== LOGS WINDOW ===== */
        .app-window {
            background: rgba(0,0,0,0.5); /* Koyu cam terminal */
            border-radius: var(--radius-card);
            overflow: hidden;
            box-shadow: var(--glass-shadow);
            max-width: 1000px;
            margin: 20px auto;
            border: 1px solid var(--glass-border);
            backdrop-filter: blur(24px); /* Terminal daha bulanık */
            -webkit-backdrop-filter: blur(24px);
        }

        .app-header {
            background: rgba(255,255,255,0.05);
            padding: 12px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--glass-text-muted);
            font-size: 0.8rem;
            border-bottom: 1px solid var(--glass-border);
        }

        .app-body {
            padding: 24px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 0.85rem;
            color: #E2E8F0;
            min-height: 450px;
            max-height: 550px;
            overflow-y: auto;
            line-height: 1.6;
        }
        
        /* Custom scrollbar for terminal */
        .app-body::-webkit-scrollbar {
            width: 8px;
        }
        .app-body::-webkit-scrollbar-track {
            background: transparent;
        }
        .app-body::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
        }

        .log-line {
            margin-bottom: 6px;
        }

        .log-line .highlight {
            color: var(--glass-accent-cyan);
            font-weight: 500;
        }

        .log-line .time {
            color: rgba(255,255,255,0.4);
            margin-right: 12px;
        }

        .log-line.error .message {
            color: #F87171; /* red-400 */
        }

        .log-line.success .message {
            color: var(--glass-accent-green);
        }

        /* ===== COST CARDS ===== */
        .cost-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .cost-card {
            background: var(--glass-surface);
            padding: 24px;
            border-radius: var(--radius-card);
            border: 1px solid var(--glass-border);
            text-align: center;
            transition: transform var(--transition-speed);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--glass-shadow-soft);
        }

        .cost-card:hover {
            transform: translateY(-2px);
        }

        .cost-label {
            font-size: 0.8rem;
            color: var(--glass-text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }

        .cost-value {
            font-size: 2.25rem; /* text-4xl */
            font-weight: 600;
            margin-top: 8px;
            letter-spacing: -0.025em;
            color: #ffffff;
        }

        .cost-value.green {
            color: var(--glass-accent-green);
        }

        .cost-value.blue {
            color: var(--glass-accent-cyan);
        }

        .cost-value.purple {
            color: #C084FC; /* purple-400 */
        }

        /* ===== MODAL ===== */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 2000;
            align-items: center;
            justify-content: center;
        }

        /* ===== NOTIFICATIONS ===== */
        #notification-container {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 3000;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
            width: 100%;
            max-width: 400px;
        }

        .notification-toast {
            background: rgba(15,23,42,0.85); /* dark glass */
            border: 1px solid var(--glass-border);
            border-left: 4px solid var(--glass-primary);
            padding: 16px 20px;
            border-radius: 16px;
            box-shadow: var(--glass-shadow);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            display: flex;
            align-items: center;
            gap: 12px;
            pointer-events: auto;
            animation: slideInDown 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
            transition: all 0.3s ease;
        }

        .notification-toast.error {
            border-left-color: #F87171; /* red-400 */
        }

        .notification-toast.success {
            border-left-color: var(--glass-accent-green);
        }

        .notification-toast.warning {
            border-left-color: #FBBF24; /* amber-400 */
        }

        .notification-toast .icon {
            font-size: 1.2rem;
            color: #ffffff;
        }

        .notification-toast .message {
            font-size: 0.9rem;
            font-weight: 500;
            color: #ffffff;
            flex: 1;
        }

        .notification-toast .close-btn {
            cursor: pointer;
            color: rgba(255,255,255,0.5);
            background: transparent;
            border: none;
            font-size: 1.2rem;
            transition: color var(--transition-speed);
            padding: 4px;
        }

        .notification-toast .close-btn:hover {
            color: #ffffff;
        }

        @keyframes slideInDown {
            from {
                transform: translateY(-20px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }

        @keyframes fadeOutUp {
            from {
                transform: translateY(0);
                opacity: 1;
            }
            to {
                transform: translateY(-20px);
                opacity: 0;
            }
        }

        /* ===== PROJECTS PAGE ===== */
        .projects-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 24px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .project-card {
            background: var(--glass-surface);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-card);
            padding: 24px;
            transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: var(--glass-shadow-soft);
        }

        .project-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--glass-accent-cyan), var(--glass-primary));
            opacity: 0;
            transition: opacity 0.3s;
        }

        .project-card:hover {
            transform: translateY(-4px);
            border-color: rgba(255,255,255,0.25);
            background: var(--glass-surface-hover);
            box-shadow: var(--glass-shadow);
        }

        .project-card:hover::before {
            opacity: 1;
        }

        .project-card .proj-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 16px;
        }

        .project-card .proj-name {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: -0.025em;
            color: #ffffff;
        }

        .project-card .proj-badge {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: rgba(255,255,255,0.1);
            color: #ffffff;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .proj-badge.fullstack { background: rgba(59,130,246,0.2); color: #93C5FD; border-color: rgba(59,130,246,0.3); }
        .proj-badge.frontend { background: rgba(236,72,153,0.2); color: #F9A8D4; border-color: rgba(236,72,153,0.3); }
        .proj-badge.backend { background: rgba(16,185,129,0.2); color: #6EE7B7; border-color: rgba(16,185,129,0.3); }
        .proj-badge.static { background: rgba(245,158,11,0.2); color: #FCD34D; border-color: rgba(245,158,11,0.3); }
        .proj-badge.other { background: rgba(156,163,175,0.2); color: #D1D5DB; border-color: rgba(156,163,175,0.3); }

        .project-card .proj-files {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 16px;
        }

        .proj-file-chip {
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 500;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            color: var(--glass-text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .proj-file-chip .dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
        }

        .dot.python { background: #3572A5; }
        .dot.javascript, .dot.jsx { background: #f1e05a; }
        .dot.typescript, .dot.tsx { background: #2b7489; }
        .dot.html { background: #e34c26; }
        .dot.css { background: #563d7c; }
        .dot.json { background: #292929; }
        .dot.markdown { background: #083fa1; }
        .dot.text { background: #999; }

        .project-card .proj-meta {
            display: flex;
            align-items: center;
            gap: 18px;
            font-size: 0.8rem;
            color: rgba(255,255,255,0.4);
            font-weight: 500;
        }

        .project-card .proj-actions {
            display: flex;
            gap: 8px;
            margin-top: 18px;
        }

        /* Project Cards uses specific buttons */
        .proj-actions .btn-proj {
            flex: 1;
            padding: 8px 12px;
            border-radius: 12px;
            border: 1px solid var(--glass-border);
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            background: rgba(255,255,255,0.05);
            color: #ffffff;
        }

        .proj-actions .btn-proj:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,0.2);
        }

        .proj-actions .btn-proj.primary {
            background: rgba(255,255,255,0.15);
            border-color: rgba(255,255,255,0.25);
        }

        .proj-actions .btn-proj.primary:hover {
            background: rgba(255,255,255,0.25);
        }

        /* Project Detail Panel (Modal) */
        .proj-detail-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            z-index: 2000;
            align-items: center;
            justify-content: center;
        }

        .proj-detail-overlay.active {
            display: flex;
        }

        .proj-detail-panel {
            background: rgba(15,23,42,0.9); /* slate-900 with opacity */
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-card);
            width: 95%;
            max-width: 1200px;
            height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: var(--glass-shadow);
        }

        .proj-detail-header {
            padding: 16px 24px;
            border-bottom: 1px solid var(--glass-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255,255,255,0.03);
        }

        .proj-detail-header h3 {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: -0.025em;
            color: #ffffff;
        }
        
        /* Modal close button */
        .proj-detail-header button {
            background: transparent;
            border: none;
            color: rgba(255,255,255,0.5);
            cursor: pointer;
            padding: 8px;
            border-radius: 8px;
            transition: all 0.2s;
        }
        .proj-detail-header button:hover {
            background: rgba(255,255,255,0.1);
            color: #ffffff;
        }

        .proj-detail-body {
            display: grid;
            grid-template-columns: 260px 1fr;
            flex: 1;
            overflow: hidden;
        }

        .proj-file-list {
            border-right: 1px solid var(--glass-border);
            overflow-y: auto;
            background: rgba(0,0,0,0.2);
        }
        
        /* Custom scrollbar for file list */
        .proj-file-list::-webkit-scrollbar { width: 6px; }
        .proj-file-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }

        .proj-file-item {
            padding: 10px 16px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.15s;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            color: var(--glass-text-muted);
        }

        .proj-file-item:hover {
            background: rgba(255,255,255,0.05);
            color: #ffffff;
        }

        .proj-file-item.active {
            background: rgba(255,255,255,0.1);
            color: var(--glass-accent-cyan);
            border-left: 2px solid var(--glass-accent-cyan);
        }

        .proj-file-item .file-size {
            margin-left: auto;
            font-size: 0.7rem;
            color: rgba(255,255,255,0.3);
        }

        .proj-preview-area {
            flex: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            background: rgba(0,0,0,0.4);
        }

        .proj-preview-tabs {
            display: flex;
            border-bottom: 1px solid var(--glass-border);
            background: rgba(0,0,0,0.2);
        }

        .proj-preview-tab {
            padding: 10px 20px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            color: var(--glass-text-muted);
        }

        .proj-preview-tab:hover {
            color: #ffffff;
            background: rgba(255,255,255,0.05);
        }

        .proj-preview-tab.active {
            color: var(--glass-text);
            border-bottom-color: var(--glass-accent-cyan);
            background: rgba(255,255,255,0.03);
        }

        .proj-preview-content {
            flex: 1;
            overflow: hidden;
            position: relative;
        }

        .proj-preview-content iframe {
            width: 100%;
            height: 100%;
            border: none;
            background: #ffffff; /* Iframe contents are usually design to be on white */
            color: black;
        }

        .proj-preview-content pre {
            height: 100%;
            overflow: auto;
            margin: 0;
            padding: 24px;
            background: transparent;
            color: #E2E8F0;
            font-family: 'SFMono-Regular', Consolas, monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            tab-size: 4;
        }
        
        .proj-preview-content pre::-webkit-scrollbar { width: 8px; height: 8px; }
        .proj-preview-content pre::-webkit-scrollbar-corner { background: transparent; }
        .proj-preview-content pre::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }

        /* Responsive Breakpoints */
        @media (max-width: 1440px) {
            /* Desktop/Laptop padding tweaks if needed */
        }

        @media (max-width: 1024px) {
            .builder-layout,
            .cost-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 768px) {
            .proj-detail-body {
                grid-template-columns: 1fr;
                grid-template-rows: 200px 1fr;
            }
            .proj-file-list {
                border-right: none;
                border-bottom: 1px solid var(--glass-border);
            }
            .cost-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 375px) {
            .hero { padding: 40px 10px 30px; }
            .tabs { gap: 15px; }
            .domain-card { padding: 20px; }
            .btn { width: 100%; }
        }
    </style>
"""

new_content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)

with open('monitor/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('CSS güncellendi.')
