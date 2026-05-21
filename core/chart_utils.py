import matplotlib.pyplot as plt


def dark_fig(figsize=(10, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("#0a0e17")
    ax.set_facecolor("#111827")
    for spine in ax.spines.values():
        spine.set_color("#1e2d45")
    ax.tick_params(colors="#6b7c99")
    ax.xaxis.label.set_color("#6b7c99")
    ax.yaxis.label.set_color("#6b7c99")
    ax.title.set_color("#e8edf5")
    return fig, ax
