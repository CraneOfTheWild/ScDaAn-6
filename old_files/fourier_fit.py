import data_visualizers as dv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

FILENAME = "data/file.csv"
DATE_COLUMN_NAME = "Transaction_Date"
CATEGORY_COLUMN_NAME = "Product_Category"
FOURIER_COMPONENTS = 30


def rolling_average(nr_days):
    # read in the data
    df = pd.read_csv(FILENAME, parse_dates=[DATE_COLUMN_NAME])
    # aggregate by date
    df_per_day = pd.crosstab(df[DATE_COLUMN_NAME].dt.date,
                             df[CATEGORY_COLUMN_NAME])
    # sort for certainty
    df_per_day = df_per_day.sort_index()
    # get roling average
    df_rolling_avg = df_per_day.rolling(window=nr_days,
                                        center=True,
                                        min_periods=1).mean()
    df_rolling_avg = df_rolling_avg.dropna()
    # plotting
    df_rolling_avg.plot.line(ax=plt.gca())
    plt.xlabel("Date")
    plt.ylabel("Sales_Number")
    plt.title(f"roling average of sales for surrounding {nr_days} days")
    plt.show()


def fourier_fit(nr_days=1):
    # read in the data
    df = pd.read_csv(FILENAME, parse_dates=[DATE_COLUMN_NAME])
    # aggregate by date
    df_per_day = pd.crosstab(df[DATE_COLUMN_NAME].dt.date,
                             df[CATEGORY_COLUMN_NAME])
    # sort for certainty
    df_per_day = df_per_day.sort_index()
    # get roling average
    df_rolling_avg = df_per_day.rolling(window=nr_days,
                                        center=True,
                                        min_periods=1).mean()
    df_rolling_avg = df_rolling_avg.dropna()
    # convert to numpy for use of np.fft
    column_names = df_rolling_avg.columns.tolist()
    data = df_rolling_avg.to_numpy()

    big_fig, figs = plt.subplots(4, 4)
    # save the fourier analysis values
    true_fourier_values = []
    for x in range(4):
        for y in range(4):
            index = x + 4 * y
            # make a fourier fit
            fft_analysis = np.fft.fft(data.T[index])
            true_fourier_values.append(fft_analysis)
            fft_analysis_truncated = np.zeros_like(fft_analysis)
            fft_analysis_truncated[:FOURIER_COMPONENTS] = fft_analysis[:FOURIER_COMPONENTS]
            reconstructed_data = np.fft.ifft(fft_analysis_truncated).real
            figs[x, y].plot(df_rolling_avg.index, data.T[index],
                            label="Original Rolling Average")
            figs[x, y].plot(df_rolling_avg.index, reconstructed_data,
                            label='Fourier Fit', linestyle='--')
            figs[x, y].set_xlabel("Date")
            figs[x, y].set_ylabel("Sales Number")
            figs[x, y].set_title(column_names[index])
    big_fig.align_labels
    plt.tight_layout()
    big_fig.subplots_adjust(top=0.88, wspace=0.4, hspace=0.6)
    plt.legend()
    big_fig.suptitle(f"fourier analysis using {FOURIER_COMPONENTS} components on the rolling average of the {
        nr_days} days surrounding a date")
    plt.show()
    return np.array(true_fourier_values)


def complex_similarity(vec_0, vec_1):
    dot_product = np.dot(vec_0, vec_1)
    magnitude_0 = np.linalg.norm(vec_0)
    magnitude_1 = np.linalg.norm(vec_1)
    return np.real(dot_product) / (magnitude_0 * magnitude_1)


def similarity_matrix(array):
    nr_to_compare = len(array)
    matrix = np.zeros((nr_to_compare, nr_to_compare))
    for index_0 in range(nr_to_compare):
        for index_1 in range(index_0, nr_to_compare):
            if index_0 == index_1:
                similarity = 1.0
                matrix[index_0, index_1] = similarity
            else:
                similarity = complex_similarity(array[index_0], array[index_1])
                matrix[index_0, index_1] = similarity
                matrix[index_1, index_0] = similarity
    return matrix


fourier_vectors = fourier_fit(14)
similarity = similarity_matrix(fourier_vectors)

plt.imshow(similarity, cmap='gray')
plt.title("Cosine Similarity Matrix")
plt.show()
