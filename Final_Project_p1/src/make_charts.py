import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- Data captured from actual benchmark runs (see output_*.txt) ----
ll_n = [10_000, 50_000, 100_000, 500_000, 1_000_000, 2_000_000]
ll_linked = [0.565, 2.790, 5.767, 28.667, 57.639, 114.683]
ll_array = [0.229, 1.342, 2.254, 11.290, 23.723, 48.482]

soa_n = [1_000, 10_000, 100_000, 500_000, 1_000_000]
soa_aos = [6.146, 63.156, 622.942, 3126.894, 6272.634]
soa_soa = [0.138, 0.392, 5.714, 41.385, 80.251]

# ---------------------------------------------------------------------
# Figure 1: Linked List vs Array traversal time
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(ll_n, ll_linked, marker="o", color="#c0392b", label="Linked List (pointer chasing)")
ax.plot(ll_n, ll_array, marker="s", color="#2980b9", label="Contiguous Array")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Number of elements (N)")
ax.set_ylabel("Traversal time (ms, log scale)")
ax.set_title("Sequential Traversal: Linked List vs Contiguous Array")
ax.legend()
ax.grid(True, which="both", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig("/home/claude/project/figures/fig1_linkedlist_vs_array.png", dpi=160)
plt.close(fig)

# ---------------------------------------------------------------------
# Figure 2: AoS vs SoA update time
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(soa_n, soa_aos, marker="o", color="#c0392b", label="Array-of-Structures (AoS)")
ax.plot(soa_n, soa_soa, marker="s", color="#27ae60", label="Structure-of-Arrays (SoA / NumPy)")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("Number of particles (N)")
ax.set_ylabel("Time for 20 update steps (ms, log scale)")
ax.set_title("Particle Position Update: AoS vs SoA Layout")
ax.legend()
ax.grid(True, which="both", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig("/home/claude/project/figures/fig2_aos_vs_soa.png", dpi=160)
plt.close(fig)

# ---------------------------------------------------------------------
# Figure 3: Speedup comparison bar chart
# ---------------------------------------------------------------------
speedup_ll = [a / b for a, b in zip(ll_linked, ll_array)]
speedup_soa = [a / b for a, b in zip(soa_aos, soa_soa)]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

axes[0].bar([str(n) for n in ll_n], speedup_ll, color="#2980b9")
axes[0].set_title("Speedup: Array vs Linked List")
axes[0].set_xlabel("N")
axes[0].set_ylabel("Speedup (x)")
axes[0].tick_params(axis="x", rotation=45)
for i, v in enumerate(speedup_ll):
    axes[0].text(i, v + 0.05, f"{v:.1f}x", ha="center", fontsize=8)

axes[1].bar([str(n) for n in soa_n], speedup_soa, color="#27ae60")
axes[1].set_title("Speedup: SoA vs AoS")
axes[1].set_xlabel("N")
axes[1].set_ylabel("Speedup (x)")
axes[1].tick_params(axis="x", rotation=45)
for i, v in enumerate(speedup_soa):
    axes[1].text(i, v + 2, f"{v:.0f}x", ha="center", fontsize=8)

fig.suptitle("Observed Speedup From Data-Structure/Layout Optimization")
fig.tight_layout()
fig.savefig("/home/claude/project/figures/fig3_speedup_comparison.png", dpi=160)
plt.close(fig)

# ---------------------------------------------------------------------
# Figure 4: Conceptual memory layout diagram (AoS vs SoA)
# ---------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.axis("off")

def draw_block(ax, x0, y0, w, h, label, color, fontsize=8):
    rect = plt.Rectangle((x0, y0), w, h, facecolor=color, edgecolor="black", linewidth=1)
    ax.add_patch(rect)
    ax.text(x0 + w / 2, y0 + h / 2, label, ha="center", va="center", fontsize=fontsize)

# AoS: each particle's 3 fields adjacent, but particles are objects on the heap
ax.text(0.5, 0.95, "Array-of-Structures (AoS)", fontsize=12, fontweight="bold", ha="center")
colors_p = ["#f1c40f", "#e67e22", "#e74c3c"]
x = 0.05
for p in range(3):
    draw_block(ax, x, 0.72, 0.10, 0.12, f"P{p}.x", colors_p[p])
    draw_block(ax, x + 0.10, 0.72, 0.10, 0.12, f"P{p}.y", colors_p[p])
    draw_block(ax, x + 0.20, 0.72, 0.10, 0.12, f"P{p}.z", colors_p[p])
    ax.annotate("", xy=(x + 0.34, 0.78), xytext=(x + 0.30, 0.78),
                arrowprops=dict(arrowstyle="->"))
    x += 0.34
ax.text(0.5, 0.60, "Heap object per particle -> pointer hop between particles;\n"
                    "kernel touching only 'x' still pulls in y, z, header bytes.",
        fontsize=8.5, ha="center", style="italic")

# SoA: one contiguous array per field
ax.text(0.5, 0.42, "Structure-of-Arrays (SoA)", fontsize=12, fontweight="bold", ha="center")
fields = [("x", "#3498db"), ("y", "#9b59b6"), ("z", "#1abc9c")]
y = 0.28
for fname, color in fields:
    xx = 0.10
    for p in range(6):
        draw_block(ax, xx, y, 0.10, 0.09, f"{fname}{p}", color, fontsize=7)
        xx += 0.10
    y -= 0.11
ax.text(0.5, -0.02, "One contiguous buffer per field -> sequential access,\n"
                    "cache-line reuse, and SIMD/vectorized updates.",
        fontsize=8.5, ha="center", style="italic")

ax.set_xlim(0, 1)
ax.set_ylim(-0.08, 1.0)
fig.tight_layout()
fig.savefig("/home/claude/project/figures/fig4_aos_soa_layout_diagram.png", dpi=160)
plt.close(fig)

print("Charts written to /home/claude/project/figures/")
