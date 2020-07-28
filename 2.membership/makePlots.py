
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from astropy.table import Table
from clustering import input_folder, readFiles


def main(Plx_offset=0.029, prob_cut=0.5):
    """
    Make plots using the final probabilities in the "_probs.dat" files.
    """
    inputfiles = readFiles(input_folder, "_match.dat")

    coords_pms = {}
    for file_path in inputfiles:
        print("{:<20}: {}".format("\nFile", file_path.parts[-1]))

        data_all = Table.read(
            file_path, format='ascii', fill_values=[('', '0'), ('nan', '0')])

        ff = file_path.parts[-1].replace("_match", "_probs")
        data = Table.read(ff, format='ascii', header_start=0)

        N_cols = list(data.columns)
        N_cols.remove('ID')
        probs_all = np.array([data[_].data for _ in N_cols])

        probs_mean = probs_all.mean(0)
        prob_cut = min(prob_cut, probs_mean.max())
        msk_memb = probs_mean >= prob_cut

        fname = file_path.parts[-1].replace("_match.dat", "")

        coords_pms[fname] = data_all[msk_memb]

        # makeSinglePlot(
        #     prob_cut, Plx_offset, data_all, probs_mean, msk_memb, fname)

    makeCombPlot(coords_pms, Plx_offset, prob_cut)


def makeCombPlot(coords_pms, Plx_offset, prob_cut):
    """
    """
    fig = plt.figure(figsize=(15, 15))
    G = gridspec.GridSpec(2, 2)
    plt.suptitle("Members selection: P>={:.2f}".format(prob_cut), y=1.02)

    ax1 = plt.subplot(G[0, 0])
    colors = ('r', 'b', 'g', 'purple')
    pos = {
        "LYNGA14": (.2, .1), "LYNGA13": (.4, .4), "NGC6242": (.17, .9),
        "NGC6192": (.78, .28)}
    for i, (cl_name, cl_data) in enumerate(coords_pms.items()):
        # print(cl_name,
        #     (cl_data['pmRA'] / np.cos(np.deg2rad(cl_data['pmDE']))).mean(),
        #     cl_data['pmDE'].mean())
        ax1.quiver(
            cl_data['RA_ICRS'], cl_data['DE_ICRS'],
            cl_data['pmRA'] / np.cos(np.deg2rad(cl_data['pmDE'])),
            cl_data['pmDE'], angles='xy', units='xy', width=.02,
            linewidth=.5, edgecolors='w', alpha=.7,
            label=cl_name, color=colors[i])

        pmRA_mean = (
            cl_data['pmRA'] / np.cos(np.deg2rad(cl_data['pmDE']))).mean()
        pmDE_mean = cl_data['pmDE'].mean()
        plt.text(*pos[cl_name], "~({:.3f}, {:.3f})".format(
            pmRA_mean, pmDE_mean), transform=ax1.transAxes)

    # TRUMPLER 24
    plt.scatter(254.25, -40.6666, marker='x', c='k', s=100, label='TRUMPLER24')
    ax1.set_xlabel('RA')
    ax1.set_ylabel('DE')
    plt.gca().invert_xaxis()
    plt.legend()

    ax2 = plt.subplot(G[0, 1])
    ax2.set_title("Plx offset: +{}".format(Plx_offset))
    colors = ('r', 'b', 'g', 'purple')
    pos = {
        "LYNGA14": (.5, .6), "LYNGA13": (.85, .2), "NGC6242": (.3, .75),
        "NGC6192": (.18, .9)}
    for i, (cl_name, cl_data) in enumerate(coords_pms.items()):
        ax2.scatter(
            cl_data['pmRA'], cl_data['pmDE'], alpha=.5,
            edgecolors='w', label=cl_name, color=colors[i])
        dist = 1000. / (Plx_offset + cl_data['Plx']).mean()
        plt.text(*pos[cl_name], "~{:.0f} [pc]".format(dist),
                 transform=ax2.transAxes)
    ax2.set_xlabel(r'$\mu_{\alpha} \cos \delta$ [mas/yr]')
    ax2.set_ylabel(r'$\mu_{\delta}$ [mas/yr]')
    plt.gca().invert_xaxis()
    plt.legend()

    # plt.show()
    file_out = "combined.png"
    fig.tight_layout()
    plt.savefig(file_out, dpi=150, bbox_inches='tight')
    plt.close()


