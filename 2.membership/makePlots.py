
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from astropy.table import Table


def main(prob_cut=0.75, Plx_offset=0.029):
    """
    Make plots using the final probabilities in the "_probs.dat" files.
    """
    inputfiles = {
        "LYNGA14": "LYNGA14_match.dat", "NGC6192": "NGC6192_match.dat",
        "NGC6242": "NGC6242_match.dat", "LYNGA13": "LYNGA13_match.dat"}

    coords_pms = {}
    for fname, file in inputfiles.items():
        print("{:<20}: {}".format("\nFile", file))

        data_all = Table.read(
            file, format='ascii', fill_values=[('', '0'), ('nan', '0')])

        fname, fext = file.split('.')
        ff = fname + "_probs." + fext
        data = Table.read(ff, format='ascii', header_start=0)
        probs_mean = data['probs_mean']

        prob_cut = min(prob_cut, probs_mean.max())
        msk_memb = probs_mean >= prob_cut

        coords_pms[fname] = data_all[msk_memb]

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


if __name__ == '__main__':
    main()
