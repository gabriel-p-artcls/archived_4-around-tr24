
import numpy as np
from scipy.spatial import distance
from sklearn.decomposition import PCA
import sklearn.cluster as skclust
from pathlib import Path
from astropy.io import ascii
from astropy.table import Table


# Fixed parameters
input_folder = "../1.cat_match/output/"
id_col = "ID"
data_cols = ("pmRA", "pmDE", "Plx")
err_cols = ("e_pmRA", "e_pmDE", "e_Plx")
PCAdims = 3
perc_cut = 75
min_samples_rng = (10, 60, 2)
Nruns = 10


def main():
    """
    """
    # Process all files
    inputfiles = readFiles(input_folder, "_match.dat")

    for file_path in inputfiles:
        print("{:<20}: {}".format("\nFile", file_path.parts[-1]))

        data_all = Table.read(
            file_path, format='ascii', fill_values=[('', '0'), ('nan', '0')])
        N_d = len(data_all)
        print("{:<20}: {}".format("Stars read", N_d))
        # Remove stars with no valid data
        try:
            msk_accpt = np.logical_and.reduce([
                ~data_all[_].mask for _ in data_cols])
            data = data_all[msk_accpt]
            print("{:<20}: {}".format("Stars removed", N_d - len(data)))
        except AttributeError:
            # No masked columns
            msk_accpt = np.array([True for _ in range(N_d)])
            data = data_all
            pass

        data_err = data[err_cols]
        data_c = data[data_cols]

        probs_dict = {"ID": data_all[id_col]}
        for min_samples in np.arange(
                min_samples_rng[0], min_samples_rng[1], min_samples_rng[2]):
            print(min_samples)

            probs_all = []
            for _ in range(Nruns):

                # Resample
                data_arr = np.array([data_c[_] for _ in data_c.columns]).T
                e_data_arr = np.array([
                    data_err[_] for _ in data_err.columns]).T
                data_arr = reSampleData(data_arr, e_data_arr)
                data_pca = dimReduc(data_arr, PCAdims)

                model_OPTIC = clusterMethod(data_pca, min_samples)
                reachability = model_OPTIC.reachability_[model_OPTIC.ordering_]
                # labels = model_OPTIC.labels_[model_OPTIC.ordering_]

                # Auto eps selection
                eps = findEps(data_pca, model_OPTIC, reachability, perc_cut)

                # DBSCAN labels
                labels_dbs = skclust.cluster_optics_dbscan(
                    reachability=model_OPTIC.reachability_,
                    core_distances=model_OPTIC.core_distances_,
                    ordering=model_OPTIC.ordering_, eps=eps)

                msk_memb = labels_dbs != -1
                probs = np.zeros(N_d)
                j = 0
                for i, st_f in enumerate(msk_accpt):
                    if st_f:
                        if msk_memb[j]:
                            probs[i] = 1
                        j += 1
                probs_all.append(probs)

            probs_dict[str(min_samples)] = np.mean(probs_all, 0)

        # Write to file
        fname = file_path.parts[-1].replace("_match.dat", "_probs.dat")
        ascii.write(probs_dict, fname, overwrite=True)


def findEps(data, model_OPTIC, reachability, perc_cut):
    """
    Finding eps manually:
    https://towardsdatascience.com/
    machine-learning-clustering-dbscan-determine-the-optimal-value-for-
    epsilon-eps-python-example-3100091cfbc

    Another method described in:
    Amin Karami and Ronnie Johansson. Choosing dbscan parameters
    automatically using differential evolution. International Journal
    of Computer Applications, 91(7), 2014
    """
    step = 0.005

    # Select the center of the cluster using the 1th percentile of stars
    eps_min = np.percentile(reachability, 1)
    labels_dbs = skclust.cluster_optics_dbscan(
        reachability=model_OPTIC.reachability_,
        core_distances=model_OPTIC.core_distances_,
        ordering=model_OPTIC.ordering_, eps=eps_min)
    msk = labels_dbs != -1
    center = data[msk].mean(0)

    eps_final = reachability.max()
    for eps in np.arange(
            reachability.min() + step, np.percentile(reachability, 95), step):

        labels_dbs = skclust.cluster_optics_dbscan(
            reachability=model_OPTIC.reachability_,
            core_distances=model_OPTIC.core_distances_,
            ordering=model_OPTIC.ordering_, eps=eps)

        # Distance from estimated members to center
        dist_c = distance.cdist(np.array([center]), data[labels_dbs != -1])

        # Breaking condition
        if eps < dist_c.max() - np.percentile(dist_c, perc_cut):
            eps_final = eps
            break

    return eps_final


def clusterMethod(data, min_samples):
    """
    """
    # import hdbscan
    # model_HDBSCAN = hdbscan.HDBSCAN(allow_single_cluster=True)
    # model_HDBSCAN.fit(data)

    model_OPTIC = skclust.OPTICS(min_samples=min_samples)
    # Fit the model
    model_OPTIC.fit(data)
    # labels = model.labels_

    return model_OPTIC


def dimReduc(data, PCAdims=2):
    """
    Perform PCA and feature reduction
    """
    pca = PCA(n_components=PCAdims)
    data_pca = pca.fit(data).transform(data)
    # print("Selected N={} PCA features".format(PCAdims))
    # var_r = ["{:.2f}".format(_) for _ in pca.explained_variance_ratio_]
    # print(" Variance ratio: ", ", ".join(var_r))

    return data_pca


def reSampleData(data, data_err):
    """
    Re-sample the data given its uncertainties using a normal distribution
    """
    # Gaussian random sample
    grs = np.random.normal(0., 1., data.shape[0])
    sampled_data = data + grs[:, np.newaxis] * data_err

    return sampled_data


def readFiles(path_fold, yes_end, not_end="no_match.dat"):
    """
    Read files from the input folder
    """
    files = []
    for pp in Path(path_fold).iterdir():
        if pp.is_file() and str(pp).endswith(yes_end) and not\
                str(pp).endswith(not_end):
            files += [pp]

    return files


if __name__ == '__main__':
    main()
