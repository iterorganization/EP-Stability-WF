# --------------------------------------------
# Analysis componenet for Python EP workflow
# --------------------------------------------


# NEEDED MODULES
import os
import imas
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from ep_stability_wf.workflow.functions_wf import time_construction, parameters_workflow
from collections import defaultdict


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


def values_filler(backend_value, mode):
    # Select which LIGKA MODE to plot:
    if int(mode) == 1:
        occurence = 2
    elif int(mode) == 4:
        occurence = 1
    elif int(mode) == 5:
        occurence = 0
    else:
        occurence = 3
    if int(backend_value):
        return imas.imasdef.HDF5_BACKEND, occurence
    else:
        return imas.imasdef.MDSPLUS_BACKEND, occurence


def labelscaler(fig=None, axarr=None, labelsize=None, labelmult=None, linemult=None, fig_tight=None):
    """Function for rescaling labels and line sizes by T. Hayward-Schneider
    Usage:
        labelscaler(fig=fig, axarr=[ax], labelmult=2.0,linemult=2.0 fig_tight=True)
    """
    if type(axarr) != list:
        axarr = [axarr]
    for ax in axarr:
        if ax is None:
            continue
        if labelsize is not None:
            ax.xaxis.label.set_size(labelsize)
            ax.yaxis.label.set_size(labelsize)
        if labelmult is not None:
            for tk in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
                tk.set_fontsize(tk.get_fontsize()*labelmult)
        if linemult is not None:
            for line in ax.lines[:]:
                line.set_linewidth(line.get_linewidth()*linemult)
        if labelmult is not None:
            try:
                legend = ax.get_legend()
                for itk, tk in enumerate(legend.get_texts()):
                    tk.set_fontsize(tk.get_fontsize()*labelmult)
            except AttributeError:
                pass
    if fig_tight is not None and fig_tight is not False and fig is not None:
        fig.tight_layout()


def create_shot_dir(machine, shot_nr, run_out):
    # SEPARATE FOLDERS FOR DIFFERENT RUNS/SHOTS
    # create new directory if none exists
    shot_dir = (os.path.join(
        os.getcwd(), f'workflow/Analysis/{machine}/{shot_nr}_{run_out}'))
    shot_dir_check = os.path.isdir(shot_dir)
    if not shot_dir_check:
        os.makedirs(shot_dir)
        print(f'Shot + run folder: {shot_dir} was created')
    return shot_dir


def data_retrieve(backend_name, database_in, shot, run, user, ids_name, occurrence):
    """Method to retrieve data from the database

    Returns:
        [ids]: [ids specified in 'ids_name']
    """
    input = imas.DBEntry(backend_name,
                         database_in, int(shot), int(run), user)
    status, _ = input.open()
    if status != 0:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)

    return input.get(ids_name, occurrence=occurrence)


