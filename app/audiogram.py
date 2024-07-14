import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

COLOR_LEFT = 'blue'
COLOR_RIGHT = 'firebrick'
COLOR_BINAURAL = 'black'
LINE_WIDTH = 1.5
MARKER_SIZE = 12
NOT_HEARD_MARKER_SIZE = 25
MARKER_EDGE_WIDTH = LINE_WIDTH
SHIFT = 0.4
MARKER_LEFT = 'x'
MARKER_RIGHT = 'o'
MARKER_BINAURAL = 'x'
NOT_HEARD_MARKER = '|'
NOT_HEARD_LEFT_MARKER = '3'
NOT_HEARD_RIGHT_MARKER = '4'

HEADER_SIZE = 18
LABEL_FONT_SIZE = 12
LEGEND_FONT_SIZE = 12
TICK_FONT_SIZE = 10
TEXT_FONT_SIZE = 9

#TODO maybe add date as subtitle (subtitle is already implemented)

freq_levels = {125: 20, 250: 20, 500: 20, 1000: 20, 2000: 20, 4000: 20, 8000: 20}

def split_values(x_vals, values, target_values):
    heard = np.array([[i, int(v)] for i, v in zip(x_vals, values) if v != 'NH' and v != None]).T
    if len(heard) == 0:
        heard_i, heard_level = [], []
    else:
        heard_i, heard_level = heard

    not_heard = np.array([[i, t] for i, v, t in zip(x_vals, values, target_values) if v == 'NH' and v != None]).T
    if len(not_heard) == 0:
        not_heard_i, not_heard_level = [], []
    else:
        not_heard_i, not_heard_level = not_heard

    return np.array(heard_i, dtype=int), np.array(heard_level, dtype=int), np.array(not_heard_i, dtype=int), np.array(not_heard_level, dtype=int)

def filter_none(x_vals, values):
    filtered = np.array([[i, v] for i, v in zip(x_vals, values) if v not in (None, "NaN")]).T
    if len(filtered) == 0:
        return np.array([], dtype=int), np.array([], dtype=int)
    i_vals, v_vals = filtered
    return np.array(i_vals, dtype=int), np.array(v_vals, dtype=int)

