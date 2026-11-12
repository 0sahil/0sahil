"""Profile header. Usage: python3 scripts/gen_header.py assets
Name card with a rotating last word over a slow-drifting soft gradient glow,
written as header-light.svg and header-dark.svg. Self-contained SVG, system fonts, respects reduced motion.
"""
import sys

out = sys.argv[1]
W, H = 880, 240
WORDS = ["backends", "frontends", "infrastructure", "AI agents"]
HOLD = 2.6        # seconds each word stays
CYCLE = HOLD * len(WORDS)
SANS = 'ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'

THEMES = {
    "dark":  dict(fg="#f0f6fc", mut="#9198a1", acc="#79c0ff", acc2="#d2a8ff", card="#0d1117", bd="#30363d"),
    "light": dict(fg="#1f2328", mut="#59636e", acc="#0969da", acc2="#8250df", card="#ffffff", bd="#d0d7de"),
}

def rotating(x, y, t):
    """Each word holds, slides up and out, then comes back in from below.
    Keyframe 0% is the fully visible state and word 0 starts there, so a
    viewer that never runs the animation still shows "I build backends"."""
    p = 100 / len(WORDS)          # % of cycle per word
    io = 0.35 / CYCLE * 100       # % used for in/out motion
    css = (f"@keyframes rot{{0%{{opacity:1;transform:none}}"
           f"{p-io:.2f}%{{opacity:1;transform:none}}"
           f"{p:.2f}%{{opacity:0;transform:translateY(-22px)}}"
           f"{p+0.01:.2f}%{{opacity:0;transform:translateY(22px)}}"
           f"{100-io:.2f}%{{opacity:0;transform:translateY(22px)}}"
           f"100%{{opacity:1;transform:none}}}}"
           f".w{{opacity:0;animation:rot {CYCLE}s cubic-bezier(.3,.7,.2,1) infinite}}.w0{{opacity:1}}")
    els = []
    for i, w in enumerate(WORDS):
        delay = 0 if i == 0 else -(CYCLE - i * HOLD)
        els.append(f'<text class="big w w{i}" x="{x}" y="{y}" style="animation-delay:{delay:.2f}s"><tspan class="ghost">I build </tspan><tspan class="hl">{w}</tspan></text>')
    return css, "\n".join(els)

def build(variant, theme):
    c = THEMES[theme]
    css_rot, words = rotating(38, 150, theme)
    bg, extra_css = "", ""
    if variant == "aurora":
        o = 0.55 if theme == "dark" else 0.35
        bg = f'''<defs>
<radialGradient id="g1"><stop offset="0" stop-color="{c['acc']}" stop-opacity="{o}"/><stop offset="1" stop-color="{c['acc']}" stop-opacity="0"/></radialGradient>
<radialGradient id="g2"><stop offset="0" stop-color="{c['acc2']}" stop-opacity="{o}"/><stop offset="1" stop-color="{c['acc2']}" stop-opacity="0"/></radialGradient>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
</defs>
<g clip-path="url(#clip)">
<rect width="{W}" height="{H}" fill="{c['card']}"/>
<g filter="url(#blur)">
<ellipse class="b1" cx="700" cy="70" rx="210" ry="120" fill="url(#g1)"/>
<ellipse class="b2" cx="560" cy="210" rx="230" ry="110" fill="url(#g2)"/>
</g></g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{c['bd']}"/>'''
        extra_css = (".b1{animation:d1 14s ease-in-out infinite alternate}"
                     ".b2{animation:d2 17s ease-in-out infinite alternate}"
                     "@keyframes d1{to{transform:translate(-160px,40px)}}"
                     "@keyframes d2{to{transform:translate(150px,-50px)}}")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Sahil. I build backends, frontends, infrastructure and AI agents.">
<style>
.small{{font:500 15px {SANS};fill:{c['mut']};letter-spacing:.2px}}
.big{{font:700 40px {SANS};fill:{c['fg']};letter-spacing:-1px}}
.hl{{fill:{c['acc']}}}
.ghost{{fill:none}}
.foot{{font:400 15px {SANS};fill:{c['mut']}}}
{css_rot}
{extra_css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
{bg}
<text class="small in" x="40" y="92">Hi, I'm Sahil.</text>
<text class="big in d1" x="38" y="150">I build </text>
{words}
<text class="foot in d2" x="40" y="194">Backend at heart · deep on DevOps · building with AI agents</text>
</svg>'''

for t in THEMES:
    open(f"{out}/header-{t}.svg", "w").write(build("aurora", t))
print("ok")
