from tkinter import * 
from tkinter import filedialog, ttk
from lxml import etree
import os, sys
import interface.colour_definitions as col
from interface.create_workflow_param import update_xml_param, save_xml_param_to_file
from workflow.analysis_modes import analysis_ligka_mode5,analysis_ligka_mode2,analysis_ligka_mode1




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
def analysis_window():
  #create analysis directory if none exists
  analysis_dir = ('workflow/Analysis')
  analysis_dir_check = os.path.isdir(analysis_dir)

  if not analysis_dir_check:
    os.makedirs(analysis_dir)
    print('Analysis folder was created')

  window_a = Tk()
  window_a.title('LIGKA Analysis')
  window_a.configure(bg = col.c1)
  window_a.geometry('300x500')

  fr_ana = Frame(window_a, width = 300, height = 500, background = col.c2)
  fr_ana.grid(row = 0, column = 0, rowspan = 2,  sticky = 'nwes', padx = 3, pady = 3)

  button_analysis = Button(fr_ana, text = 'Mode 5', bg = col.c2)
  button_analysis.grid(row = 5, column = 0, padx = 5, pady = 5, sticky = 'ew')
  button_analysis.configure(command = lambda: analysis_ligka_mode5())

  button_analysis = Button(fr_ana, text = 'Mode 1', bg = col.c2)
  button_analysis.grid(row = 6, column = 0, padx = 5, pady = 5, sticky = 'ew')
  button_analysis.configure(command = lambda: analysis_ligka_mode1())

  button_analysis = Button(fr_ana, text = 'Mode 2', bg = col.c2)
  button_analysis.grid(row = 7, column = 0, padx = 5, pady = 5, sticky = 'ew')
  button_analysis.configure(command = lambda: analysis_ligka_mode2())