def create_audiogram(freqs, left_values=None, right_values=None, binaural=False, name="audiogram.png", freq_levels=freq_levels, subtitle=None):
    print("Creating audiogram with frequencies:", freqs)
    print("Left ear values:", left_values)
    print("Right ear values:", right_values)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.axhspan(-10, 20, facecolor='lightgreen', alpha=0.2)
    ax.axhspan(20, 40, facecolor='lightskyblue', alpha=0.2)
    ax.axhspan(40, 70, facecolor='yellow', alpha=0.2)
    ax.axhspan(70, 90, facecolor='orange', alpha=0.2)
    ax.axhspan(90, 120, facecolor='red', alpha=0.2)

    t1 = ax.text(6.4, 5, 'Normalhörigkeit', ha='left', va='center', fontsize=TEXT_FONT_SIZE)
    t2 = ax.text(6.4, 30, 'Leichte\nSchwerhörigkeit', ha='left', va='center', fontsize=TEXT_FONT_SIZE)
    t3 = ax.text(6.4, 55, 'Mittlere\nSchwerhörigkeit', ha='left', va='center', fontsize=TEXT_FONT_SIZE)
    t4 = ax.text(6.4, 80, 'Schwere\nSchwerhörigkeit', ha='left', va='center', fontsize=TEXT_FONT_SIZE)
    t5 = ax.text(6.4, 105, 'Hochgradige\nSchwerhörigkeit', ha='left', va='center', fontsize=TEXT_FONT_SIZE)

    x_vals = range(len(freqs))
    target_values = np.array(list(freq_levels.values()))

    nan_freqs_left = [freq for i, freq in zip(left_values, freqs) if i == 'NaN']
    nan_freqs_right = [freq for i, freq in zip(right_values, freqs) if i == 'NaN']

    nan_text = ""

    if 'NH' in left_values or 'NH' in right_values:
        heard_i_left, heard_level_left, not_heard_i_left, not_heard_level_left = split_values(x_vals, left_values, target_values)
        heard_i_right, heard_level_right, not_heard_i_right, not_heard_level_right = split_values(x_vals, right_values, target_values)

        if binaural:
            ax.plot(x_vals, target_values, linestyle='-', color=COLOR_BINAURAL)
            ax.plot(heard_i_left, heard_level_left, marker=MARKER_BINAURAL, markersize=MARKER_SIZE, linestyle='None', color=COLOR_BINAURAL, label='gehört')
            ax.plot(not_heard_i_left, not_heard_level_left, marker=NOT_HEARD_MARKER, markersize=NOT_HEARD_MARKER_SIZE, linestyle='None', color=COLOR_BINAURAL, label='nicht gehört')
        else:
            ax.plot(x_vals, target_values, linestyle='-', color=COLOR_RIGHT)
            ax.plot(heard_i_right, heard_level_right, marker=MARKER_RIGHT, markersize=MARKER_SIZE, linestyle='None', linewidth=LINE_WIDTH, color=COLOR_RIGHT, markerfacecolor='none', markeredgewidth=MARKER_EDGE_WIDTH, label='rechts gehört')
            ax.plot(not_heard_i_right, not_heard_level_right, marker=NOT_HEARD_RIGHT_MARKER, markersize=NOT_HEARD_MARKER_SIZE, linestyle='None', linewidth=LINE_WIDTH, color=COLOR_RIGHT, markeredgewidth=MARKER_EDGE_WIDTH, label='rechts nicht gehört')
            ax.plot(x_vals, target_values+SHIFT, linestyle='-', color=COLOR_LEFT)
            ax.plot(heard_i_left, heard_level_left+SHIFT, marker=MARKER_LEFT, markersize=MARKER_SIZE, linestyle='None', linewidth=LINE_WIDTH, color=COLOR_LEFT, markeredgewidth=MARKER_EDGE_WIDTH, label='links gehört')
            ax.plot(not_heard_i_left, not_heard_level_left+SHIFT, marker=NOT_HEARD_LEFT_MARKER, markersize=NOT_HEARD_MARKER_SIZE, linestyle='None', linewidth=LINE_WIDTH, color=COLOR_LEFT, markeredgewidth=MARKER_EDGE_WIDTH, label='links nicht gehört')

    else:
        x_vals_left, left_values = filter_none(x_vals, left_values)
        x_vals_right, right_values = filter_none(x_vals, right_values)

        if binaural:
            ax.plot(x_vals_left, left_values, marker=MARKER_BINAURAL, markersize=MARKER_SIZE, linestyle='-', color=COLOR_BINAURAL, label='binaural')
        else:
            ax.plot(x_vals_right, right_values, marker=MARKER_RIGHT, markersize=MARKER_SIZE, linestyle='-', linewidth=LINE_WIDTH, color=COLOR_RIGHT, markeredgewidth=MARKER_EDGE_WIDTH, markerfacecolor='none', label='rechtes Ohr')
            ax.plot(x_vals_left, left_values+SHIFT, marker=MARKER_LEFT, markersize=MARKER_SIZE, linestyle='-', linewidth=LINE_WIDTH, color=COLOR_LEFT, markeredgewidth=MARKER_EDGE_WIDTH, label='linkes Ohr')

        if nan_freqs_left or nan_freqs_right:
            and_str = ""
            nan_text = "Bei folgenden Frequenzen konnte kein Wert ermittelt werden:\n"
            print(nan_freqs_left, nan_freqs_right)
            if nan_freqs_left:
                nan_text += f"links: {', '.join(map(str, nan_freqs_left))} "
                and_str = "und "
            if nan_freqs_right:
                nan_text += f"{and_str}rechts: {', '.join(map(str, nan_freqs_right))}"
            nan_t = ax.text(0.05, -0.2, nan_text, transform=ax.transAxes, fontsize=TEXT_FONT_SIZE, ha='left', va='top', bbox=dict(facecolor='None', edgecolor='None'))

    ax.invert_yaxis()
    if subtitle:
        title = fig.suptitle('Audiogramm', fontsize=HEADER_SIZE, y=1.02) 
        ax.set_title(subtitle, fontsize=LABEL_FONT_SIZE, pad=20)
    else:
        title = fig.suptitle('Audiogramm', fontsize=HEADER_SIZE) 
    ax.set_xlabel('Frequenzen (Hz)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylabel('Hörschwelle (dB HL)', fontsize=LABEL_FONT_SIZE)
    ax.set_ylim(120, -10)
    ax.set_xticks(range(len(freqs)))
    ax.set_xticklabels([f"{int(freq)}" for freq in freqs], fontsize=TICK_FONT_SIZE)
    ax.set_yticks(np.arange(0, 121, 10))
    ax.set_yticklabels(np.arange(0, 121, 10), fontsize=TICK_FONT_SIZE)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    lgd = ax.legend(loc='upper left', bbox_to_anchor=(1.15, 0.205), fontsize=LEGEND_FONT_SIZE, frameon=False, labelspacing=1)
    if nan_t:
        fig.savefig(name, bbox_extra_artists=(title, lgd, t1, t2, t3, t4, t5, nan_t), bbox_inches='tight')
    else:
        fig.savefig(name, bbox_extra_artists=(lgd, t1, t2, t3, t4, t5), bbox_inches='tight')
    plt.close(fig)

# if __name__ == '__main__':
#     freqs = [125, 250, 500, 1000, 2000, 4000, 8000]
#     left_values = [5, 15, 15, 20, 20, 0, 0]
#     right_values = [5, 15, 10, "NaN", 25, 15, 5]
#     create_audiogram(freqs, left_values, right_values, binaural=False, name="audiogram.png")
#     print("Audiogram created")
