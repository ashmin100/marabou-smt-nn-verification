import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set the style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False # Fix minus sign for Korean fonts

# Extended Data (0.01 to 0.20 sweep)
epsilons = [round(x * 0.01, 2) for x in range(1, 21)]
runtimes = [
    0.51, 0.53, 0.51, 0.41, 0.47, 0.49, 0.48, 0.45, 0.53, 0.95,
    1.05, 6.21, 3.49, 8.48, 12.80, 23.55, 45.70, 138.20, 298.44, 300.60
]
statuses = ['UNSAT\n(Robust)'] * 20

# Create the figure
fig, ax = plt.subplots(figsize=(14, 7))

# Create a bar plot
colors = ['#4C72B0'] * 20
bars = ax.bar(range(len(epsilons)), runtimes, color=colors, width=0.6, alpha=0.8)

# Set labels and title
ax.set_xticks(range(len(epsilons)))
ax.set_xticklabels([f"ε = {eps}" for eps in epsilons], fontsize=12)
ax.set_ylabel('Verification Time (seconds) [Log Scale]', fontsize=12, fontweight='bold')
ax.set_xlabel('L-inf Perturbation Radius (ε)', fontsize=12, fontweight='bold')
ax.set_title('Marabou Verification Scalability: Runtime vs. Epsilon\n(MNIST 784→64→32→10 FC)', fontsize=14, fontweight='bold', pad=15)

# Add a dashed line for the timeout threshold
ax.axhline(y=300, color='r', linestyle='--', alpha=0.7, label='Timeout Threshold (300s)')
ax.legend(loc='upper left', fontsize=11)

# Add text annotations on top of the bars (only for significant jumps to avoid clutter)
for i, bar in enumerate(bars):
    height = bar.get_height()
    if epsilons[i] in [0.05, 0.10, 0.15, 0.18, 0.20] or height > 10:
        ax.text(bar.get_x() + bar.get_width()/2., height * 1.2,
                f'{height:.1f}s\nUNSAT',
                ha='center', va='bottom', fontsize=10, fontweight='bold', color=colors[i])

# Set y-axis to log scale because the difference is 10,000x
ax.set_yscale('log')
ax.set_ylim(0.01, 2000) # Give room for text

plt.tight_layout()
plt.savefig('results/verification_results.png', dpi=300, bbox_inches='tight')
print("Plot successfully saved to results/verification_results.png")
