from tkinter import *
from tkinter import filedialog, ttk
from lxml import etree
import interface.colour_definitions as col
from interface.create_workflow_param import create_workflow_param_from_file, create_xml_param_from_file, save_xml_param_to_file, update_xml_param, update_xml_param_wf
from workflow.analysis_modes import mode_analysis_ligka, export_data
import os
import sys
import glob
import yaml
import argparse
import re
from operator import itemgetter
from shutil import copy2
from stat import *


class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def copy_workflow_param_to_file(previous_folder, current_wf_param_folder, wf_param_folder_default, workflow_param, wfp_ref, fur_ref, act_ref, saveAs):

    # Copy the default workflow parameter file into the current one

    copy2(wf_param_folder_default+'/input_workflow_default.xml',
          current_wf_param_folder, follow_symlinks=True)

    tree = etree.parse(current_wf_param_folder+'/input_workflow_default.xml')
    root = tree.getroot()
    rl = [wfp_ref, fur_ref, act_ref]
    for iroot in range(3):
        for elem in root[iroot].iter():
            if elem.tag is not etree.Comment and len(elem) == 0:
                elem.text = workflow_param[rl[iroot]][elem.tag][0]
    tree.write(current_wf_param_folder+'/input_workflow_default.xml')

    # Copy the actors xml files into the current dir
    # Only in case of saveAs, because the individual .xml of the actors are saved separately
    if saveAs == 1:
        for ep_files in ['analysis.xml', 'finder_input.xml', 'hagis1.xml', 'hagis2.xml', 'helena.xml', 'z_ligka.xml', 'actor_settings.xml', 'scenario.xml', 'ids_merge.xml']:
            if previous_folder is not None:
                copy2(previous_folder+'/'+ep_files,
                      current_wf_param_folder, follow_symlinks=True)
            else:
                copy2(wf_param_folder_default+'/'+ep_files,
                      current_wf_param_folder, follow_symlinks=True)

    return 0


def load(chosen_folder, open_gui):

    if chosen_folder is () or chosen_folder == '':
        print('Load cancelled', file=sys.stderr)
        return

    # Check if the chosen folder is a valid configuration folder
    if not os.path.exists(chosen_folder+'/input_workflow_default.xml'):
        print('The selected folder '+chosen_folder +
              ' does not appear to be a proper', file=sys.stderr)
        print('configuration folder since it contains no input_workflow_default.xml file ' +
              '--> Nothing loaded.', file=sys.stderr)
        return
    for ep_files in ['analysis.xml', 'finder_input.xml', 'hagis1.xml', 'hagis2.xml', 'helena.xml', 'z_ligka.xml', 'actor_settings.xml', 'scenario.xml', 'ids_merge.xml']:
        if not os.path.exists(chosen_folder+'/'+ep_files):
            print('The selected folder '+chosen_folder +
                  ' does not appear to be a proper', file=sys.stderr)
            print('configuration folder since it contains no ' +
                  ep_files+' file '+'--> Nothing loaded.', file=sys.stderr)
            return

    print('---> Configuration loaded from '+chosen_folder, file=sys.stdout)
    open_gui(chosen_folder)


def save(current_config_folder, previous_folder, wf_param_folder_default, workflow_param, wfp_ref, fur_ref, act_ref, saveAs):

    from datetime import datetime

    # Define the current folder (either chosen by the system with 'save'
    # or by the user with 'save as')
    if current_config_folder is None:
        first_save = 1
        current_config_folder = os.path.join(
            os.getcwd(), 'user_profiles/run_'+datetime.now().strftime('%y%m%d_%H:%M:%S'))
    else:
        first_save = 0

    # When operation is cancelled from the interface
    if current_config_folder is () or current_config_folder == '':
        print('Save_as cancelled.', file=sys.stderr)
        return None

    if not os.path.exists(current_config_folder):
        os.mkdir(current_config_folder)

    # Copy/update the workflow parameter file if changed from the interface
    err = copy_workflow_param_to_file(previous_folder, current_config_folder,
                                      wf_param_folder_default, workflow_param, wfp_ref, fur_ref, act_ref, saveAs)

    if err == 0:
        print('---> Configuration saved in ' +
              current_config_folder, file=sys.stdout)
    else:
        current_config_folder = None

    return current_config_folder


