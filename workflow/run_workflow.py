# --------------------------------------------
# PYTHON WRAPPER TO CALL HELENA + LIGKA + HAGIS1 + HAGIS2
# --------------------------------------------


# NEEDED MODULES
import os, imas, sys, pdb, random, copy
from lxml import etree
import xml.etree.ElementTree as ET
from workflow.functions_wf import parameters_workflow, profiles_get
from interface.create_workflow_param import save_xml_param_to_file_on_run, update_xml_param_on_run
from workflow.workflow_components import actor_call
sys.path.append(os.getcwd())
sys.path.append('input')



def workflow_EP(current_config_folder):
    
    # IMPORT PARAMETERS FROM WORKFLOW XML--------------------------------------
    param = parameters_workflow(current_config_folder+'/input_workflow_default.xml')

    # CHECK FOR EXISTING DB
    output_folder = os.getenv('HOME')+'/public/imasdb/'+param['machine_out']+'/3/0'
    if os.path.isdir(output_folder) == False:
      print('-- Create local database for output file '+output_folder, file=sys.stdout)
      os.makedirs(output_folder)
    
    if param['pulse_list'] == 1:
      with open("shots.dat") as f:
        pulse_list = eval(f.read())
    else:
        pulse_list = [(param['shot_nr'],param['run_in'])]

    for i in pulse_list:
        if len(pulse_list) == 1:
            print('The workflow will now run with one shot/run as input: ',pulse_list)
        else:
            print('The Workflow will run with the same settings (and update the required ones) for all selected shots/runs as input: ',pulse_list)
            update_xml_param_on_run(param, 'shot_nr', i[0])
            save_xml_param_to_file_on_run(current_config_folder+'/input_workflow_default.xml', 'shot_nr', str(i[0]))
            update_xml_param_on_run(param, 'run_in', i[1])
            save_xml_param_to_file_on_run(current_config_folder+'/input_workflow_default.xml', 'run_in', str(i[1]))
            param = parameters_workflow(current_config_folder+'/input_workflow_default.xml')

        if param['ligka_541'] == 1:
            print('=================Starting HELENA and LIGKA mode 5 - 4 - 1=================')
            if param['Equilibrium_code'] == 'Helena':
                actor_call("Helena", current_config_folder, param)

                print(param['Equilibrium_code'],' done. STARTING LIGKA MODE 5')
            else:
                print('Equilibrium code was not selected, skip and run LIGKA MODE 5.')

             # MODIFY LIGKA XML TO TAKE NSPEC automatically!!
            param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')
            print('Now modifying LIGKA XML by taking the species present in core_profiles IDS')
            curr_str, nspec, nback, nhot = profiles_get(param)
            update_xml_param_on_run(param_ligka, 'spec_str', curr_str)
            save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'spec_str', str(curr_str))
            update_xml_param_on_run(param_ligka, 'nspec', nspec)
            save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'nspec', str(nspec))
            update_xml_param_on_run(param_ligka, 'nback', nback)
            save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'nback', str(nback))
            update_xml_param_on_run(param_ligka, 'nhot', nhot)
            save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'nhot', str(nhot))
            param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')


            update_xml_param_on_run(param_ligka, 'modus', '5')
            save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'modus', '5')
            param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')
            if param_ligka['modus'] == 5:
                actor_call("Ligka_m5", current_config_folder, param)
               
                print('Done LIGKA mode 5, starting MODE 4')

            update_xml_param_on_run(param_ligka, 'modus', '4')
            save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'modus', '4')
            param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')
            if param_ligka['modus'] == 4:
                actor_call("Ligka_m4", current_config_folder, param)
                
                print('Done LIGKA mode 4, starting MODE 1')

            
            update_xml_param_on_run(param_ligka, 'modus', '1')
            save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'modus', '1')
            param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')
            if param_ligka['modus'] == 1:
                actor_call("Ligka_m1", current_config_folder, param)
               
            print('Done WORKFLOW, LIGKA 541.')

        else:
            if param['Equilibrium_code'] == 'Helena':
                actor_call("Helena", current_config_folder, param)

            # MODIFY LIGKA XML TO TAKE NSPEC automatically!!
            if str(param['Stability_code']) != '0' or str(param['Orbit_Finder']) != '0':
                param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')
                print('Now modifying LIGKA XML by taking the species present in core_profiles IDS')
                curr_str, nspec, nback, nhot = profiles_get(param)
                update_xml_param_on_run(param_ligka, 'spec_str', curr_str)
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'spec_str', str(curr_str))
                update_xml_param_on_run(param_ligka, 'nspec', nspec)
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'nspec', str(nspec))
                update_xml_param_on_run(param_ligka, 'nback', nback)
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'nback', str(nback))
                update_xml_param_on_run(param_ligka, 'nhot', nhot)
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'nhot', str(nhot))
                param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')


            if param['Stability_code'] == 'Ligka_m1':
                update_xml_param_on_run(param_ligka, 'modus', '1')
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'modus', '1')
                param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')

                actor_call("Ligka_m1", current_config_folder, param)
                
            
            if param['Stability_code'] == 'Ligka_m4':
                update_xml_param_on_run(param_ligka, 'modus', '4')
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'modus', '4')
                param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')

                actor_call("Ligka_m4", current_config_folder, param)
               
            
            if param['Stability_code'] == 'Ligka_m5':
                update_xml_param_on_run(param_ligka, 'modus', '5')
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'modus', '5')
                param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')

                actor_call("Ligka_m5", current_config_folder, param)
                

            if param['Stability_code'] == 'Ligka_m6':
                update_xml_param_on_run(param_ligka, 'modus', '6')
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'modus', '6')
                param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')

                actor_call("Ligka_m6", current_config_folder, param)
                
                
            if param['Stability_code'] == 'Ligka_m2':
                update_xml_param_on_run(param_ligka, 'modus', '2')
                save_xml_param_to_file_on_run(current_config_folder+'/z_ligka.xml', 'modus', '2')
                param_ligka = parameters_workflow(current_config_folder+'/z_ligka.xml')

                actor_call("Ligka_m2", current_config_folder, param)
                

            # For now it is moved here, because it runs after LIGKA m 5/4/1. 
            # Soon, automatic way of checking who to run first, but after a first version of the wf is ready
            # i.e all actors are established. 
            if param['Distributions_1'] == 'Hagis_1':

                actor_call("Hagis_1", current_config_folder, param)
                
            if param['Distributions_2'] == 'Hagis_2':

                actor_call("Hagis_2", current_config_folder, param)
                
            if param['Orbit_Finder'] == 'Finder':
                print('=====================ADJUSTING FINDER XML===================')
                param_finder = parameters_workflow(current_config_folder+'/finder_input.xml')
                species_string = param_ligka['spec_str']
                # ADD NPSI_OUT
                update_xml_param_on_run(param_finder, 'num_kin_rad', param_ligka['npsi_out'])
                save_xml_param_to_file_on_run(current_config_folder+'/finder_input.xml', 'num_kin_rad', str(param_ligka['npsi_out']))
                # ADD min/max n/m
                update_xml_param_on_run(param_finder, 'n_prop_min', param_ligka['min_n_tor'])
                save_xml_param_to_file_on_run(current_config_folder+'/finder_input.xml', 'n_prop_min', str(param_ligka['min_n_tor']))
                update_xml_param_on_run(param_finder, 'n_prop_max', param_ligka['max_n_tor'])
                save_xml_param_to_file_on_run(current_config_folder+'/finder_input.xml', 'n_prop_max', str(param_ligka['max_n_tor']))
                update_xml_param_on_run(param_finder, 'm_min_prop', param_ligka['min_m'])
                save_xml_param_to_file_on_run(current_config_folder+'/finder_input.xml', 'm_min_prop', str(param_ligka['min_m']))
                update_xml_param_on_run(param_finder, 'm_max_prop', param_ligka['max_m'])
                save_xml_param_to_file_on_run(current_config_folder+'/finder_input.xml', 'm_max_prop', str(param_ligka['max_m']))

                for i in range(0, len(species_string), 2):
                    species = species_string[i:i+2]
                    print('=====================STARTING Finder for '+species+' ===================')
                    # ADD SPECIES
                    update_xml_param_on_run(param_finder, 'spec', species)
                    save_xml_param_to_file_on_run(current_config_folder+'/finder_input.xml', 'spec', str(species))

                    actor_call("Finder", current_config_folder, param)
                    
    
    print('Workflow Finished.')
