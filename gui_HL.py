import os, sys
import subprocess
sys.path.append('workflow')
sys.path.append('interface')
sys.path.append('workflow/input')
sys.path.append(os.getcwd())

from tkinter import * 
from tkinter import filedialog, ttk
from lxml import etree
from datetime import datetime
from shutil import copy2, copytree, rmtree
from run_physics_code_final_no_kep import run_HL_noKEP
from create_workflow_param import create_workflow_param_from_file
from create_workflow_param import create_ligka_param_from_file
from analysis_modes import analysis_ligka_mode5
from analysis_modes import analysis_ligka_mode1
from analysis_modes import analysis_ligka_mode2

# set the path to the folders where the configuration and codeparameters are stored
    
run_config_folder_path = os.path.join(os.getcwd(), 'workflow/input')

run_workflow_param_path = run_config_folder_path+ '/input_workflow.xml'
run_ligka_param_path = run_config_folder_path+ '/z_ligka.xml'

root1 = etree.parse(run_config_folder_path+ '/input_workflow.xml').getroot()


copy2(run_config_folder_path+ '/input_workflow_default.xml', run_config_folder_path+ '/input_workflow.xml', follow_symlinks=True)

#=====================A FEW COLOR SCHEMES======================
c1 = 'white'
c2 = 'white smoke'
c3 = 'azure2'
c4 = 'ghost white'
c5 = 'azure4'
cb = 'LavenderBlush3'

default_workflow_param_path = run_config_folder_path+ '/input_workflow_default.xml'
default_ligka_param_path = run_config_folder_path+ '/z_ligka.xml'
window = Tk()
## create mainwindow
      
