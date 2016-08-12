import numpy as np
from sklearn.neighbors import LSHForest
from timeit import default_timer as timer

def main():
    sample = np.array([[1.2, 2.3, 3.5]])
    library = np.array([[0, 1.0, 2.0], [1.0, 2.0, 3.5], [2.0, 2.0, 2.0],  [2.0, 2.0, 2.0], [1.0, 2.0, 3.5], [400, 1.0, 2.0]])

    start = timer()

    lshf = LSHForest(min_hash_match=1, n_candidates=6, n_neighbors=1)
    lshf.fit(sample)

    distances, indices = lshf.kneighbors(library)

    print(distances)
    print(indices)

    # print(sample)
    # print(library)

if __name__ == '__main__':
    main()
