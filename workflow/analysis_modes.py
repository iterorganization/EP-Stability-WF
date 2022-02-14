# --------------------------------------------
# Analysis componenet for Python EP workflow
# --------------------------------------------


# NEEDED MODULES
import os
import imas
import sys
import pdb
import random
import copy
from pyal import ALEnv
from lxml import etree
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from datetime import datetime
from workflow.functions_wf import parameters_workflow
from imas import imasdef
import collections
from matplotlib.transforms import Bbox


def create_shot_dir(shot_nr, run_out):
    # SEPARATE FOLDERS FOR DIFFERENT RUNS/SHOTS
    # create new directory if none exists
    shot_dir = (os.path.join(os.getcwd(), f'workflow/Analysis/{shot_nr}_{run_out}'))
    shot_dir_check = os.path.isdir(shot_dir)
    if not shot_dir_check:
        os.makedirs(shot_dir)
        print(f'Shot + run folder: {shot_dir} was created')
    return shot_dir

# Directly from ligka output (nyquist array) (as saved in the IDS)


def get_nyq_from_mode(mode):
    nyq_m5 = mode.plasma.velocity_perturbed.coordinate1.coefficients_real
    return nyq_m5


def search_nyq(nyq):
    fnyq = {}
    # convert indices to fortran ordering for convenience (same as nyquist in LIGKA)
    for k in range(nyq.shape[0]):
        fnyq[k+1] = nyq[k]
    q_TAE = fnyq[2]
    r_TAE = fnyq[1]
    return q_TAE, r_TAE


