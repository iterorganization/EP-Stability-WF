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
from run_physics_code import not_timed_HL
from create_workflow_param import create_workflow_param_from_file
from create_workflow_param import create_ligka_param_from_file

#======================CHECK IF LOCAL KEPLER IS LOADED===============

if (os.getenv('KEPLER') is None)  or ('/work/imas/extra' in os.getenv('KEPLER')):
    print('ERROR: the local version of Kepler is not loaded')
    sys.exit()
    
    
# set the path to the folders where the configuration and codeparameters are stored
    
run_config_folder_path = os.path.join(os.getcwd(), 'run_configurations/run_'+datetime.now().strftime('%m%d_%H%M%S'))

run_workflow_param_path = run_config_folder_path+ '/input_workflow.xml'

root1 = etree.parse('input_workflow_default.xml').getroot()

os.makedirs(run_config_folder_path)

copy2('input_workflow_default.xml', run_config_folder_path+'/input_workflow.xml', follow_symlinks=True)
copy2('input/z_ligka.xml', run_config_folder_path+'/z_ligka.xml', follow_symlinks=True)
#=====================A FEW COLOR SCHEMES======================
c1 = 'white'
c2 = 'white smoke'
c3 = 'azure2'
c4 = 'ghost white'
c5 = 'azure4'
cb = 'LavenderBlush3'

default_workflow_param_path = 'input_workflow_default.xml'
default_ligka_param_path = 'input/z_ligka.xml'
window = Tk()
## create mainwindow
      
window.title('H-L WORKFLOW')
window.configure(bg = c1)


def open_gui(input_filepath):

    try:
        wh = window.winfo_reqheight()
        ww = window.winfo_reqwidth()
        wx = window.winfo_x()
        wy = window.winfo_y()
        window.geometry("+%d+%d" %(wx, wy))
        
    except: 
     if not os.path.exists(run_config_folder_path):
        for systemname in maindict[list(maindict.keys())[0]]:
            os.makedirs(run_config_folder_path+'/'+systemname)
            copy2(input_filepath, run_workflow_param_path, follow_symlinks=True)
        pass
    workflow_param = create_workflow_param_from_file(input_filepath)
    ligka_param = create_ligka_param_from_file('input/z_ligka.xml')

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
    
                
                
    ## BUTTONS 
    
    # left: 
    button_saveconfig = Button(fr_wfp, text = 'Save Configuration', bg = c2)
    button_saveconfig.grid(row = 52, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: save_workflow_param_to_file(run_workflow_param_path))
    # save xml to the run folder
    button_loadconfig = Button(fr_wfp, text = 'Load Configuration', bg = c2)
    button_loadconfig.grid(row = 52, column = 1, padx = 5, pady = 5, sticky = 'ew')
    button_loadconfig.configure(command = lambda: load_configuration_from_file(filedialog.askopenfilename(initialdir =  os.path.join(os.getcwd(), 'run_configurations'))))

    button_saveandrun = Button(fr_wfp, text = 'Save and Run', bg = c2)
    button_saveandrun.grid(row = 51, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveandrun.configure(command = lambda: save_and_run(run_workflow_param_path, True))


    button_run_nosave = Button(fr_wfp, text = 'Run (without Saving)', bg = c2)
    button_run_nosave.grid(row = 51, column = 1, padx = 5, pady = 5, sticky = 'ew')
    button_run_nosave.configure(command = lambda: save_and_run(run_workflow_param_path, False))

    button_save_asdef = Button(fr_wfp, text = 'Save Configuration as Default', bg = c2)
    button_save_asdef.grid(row = 53, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_save_asdef.configure(command = lambda: save_workflow_param_to_file('input_workflow_default.xml'))

    button_restore_def = Button(fr_wfp, text = 'Restore Default', bg =c2)
    button_restore_def.grid(row = 53, column = 1, padx = 5, pady = 5, sticky = 'ew')
    button_restore_def.configure(command = lambda: open_gui('input_workflow_default.xml'))

    button_exit = Button(fr_wfp, text = 'Exit', bg = 'light grey')
    button_exit.grid(row = 54, column = 0, padx = 5, pady = 5, sticky = 'w')
    button_exit.configure(command = lambda: sys.exit())
    
    button_saveconfig = Button(fr_as, text = 'Save LIGKA Configuration', bg = c2)
    button_saveconfig.grid(row = 52, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: save_ligka_param_to_file('input/z_ligka.xml'))

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
        
        save_workflow_param_to_file(filepath)

        #window.destroy()
        not_timed_HL(run_config_folder_path)

        if save_yn == 0:
            rmtree(run_config_folder_path)

    def load_configuration_from_file(filepath):
        if 'input_workflow_default.xml' in filepath:
            print('if you want to load the default configuration please choose load default')
            filepath = ()
        elif 'input_workflow.xml' not in filepath: 
            print('please choose an input_workflow.xml file')
            filepath = ()
       

        if filepath is not (): 
            source_folder = filepath[:-19]

            #    rmtree(run_config_folder_path)
            if source_folder.find(run_config_folder_path) is -1:
                try:
                    copytree(source_folder, run_config_folder_path)
                except:
                    rmtree(run_config_folder_path)
                    copytree(source_folder, run_config_folder_path)

                    

                open_gui(run_config_folder_path+ '/input_workflow.xml')

            else:
                print('this folder is the current folder. it is not possible to load the current configuration')


        else:
            print('no file selected')

        

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
    