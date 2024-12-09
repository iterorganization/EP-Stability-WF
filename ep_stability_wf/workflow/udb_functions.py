import numpy as np
import imas
import sys
from ep_stability_wf.workflow.functions_wf import parameters_workflow
from ep_stability_wf.interface.create_workflow_param import create_xml_param_from_file
from ep_stability_wf.workflow.libs.rw_for import (
    wr_for,
    ssplit,
)
from ep_stability_wf.workflow.libs.ufiles import (
    split_uname,
    UFILE,
)
import ep_stability_wf.workflow.libs.ufiles 
from ep_stability_wf.workflow.functions_wf import (
    read_timestep,
    actor_settings,
    imports_check,
    scenario_mod,
    time_construction,
    profiles_get,
)

# If one wants to read hdf5 files the tick needs to be present in the general wf settings.
# The "input" for this program is taken from the "*_out" parameters of the wf, and the first time index is taken even if a list is put in the itime (only 1 time point is possible)
# To run this one needs to have the USER, SHOT_NR, MACHINE_OUT, RUN_OUT, ITIME fields filled accordingly in the general wf interface 
def write_zf_udb(current_config_folder):
    print('Now write UDB file for ASTRA')
    params = parameters_workflow(current_config_folder + "/input_workflow_default.xml")
    
    if params["hdf5"] == 1:
        backend = imas.imasdef.HDF5_BACKEND
    else:
        backend = imas.imasdef.MDSPLUS_BACKEND
    database_out = params["machine_out"]
    shot_no = params["shot_nr"]
    run_out = params["run_out"]
    user = params["user"]
    time_index_list, _ = time_construction(params["itime"])
    itime = time_index_list[0]
    time, ntime = read_timestep(
        user=user,
        database=database_out,
        run=run_out,
        current_config_folder=current_config_folder,
        backend=backend,
        occurrence=2,
    )
    
    input = imas.DBEntry(backend, database_out, shot_no, run_out, user)
    status, _ = input.open()
    if status != 0:
        print("Can't open the selected dataset!", file=sys.stderr)
        sys.exit(1)
    
    ids_name = 'equilibrium'
    occurrence_eq = 2
    equilibrium_in = input.get_slice(ids_name, time[itime], imas.imasdef.PREVIOUS_SAMPLE, occurrence=occurrence_eq)
    
    # EQUILIBRIUM PART
    rho_tor_norm_eq = equilibrium_in.time_slice[0].profiles_1d.rho_tor_norm
    psi_eq = equilibrium_in.time_slice[0].profiles_1d.psi
    psi = []
    # take (psi(rho)-psi(magnetic_axis)) / (psi(LCFS)-psi(magnetic_axis)) and then square root
    for i in psi_eq:
        j = (i-psi_eq[0])/(psi_eq[-1]-psi_eq[0])
        j = np.sqrt(j)
        psi.append(j)
    print(psi)
    
    
    ids_name = 'mhd_linear'
    occurrence_mhd = 6
    mhd_linear_in = input.get_slice(ids_name, time[itime], imas.imasdef.PREVIOUS_SAMPLE, occurrence=occurrence_mhd)

    # #BUG: read core_profs (backup), equilibrium (by chease - rho_tor and rho_pol), and mhd_linear (phi potential - real) (occ 6, mod 2 output)
    for imode, mode in enumerate(mhd_linear_in.time_slice[0].toroidal_mode):
        if mode.n_phi == 0 and mode.m_pol_dominant == 0:
            phi_pot = mode.plasma.phi_potential_perturbed.real
            rho_pol_mhd_dim1 = mode.plasma.grid.dim1
            rho_pol_mhd_dim2 = mode.plasma.grid.dim2
    
            # uf = UFILE()
            
            # uf.pre = 'EREP'
            # uf.ext = 'EREPR'  
            # #uf.shot = equ.shot
            
            # #uf.X = {'label': 'rho_tor'      , 'data': equ.rho_tor_n[0, :] }
            # #uf.f = {'label': 'radial electric field from EPs', 'data': np.abs(equ.q[0, :]) }

            # #uf.comment  = 'time=%8.4f s\n' %equ.time[0]
            # #uf.comment += ' exp=%s\n diag=%s\n ed=%d' %(equ.exp, equ.diag, equ.ed)
            # uf.write(udir=udir)
    print('written UDB file for ASTRA')