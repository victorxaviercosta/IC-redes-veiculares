"""


"""

import numpy as np
import matplotlib.pyplot as plt


TESTS_DATA_PATH: str = "data/tests/"


def read_stats(filepath: str) -> dict:
    """
    Reads the statistics file and returns:
    data[percentage][quantity] = (time, distance)
    """

    data: dict[int, dict[int, tuple]] = {}
    current_percentage = None

    with open(filepath, "r") as f:
        for line in f:
            line: str = line.strip()

            if not line:
                continue

            # Percentage
            if line.endswith("%"):
                current_percentage = int(line[:-1])
                data[current_percentage] = {}

            # Quantity
            else:
                qtt_str, values_str = line.split(":")
                qtt: int = int(qtt_str.strip())

                time_str, dist_str = values_str.strip().split()
                time: float     = float(time_str)
                distance: float = float(dist_str)

                data[current_percentage][qtt] = (time, distance)

    return data


def plot_method_stats(stats: dict, value_index: int, ylabel, title: str) -> None:
    
    if value_index < 0 or value_index > 1:
        raise ValueError("Invalid Value Index")

    bar_colors = [ "#C8E6C9", "#81C784", "#4CAF50", "#388E3C", "#1B5E20" ]
    n_colors = len(bar_colors)

    percentages = sorted(stats.keys())
    quantities  = sorted(next(iter(stats.values())).keys())

    x = np.arange(len(percentages))
    bar_width = 0.8 / len(quantities)

    plt.figure()

    for i, q in enumerate(quantities):
        values = [stats[p][q][value_index] for p in percentages]
        plt.bar(x + i * bar_width, values, width=bar_width, label=f"$\mathcal{{Q}}_{{CS}}$ = {q}", 
                color=bar_colors[i % n_colors], edgecolor="black", alpha=0.9)

    plt.xticks(
        x + bar_width * (len(quantities) - 1) / 2,
        [f"{p}%" for p in percentages]
    )

    if value_index == 0:    # time graphs
        plt.ylim(0, 300)
    else:                   # distance graphs
        plt.ylim(0, 2800)

    plt.xlabel("Porcentagem de EV's (p%)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(
        title = "Nº de Estações \nde Carregamento",
        loc = "upper right"
    )
    plt.tight_layout()
    plt.show()


def plot_method_times(stats: dict, method_name: str) -> None:
    plot_method_stats(stats, 0, "Tempo [s]", f"{method_name} - Tempo médio sem Estação de Carregamento")

def plot_method_distances(stats: dict, method_name: str) -> None:
    plot_method_stats(stats, 1, "Distância [m]", f"{method_name} - Distância média percorrida")



def get_general_average_time(list_stats: list[dict]) -> None:
    for method_stats in list_stats:
        ...



if __name__ == "__main__":
    import os
    stats_files: list[str] = [ file for file in os.listdir(TESTS_DATA_PATH) if file.endswith(".data") ]

    for filename in stats_files:
        filepath: str = os.path.join(TESTS_DATA_PATH, filename)
        print(f"Viewing file: {filepath}")

        stats: dict = read_stats((filepath)) # Reading stats data
 
        method_name: str = filename.split(".")[0].replace("_", " ").title()
        print(f"Method name: {method_name}")

        plot_method_times(stats, method_name)
        plot_method_distances(stats, method_name)