def actor_window(wfp_ref_l, wf_param_folder, l):

    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    window_a = Toplevel()
    if l == 0:
        window_a.title('LIGKA PARAMETERS')
        ligka_param = create_xml_param_from_file(
            wf_param_folder+'/z_ligka.xml')
    elif l == 1:
        window_a.title('HAGIS 1 PARAMETERS')
        ligka_param = create_xml_param_from_file(wf_param_folder+'/hagis1.xml')
    elif l == 2:
        window_a.title('HAGIS 2 PARAMETERS')
        ligka_param = create_xml_param_from_file(wf_param_folder+'/hagis2.xml')
    elif l == 3:
        window_a.title('HELENA PARAMETERS')
        ligka_param = create_xml_param_from_file(wf_param_folder+'/helena.xml')
    elif l == 4:
        window_a.title('FINDER PARAMETERS')
        ligka_param = create_xml_param_from_file(
            wf_param_folder+'/finder_input.xml')
    elif l == 5:
        window_a.title('SPECIES SETTINGS')
        ligka_param = create_xml_param_from_file(
            wf_param_folder+'/actor_settings.xml')
    elif l == 6:
        window_a.title('SCENARIO PARAMETERS')
        ligka_param = create_xml_param_from_file(
            wf_param_folder+'/scenario.xml')

    window_a.configure(bg=col.c1)

    try:
        wh = window_a.winfo_reqheight()
        ww = window_a.winfo_reqwidth()
        wx = window_a.winfo_x()
        wy = window_a.winfo_y()
        window_a.geometry("+%d+%d" % (wx, wy))
    except:
        pass

    fr_l = Frame(window_a, width=350, height=500, background=col.c2)
    fr_l.grid(row=0, column=0, rowspan=2,  sticky='nwes', padx=3, pady=3)

    canvas = Canvas(fr_l, width=350, height=500, background=col.c2)
    canvas.grid(row=0, column=0, sticky="nsew")

    canvasFrame = Frame(canvas, background=col.c2)
    canvas.create_window(0, 0, window=canvasFrame, anchor='nw')

    irow = 0
    for ref in wfp_ref_l:

        Label(canvasFrame, text=ref, bg=col.c3, font='15').grid(
            row=irow, column=0, columnspan=3, pady=10, padx=5, sticky='we')
        irow += 1

        for elem in ligka_param[ref]:

            Label(canvasFrame, text=elem, bg=col.c3).grid(
                row=irow,  column=0, padx=3, pady=2, sticky='w')
            if elem == 'DT':
                entrystring = StringVar()
                entrystring.set(ligka_param[ref][elem])
                c = Checkbutton(canvasFrame, variable=entrystring)
                c.grid(row=irow, column=1, padx=3, pady=2, sticky='e')
                entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                  ref=ref: update_xml_param(ligka_param, ref, elem, entrystring.get()))

            else:

                entrystring = StringVar()
                entrystring.set(ligka_param[ref][elem])
                entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                  ref=ref: update_xml_param(ligka_param, ref, elem, entrystring.get()))
                Entry(canvasFrame, textvariable=entrystring, bg=col.c1).grid(
                    row=irow, column=1, padx=3, pady=2, sticky='e')
            irow += 1

    scroll = Scrollbar(fr_l, orient=VERTICAL)
    scroll.config(command=canvas.yview)
    canvas.config(yscrollcommand=scroll.set)
    scroll.grid(row=0, column=2, sticky="ns")

    canvasFrame.bind("<Configure>", update_scrollregion)

    if l == 0:
        button_saveconfig = Button(
            fr_l, text='Save LIGKA Configuration', bg=col.c2)
        button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
        button_saveconfig.configure(command=lambda: save_xml_param_to_file(
            ligka_param, wf_param_folder+'/z_ligka.xml'))
    elif l == 1:
        button_saveconfig = Button(
            fr_l, text='Save HAGIS 1 Configuration', bg=col.c2)
        button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
        button_saveconfig.configure(command=lambda: save_xml_param_to_file(
            ligka_param, wf_param_folder+'/hagis1.xml'))
    elif l == 2:
        button_saveconfig = Button(
            fr_l, text='Save HAGIS 2 Configuration', bg=col.c2)
        button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
        button_saveconfig.configure(command=lambda: save_xml_param_to_file(
            ligka_param, wf_param_folder+'/hagis2.xml'))
    elif l == 3:
        button_saveconfig = Button(
            fr_l, text='Save HELENA Configuration', bg=col.c2)
        button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
        button_saveconfig.configure(command=lambda: save_xml_param_to_file(
            ligka_param, wf_param_folder+'/helena.xml'))
    elif l == 4:
        button_saveconfig = Button(
            fr_l, text='Save FINDER Configuration', bg=col.c2)
        button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
        button_saveconfig.configure(command=lambda: save_xml_param_to_file(
            ligka_param, wf_param_folder+'/finder_input.xml'))
    elif l == 5:
        button_saveconfig = Button(
            fr_l, text='Save Species Configuration', bg=col.c2)
        button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
        button_saveconfig.configure(command=lambda: save_xml_param_to_file(
            ligka_param, wf_param_folder+'/actor_settings.xml'))
    elif l == 6:
        button_saveconfig = Button(
            fr_l, text='Save SCENARIO Configuration', bg=col.c2)
        button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
        button_saveconfig.configure(command=lambda: save_xml_param_to_file(
            ligka_param, wf_param_folder+'/scenario.xml'))