def mode_analysis_ligka(val_plot, wf_param_folder):

    def fill_zdata_dict(ydict, sgrid, chigrid, mlist):
        zdata = np.zeros((sgrid.shape[0], chigrid.shape[0]))
        harm_data = np.zeros(sgrid.shape[0])
        nspos = len(sgrid)
        for mharm in mlist:
            harm_data[:] = ydict[mharm]
            for ispos in range(len(sgrid)):
                zdata[ispos, :] = zdata[ispos, :] + \
                    harm_data[ispos] * np.cos(mharm*chigrid[:])
        return zdata

    def plot_plane(r, z, data, ghost=False, add_boundary=False, sym=False, **kwargs):
        fig, ax = plt.subplots()
        if ghost:
            r = add_ghost(r, dim=1)
            z = add_ghost(z, dim=1)
            data = add_ghost(data, dim=1)
        im = ax.pcolormesh(r, z, data, **kwargs)
        if sym:
            im.set_clim(np.array([-1, 1])*np.max(np.abs(im.get_clim())))
        if add_boundary:
            ax.plot(r[0, :], z[0, :], 'k-')
        return fig, ax

    def pert_array_to_dict(ydata, mlist):
        out_dict = {}
        for mharm, mdata in zip(mlist, ydata):
            out_dict[mharm] = mdata
        return out_dict

    def add_ghost(array, dim=0):
        new_array = np.zeros(
            (array.shape[0]+(dim == 0), array.shape[1]+(dim == 1)))
        if dim == 0:
            new_array[:-1, :] = array[:, :]
            new_array[-1, :] = array[0, :]
        elif dim == 1:
            new_array[:, :-1] = array[:, :]
            new_array[:, -1] = array[:, 0]
        return new_array

    def data_structure(mhd_linear_in, val_plot, eq=None):
        if val_plot == 5:
            sgrid = np.linspace(0., 1., 256)
            chigrid = 2.0 * np.pi * np.arange(256)/256
            y = eq.time_slice[0].profiles_2d[0]
        fig, ax = plt.subplots()
        time_list = []
        freq_dict = collections.defaultdict(list)
        damp_dict = collections.defaultdict(list)
        radius_dict = collections.defaultdict(list)
        n_list = []
        m_list = []
        s_list = mhd_linear_in.time_slice[0].toroidal_mode[0].plasma.grid.dim1
        i = 0
        for itime, time_val in enumerate(mhd_linear_in.time):
            if val_plot == 6:
                n_list = []
                m_list = []
                freq_list = []
                damp_list = []
                r_TAE_list = []
                q_TAE_list = []

            if itime >= itbegin and itime <= itend:
                time_list.append(time_val)
                time_slice = mhd_linear_in.time_slice[itime]

                for imode, mode in enumerate(time_slice.toroidal_mode):
                    if mode.n_tor <= n_max and mode.n_tor >= n_min:
                        if mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
                            nyq_m5 = get_nyq_from_mode(mode)
                            nyq = nyq_m5[:, 0, 0]
                            q_TAE, r_TAE = search_nyq(nyq)
                            freq = mode.frequency
                            damp = mode.growthrate
                            if r_TAE >= s_min and r_TAE <= s_max:
                                if val_plot == 6:
                                    n_list.append(mode.n_tor)
                                    m_list.append(mode.m_pol_dominant)
                                    freq_list.append(freq)
                                    damp_list.append(damp)
                                    r_TAE_list.append(r_TAE)
                                    q_TAE_list.append(q_TAE)
                                else:
                                    if val_plot == 1 or val_plot == 2 or val_plot == 3:
                                        if mode.n_tor not in n_list:
                                            n_list.append(mode.n_tor)
                                        if mode.m_pol_dominant not in m_list:
                                            m_list.append(
                                                int(mode.m_pol_dominant))

                                    if val_plot == 1:
                                        if (mode.n_tor, int(mode.m_pol_dominant)) not in freq_dict:
                                            freq_dict[(mode.n_tor, int(mode.m_pol_dominant))] = [
                                                None] * (itend - itbegin + 1)
                                            freq_dict[(mode.n_tor, int(
                                                mode.m_pol_dominant))][i] = freq
                                        else:
                                            freq_dict[(mode.n_tor, int(
                                                mode.m_pol_dominant))][i] = freq

                                    if val_plot == 2:
                                        if (mode.n_tor, int(mode.m_pol_dominant)) not in damp_dict:
                                            damp_dict[(mode.n_tor, int(mode.m_pol_dominant))] = [
                                                None] * (itend - itbegin + 1)
                                            damp_dict[(mode.n_tor, int(
                                                mode.m_pol_dominant))][i] = damp
                                        else:
                                            damp_dict[(mode.n_tor, int(
                                                mode.m_pol_dominant))][i] = damp

                                    if val_plot == 3:
                                        if (mode.n_tor, int(mode.m_pol_dominant)) not in radius_dict:
                                            radius_dict[(mode.n_tor, int(mode.m_pol_dominant))] = [
                                                None] * (itend - itbegin + 1)
                                            radius_dict[(mode.n_tor, int(
                                                mode.m_pol_dominant))][i] = r_TAE
                                        else:
                                            radius_dict[(mode.n_tor, int(
                                                mode.m_pol_dominant))][i] = r_TAE

                                    if val_plot == 5:
                                        freq_m1_r = mode.plasma.phi_potential_perturbed.real
                                        freq_m1_i = mode.plasma.phi_potential_perturbed.imaginary
                                        freq_m1 = freq_m1_r + 1j * freq_m1_i
                                        mlist = [int(i)
                                                 for i in mode.plasma.grid.dim2]
                                        out_gauss = pert_array_to_dict(
                                            freq_m1.T, mlist)
                                        ax.clear()

                                        zdata = fill_zdata_dict(
                                            out_gauss, sgrid, chigrid, mlist)
                                        fig, ax = plot_plane(
                                            y.r, y.z, zdata, ghost=True, sym=True, add_boundary=True, cmap='RdBu_r')
                                        ax.set_aspect(1.0)
                                        ax.set_xlabel('R [m]')
                                        ax.set_ylabel('Z [m]')
                                        ax.set_title(r'$\Phi$ perturbation')
                                        plot_filename = os.path.join(shot_dir,
                                            f'{shot_nr}_{run_out}_n_{mode.n_tor}_m_{mode.m_pol_dominant}_t_{time_val}_2D_structure.png')
                                        fig.savefig(plot_filename)

                                    if val_plot == 4:
                                        poloidals = []
                                        potential = mode.plasma.phi_potential_perturbed.real
                                        m_list = mode.plasma.grid.dim2
                                        if len(potential) != 0:
                                            for k in m_list:
                                                poloidals.append(f'm = {int(k)}')
                                            ax.clear()
                                            ax.plot(s_list, potential)
                                            plot_title = f'Mode Structure for n = {mode.n_tor} m = {mode.m_pol_dominant} time = {time_val}'
                                            ax.set(xlabel='s', ylabel='Electrostatic Potential', title=plot_title)
                                            ax.grid()
                                            plt.legend(poloidals)
                                            plot_filename = os.path.join(shot_dir,
                                                f'{shot_nr}_{run_out}_n_{mode.n_tor}_m_{mode.m_pol_dominant}_t_{time_val}_structure.png')
                                            fig.savefig(plot_filename)

                if val_plot == 6:
                    a = np.empty(len(r_TAE_list))
                    a.fill(time_val)
                    r_TAE_list_arr = np.array(r_TAE_list)
                    plt.scatter(a, r_TAE_list_arr, c=np.array(
                        n_list), s=len(n_list), alpha=1, cmap='viridis')

                i = i + 1

        if val_plot == 6:
            clb = plt.colorbar()
            clb.ax.set_ylabel('Toroidal Mode Number')
            ax.set(xlabel='Time [s]', ylabel='Radial Position')
            plt.show()

        # FREQUENCY
        if val_plot == 1:
            lines = []
            lined = {}  # Will map legend lines to original lines.
            for i in n_list:
                for j in m_list:
                    if len(freq_dict[(i, j)]) != 0:
                        line, = ax.plot(time_list, freq_dict[(
                            i, j)], lw=2, label=f'n = {i} m = {j}')
                        lines.append(line)

            leg = ax.legend(fancybox=True, shadow=True, loc='upper left',
                            bbox_to_anchor=(1, 1), borderaxespad=0.)
            for legline, origline in zip(leg.get_lines(), lines):
                legline.set_picker(True)  # Enable picking on the legend line.
                lined[legline] = origline

            # pixels to scroll per mousewheel event
            d = {"down": 30, "up": -30}

            def func(evt):
                if leg.contains(evt):
                    bbox = leg.get_bbox_to_anchor()
                    bbox = Bbox.from_bounds(
                        bbox.x0, bbox.y0+d[evt.button], bbox.width, bbox.height)
                    tr = leg.axes.transAxes.inverted()
                    leg.set_bbox_to_anchor(bbox.transformed(tr))
                    fig.canvas.draw_idle()

            def on_pick(event):
                # On the pick event, find the original line corresponding to the legend
                # proxy line, and toggle its visibility.
                legline = event.artist
                origline = lined[legline]
                visible = not origline.get_visible()
                origline.set_visible(visible)
                # Change the alpha on the line in the legend so we can see what lines
                # have been toggled.
                legline.set_alpha(1.0 if visible else 0.2)
                fig.canvas.draw()

            ax.set(xlabel='Time [s]', ylabel='Mode Frequency [Hz]')
            fig.canvas.mpl_connect("scroll_event", func)
            fig.canvas.mpl_connect('pick_event', on_pick)
            plt.subplots_adjust(right=0.8)
            plt.show()

        # DAMPING
        if val_plot == 2:
            lines = []
            lined = {}  # Will map legend lines to original lines.
            for i in n_list:
                for j in m_list:
                    if len(damp_dict[(i, j)]) != 0:
                        line, = ax.plot(time_list, damp_dict[(
                            i, j)], lw=2, label=f'n = {i} m = {j}')
                        lines.append(line)
            leg = ax.legend(fancybox=True, shadow=True, loc='upper left',
                            bbox_to_anchor=(1, 1), borderaxespad=0.)
            for legline, origline in zip(leg.get_lines(), lines):
                legline.set_picker(True)  # Enable picking on the legend line.
                lined[legline] = origline

            # pixels to scroll per mousewheel event
            d = {"down": 30, "up": -30}

            def func(evt):
                if leg.contains(evt):
                    bbox = leg.get_bbox_to_anchor()
                    bbox = Bbox.from_bounds(
                        bbox.x0, bbox.y0+d[evt.button], bbox.width, bbox.height)
                    tr = leg.axes.transAxes.inverted()
                    leg.set_bbox_to_anchor(bbox.transformed(tr))
                    fig.canvas.draw_idle()

            def on_pick(event):
                # On the pick event, find the original line corresponding to the legend
                # proxy line, and toggle its visibility.
                legline = event.artist
                origline = lined[legline]
                visible = not origline.get_visible()
                origline.set_visible(visible)
                # Change the alpha on the line in the legend so we can see what lines
                # have been toggled.
                legline.set_alpha(1.0 if visible else 0.2)
                fig.canvas.draw()

            ax.set(xlabel='Time [s]', ylabel='Mode Damping Rate [Hz]')
            fig.canvas.mpl_connect("scroll_event", func)
            fig.canvas.mpl_connect('pick_event', on_pick)
            plt.subplots_adjust(right=0.8)
            plt.show()

        # RADIAL POSITION
        if val_plot == 3:
            lines = []
            lined = {}  # Will map legend lines to original lines.
            for i in n_list:
                for j in m_list:
                    if len(radius_dict[(i, j)]) != 0:
                        line, = ax.plot(time_list, radius_dict[(
                            i, j)], lw=2, label=f'n = {i} m = {j}')
                        lines.append(line)
            leg = ax.legend(fancybox=True, shadow=True, loc='upper left',
                            bbox_to_anchor=(1, 1), borderaxespad=0.)
            for legline, origline in zip(leg.get_lines(), lines):
                legline.set_picker(True)  # Enable picking on the legend line.
                lined[legline] = origline

            # pixels to scroll per mousewheel event
            d = {"down": 30, "up": -30}

            def func(evt):
                if leg.contains(evt):
                    bbox = leg.get_bbox_to_anchor()
                    bbox = Bbox.from_bounds(
                        bbox.x0, bbox.y0+d[evt.button], bbox.width, bbox.height)
                    tr = leg.axes.transAxes.inverted()
                    leg.set_bbox_to_anchor(bbox.transformed(tr))
                    fig.canvas.draw_idle()

            def on_pick(event):
                # On the pick event, find the original line corresponding to the legend
                # proxy line, and toggle its visibility.
                legline = event.artist
                origline = lined[legline]
                visible = not origline.get_visible()
                origline.set_visible(visible)
                # Change the alpha on the line in the legend so we can see what lines
                # have been toggled.
                legline.set_alpha(1.0 if visible else 0.2)
                fig.canvas.draw()

            ax.set(xlabel='Time [s]', ylabel='Mode Radial Position [Hz]')
            fig.canvas.mpl_connect("scroll_event", func)
            fig.canvas.mpl_connect('pick_event', on_pick)
            plt.subplots_adjust(right=0.8)
            plt.show()
        return 0

    param = parameters_workflow(wf_param_folder+'/analysis.xml')

    user = param['user']
    version = os.getenv('IMAS_VERSION')[0]
    shot_nr = param['shot_number']
    run_out = param['run']
    machine_out = param['machine']
    n_min = param['n_min']
    n_max = param['n_max']
    s_min = param['r_TAE_min']
    s_max = param['r_TAE_max']
    m_min = param['m_min']
    m_max = param['m_max']
    itbegin = param['itbegin']
    itend = param['itend']
    mode = param['mode']

    # Select which LIGKA MODE to plot:
    if mode == 1:
        occurence = 2
    elif mode == 4:
        occurence = 1
    else:
        occurence = 0

    np.set_printoptions(threshold=sys.maxsize)

    # GET MHD_LINEAR/EQUILIBRIUM DATA
    input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,
                         machine_out, shot_nr, run_out, user)
    status, _ = input.open()
    if status != 0:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)
    shot_dir = create_shot_dir(shot_nr, run_out)
    if param['compare_modes'] == 0:
       # if compare_modes is not selected, only one mode (5, 4 or 1)
        mhd_linear_in = input.get("mhd_linear", occurrence=occurence)
        if val_plot == 5:
            equilibrium_in = input.get("equilibrium", occurrence=0)
            data_structure(mhd_linear_in, val_plot, eq=equilibrium_in)
        else:
            data_structure(mhd_linear_in, val_plot)
        print('Done, check the results.')

    # TO BE ADDED COMPARISON BETWEEN DIFFERENT MODES (mode 5/4/1 LIGKA)
    # else:
    #   # load all data (3 IDSs) (this might take a while to complete)
    #   mhd_linear_in_5 = input.get("mhd_linear",occurrence=0)
    #   data_structure(mhd_linear_in_5)
    #   mhd_linear_in_4 = input.get("mhd_linear",occurrence=1)
    #   data_4, time_list_4, mode_10 = data_structure(mhd_linear_in_4)
    #   mhd_linear_in_1 = input.get("mhd_linear",occurrence=2)
    #   data_1, time_list_1,mode_10 = data_structure(mhd_linear_in_1)


