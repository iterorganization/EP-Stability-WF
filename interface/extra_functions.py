from tkinter import * 
from tkinter import filedialog, ttk
from lxml import etree
import interface.colour_definitions as col
from interface.create_workflow_param import create_workflow_param_from_file, create_xml_param_from_file, save_xml_param_to_file, update_xml_param
from workflow.analysis_modes import mode_analysis_ligka
import os, sys, glob, yaml, argparse, re
from operator import itemgetter
from stat import *



def actor_window(wfp_ref_l, ligka_param, l):

  window_a = Toplevel()
  if l ==0:
    window_a.title('LIGKA Parameters')
  else:
    window_a.title('HAGIS 1 PARAMETERS')
  window_a.configure(bg = col.c1)
  
  try:
    wh = window_a.winfo_reqheight()
    ww = window_a.winfo_reqwidth()
    wx = window_a.winfo_x()
    wy = window_a.winfo_y()
    window_a.geometry("+%d+%d" %(wx, wy))
  except: 
    pass   
  
  fr_l = Frame(window_a, width = 300, height = 500, background = col.c2)
  fr_l.grid(row = 0, column = 0, rowspan = 2,  sticky = 'nwes', padx = 3, pady = 3)

  irow = 0
  for ref in wfp_ref_l:
      
      Label(fr_l, text = ref, bg = col.c3, font = '15').grid(row = irow, column = 0, columnspan = 3, pady = 10, padx = 5, sticky = 'we')
      irow += 1

      for elem in ligka_param[ref]:
          
          Label(fr_l, text = elem, bg = col.c3).grid(row = irow,  column = 0, padx = 3, pady = 2, sticky = 'w')

          entrystring = StringVar()
          entrystring.set(ligka_param[ref][elem])
          entrystring.trace('w', lambda name, index, mode, elem = elem, entrystring = entrystring, ref = ref: update_xml_param(ligka_param, ref, elem, entrystring.get()))                      # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
          Entry(fr_l, textvariable = entrystring, bg = col.c1).grid(row = irow, column = 1, padx = 3, pady = 2, sticky = 'e')
          irow += 1
  if l == 0:
    button_saveconfig = Button(fr_l, text = 'Save LIGKA Configuration', bg = col.c2)
    button_saveconfig.grid(row = 52, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: save_xml_param_to_file(ligka_param, 'workflow/input/z_ligka.xml'))
  else:
    button_saveconfig = Button(fr_l, text = 'Save HAGIS 1 Configuration', bg = col.c2)
    button_saveconfig.grid(row = 52, column = 0, padx = 5, pady = 5, sticky = 'ew')
    button_saveconfig.configure(command = lambda: save_xml_param_to_file(ligka_param, 'workflow/input/hagis1.xml'))


    ## FUNCTION NEW ANALYSIS WINDOW 
def analysis_window(ana_ref, analysis_param):
  #create analysis directory if none exists
  analysis_dir = ('workflow/Analysis')
  analysis_dir_check = os.path.isdir(analysis_dir)

  if not analysis_dir_check:
    os.makedirs(analysis_dir)
    print('Analysis folder was created')

  window_an = Toplevel()
  window_an.title('LIGKA Analysis')
  window_an.configure(bg = col.c1)

  try:
    wh = window_an.winfo_reqheight()
    ww = window_an.winfo_reqwidth()
    wx = window_an.winfo_x()
    wy = window_an.winfo_y()
    window_an.geometry("+%d+%d" %(wx, wy))
  except: 
    pass

  fr_ana = Frame(window_an, width = 300, height = 500, background = col.c2)
  fr_ana.grid(row = 0, column = 0, rowspan = 2,  sticky = 'nwes', padx = 3, pady = 3)

  # LEFT SIDE
  irow = 0
  for ref in [ana_ref]:
      
      Label(fr_ana, text = ref, bg = col.c3, font = '15').grid(row = irow, column = 0, columnspan = 3, pady = 10, padx = 5, sticky = 'we')
      irow += 1

      for elem in analysis_param[ref]:  
          
        Label(fr_ana, text = elem, bg = col.c3).grid(row = irow,  column = 0, padx = 3, pady = 2, sticky = 'w')
        if elem == 'mode':
          entrystring = StringVar()
          entrystring.set(analysis_param[ref][elem])
          Label(fr_ana, text = elem, bg = col.c3).grid(row = irow, column = 0, padx = 3, pady = 2, sticky = 'w')
          combobox = ttk.Combobox(fr_ana, textvariable = entrystring)
          combobox.grid(row = irow, column = 1, padx = 3, pady = 2, sticky = 'e')
          combobox.config(values = ('5', '4', '1'))
          entrystring.trace('w', lambda name, index, mode, elem = elem, entrystring = entrystring, ref = ref: update_xml_param(analysis_param, ref, elem, entrystring.get()))
          irow += 1
        else:
          entrystring = StringVar()
          entrystring.set(analysis_param[ref][elem])
          entrystring.trace('w', lambda name, index, mode, elem = elem, entrystring = entrystring, ref = ref: update_xml_param(analysis_param, ref, elem, entrystring.get()))                      # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
          Entry(fr_ana, textvariable = entrystring, bg = col.c1).grid(row = irow, column = 1, padx = 3, pady = 2, sticky = 'e')
          irow += 1

  button_saveconfig = Button(fr_ana, text = 'Save Analysis Configuration', bg = col.c2)
  button_saveconfig.grid(row = 52, column = 0, padx = 5, pady = 5, sticky = 'ew')
  button_saveconfig.configure(command = lambda: save_xml_param_to_file(analysis_param, 'workflow/input/analysis.xml'))

  # # RIGHT SIDE

  button_analysis = Button(fr_ana, text = 'Frequency', bg = col.c2)
  button_analysis.grid(row = 1, column = 3, padx = 5, pady = 5, sticky = 'ew')
  button_analysis.configure(command = lambda: mode_analysis_ligka(1))

  button_analysis = Button(fr_ana, text = 'Damping', bg = col.c2)
  button_analysis.grid(row = 2, column = 3, padx = 5, pady = 5, sticky = 'ew')
  button_analysis.configure(command = lambda: mode_analysis_ligka(2))

  button_analysis = Button(fr_ana, text = 'Radial Position', bg = col.c2)
  button_analysis.grid(row = 3, column = 3, padx = 5, pady = 5, sticky = 'ew')
  button_analysis.configure(command = lambda: mode_analysis_ligka(3))

  button_analysis = Button(fr_ana, text = 'Mode Structure', bg = col.c2)
  button_analysis.grid(row = 4, column = 3, padx = 5, pady = 5, sticky = 'ew')
  button_analysis.configure(command = lambda: mode_analysis_ligka(4))

  # button_analysis = Button(fr_ana, text = 'Rational Surfaces / q - profile', bg = col.c2)
  # button_analysis.grid(row = 4, column = 3, padx = 5, pady = 5, sticky = 'ew')
  # button_analysis.configure(command = lambda: mode_analysis_ligka(5))



