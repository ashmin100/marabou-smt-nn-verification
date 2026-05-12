import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np

sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False

epsilons = [round(x * 0.01, 2) for x in range(1, 21)]

samples = {
    'idx=0  (label: 7)': {
        'runtimes': [0.39, 0.42, 0.51, 0.53, 0.48, 0.48, 0.48, 0.49, 0.52, 0.91,
                     1.02, 6.17, 3.57, 8.90, 14.28, 25.79, 38.15, 138.94, 300.54, 300.48],
        'verdicts': ['UNSAT'] * 20,
        'eps_star': None,
        'subtitle': 'Fully robust — certified ∀ε ≤ 0.20',
    },
    'idx=8  (label: 5)': {
        'runtimes': [0.52, 0.58, 0.51, 0.56, 0.83, 0.59, 0.61, 1.05, 0.88, 0.92,
                     1.58, 9.25, 16.55, 82.15, 1.08, 0.78, 0.61, 0.74, 0.62, 0.62],
        'verdicts': ['UNSAT', 'UNSAT'] + ['SAT'] * 18,
        'eps_star': 0.03,
        'subtitle': 'Non-robust — ε* ≈ 0.03  (adv class: 6)',
    },
    'idx=33  (label: 4)': {
        'runtimes': [0.48, 0.49, 0.54, 0.56, 0.53, 0.55, 0.51, 0.52, 0.52, 0.58,
                     0.49, 0.53, 0.54, 0.57, 0.49, 0.52, 0.51, 0.55, 0.57, 0.54],
        'verdicts': ['UNSAT'] * 4 + ['SAT'] * 16,
        'eps_star': 0.05,
        'subtitle': 'Non-robust — ε* ≈ 0.05  (adv class: 0)',
    },
}

UNSAT_C = '#4878CF'   # muted blue
SAT_C   = '#D65F5F'   # muted red
BND_C   = '#C44E52'   # boundary marker

fig = plt.figure(figsize=(18, 11))
gs = gridspec.GridSpec(2, 3, figure=fig,
                       height_ratios=[3, 1.1],
                       hspace=0.45, wspace=0.32)

axes_bar  = [fig.add_subplot(gs[0, i]) for i in range(3)]
ax_heat   = fig.add_subplot(gs[1, :])

# ── Top row: bar charts ────────────────────────────────────────────────────────
for ax, (title, d) in zip(axes_bar, samples.items()):
    bar_colors = [SAT_C if v == 'SAT' else UNSAT_C for v in d['verdicts']]
    xs = np.arange(len(epsilons))
    bars = ax.bar(xs, d['runtimes'], color=bar_colors,
                  width=0.72, alpha=0.88, edgecolor='white', linewidth=0.4)

    ax.set_yscale('log')
    ax.set_ylim(0.08, 3000)
    ax.axhline(300, color='#555', linestyle='--', linewidth=1, alpha=0.55, zorder=0)
    ax.text(len(epsilons) - 0.5, 330, '300 s timeout',
            ha='right', va='bottom', fontsize=8, color='#555', style='italic')

    if d['eps_star'] is not None:
        star_i = epsilons.index(d['eps_star'])
        ax.axvline(star_i - 0.5, color=BND_C, linestyle=':', linewidth=1.8, zorder=3)
        ax.text(star_i - 0.5, 1200, f" ε* = {d['eps_star']}", color=BND_C,
                fontsize=9, fontweight='bold', va='top')

    # Value labels on tall bars only
    for bar, rt in zip(bars, d['runtimes']):
        if rt >= 8:
            ax.text(bar.get_x() + bar.get_width() / 2., rt * 1.25,
                    f'{rt:.0f}s', ha='center', va='bottom',
                    fontsize=7.5, fontweight='bold', color='#222')

    ax.set_xticks(xs[::4])
    ax.set_xticklabels([f'{epsilons[i]:.2f}' for i in range(0, 20, 4)], fontsize=9)
    ax.set_xlabel('ε (normalized L∞ radius)', fontsize=9)
    ax.set_ylabel('Verification Time (s) · log scale', fontsize=9)
    ax.set_title(f'{title}\n{d["subtitle"]}',
                 fontsize=10.5, fontweight='bold', pad=6)
    ax.yaxis.grid(True, which='both', alpha=0.4)
    ax.set_axisbelow(True)

# ── Bottom row: verdict heatmap ────────────────────────────────────────────────
verdict_matrix = np.array([
    [0 if v == 'UNSAT' else 1 for v in d['verdicts']]
    for d in samples.values()
])

annot_labels = np.where(verdict_matrix == 0, 'UNSAT', 'SAT')
cmap_heat = sns.color_palette([UNSAT_C, SAT_C], as_cmap=True)

sns.heatmap(
    verdict_matrix,
    ax=ax_heat,
    cmap=cmap_heat,
    vmin=0, vmax=1,
    xticklabels=[f'{e:.2f}' for e in epsilons],
    yticklabels=[k.split('(')[0].strip() for k in samples],
    cbar=False,
    linewidths=0.6,
    linecolor='white',
    annot=annot_labels,
    fmt='',
    annot_kws={'size': 8.5, 'weight': 'bold', 'color': 'white'},
)
ax_heat.set_title('Verdict Map  (blue = UNSAT · certified robust,  red = SAT · adversarial example found)',
                  fontsize=10.5, pad=7)
ax_heat.set_xlabel('ε (normalized)', fontsize=10)
ax_heat.tick_params(axis='y', labelsize=9.5, rotation=0)
ax_heat.tick_params(axis='x', labelsize=9)

# ── Shared legend ──────────────────────────────────────────────────────────────
handles = [
    mpatches.Patch(facecolor=UNSAT_C, alpha=0.88, label='UNSAT — network certified robust'),
    mpatches.Patch(facecolor=SAT_C,   alpha=0.88, label='SAT  — adversarial example found'),
    plt.Line2D([0], [0], color=BND_C, linestyle=':', linewidth=2, label='ε*  robustness boundary'),
]
fig.legend(handles=handles, loc='upper right',
           bbox_to_anchor=(0.995, 0.985),
           fontsize=9.5, framealpha=0.92)

fig.suptitle(
    'Marabou Local Robustness Verification — Runtime & Verdict Comparison\n'
    'MNIST FC (784→64→32→10 · 96 ReLU neurons) · Three Test Samples',
    fontsize=13, fontweight='bold', y=1.03,
)

import os; os.makedirs('results', exist_ok=True)
plt.savefig('results/verification_results.png', dpi=200, bbox_inches='tight')
print("Saved → results/verification_results.png")