window.title('H-L WORKFLOW')
window.configure(bg = c1)


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
    ligka_param = create_ligka_param_from_file('workflow/input/z_ligka.xml')

    fr_wfp = Frame(window, width = 300, height = 500, background = c3)
    fr_wfp.grid(row = 0, column = 0, rowspan = 2,  sticky = 'nwes', padx = 3, pady = 3)

    fr_as = Frame(window, width = 500, height = 500, background = c1)
    fr_as.grid(row = 0, column = 1, rowspan = 2,  sticky = 'nwes', padx = 3, pady = 3)

    fr_fc = Frame(window, width = 100, height = 100, background = c1)
    fr_fc.grid(row = 0, column = 2, sticky = 'news', padx = 3, pady = 3)
    fr_fc.grid_remove()
    
    old_Fr = fr_fc
    
    ## abbreviations for the keys - makes it easier to change them in the xml file
    wfp_ref = list(workflow_param.keys())[0]
    fur_ref = list(workflow_param.keys())[1]
    wfp_ref_l = list(ligka_param.keys())
  



    ## LEFT - CONFIGURING THE WORKFLOW PARAMETERS
    irow = 0
    for ref in [wfp_ref, fur_ref]:
        
        Label(fr_wfp, text = ref, bg = c3, font = '15').grid(row = irow, column = 0, columnspan = 3, pady = 10, padx = 5, sticky = 'we')
        irow += 1

        for elem in workflow_param[ref]:  
            if elem == 'Equilibrium_code':
              continue
            
            Label(fr_wfp, text = elem, bg = c3).grid(row = irow,  column = 0, padx = 3, pady = 2, sticky = 'w')

            entrystring = StringVar()
            entrystring.set(workflow_param[ref][elem])
            entrystring.trace('w', lambda name, index, mode, elem = elem, entrystring = entrystring, ref = ref: update_workflow_param(ref, elem, entrystring.get()))                      # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
            Entry(fr_wfp, textvariable = entrystring, bg = c1).grid(row = irow, column = 1, padx = 3, pady = 2, sticky = 'e')
            irow += 1
            
    ## RIGHT - CONFIGURING LIGKA PARAMETERS
    irow = 0
    for ref in wfp_ref_l:
        
        Label(fr_as, text = ref, bg = c3, font = '15').grid(row = irow, column = 0, columnspan = 3, pady = 10, padx = 5, sticky = 'we')
        irow += 1

        for elem in ligka_param[ref]:
            
            Label(fr_as, text = elem, bg = c3).grid(row = irow,  column = 0, padx = 3, pady = 2, sticky = 'w')

            entrystring = StringVar()
            entrystring.set(ligka_param[ref][elem])
            entrystring.trace('w', lambda name, index, mode, elem = elem, entrystring = entrystring, ref = ref: update_ligka_param(ref, elem, entrystring.get()))                      # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
            Entry(fr_as, textvariable = entrystring, bg = c1).grid(row = irow, column = 1, padx = 3, pady = 2, sticky = 'e')
            irow += 1
    
                
                
    ## CONFIGURE EQUILIBRIUM CODE SELECTBOX
    
    equilibrium = StringVar()
    #equilibrium.trace('w', lambda name, index, mode, elem = 'Equilibrium_code', entrystring = equilibrium, ref = fur_ref: update_workflow_param(ref, elem, entrystring.get())
    equilibrium.set(workflow_param[fur_ref]['Equilibrium_code'])
    Label(fr_wfp, text = 'Equilibrium code:', bg = c3).grid(row = 50, column = 0, padx = 3, pady = 2, sticky = 'w')
    combobox = ttk.Combobox(fr_wfp, textvariable = equilibrium)
    combobox.grid(row = 50, column = 1, padx = 3, pady = 2, sticky = 'e')
    combobox.config(values = ('Helena', 'Chease'))
    equilibrium.trace('w', lambda name, index, mode, elem = 'Equilibrium_code', entrystring = equilibrium, ref = fur_ref: update_workflow_param(ref, elem, entrystring.get()))
    
   
    
    ## BUTTONS 
    
    # left: 
    button_saveconfig = Button(fr_wfp, text = 'Save Configuration', bg = c2)
    button_saveconfig.grid(row = 52, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: save_workflow_param_to_file(run_workflow_param_path))

    button_saveandrun = Button(fr_wfp, text = 'Save and Run', bg = c2)
    button_saveandrun.grid(row = 51, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveandrun.configure(command = lambda: save_and_run(run_workflow_param_path, True))

    button_run_nosave = Button(fr_wfp, text = 'Run (without Saving)', bg = c2)
    button_run_nosave.grid(row = 51, column = 1, padx = 5, pady = 5, sticky = 'ew')
    button_run_nosave.configure(command = lambda: save_and_run(run_workflow_param_path, False))
    
    button_analysis = Button(fr_wfp, text = 'LIGKA Analysis', bg = c2)
    button_analysis.grid(row = 52, column = 1, padx = 5, pady = 5, sticky = 'ew')
    button_analysis.configure(command = lambda: analysis_window())

    button_save_asdef = Button(fr_wfp, text = 'Save Configuration as Default', bg = c2)
    button_save_asdef.grid(row = 53, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_save_asdef.configure(command = lambda: save_workflow_param_to_file('workflow/input/input_workflow_default.xml'))

    button_exit = Button(fr_wfp, text = 'Exit', bg = 'light grey')
    button_exit.grid(row = 54, column = 0, padx = 5, pady = 5, sticky = 'w')
    button_exit.configure(command = lambda: sys.exit())
    
    button_saveconfig = Button(fr_as, text = 'Save LIGKA Configuration', bg = c2)
    button_saveconfig.grid(row = 52, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: save_ligka_param_to_file('workflow/input/z_ligka.xml'))

    

     ## FUNCTION NEW ANALYSIS WINDOW
     
    def analysis_window():
      #create analysis directory if none exists
      analysis_dir = ('workflow/Analysis')
      analysis_dir_check = os.path.isdir(analysis_dir)
      
      if not analysis_dir_check:
        os.makedirs(analysis_dir)
        print('Analysis folder was created')
      
      window_a = Tk()
      window_a.title('LIGKA Analysis')
      window_a.configure(bg = c1)
      window_a.geometry('300x500')
      
      fr_ana = Frame(window_a, width = 300, height = 500, background = c2)
      fr_ana.grid(row = 0, column = 0, rowspan = 2,  sticky = 'nwes', padx = 3, pady = 3)
      
      button_analysis = Button(fr_ana, text = 'Mode 5', bg = c2)
      button_analysis.grid(row = 5, column = 0, padx = 5, pady = 5, sticky = 'ew')
      button_analysis.configure(command = lambda: analysis_mode5())
      
      button_analysis = Button(fr_ana, text = 'Mode 1', bg = c2)
      button_analysis.grid(row = 6, column = 0, padx = 5, pady = 5, sticky = 'ew')
      button_analysis.configure(command = lambda: analysis_mode1())
      
      button_analysis = Button(fr_ana, text = 'Mode 2', bg = c2)
      button_analysis.grid(row = 7, column = 0, padx = 5, pady = 5, sticky = 'ew')
      button_analysis.configure(command = lambda: analysis_mode2())
      
    def analysis_mode5():
      analysis_ligka_mode5()
    def analysis_mode1():
      analysis_ligka_mode1()
    def analysis_mode2():
      analysis_ligka_mode2()
      

     ## FUNCTIONS - SAVING & UPDATING


    def update_workflow_param(ref, elem, newvalue):
        workflow_param[ref][elem] = newvalue
        
    def update_ligka_param(ref, elem, newvalue):
        ligka_param[ref][elem] = newvalue
      
        
    def save_workflow_param_to_file(filepath):

        tree = etree.parse(filepath)
        root = tree.getroot()
        
        rl = [wfp_ref, fur_ref]
        
        for iroot in range(2):
            for elem in root[iroot].iter():
                if((elem.tag is not etree.Comment) and (len(elem) == 0)):

                   elem.text = workflow_param[rl[iroot]][elem.tag]
                   
        tree.write(filepath)
        
    def save_ligka_param_to_file(filepath):

        tree = etree.parse(filepath)
        root = tree.getroot()
        
        name0 = root.attrib['display']
        for elem in root.iter():
          if((elem.tag is not etree.Comment) and (len(elem) == 0)):

            elem.text = ligka_param[name0][elem.tag]
                   
        tree.write(filepath)

    def save_and_run(filepath, save_yn):
        
        if save_yn == True:
          save_workflow_param_to_file(filepath)

        run_HL_noKEP()


        

    def save_codeparam_to_file(filepath, codeparam_dict):

        tree = etree.parse(filepath)
        root = tree.getroot()
        
        for elem in root.iter():
            if((elem.tag is not etree.Comment) and (len(elem) == 0)):
               elem.text = codeparam_dict[elem.tag]
        pass
        
        tree.write(filepath)

    window.mainloop()


open_gui(default_workflow_param_path)
    