def export_data(wf_param_folder):
    param = parameters_workflow(os.path.join(wf_param_folder, 'analysis.xml'))

    user = param['user']
    version = os.getenv('IMAS_VERSION')[0]
    shot_nr = param['shot_number']
    run_out = param['run']
    machine_out = param['machine']
    n_min = param['n_min']
    n_max = param['n_max']
    s_min = param['r_TAE_min']
    s_max = param['r_TAE_max']
    m_min = param['m_min']
    m_max = param['m_max']
    itbegin = param['itbegin']
    itend = param['itend']
    mode = param['mode']

    if mode == 1:
        occurence = 2
    elif mode == 4:
        occurence = 1
    else:
        occurence = 0

    shot_dir = create_shot_dir(shot_nr, run_out)
    now = datetime.now()
    date_time = now.strftime("%m%d%Y_%H_%M_%S")
    filename = os.path.join(shot_dir, f"exported_{shot_nr}_{run_out}_{date_time}.txt")

    with open(filename, 'w+') as out_file:
        out_file.write(f"{user} {shot_nr} {run_out} {machine_out} {occurence}\n")

        input = imas.DBEntry(imasdef.MDSPLUS_BACKEND,
                             machine_out, shot_nr, run_out, user)
        status, _ = input.open()
        if status != 0:
            print("Can't open the selected dataset!", file=sys.stderr)
            sys.exit(1)

        mhd_linear_in = input.get("mhd_linear", occurrence=occurence)

        for itime, time_val in enumerate(mhd_linear_in.time):
            if itime >= itbegin and itime <= itend:
                time_slice = mhd_linear_in.time_slice[itime]
                for imode, mode in enumerate(time_slice.toroidal_mode):
                    if mode.n_tor <= n_max and mode.n_tor >= n_min:
                        if mode.m_pol_dominant >= m_min and mode.m_pol_dominant <= m_max:
                            nyq_m5 = get_nyq_from_mode(mode)
                            nyq = nyq_m5[:, 0, 0]
                            q_TAE, r_TAE = search_nyq(nyq)
                            if r_TAE >= s_min and r_TAE <= s_max:
                                out_file.write(f'{time_val} {itime} ')
                                out_file.write(" ".join(map(str, nyq))+"\n")

    # TODO: CHECK THE FORMATTING OF THE FILE BEING SAVED
    print('Done, data is saved in '+str(filename))