class Plot():
    def __init__(self, param):
        """Simple plot class.

        Args:
            database_in (str): Database where the data is located at
            shot (int): Shot number
            run (int): Run number
            user (str): Username of the user who has the DB
            occurrence (int): For WF users: mhd_linear: 0 -  mode 5, 1 - mode 4, 2 - mode 1. For equilibrium 0 in general.
            ids_name (str): mhd_linear or equilibrium (defined by dd_doc)
            backend_name (object, optional): Backends: HDF5 -> imas.imasdef.HDF5_BACKEND(1) as defined by AL. Defaults to imas.imasdef.MDSPLUS_BACKEND(0).
        """
        self.user = param['user']
        self.version = os.getenv('IMAS_VERSION')[0]
        self.shot = param['shot_number']
        self.run = param['run']
        self.database_in = param['machine']
        self.n_min = param['n_min']
        self.n_max = param['n_max']
        self.s_min = param['r_TAE_min']
        self.s_max = param['r_TAE_max']
        self.m_min = param['m_min']
        self.m_max = param['m_max']
        self.time_list, _ = time_construction(param['itime'])
        self.mode = param['mode']
        self.backend_name, self.occurrence = values_filler(
            param['backend_HDF5'], param['mode'])
        self.ids_name = param['ids_name']
        self.label_scaler = param['label_scaler']
        self.line_scaler = param['line_scaler']
        self.compare_modes = param['compare_modes']

    def EFs_plot(self):
        """Plotting mhd_linear_in EFs.

        Args:
            mhd_linear_in (ids): Input mhd_linear IDS
        """
        mhd_linear_in = data_retrieve(self.backend_name, self.database_in,
                                      self.shot, self.run, self.user, self.ids_name, self.occurrence)
        shot_dir = create_shot_dir(self.database_in, self.shot, self.run)
        EF_dir = f'{shot_dir}/EF_plots'
        if not os.path.exists(EF_dir):
            os.mkdir(EF_dir)

        for itime, time in enumerate(mhd_linear_in.time):
            if itime in self.time_list:
                for imode, mode in enumerate(mhd_linear_in.time_slice[itime].toroidal_mode):
                    fig, ax = plt.subplots()
                    n = mode.n_tor
                    m = mode.m_pol_dominant
                    m_list = mode.plasma.grid.dim2
                    r_list = mode.plasma.grid.dim1
                    freq = mode.frequency
                    if freq > 0 and self.n_min <= n <= self.n_max and self.m_min <= m <= self.m_max:

                        growth = mode.growthrate
                        phi_potential = mode.plasma.phi_potential_perturbed.real
                        r_TAE = mode.plasma.velocity_perturbed.coordinate1.coefficients_real[
                            0][0][0]
                        q_TAE = mode.plasma.velocity_perturbed.coordinate1.coefficients_real[
                            1][0][0]
                        print(
                            f'TIME: {itime} Mode number {imode} with n={n} and m={m} with frequency {freq} and growth {growth} at position {r_TAE} with {q_TAE}')
                        ax.plot(r_list, phi_potential)
                        ax.set(xlabel='S', ylabel='Electrostatic Potential')
                        m_list = [f'm = {int(x)}' for x in m_list]
                        ax.legend(m_list,  bbox_to_anchor=(
                            1.05, 1.0), loc='upper left')
                        labelscaler(fig=fig, axarr=[
                                    ax], labelmult=float(self.label_scaler), linemultiplier=float(self.line_scaler), fig_tight=True)
                        plt.savefig(
                            f'{EF_dir}/structure_mode_{self.mode}_time_{time:.2f}_mode_n_{n}_m_{m}.png')
                        print(f'Figure saved in {EF_dir} for time {time:.2f}')
        print('No more modes found! Finished!')

    def EFs_plot_2d(self):
        """Plotting mhd_linear_in EFs 2D.

        Args:
            mhd_linear_in (ids): Input mhd_linear IDS
            equilibrium (ids): Input equilibrium IDS
        """
        shot_dir = create_shot_dir(self.database_in, self.shot, self.run)
        EF_dir = f'{shot_dir}/EF_2d_plots'
        if not os.path.exists(EF_dir):
            os.mkdir(EF_dir)

        equilibrium_in = data_retrieve(self.backend_name, self.database_in,
                                       self.shot, self.run, self.user, 'equilibrium', 0)
        y = equilibrium_in.time_slice[0].profiles_2d[0]
        grid_size = len(y.r)
        sgrid = np.linspace(0., 1., grid_size)
        chigrid = 2.0 * np.pi * np.arange(grid_size)/grid_size

        mhd_linear_in = data_retrieve(self.backend_name, self.database_in,
                                      self.shot, self.run, self.user, self.ids_name, self.occurrence)

        for itime, time in enumerate(mhd_linear_in.time):
            if itime in self.time_list:
                for imode, mode in enumerate(mhd_linear_in.time_slice[itime].toroidal_mode):
                    fig, ax = plt.subplots()
                    n = mode.n_tor
                    m = mode.m_pol_dominant
                    growth = mode.growthrate
                    freq = mode.frequency
                    if freq > 0 and self.n_min <= n <= self.n_max and self.m_min <= m <= self.m_max:
                        freq_m1_r = mode.plasma.phi_potential_perturbed.real
                        freq_m1_i = mode.plasma.phi_potential_perturbed.imaginary
                        r_TAE = mode.plasma.velocity_perturbed.coordinate1.coefficients_real[
                            0][0][0]
                        q_TAE = mode.plasma.velocity_perturbed.coordinate1.coefficients_real[
                            1][0][0]
                        print(
                            f'TIME: {itime} Mode number {imode} with n={n} and m={m} with frequency {freq} and growth {growth} at position {r_TAE} with {q_TAE}')
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
                        labelscaler(fig=fig, axarr=[
                            ax], labelmult=float(self.label_scaler), linemultiplier=float(self.line_scaler), fig_tight=True)
                        plt.savefig(
                            f'{EF_dir}/2d_structure_mode_{self.mode}_time_{time:.2f}_mode_n_{n}_m_{m}.png')
                        print(f'Figure saved in {EF_dir} for time {time:.2f}')
        print('No more modes found! Finished!')

    def profile_plot(self):
        """Plots of density profiles for all ions.

        Args:
            ids_in (ids): Input core_profile IDS
        """
        shot_dir = create_shot_dir(self.database_in, self.shot, self.run)
        profile_dir = f'{shot_dir}/n_profiles'
        if not os.path.exists(profile_dir):
            os.mkdir(profile_dir)
        ids_in = data_retrieve(self.backend_name, self.database_in,
                               self.shot, self.run, self.user, 'core_profiles', 0)
        nspecies = len(ids_in.profiles_1d[0].ion)
        species = []
        for ispecies in range(nspecies):
            species.append(
                ids_in.profiles_1d[0].ion[ispecies].label)
        r = ids_in.profiles_1d[0].grid.rho_tor_norm
        for itime, time in enumerate(ids_in.time):
            if itime in self.time_list:
                fig, ax = plt.subplots()
                for ispecies in range(nspecies):
                    n_T_profile = ids_in.profiles_1d[itime].ion[ispecies].density_thermal
                    ax.plot(r, n_T_profile, label=f'{species[ispecies]}')

                n_e_profile = ids_in.profiles_1d[itime].electrons.density
                ax.plot(r, n_e_profile, label='e', color='green')
                ax.set(
                    xlabel=r"$rho_{tor}$", ylabel="Density" + "[" + r" $m^{-3}$" + "]", title='t = {:.2f} [s]'.format(time))
                ax.legend(loc='upper left')
                ax.set_ylim((0, 6e18))
                ax.set_xlim((0, 1))
                labelscaler(fig=fig, axarr=[
                    ax], labelmult=float(self.label_scaler), linemultiplier=float(self.line_scaler), fig_tight=True)
                plt.savefig(f'{profile_dir}/n_profile_{itime:02d}')
                print(f'Figure saved in {profile_dir} for time {time:.2f}')
        print('No more profiles found! Finished!')

    def growth_freq_EF(self, plot):
        shot_dir = create_shot_dir(self.database_in, self.shot, self.run)

        freq_dir = f'{shot_dir}/freq'
        growth_dir = f'{shot_dir}/growth'
        if not os.path.exists(freq_dir):
            os.mkdir(freq_dir)
        if not os.path.exists(growth_dir):
            os.mkdir(growth_dir)
        m_list = [*range(self.m_min, int(self.m_max) + 1)]
        mhd_linear_in = data_retrieve(self.backend_name, self.database_in,
                                      self.shot, self.run, self.user, self.ids_name, self.occurrence)
        plot_dict_freq = defaultdict(list)
        plot_dict_growth = defaultdict(list)
        time_list = []
        for itime, time in enumerate(mhd_linear_in.time):
            if itime in self.time_list:
                m_check = []
                time_list.append(time)
                for imode, mode in enumerate(mhd_linear_in.time_slice[itime].toroidal_mode):
                    n = mode.n_tor
                    m = mode.m_pol_dominant
                    r_TAE = mode.plasma.velocity_perturbed.coordinate1.coefficients_real[0][0][0]
                    q_TAE = mode.plasma.velocity_perturbed.coordinate1.coefficients_real[1][0][0]
                    freq = None
                    growth = None
                    if self.n_min <= n <= self.n_max and self.m_min <= m <= self.m_max and self.s_min <= r_TAE <= self.s_max:
                        freq = mode.frequency
                        growth = mode.growthrate
                        plot_dict_freq[m].append(freq)
                        plot_dict_growth[m].append(growth)
                        m_check.append(m)
                    else:
                        plot_dict_freq[m].append(None)
                        plot_dict_growth[m].append(None)
                if m_check != m_list:
                    m_miss = [x for x in m_list if x not in m_check]
                    for i in m_miss:
                        plot_dict_freq[i].append(None)
                        plot_dict_growth[i].append(None)
        legend = [f'm = {i}' for i in m_list]
        fig, ax = plt.subplots()
        if plot == 'freq':
            for m in plot_dict_freq.keys():
                print(plot_dict_freq[m])
                plot_dict_freq[m] = [
                    x/1000 if x is not None else x for x in plot_dict_freq[m]]
                print(plot_dict_freq[m])
                ax.plot(time_list, plot_dict_freq[m])
            ax.legend(legend, loc='best', fancybox=True)
            ax.set(xlabel='Time [s]', ylabel='Mode Frequency [ kHz ]')
            labelscaler(fig=fig, axarr=[
                ax], labelmult=float(self.label_scaler), linemultiplier=float(self.line_scaler), fig_tight=True)
            plt.savefig(
                f'{freq_dir}/FREQ_n_{n}_m_{int(m)}_mode_{self.mode}.png')
            print(f'Figure saved in {freq_dir}')
        elif plot == 'growth':
            for m in plot_dict_growth.keys():
                ax.plot(time_list, plot_dict_growth[m])
            ax.legend(legend, loc='best', fancybox=True)
            ax.set(xlabel='Time [s]', ylabel='Mode Growth')
            labelscaler(fig=fig, axarr=[
                ax], labelmult=float(self.label_scaler), linemultiplier=float(self.line_scaler), fig_tight=True)
            plt.savefig(
                f'{growth_dir}/GROWTH_n_{n}_m_{int(m)}_mode_{self.mode}.png')
            print(f'Figure saved in {growth_dir}')

    def compare_runs(self, plot):
        if int(self.compare_modes):
            run_list = self.run.split(',')
            shot_dir = create_shot_dir(
                self.database_in, self.shot, run_list[0])
            compare_dir = f'{shot_dir}/comparison'
            if not os.path.exists(compare_dir):
                os.mkdir(compare_dir)
            ids_in_list = []
            for i in run_list:
                ids_in_list.append((data_retrieve(self.backend_name, self.database_in,
                                                  self.shot, i, self.user, self.ids_name, self.occurrence), i))

            growth_list = []
            freq_list = []
            r_list_complete = []
            r_list_EF = []
            m_list_complete = []
            phi_potential_complete = []
            count_modes = []
            time_complete = []
            for ids in ids_in_list:
                time_list = []
                growth = []
                freq = []
                r = []
                m_processed = []

                count = 0
                for itime, time in enumerate(ids[0].time):
                    time_list.append(time)
                    growth_value = None
                    freq_value = None
                    r_TAE = None

                    for imode, mode in enumerate(ids[0].time_slice[itime].toroidal_mode):
                        n = mode.n_tor
                        m = mode.m_pol_dominant
                        if itime in self.time_list and n == self.n_min and m == self.m_min:
                            phi_potential = mode.plasma.phi_potential_perturbed.real
                            r_list = mode.plasma.grid.dim1
                            m_list = mode.plasma.grid.dim2

                        if n == self.n_min and m == self.m_min and time not in m_processed and mode.frequency > 0:
                            m_processed.append(time)
                            r_TAE = mode.plasma.velocity_perturbed.coordinate1.coefficients_real[
                                0][0][0]
                            growth_value = mode.growthrate
                            freq_value = mode.frequency

                    growth.append(growth_value)
                    freq.append(freq_value)
                    r.append(r_TAE)

                time_complete.append(time_list)
                growth_list.append(growth)
                freq_list.append(freq)
                r_list_complete.append(r)
                r_list_EF.append(r_list)
                m_list_complete.append(m_list)
                phi_potential_complete.append(phi_potential)
                count_modes.append(count)

            fig, ax = plt.subplots()
            if plot == 'EFs':
                colours = ['red', 'green', 'orange', 'blue', 'purple']
                alphas = [1, 0.85, 0.75, 0.65, 0.55]
                max_abs_list = []
                for i in range(len(ids_in_list)):
                    max_abs = 0.
                    for outer_element in phi_potential_complete[i]:
                        for inner_element in outer_element:
                            if np.abs(inner_element) > np.abs(max_abs):
                                max_abs = inner_element
                    max_abs_list.append(max_abs)

                for i in range(len(ids_in_list)):
                    ax.plot(
                        r_list, phi_potential_complete[i]/max_abs_list[i], color=colours[i], alpha=alphas[i], label=f'run = {ids_in_list[i][1]}')
                ax.set_xlim((0, 1))
                ax.set(xlabel='S', ylabel='Electrostatic Potential [a.u.]')
                labelscaler(fig=fig, axarr=[
                    ax], labelmult=float(self.label_scaler), linemultiplier=float(self.line_scaler), fig_tight=True)
                plt.savefig(
                    f'{compare_dir}/comparison_STRUCTURE_{self.run}.png')
                print(f'Figure saved in {compare_dir}')

            if plot == 'growth':
                alphas = [1, 0.85, 0.75, 0.65, 0.55]
                colours = colours = ['red', 'green',
                                     'orange', 'blue', 'purple']
                for i in range(len(ids_in_list)):
                    ax.plot(time_complete[i], growth_list[i], color=colours[i], alpha=alphas[i],
                            label=f'm = {self.m_min} (run = {ids_in_list[i][1]})')

                ax.set(xlabel='Time [s]', ylabel='Mode Growth/Damping [1/s]')
                ax.legend()
                labelscaler(fig=fig, axarr=[
                    ax], labelmult=float(self.label_scaler), linemultiplier=float(self.line_scaler), fig_tight=True)
                plt.savefig(
                    f'{compare_dir}/comparison_GROWTH_{self.run}.png')
                print(f'Figure saved in {compare_dir}')

            elif plot == 'freq':
                alphas = [1, 0.85, 0.75, 0.65, 0.55]
                colours = ['red', 'green',
                           'orange', 'blue', 'purple']
                for i in range(len(ids_in_list)):

                    freq_list[i] = [
                        x/1000 if x is not None else x for x in freq_list[i]]

                    ax.plot(time_complete[i], freq_list[i], color=colours[i], alpha=alphas[i],
                            label=f'm = {self.m_min} (run = {ids_in_list[i][1]})')

                ax.set(xlabel='Time [s]', ylabel='Mode Frequency [KHz]')
                ax.legend()
                labelscaler(fig=fig, axarr=[
                    ax], labelmult=float(self.label_scaler), linemultiplier=float(self.line_scaler), fig_tight=True)
                plt.savefig(
                    f'{compare_dir}/comparison_FREQ_{self.run}.png')
                print(f'Figure saved in {compare_dir}')
        elif plot == 'EFs':
            self.EFs_plot()
        elif plot == 'growth':
            self.growth_freq_EF(plot)
        else:
            self.growth_freq_EF(plot)


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
    filename = os.path.join(
        shot_dir, f"exported_{shot_nr}_{run_out}_{date_time}.txt")

    with open(filename, 'w+') as out_file:
        out_file.write(
            f"{user} {shot_nr} {run_out} {machine_out} {occurence}\n")

        input = imas.DBEntry(imas.imasdef.MDSPLUS_BACKEND,
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
