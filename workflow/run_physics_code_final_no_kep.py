# --------------------------------------------
# PYTHON WRAPPER TO CALL HELENA + HAGIS1 + LIGKA
# --------------------------------------------


# NEEDED MODULES
import os, imas, sys, pdb, random, copy
from lxml import etree
import xml.etree.ElementTree as ET
from workflow.functions_wf import parameters_workflow
from interface.create_workflow_param import save_xml_param_to_file_on_run, update_xml_param_on_run
from workflow_components import helena, hagis_1, ligka_mode_1, ligka_mode_4, ligka_mode_5, ligka_mode_2
sys.path.append(os.getcwd())
sys.path.append('input')





def run_HL_noKEP():

    # IMPORT PARAMETERS FROM WORKFLOW AND LIGKA XML --------------------------------------
    print('----- WF PARAMETERS ----')
    param = parameters_workflow('workflow/input/input_workflow_default.xml')
    print('----- LIGKA PARAMETERS ----')
    param_ligka = parameters_workflow('workflow/input/z_ligka.xml')
    wfp_ref_l = list(param_ligka.keys())
    print('----- HAGIS 1 PARAMETERS ----')
    param_hagis1 = parameters_workflow('workflow/input/hagis1.xml')


    # TIME SETTINGS FOR RUNS
    time_runs = param['itend'] - param['itbegin']  # runs for all other than the first one that takes data from public

    # PUBLIC and LOCAL DATABASE ENVIRONMENT
    # SETTINGS
    user = os.getenv('USER')
    version = os.getenv('IMAS_VERSION')[0]

    if param['ligka_541'] == 1:
        if param['Equilibrium_code'] == 'Helena':
            print('=================Starting HELENA and LIGKA mode 5 - 4 - 1=================')
            
            helena(param, user)

            print(param['Equilibrium_code'],' done. STARTING LIGKA MODE 5')
        else:
            print('Equilibrium code was not selected, skip and run LIGKA MODE 5.')

        
        update_xml_param_on_run(param_ligka, 'modus', '5')
        save_xml_param_to_file_on_run('workflow/input/z_ligka.xml', 'modus', '5')
        param_ligka = parameters_workflow('workflow/input/z_ligka.xml')
        if param_ligka['modus'] == 5:
            ligka_mode_5(param, user, time_runs)
            print('Done LIGKA mode 5, starting MODE 4')

        update_xml_param_on_run(param_ligka, 'modus', '4')
        save_xml_param_to_file_on_run('workflow/input/z_ligka.xml', 'modus', '4')
        param_ligka = parameters_workflow('workflow/input/z_ligka.xml')
        if param_ligka['modus'] == 4:
            ligka_mode_4(param, user, time_runs)
            print('Done LIGKA mode 4, starting MODE 1')

        
        update_xml_param_on_run(param_ligka, 'modus', '1')
        save_xml_param_to_file_on_run('workflow/input/z_ligka.xml', 'modus', '1')
        param_ligka = parameters_workflow('workflow/input/z_ligka.xml')
        if param_ligka['modus'] == 1:
            ligka_mode_1(param, user, time_runs)
        print('Done WORKFLOW, LIGKA 541.')

    else:
        if param['Equilibrium_code'] == 'Helena':
            print('=====================STARTING HELENA===================')
            helena(param, user)
            print(param['Equilibrium_code'],' done.')
        if param['Distributions_1'] == 'Hagis_1':
            print('=====================STARTING HAGIS 1===================')
            hagis_1(param, user, time_runs)

        ## LEAVE PLACE FOR HAGIS 2

        if param['Stability_code'] == 'Ligka_m1':
            update_xml_param_on_run(param_ligka, 'modus', '1')
            save_xml_param_to_file_on_run('workflow/input/z_ligka.xml', 'modus', '1')
            param_ligka = parameters_workflow('workflow/input/z_ligka.xml')
            print('=====================STARTING LIGKA MODE 1===================')
            ligka_mode_1(param, user, time_runs)
        
        if param['Stability_code'] == 'Ligka_m4':
            update_xml_param_on_run(param_ligka, 'modus', '4')
            save_xml_param_to_file_on_run('workflow/input/z_ligka.xml', 'modus', '4')
            param_ligka = parameters_workflow('workflow/input/z_ligka.xml')
            print('=====================STARTING LIGKA MODE 4===================')
            ligka_mode_4(param, user, time_runs)
        
        if param['Stability_code'] == 'Ligka_m5':
            update_xml_param_on_run(param_ligka, 'modus', '5')
            save_xml_param_to_file_on_run('workflow/input/z_ligka.xml', 'modus', '5')
            param_ligka = parameters_workflow('workflow/input/z_ligka.xml')
            print('=====================STARTING LIGKA MODE 5===================')
            ligka_mode_5(param, user, time_runs)
        
        if param['Stability_code'] == 'Ligka_m2':
            update_xml_param_on_run(param_ligka, 'modus', '2')
            save_xml_param_to_file_on_run('workflow/input/z_ligka.xml', 'modus', '2')
            param_ligka = parameters_workflow('workflow/input/z_ligka.xml')
            print('=====================STARTING LIGKA MODE 2===================')
            ligka_mode_2(param, user, time_runs)