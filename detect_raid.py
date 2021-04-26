import math

from array import array

import mmap
import matplotlib.pyplot as plt
from matplotlib import rcParams


def entropy_from_bytes(bytes):
    entropy = 0.0
    probability = dict()
    for byte in bytes:
        if byte in probability:
            probability[byte] += 1
        else:
            probability[byte] = 1

    for prob in probability.values():
        if prob != 0.0:
            entropy -= (prob / len(bytes)) * math.log(prob / len(bytes), 2)
    return abs(entropy)


if __name__ == '__main__':
    stream_1 = open('resources/001.dd')
    stream_2 = open('resources/002.dd')
    stream_3 = open('resources/003.dd')

    mmaps = [
        mmap.mmap(stream_1.fileno(), 0, mmap.MAP_SHARED, mmap.ACCESS_READ),
        mmap.mmap(stream_2.fileno(), 0, mmap.MAP_SHARED, mmap.ACCESS_READ),
        mmap.mmap(stream_3.fileno(), 0, mmap.MAP_SHARED, mmap.ACCESS_READ)
    ]
    entropies = [
        [],
        [],
        []
    ]

    stop_loop = False

    while not stop_loop:
        for index, mmap in enumerate(mmaps):
            data = mmap.read(512 * 32)
            if len(data) == 0:
                stop_loop = True
                break
            entropy = entropy_from_bytes(data)
            # print(f"Entropy {entropy} for {index}")
            entropies[index].append(entropy)

    rcParams['figure.figsize'] = 25, 10
    fig, axs = plt.subplots(3)
    axs[0].scatter(range(len(entropies[0])), entropies[0], c="r", label="Entropy 1", linewidths=0.5)
    axs[1].scatter(range(len(entropies[1])), entropies[1], c="g", label="Entropy 2", linewidths=0.5)
    axs[2].scatter(range(len(entropies[2])), entropies[2], c="b", label="Entropy 3", linewidths=0.5)
    fig.show()
    #
    # rcParams['figure.figsize'] = 25, 10
    # plt.scatter(range(len(entropies[0])), entropies[0], c="r", label="Entropy 1", markersize=0.5)
    # plt.scatter(range(len(entropies[1])), entropies[1], c="g", label="Entropy 2", linewidths=0.5)
    # plt.scatter(range(len(entropies[2])), entropies[2], c="b", label="Entropy 3", linewidths=0.5)
    # plt.show()

    stream_1.close()
    stream_2.close()
    stream_3.close()