def makeSinglePlot(
    prob_cut, Plx_offset, data_all, probs_mean, msk_memb,
        fname):
    """
    """
    fig = plt.figure(figsize=(15, 10))
    G = gridspec.GridSpec(4, 3)
    ax1 = plt.subplot(G[0:2, 0])
    ax21 = plt.subplot(G[0:1, 1])
    ax22 = plt.subplot(G[1:2, 1])
    ax3 = plt.subplot(G[0:2, 2])
    ax4 = plt.subplot(G[2:4, 0])
    ax5 = plt.subplot(G[2:4, 1])
    ax6 = plt.subplot(G[2:4, 2])

    data_all['Plx'] += Plx_offset

    # # Reachability plot
    # space = np.arange(len(data))
    # msk = reachability < eps
    # ax1.plot(space[~msk], reachability[~msk], 'k.', alpha=0.3)
    # ax1.plot(space[msk], reachability[msk], 'g.')
    # ax1.axhline(eps, c='k', ls='-.', label="eps={:.3f}".format(eps))
    # ax1.set_ylabel('Reachability (epsilon distance)')
    # ax1.set_title('Reachability Plot (min_samples={})'.format(
    #     min_samples))
    # ymin, ymax = max(0, eps - eps * .5), min(3. * eps, max(reachability))
    # ax1.set_xlim(0, max(space[reachability < ymax]))
    # ax1.set_ylim(ymin, ymax)
    # ax1.legend()

    ax1.hist(probs_mean, alpha=.5)
    ax1.axvline(prob_cut, c='g', zorder=6)
    ax12 = ax1.twinx()
    psum = np.cumsum(probs_mean)
    xsum = np.linspace(probs_mean.min(), probs_mean.max(), psum.size)
    ax12.plot(xsum, psum, c='r', lw=3)
    ax12.set_yscale('log')
    ax12.set_yticks([])
    ax1.set_xlabel('Probabilities')
    ax1.set_ylabel(r'$\log (N)$')
    ax1.set_yscale('log')

    plx_prob, pmRA_prob, pmDE_prob = [], [], []
    for pp in np.arange(.05, .95, .01):
        msk = probs_mean >= pp
        plx_prob.append([
            pp, data_all['Plx'][msk].mean(), data_all['Plx'][msk].std()])
        pmRA_prob.append([
            pp, data_all['pmRA'][msk].mean(), data_all['pmRA'][msk].std()])
        pmDE_prob.append([
            pp, data_all['pmDE'][msk].mean(), data_all['pmDE'][msk].std()])

    plx_prob, pmRA_prob, pmDE_prob = [
        np.array(_).T for _ in (plx_prob, pmRA_prob, pmDE_prob)]

    ax21.plot(pmDE_prob[0], pmDE_prob[1], c='b', label='pmDE')
    ax21.fill_between(
        pmDE_prob[0], pmDE_prob[1] - pmDE_prob[2], pmDE_prob[1] + pmDE_prob[2],
        color='blue', alpha=0.1)
    ax21.axvline(prob_cut, c='g', zorder=6)
    ax21.set_xlabel(r'$P_{cut}$')
    ax21.set_ylabel(r'$\mu_{\delta}$ [mas/yr]')

    ax22.plot(pmRA_prob[0], pmRA_prob[1], c='r', label='pmRA')
    ax22.fill_between(
        pmRA_prob[0], pmRA_prob[1] - pmRA_prob[2], pmRA_prob[1] + pmRA_prob[2],
        color='red', alpha=0.1)
    ax22.axvline(prob_cut, c='g', zorder=6)
    ax22.set_ylabel(r'$\mu_{|alpha} \cos \delta$ [mas/yr]')
    ax22.set_xlabel(r'$P_{cut}$')

    ax3.plot(plx_prob[0], plx_prob[1])
    ax3.fill_between(
        plx_prob[0], plx_prob[1] - plx_prob[2], plx_prob[1] + plx_prob[2],
        color='k', alpha=0.1)
    ax3.axvline(prob_cut, c='g', zorder=6)
    ax3.set_ylabel(r'$Plx$')
    ax3.set_xlabel(r'$P_{cut}$')

    ax4.scatter(
        data_all['RA_ICRS'][msk_memb], data_all['DE_ICRS'][msk_memb],
        marker='o', edgecolor='w', lw=.3, zorder=5)
    ax4.plot(
        data_all['RA_ICRS'][~msk_memb],
        data_all['DE_ICRS'][~msk_memb], 'k.', alpha=0.3, zorder=1)
    ax4.set_xlabel('RA')
    ax4.set_ylabel('DE')
    ax4.set_xlim(max(data_all['RA_ICRS']), min(data_all['RA_ICRS']))
    ax4.set_ylim(min(data_all['DE_ICRS']), max(data_all['DE_ICRS']))

    # PMs plot
    pmRA_mean = (
        data_all['pmRA'][msk_memb] /
        np.cos(np.deg2rad(data_all['pmDE'][msk_memb]))).mean()
    pmDE_mean = data_all['pmDE'][msk_memb].mean()
    ax5.set_title(r"$(\mu_{\alpha}, \mu_{\delta})=$" +
                  "({:.3f}, {:.3f})".format(pmRA_mean, pmDE_mean))
    ax5.scatter(
        data_all['pmRA'][msk_memb], data_all['pmDE'][msk_memb], marker='.',
        edgecolor='w', lw=.1, alpha=.7, zorder=5)
    ax5.plot(
        data_all['pmRA'][~msk_memb], data_all['pmDE'][~msk_memb],
        'k+', alpha=0.3, zorder=1)
    ax5.set_xlabel(r'$\mu_{\alpha} \cos \delta$ [mas/yr]')
    ax5.set_ylabel(r'$\mu_{\delta}$ [mas/yr]')
    xmin, xmax = np.percentile(data_all['pmRA'][~msk_memb], (25, 75))
    ymin, ymax = np.percentile(data_all['pmDE'][~msk_memb], (25, 75))
    xclmin = data_all['pmRA'][msk_memb].mean() -\
        5. + data_all['pmRA'][msk_memb].std()
    xclmax = data_all['pmRA'][msk_memb].mean() +\
        5. + data_all['pmRA'][msk_memb].std()
    yclmin = data_all['pmDE'][msk_memb].mean() -\
        5. + data_all['pmDE'][msk_memb].std()
    yclmax = data_all['pmDE'][msk_memb].mean() +\
        5. + data_all['pmDE'][msk_memb].std()
    ax5.set_xlim(max(xmax, xclmax), min(xmin, xclmin))
    ax5.set_ylim(min(ymin, yclmin), max(ymax, yclmax))

    # Plxs plot
    ax6.set_title("Plx offset: +{}".format(Plx_offset))
    xmin = np.percentile(data_all['Plx'][msk_memb], 1) -\
        3. * data_all['Plx'][msk_memb].std()
    xmax = np.percentile(data_all['Plx'][msk_memb], 95) +\
        3. * data_all['Plx'][msk_memb].std()
    msk1 = np.logical_and.reduce([
        (data_all['Plx'] > -2), (data_all['Plx'] < 4), (msk_memb)])
    msk2 = np.logical_and.reduce([
        (data_all['Plx'] > -2), (data_all['Plx'] < 4), (~msk_memb)])
    ax6.hist(data_all['Plx'][msk1], 20, density=True, alpha=.7, zorder=5)
    ax6.hist(
        data_all['Plx'][msk2], 75, color='k', alpha=0.3, density=True,
        zorder=1)
    plx_mean = data_all['Plx'][msk_memb].mean()
    plx_16, plx_84 = np.percentile(data_all['Plx'][msk_memb], (16, 84))
    ax6.axvline(
        plx_mean, c='r',
        label=r"$Plx_{{mean}}={:.3f}_{{{:.3f}}}^{{{:.3f}}}$".format(
            plx_mean, plx_16, plx_84), zorder=6)
    ax6.axvline(plx_16, c='orange', ls='--', zorder=6)
    ax6.axvline(plx_84, c='orange', ls='--', zorder=6)
    ax6.set_xlabel('Plx')
    ax6.set_xlim(xmin, xmax)
    ax6.legend()

    # labels_hdb = model_HDBSCAN.labels_
    # for lab in range(0, model_HDBSCAN.labels_.max() + 1):
    #     Xk = data[labels_hdb == lab]
    #     ax4.scatter(Xk[:, 0], Xk[:, 1], alpha=0.3, marker='.')
    # ax4.plot(
    #     data[labels_hdb == -1, 0], data[labels_hdb == -1, 1], 'k+', alpha=0.1)

    # plt.show()
    file_out = fname + '.png'
    fig.tight_layout()
    plt.savefig(file_out, dpi=150, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    main()