def scenario_window():
  shots_runs= []
  shots = []
  def OnDoubleClick(event):
    item = tv.selection()
    item = tv.selection()[0]
    item_run = tv.item(tv.focus())
    if tv.item(item,'text') not in shots:
      shots.append(tv.item(item,'text'))
      shots_runs.append((tv.item(item,'text'),item_run['values'][0]))
    else:
      print('The selected Pulse is already in the list.')
    print('The list is now:',shots_runs)
    workflow_param = create_workflow_param_from_file('workflow/input/input_workflow_default.xml')
    fur_ref = list(workflow_param.keys())[1]
    if workflow_param[fur_ref]['pulse_list'] == '1':
      with open('shots.dat', 'w') as f:
        f.write(repr(shots_runs))
    else:
      print('Please check the pulse_list box in order to save the selected shots and runs')

  window_a = Toplevel()
  window_a.title('Scenario Selector')
  window_a.configure(bg = col.c1)
  
  try:
    wh = window_a.winfo_reqheight()
    ww = window_a.winfo_reqwidth()
    wx = window_a.winfo_x()
    wy = window_a.winfo_y()
    window_a.geometry("+%d+%d" %(wx, wy))
  except: 
    pass   
  
  frame = Frame(window_a)
  frame.pack(fill = BOTH, anchor = 'n', expand = True)

  bottom_frame = Frame(window_a)
  bottom_frame.pack(side = BOTTOM, anchor = 's')

  closeButton = Button(bottom_frame, text='Close')
  closeButton.pack(side=BOTTOM, padx=5, pady=5)
  closeButton.configure(command = lambda: window_a.destroy())

  tv = ttk.Treeview(frame)
  tv['columns'] = ('run', 'database', 'reference', 'ip', 'b0', 'fuelling', 'confinement', 'workflow')
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
  tv.grid(sticky = 'nsew')
  treeview = tv
  tv.pack(side = TOP,fill = BOTH, expand = True)
  tv.grid_rowconfigure(0, weight = 1)
  tv.grid_columnconfigure(0, weight = 1)



  #RETRIEVE AND SELECT DATA
  trunc_number = 50
  extension = '.yaml'
  path = '/work/imas/shared/imasdb/ITER/3/0'
  files = glob.glob(path + "/*")
  data = {}
  # Fill data dictionary with yaml input files describing simulations
  j = -1
  for i in range(len(files)):
    if files[i].endswith(extension): # Work on all YAML files
      try:
        j = j + 1
        file = open(files[i], 'r')
        data[j] = yaml.load(file,Loader=yaml.CLoader)
        data[j]['location'] = files[i]
        file.close()
      except:
        print('Error reading yaml '+files[i], file=sys.stderr)
  # Sort data as a function of shot and run numbers
  sorted_indices = sorted(data, key = lambda x: data[x]['characteristics']['shot']+data[x]['characteristics']['run'])
  sdata = {}
  for i in range(len(data)):
    sdata[i] = data[sorted_indices[i]]
  #FILL WITH DATA
  j = 2
  for i in range(len(sdata)):
    if sdata[i]['status'] == 'active':
      j = j + 1
      shot          = sdata[i].get('characteristics').get('shot')
      run           = sdata[i].get('characteristics').get('run')
      database      = sdata[i].get('characteristics').get('machine')
      ref_name      = sdata[i].get('reference_name')[0:trunc_number]
      ip            = sdata[i].get('scenario_key_parameters').get('plasma_current')
      b0            = sdata[i].get('scenario_key_parameters').get('magnetic_field')
      fuelling      = sdata[i].get('scenario_key_parameters').get('main_species')
      confinement   = sdata[i].get('scenario_key_parameters').get('confinement_regime')
      workflow      = sdata[i].get('characteristics').get('workflow')
      tv.insert('','end', text = shot, values = (run, database, ref_name, ip, b0, fuelling, confinement, workflow))
  tv.bind("<Double-1>", OnDoubleClick)