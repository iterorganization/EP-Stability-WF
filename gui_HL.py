import os, sys
import subprocess
sys.path.append(os.getcwd())
sys.path.append('workflow')
sys.path.append('interface')
sys.path.append('workflow/input')

from tkinter import * 
from tkinter import filedialog, ttk
from lxml import etree
from datetime import datetime
from shutil import copy2, copytree, rmtree
from workflow.run_physics_code_final_no_kep import run_HL_noKEP
from workflow.functions_wf import read_timestep
from interface.create_workflow_param import create_workflow_param_from_file, create_xml_param_from_file, save_xml_param_to_file, update_xml_param
from interface.extra_functions import actor_window,analysis_window
from workflow.analysis_modes import analysis_ligka_mode5,analysis_ligka_mode2,analysis_ligka_mode1
import interface.colour_definitions as col

# set the path to the folders where the configuration and codeparameters are stored
    
run_config_folder_path = os.path.join(os.getcwd(), 'workflow/input')


#=====================A FEW COLOR SCHEMES======================
col.c1 = 'white'
col.c2 = 'white smoke'
col.c3 = 'azure2'
col.c4 = 'ghost white'
col.c5 = 'azure4'
cb = 'LavenderBlush3'

default_workflow_param_path = run_config_folder_path+ '/input_workflow_default.xml'
default_ligka_param_path = run_config_folder_path+ '/z_ligka.xml'
window = Tk()
## create mainwindow
      
window.title('H-L WORKFLOW')
window.configure(bg = col.c1)


