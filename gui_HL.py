#!/usr/bin/env python
from interface.extra_functions import actor_window, analysis_window, scenario_window, load, save
from tkinter import *
from interface.extra_functions import CreateToolTip
import interface.colour_definitions as col
from interface.create_workflow_param import create_workflow_param_from_file, create_xml_param_from_file, save_xml_param_to_file, update_xml_param, update_xml_param_wf
from workflow.functions_wf import read_timestep
from workflow.run_workflow import workflow_EP
from shutil import copy2, copytree, rmtree
from datetime import datetime
from lxml import etree
from tkinter import filedialog, ttk
import os
import sys
import subprocess
sys.path.append(os.getcwd())
sys.path.append('workflow')
sys.path.append('interface')
sys.path.append('workflow/input')


# set the path to the folders where the configuration and codeparameters are stored

wf_param_folder_default = os.path.join(os.getcwd(), 'user_profiles/default')

default_workflow_param_path = wf_param_folder_default + '/input_workflow_default.xml'

window = Tk()
# create mainwindow

window.title('EP WORKFLOW')
window.configure(bg=col.c1)


def open_gui(wf_param_folder):

    try:
        wh = window.winfo_reqheight()
        ww = window.winfo_reqwidth()
        wx = window.winfo_x()
        wy = window.winfo_y()
        window.geometry("+%d+%d" % (wx, wy))
    except:

        pass

    workflow_param = create_workflow_param_from_file(
        wf_param_folder+'/input_workflow_default.xml')
    ligka_param = create_xml_param_from_file(wf_param_folder+'/z_ligka.xml')
    helena_param = create_xml_param_from_file(wf_param_folder+'/helena.xml')
    hagis1_param = create_xml_param_from_file(wf_param_folder+'/hagis1.xml')
    hagis2_param = create_xml_param_from_file(wf_param_folder+'/hagis2.xml')
    finder_param = create_xml_param_from_file(
        wf_param_folder+'/finder_input.xml')
    analysis_param = create_xml_param_from_file(
        wf_param_folder+'/analysis.xml')
    species_param = create_xml_param_from_file(
        wf_param_folder+'/actor_settings.xml')
    scenario_param = create_xml_param_from_file(
        wf_param_folder+'/scenario.xml')

    fr_wfp = Frame(window, width=300, height=500, background=col.c3)
    fr_wfp.grid(row=0, column=0, rowspan=2,  sticky='nwes', padx=3, pady=3)

    fr_as = Frame(window, width=500, height=500, background=col.c1)
    fr_as.grid(row=0, column=1, rowspan=2,  sticky='nwes', padx=3, pady=3)

    fr_fc = Frame(window, width=500, height=500, background=col.c1)
    fr_fc.grid(row=0, column=2, sticky='news', padx=3, pady=3)
    fr_fc.grid_remove()

    old_Fr = fr_fc

    # abbreviations for the keys - makes it easier to change them in the xml file
    wfp_ref = list(workflow_param.keys())[0]
    fur_ref = list(workflow_param.keys())[1]
    act_ref = list(workflow_param.keys())[2]
    wfp_ref_hel = list(helena_param.keys())
    wfp_ref_l = list(ligka_param.keys())
    wfp_ref_h = list(hagis1_param.keys())
    wfp_ref_h2 = list(hagis2_param.keys())
    wfp_ref_f = list(finder_param.keys())
    ana_ref = list(analysis_param.keys())[0]
    species_ref = list(species_param.keys())
    scen_ref = list(scenario_param.keys())

    # Class to not re-generate a new folder name between two 'save' statements

    class saved_folder_name(object):
        def __init__(self):
            self.value = None

        def NoAction(self):
            self.value = self.value

        def Save(self, chosen_folder, init_folder):
            previous_folder = init_folder
            if chosen_folder == init_folder:  # Very first SAVE, or SAVE after a SAVE_AS
                self.value = save(self.value, previous_folder, wf_param_folder_default,
                                  workflow_param, wfp_ref, fur_ref, act_ref, 1)
            else:
                if chosen_folder is None:
                    if self.value is None:  # 1st SAVE after a LOAD
                        self.value = save(init_folder, previous_folder, wf_param_folder_default,
                                          workflow_param, wfp_ref, fur_ref, act_ref, 0)
                    else:  # Next SAVEs after a LOAD; SAVE after a SAVE AS which is after a LOAD;
                        self.value = save(self.value, previous_folder, wf_param_folder_default,
                                          workflow_param, wfp_ref, fur_ref, act_ref, 0)
                else:  # SAVE AS
                    if_cancelled = self.value
                    self.value = save(chosen_folder, previous_folder, wf_param_folder_default,
                                      workflow_param, wfp_ref, fur_ref, act_ref, 1)
                    if self.value is None:
                        self.value = if_cancelled
            return self.value

    saved_folder = saved_folder_name()

    # To use the folder loaded through the 'load' function for the next 'save' statements
    if wf_param_folder+'/input_workflow_default.xml' == default_workflow_param_path:
        init_folder = None
    else:
        init_folder = wf_param_folder

    # LEFT - CONFIGURING THE WORKFLOW PARAMETERS
    irow = 0
    for ref in [wfp_ref, fur_ref]:

        Label(fr_wfp, text=ref, bg=col.c3, font='15').grid(
            row=irow, column=0, columnspan=3, pady=10, padx=5, sticky='we')
        irow += 1

        for elem in workflow_param[ref]:

            Label(fr_wfp, text=elem, bg=col.c3).grid(
                row=irow,  column=0, padx=3, pady=2, sticky='w')
            if elem in ['ligka_541', 'pulse_list', 'fast_particles']:
                entrystring = StringVar()
                entrystring.set(workflow_param[ref][elem][0])
                c = Checkbutton(fr_wfp, variable=entrystring)
                c.grid(row=irow, column=1, padx=3, pady=2, sticky='e')
                CreateToolTip(c, text=workflow_param[ref][elem][1])
                entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                  ref=ref: update_xml_param_wf(workflow_param, ref, elem, entrystring.get()))
            else:
                entrystring = StringVar()
                entrystring.set(workflow_param[ref][elem][0])
                # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
                entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                  ref=ref: update_xml_param_wf(workflow_param, ref, elem, entrystring.get()))
                x = Entry(fr_wfp, textvariable=entrystring, bg=col.c1)
                x.grid(row=irow, column=1, padx=3, pady=2, sticky='e')
                CreateToolTip(x, text=workflow_param[ref][elem][1])
            irow += 1

    # RIGHT - CONFIGURING WF ACTOR LIST AND THEIR PARAMETERS
    irow = 0
    for ref in [act_ref]:

        Label(fr_as, text=ref, bg=col.c3, font='15').grid(
            row=irow, column=0, columnspan=3, pady=10, padx=5, sticky='we')
        irow += 1

        for elem in workflow_param[ref]:

            entrystring = StringVar()
            entrystring.set(workflow_param[ref][elem][0])
            Label(fr_as, text=elem, bg=col.c3).grid(
                row=irow, column=0, padx=3, pady=2, sticky='w')
            combobox = ttk.Combobox(fr_as, textvariable=entrystring)
            combobox.grid(row=irow, column=1, padx=3, pady=2, sticky='e')
            CreateToolTip(combobox, text=workflow_param[ref][elem][1])
            if elem == 'Equilibrium_code':
                combobox.config(
                    values=('0', 'Helena', 'Chease (not working yet)'))
            elif elem == 'Distributions_1':
                combobox.config(values=('0', 'Hagis_1'))
            elif elem == 'Distributions_2':
                combobox.config(values=('0', 'Hagis_2 (testing now)'))
            elif elem == 'Orbit_Finder':
                combobox.config(values=('0', 'Finder (testing now)'))
            elif elem == 'Stability_code':
                combobox.config(values=('0', 'Ligka_m5', 'Ligka_m4',
                                        'Ligka_m1', 'Ligka_m2', 'Ligka_m6', 'Ligka_m3'))
            else:
                combobox.config(values=('0', workflow_param[ref][elem][0]))
            entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                              ref=act_ref: update_xml_param_wf(workflow_param, ref, elem, entrystring.get()))
            irow += 1

    # BUTTONS

    # left:
    button_saveconfig = Button(fr_wfp, text='Save Configuration', bg=col.c2)
    button_saveconfig.grid(row=51, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(
        command=lambda: saved_folder.Save(None, init_folder))

    button_saveconfig = Button(fr_wfp, text='Save Configuration as', bg=col.c2)
    button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(command=lambda: saved_folder.Save(filedialog.askdirectory(
        initialdir=os.path.join(os.getcwd(), 'user_profiles')), init_folder))

    button_run_nosave = Button(fr_wfp, text='Save and Run', bg=col.c2)
    button_run_nosave.grid(row=51, column=1, padx=5, pady=5, sticky='ew')
    button_run_nosave.configure(command=lambda: run(
        saved_folder.Save(None, init_folder)))

    button_restore_def = Button(fr_wfp, text='Restore Default', bg=col.c2)
    button_restore_def.grid(row=53, column=0, padx=5, pady=5, sticky='ew')
    button_restore_def.configure(
        command=lambda: open_gui(wf_param_folder_default))

    button_analysis = Button(fr_wfp, text='Load Configuration', bg=col.c2)
    button_analysis.grid(row=52, column=1, padx=5, pady=5, sticky='ew')
    button_analysis.configure(command=lambda: load(filedialog.askdirectory(
        initialdir=os.path.join(os.getcwd(), 'user_profiles')), open_gui))

    button_analysis = Button(
        fr_wfp, text='LIGKA Analysis (Testing)', bg=col.c2)
    button_analysis.grid(row=53, column=1, padx=5, pady=5, sticky='ew')
    button_analysis.configure(command=lambda: analysis_window(
        ana_ref, analysis_param, wf_param_folder))

    button_scenario = Button(
        fr_wfp, text='Scenario Summary Choice', bg='light grey')
    button_scenario.grid(row=54, column=1, padx=5, pady=5, sticky='w')
    button_scenario.configure(command=lambda: scenario_window(wf_param_folder))

    button_exit = Button(fr_wfp, text='Exit', bg='light grey')
    button_exit.grid(row=55, column=0, padx=5, pady=5, sticky='w')
    button_exit.configure(command=lambda: sys.exit())

    # BUTONS RIGHT SIDE:

    button_saveconfig = Button(fr_as, text='HELENA Parameters', bg=col.c2)
    button_saveconfig.grid(row=53, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(
        command=lambda: actor_window(wfp_ref_hel, wf_param_folder, 3))

    button_saveconfig = Button(fr_as, text='LIGKA Parameters', bg=col.c2)
    button_saveconfig.grid(row=54, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(
        command=lambda: actor_window(wfp_ref_l, wf_param_folder, 0))

    button_saveconfig = Button(fr_as, text='HAGIS 1 Parameters', bg=col.c2)
    button_saveconfig.grid(row=55, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(
        command=lambda: actor_window(wfp_ref_h, wf_param_folder, 1))

    button_saveconfig = Button(fr_as, text='HAGIS 2 Parameters', bg=col.c2)
    button_saveconfig.grid(row=56, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(
        command=lambda: actor_window(wfp_ref_h2, wf_param_folder, 2))

    button_saveconfig = Button(fr_as, text='FINDER Parameters', bg=col.c2)
    button_saveconfig.grid(row=57, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(
        command=lambda: actor_window(wfp_ref_f, wf_param_folder, 4))

    button_saveconfig = Button(fr_as, text='Species Settings', bg=col.c2)
    button_saveconfig.grid(row=58, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(
        command=lambda: actor_window(species_ref, wf_param_folder, 5))

    button_saveconfig = Button(fr_as, text='SCENARIO Parameters', bg=col.c2)
    button_saveconfig.grid(row=59, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(
        command=lambda: actor_window(scen_ref, wf_param_folder, 6))

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

    def run(current_config_folder):
        saved_folder.Save(None, init_folder)
        if current_config_folder is not None:
            workflow_EP(current_config_folder)
        else:
            print('Aborted.')

    window.mainloop()


if __name__ == "__main__":

    open_gui(wf_param_folder_default)
