import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set the style
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False # Fix minus sign for Korean fonts

# Data
epsilons = [0.01, 0.05, 0.20]
runtimes = [0.03, 0.08, 300.04]
statuses = ['UNSAT\n(Robust)', 'UNSAT\n(Robust)', 'TIMEOUT\n(Unresolved)']

# Create the figure
fig, ax = plt.subplots(figsize=(9, 6))

# Create a bar plot
colors = ['#4C72B0', '#55A868', '#C44E52']
bars = ax.bar(range(len(epsilons)), runtimes, color=colors, width=0.4, alpha=0.8)

# Set labels and title
ax.set_xticks(range(len(epsilons)))
ax.set_xticklabels([f"ε = {eps}" for eps in epsilons], fontsize=12)
ax.set_ylabel('Verification Time (seconds) [Log Scale]', fontsize=12, fontweight='bold')
ax.set_xlabel('L-inf Perturbation Radius (ε)', fontsize=12, fontweight='bold')
ax.set_title('Marabou Verification Scalability: Runtime vs. Epsilon\n(MNIST 784→64→32→10 FC)', fontsize=14, fontweight='bold', pad=15)

# Add a dashed line for the timeout threshold
ax.axhline(y=300, color='r', linestyle='--', alpha=0.7, label='Timeout Threshold (300s)')
ax.legend(loc='upper left', fontsize=11)

# Add text annotations on top of the bars
for i, bar in enumerate(bars):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height * 1.2,
            f'{height:.2f}s\n{statuses[i]}',
            ha='center', va='bottom', fontsize=11, fontweight='bold', color=colors[i])

# Set y-axis to log scale because the difference is 10,000x
ax.set_yscale('log')
ax.set_ylim(0.01, 2000) # Give room for text

plt.tight_layout()
plt.savefig('verification_results.png', dpi=300, bbox_inches='tight')
print("Plot successfully saved to verification_results.png")