def open_gui(default_workflow_param_path):

    try:
        wh = window.winfo_reqheight()
        ww = window.winfo_reqwidth()
        wx = window.winfo_x()
        wy = window.winfo_y()
        window.geometry("+%d+%d" %(wx, wy))
    except: 

        pass   
    
    workflow_param = create_workflow_param_from_file(default_workflow_param_path)
    ligka_param = create_xml_param_from_file('workflow/input/z_ligka.xml')
    hagis1_param = create_xml_param_from_file('workflow/input/hagis1.xml')

    fr_wfp = Frame(window, width = 300, height = 500, background = col.c3)
    fr_wfp.grid(row = 0, column = 0, rowspan = 2,  sticky = 'nwes', padx = 3, pady = 3)

    fr_as = Frame(window, width = 500, height = 500, background = col.c1)
    fr_as.grid(row = 0, column = 1, rowspan = 2,  sticky = 'nwes', padx = 3, pady = 3)

    fr_fc = Frame(window, width = 100, height = 100, background = col.c1)
    fr_fc.grid(row = 0, column = 2, sticky = 'news', padx = 3, pady = 3)
    fr_fc.grid_remove()
    
    old_Fr = fr_fc
    
    ## abbreviations for the keys - makes it easier to change them in the xml file
    wfp_ref = list(workflow_param.keys())[0]
    fur_ref = list(workflow_param.keys())[1]
    act_ref = list(workflow_param.keys())[2]
    wfp_ref_l = list(ligka_param.keys())
    wfp_ref_h = list(hagis1_param.keys())
  



    ## LEFT - CONFIGURING THE WORKFLOW PARAMETERS
    irow = 0
    for ref in [wfp_ref, fur_ref]:
        
        Label(fr_wfp, text = ref, bg = col.c3, font = '15').grid(row = irow, column = 0, columnspan = 3, pady = 10, padx = 5, sticky = 'we')
        irow += 1

        for elem in workflow_param[ref]:  
            
          Label(fr_wfp, text = elem, bg = col.c3).grid(row = irow,  column = 0, padx = 3, pady = 2, sticky = 'w')
          if elem == 'ligka_541':
            entrystring = StringVar()
            entrystring.set(workflow_param[ref][elem])
            c = Checkbutton(fr_wfp, variable = entrystring)
            c.grid(row = irow, column = 1, padx = 3, pady = 2, sticky = 'e')
            entrystring.trace('w', lambda name, index, mode, elem = elem, entrystring = entrystring, ref = ref: update_xml_param(workflow_param, ref, elem, entrystring.get()))
          else:
            entrystring = StringVar()
            entrystring.set(workflow_param[ref][elem])
            entrystring.trace('w', lambda name, index, mode, elem = elem, entrystring = entrystring, ref = ref: update_xml_param(workflow_param, ref, elem, entrystring.get()))                      # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
            Entry(fr_wfp, textvariable = entrystring, bg = col.c1).grid(row = irow, column = 1, padx = 3, pady = 2, sticky = 'e')
          irow += 1
            
    ## RIGHT - CONFIGURING WF ACTOR LIST AND THEIR PARAMETERS
    irow = 0
    for ref in [act_ref]:
        
        Label(fr_as, text = ref, bg = col.c3, font = '15').grid(row = irow, column = 0, columnspan = 3, pady = 10, padx = 5, sticky = 'we')
        irow += 1

        for elem in workflow_param[ref]:
          
          entrystring = StringVar()
          entrystring.set(workflow_param[ref][elem])
          Label(fr_as, text = elem, bg = col.c3).grid(row = irow, column = 0, padx = 3, pady = 2, sticky = 'w')
          combobox = ttk.Combobox(fr_as, textvariable = entrystring)
          combobox.grid(row = irow, column = 1, padx = 3, pady = 2, sticky = 'e')
          if elem == 'Equilibrium_code':
            combobox.config(values = ('0', 'Helena', 'Chease'))
          elif elem == 'Stability_code':
            combobox.config(values = ('0', 'Ligka_m5', 'Ligka_m4', 'Ligka_m1', 'Ligka_m2'))
          else:
            combobox.config(values = ('0', workflow_param[ref][elem]))
          entrystring.trace('w', lambda name, index, mode, elem = elem, entrystring = entrystring, ref = act_ref: update_xml_param(workflow_param, ref, elem, entrystring.get()))
          irow += 1
    
    ## BUTTONS 
    
    # left: 
    button_saveconfig = Button(fr_wfp, text = 'Save Configuration', bg = col.c2)
    button_saveconfig.grid(row = 52, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: save_workflow_param_to_file(default_workflow_param_path))

    button_saveandrun = Button(fr_wfp, text = 'Save and Run', bg = col.c2)
    button_saveandrun.grid(row = 51, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveandrun.configure(command = lambda: save_and_run(default_workflow_param_path, True))

    button_run_nosave = Button(fr_wfp, text = 'Run (without Saving)', bg = col.c2)
    button_run_nosave.grid(row = 51, column = 1, padx = 5, pady = 5, sticky = 'ew')
    button_run_nosave.configure(command = lambda: save_and_run(default_workflow_param_path, False))
    
    button_analysis = Button(fr_wfp, text = 'LIGKA Analysis', bg = col.c2)
    button_analysis.grid(row = 52, column = 1, padx = 5, pady = 5, sticky = 'ew')
    button_analysis.configure(command = lambda: analysis_window())

    button_save_asdef = Button(fr_wfp, text = 'Save Configuration as Default', bg = col.c2)
    button_save_asdef.grid(row = 53, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_save_asdef.configure(command = lambda: save_workflow_param_to_file('workflow/input/input_workflow_default.xml'))

    button_exit = Button(fr_wfp, text = 'Exit', bg = 'light grey')
    button_exit.grid(row = 55, column = 0, padx = 5, pady = 5, sticky = 'w')
    button_exit.configure(command = lambda: sys.exit())
    
    ## BUTONS RIGHT SIDE:
    button_saveconfig = Button(fr_as, text = 'LIGKA Parameters', bg = col.c2)
    button_saveconfig.grid(row = 54, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: actor_window(wfp_ref_l, ligka_param, 0))

    button_saveconfig = Button(fr_as, text = 'HAGIS 1 Parameters', bg = col.c2)
    button_saveconfig.grid(row = 55, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: actor_window(wfp_ref_h, hagis1_param, 1))

    
     ## FUNCTIONS - SAVING & UPDATING
        
    def save_workflow_param_to_file(filepath):

        tree = etree.parse(filepath)
        root = tree.getroot()
        
        rl = [wfp_ref, fur_ref, act_ref]
        
        for iroot in range(3):
            for elem in root[iroot].iter():
                if((elem.tag is not etree.Comment) and (len(elem) == 0)):

                   elem.text = workflow_param[rl[iroot]][elem.tag]
                   
        tree.write(filepath)
    
    def save_and_run(filepath, save_yn):
        
        if save_yn == True:
          save_workflow_param_to_file(filepath)

        run_HL_noKEP()

    window.mainloop()


open_gui(default_workflow_param_path)
    