# FUNCTION NEW ANALYSIS WINDOW
def analysis_window(ana_ref, analysis_param, wf_param_folder):
    # create analysis directory if none exists
    analysis_dir = ('workflow/Analysis')
    analysis_dir_check = os.path.isdir(analysis_dir)

    if not analysis_dir_check:
        os.makedirs(analysis_dir)
        print('Analysis folder was created')

    window_an = Toplevel()
    window_an.title('EP Analysis')
    window_an.configure(bg=col.c1)

    try:
        wh = window_an.winfo_reqheight()
        ww = window_an.winfo_reqwidth()
        wx = window_an.winfo_x()
        wy = window_an.winfo_y()
        window_an.geometry("+%d+%d" % (wx, wy))
    except:
        pass

    fr_ana = Frame(window_an, width=300, height=500, background=col.c2)
    fr_ana.grid(row=0, column=0, rowspan=2,  sticky='nwes', padx=3, pady=3)

    # LEFT SIDE
    irow = 0
    for ref in [ana_ref]:

        Label(fr_ana, text=ref, bg=col.c3, font='15').grid(
            row=irow, column=0, columnspan=3, pady=10, padx=5, sticky='we')
        irow += 1

        for elem in analysis_param[ref]:

            Label(fr_ana, text=elem, bg=col.c3).grid(
                row=irow,  column=0, padx=3, pady=2, sticky='w')
            if elem == 'mode':
                entrystring = StringVar()
                entrystring.set(analysis_param[ref][elem])
                Label(fr_ana, text=elem, bg=col.c3).grid(
                    row=irow, column=0, padx=3, pady=2, sticky='w')
                combobox = ttk.Combobox(fr_ana, textvariable=entrystring)
                combobox.grid(row=irow, column=1, padx=3, pady=2, sticky='e')
                combobox.config(values=('5', '4', '1'))
                entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                  ref=ref: update_xml_param(analysis_param, ref, elem, entrystring.get()))
                irow += 1
            elif elem == 'compare_modes':
                entrystring = StringVar()
                entrystring.set(analysis_param[ref][elem])
                c = Checkbutton(fr_ana, variable=entrystring)
                c.grid(row=irow, column=1, padx=3, pady=2, sticky='e')
                entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                  ref=ref: update_xml_param(analysis_param, ref, elem, entrystring.get()))
            else:
                entrystring = StringVar()
                entrystring.set(analysis_param[ref][elem])
                # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
                entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                  ref=ref: update_xml_param(analysis_param, ref, elem, entrystring.get()))
                Entry(fr_ana, textvariable=entrystring, bg=col.c1).grid(
                    row=irow, column=1, padx=3, pady=2, sticky='e')
                irow += 1

    # LEFT SIDE BOTTOM

    button_saveconfig = Button(fr_ana, text='Export Data', bg=col.c2)
    button_saveconfig.grid(row=51, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(command=lambda: export_data(wf_param_folder))

    button_saveconfig = Button(
        fr_ana, text='Save Analysis Configuration', bg=col.c2)
    button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(command=lambda: save_xml_param_to_file(
        analysis_param, wf_param_folder+'/analysis.xml'))

    # RIGHT SIDE TOP

    button_analysis = Button(fr_ana, text='Frequency', bg=col.c2)
    button_analysis.grid(row=1, column=3, padx=5, pady=5, sticky='ew')
    button_analysis.configure(
        command=lambda: mode_analysis_ligka(1, wf_param_folder))

    button_analysis = Button(fr_ana, text='Damping', bg=col.c2)
    button_analysis.grid(row=2, column=3, padx=5, pady=5, sticky='ew')
    button_analysis.configure(
        command=lambda: mode_analysis_ligka(2, wf_param_folder))

    button_analysis = Button(fr_ana, text='Radial Position', bg=col.c2)
    button_analysis.grid(row=3, column=3, padx=5, pady=5, sticky='ew')
    button_analysis.configure(
        command=lambda: mode_analysis_ligka(3, wf_param_folder))

    button_analysis = Button(fr_ana, text='Mode Structure', bg=col.c2)
    button_analysis.grid(row=4, column=3, padx=5, pady=5, sticky='ew')
    button_analysis.configure(
        command=lambda: mode_analysis_ligka(4, wf_param_folder))

    button_analysis = Button(fr_ana, text='Mode Structure 2D', bg=col.c2)
    button_analysis.grid(row=5, column=3, padx=5, pady=5, sticky='ew')
    button_analysis.configure(
        command=lambda: mode_analysis_ligka(5, wf_param_folder))

    button_analysis = Button(
        fr_ana, text='Radial Position for all modes', bg=col.c2)
    button_analysis.grid(row=6, column=3, padx=5, pady=5, sticky='ew')
    button_analysis.configure(
        command=lambda: mode_analysis_ligka(6, wf_param_folder))

    # button_analysis = Button(fr_ana, text = 'Rational Surfaces / q - profile', bg = col.c2)
    # button_analysis.grid(row = 4, column = 3, padx = 5, pady = 5, sticky = 'ew')
    # button_analysis.configure(command = lambda: mode_analysis_ligka(5))


def scenario_window(wf_param_folder):
    shots_runs = []
    shots = []

    def OnDoubleClick(event):
        item = tv.selection()
        item = tv.selection()[0]
        item_run = tv.item(tv.focus())
        if tv.item(item, 'text') not in shots:
            shots.append(tv.item(item, 'text'))
            shots_runs.append((tv.item(item, 'text'), item_run['values'][0]))
        else:
            print('The selected Pulse is already in the list.')
        print('The list is now:', shots_runs)
        workflow_param = create_workflow_param_from_file(
            wf_param_folder+'/input_workflow_default.xml')
        fur_ref = list(workflow_param.keys())[1]
        if workflow_param[fur_ref]['pulse_list'] == '1':
            with open('shots.dat', 'w') as f:
                f.write(repr(shots_runs))
        else:
            print(
                'Please check the pulse_list box in order to save the selected shots and runs')

    window_a = Toplevel()
    window_a.title('Scenario Selector')
    window_a.configure(bg=col.c1)

    try:
        wh = window_a.winfo_reqheight()
        ww = window_a.winfo_reqwidth()
        wx = window_a.winfo_x()
        wy = window_a.winfo_y()
        window_a.geometry("+%d+%d" % (wx, wy))
    except:
        pass

    frame = Frame(window_a)
    frame.pack(fill=BOTH, anchor='n', expand=True)

    bottom_frame = Frame(window_a)
    bottom_frame.pack(side=BOTTOM, anchor='s')

    closeButton = Button(bottom_frame, text='Close')
    closeButton.pack(side=BOTTOM, padx=5, pady=5)
    closeButton.configure(command=lambda: window_a.destroy())

    tv = ttk.Treeview(frame)
    tv['columns'] = ('run', 'database', 'reference', 'ip',
                     'b0', 'fuelling', 'confinement', 'workflow')
    tv.heading('#0', text='Pulse', anchor='w')
    tv.column('#0', anchor='w', width=100)
    tv.heading('run', text='Run')
    tv.column('run', anchor='center', width=100)
    tv.heading('database', text='Database')
    tv.column('database', anchor='center', width=100)
    tv.heading('reference', text='Reference')
    tv.column('reference', anchor='center', width=300)
    tv.heading('ip', text='Ip[MA]')
    tv.column('ip', anchor='center', width=100)
    tv.heading('b0', text='B0[T]')
    tv.column('b0', anchor='center', width=100)
    tv.heading('fuelling', text='Fuelling')
    tv.column('fuelling', anchor='center', width=100)
    tv.heading('confinement', text='Confinement')
    tv.column('confinement', anchor='center', width=100)
    tv.heading('workflow', text='Workflow')
    tv.column('workflow', anchor='center', width=100)
    tv.grid(sticky='nsew')
    treeview = tv
    tv.pack(side=TOP, fill=BOTH, expand=True)
    tv.grid_rowconfigure(0, weight=1)
    tv.grid_columnconfigure(0, weight=1)

    # RETRIEVE AND SELECT DATA
    trunc_number = 50
    extension = '.yaml'
    path = '/work/imas/shared/imasdb/ITER/3/0'
    files = glob.glob(path + "/*")
    data = {}
    # Fill data dictionary with yaml input files describing simulations
    j = -1
    for i in range(len(files)):
        if files[i].endswith(extension):  # Work on all YAML files
            try:
                j = j + 1
                file = open(files[i], 'r')
                data[j] = yaml.load(file, Loader=yaml.CLoader)
                data[j]['location'] = files[i]
                file.close()
            except:
                print('Error reading yaml '+files[i], file=sys.stderr)
    # Sort data as a function of shot and run numbers
    sorted_indices = sorted(
        data, key=lambda x: data[x]['characteristics']['shot']+data[x]['characteristics']['run'])
    sdata = {}
    for i in range(len(data)):
        sdata[i] = data[sorted_indices[i]]
    # FILL WITH DATA
    j = 2
    for i in range(len(sdata)):
        if sdata[i]['status'] == 'active':
            j = j + 1
            shot = sdata[i].get('characteristics').get('shot')
            run = sdata[i].get('characteristics').get('run')
            database = sdata[i].get('characteristics').get('machine')
            ref_name = sdata[i].get('reference_name')[0:trunc_number]
            ip = sdata[i].get('scenario_key_parameters').get('plasma_current')
            b0 = sdata[i].get('scenario_key_parameters').get('magnetic_field')
            fuelling = sdata[i].get(
                'scenario_key_parameters').get('main_species')
            confinement = sdata[i].get(
                'scenario_key_parameters').get('confinement_regime')
            workflow = sdata[i].get('characteristics').get('workflow')
            tv.insert('', 'end', text=shot, values=(run, database,
                                                    ref_name, ip, b0, fuelling, confinement, workflow))
    tv.bind("<Double-1>", OnDoubleClick)
