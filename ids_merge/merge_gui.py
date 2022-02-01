from tkinter import *
from tkinter import ttk

import os
from ids_merge.merge import ids_compare
import interface.colour_definitions as col
from interface.create_workflow_param import save_xml_param_to_file_multiple, create_workflow_param_from_file, save_xml_param_to_file, update_xml_param, update_xml_param_wf
from interface.extra_functions import CreateToolTip

# FUNCTION NEW ANALYSIS WINDOW


def ids_window(ids_ref, wf_param_folder):

    window_ids = Toplevel()

    window_ids.title('IDS Merge')
    ids_merge_param = create_workflow_param_from_file(
        wf_param_folder+'/ids_merge.xml')

    window_ids.configure(bg=col.c1)

    try:
        wh = window_ids.winfo_reqheight()
        ww = window_ids.winfo_reqwidth()
        wx = window_ids.winfo_x()
        wy = window_ids.winfo_y()
        window_ids.geometry("+%d+%d" % (wx, wy))
    except:
        pass

    fr_l = Frame(window_ids, width=250, height=500, background=col.c2)
    fr_l.grid(row=0, column=0, rowspan=2,
              sticky='nwes', padx=3, pady=3)

    fr_l_settings = Frame(window_ids, width=250, height=500, background=col.c2)
    fr_l_settings.grid(row=0, column=1, rowspan=2,
                       sticky='nwes', padx=3, pady=3)

    irow = 0
    for ref in ids_ref:
        if ref == 'Inputs:' or ref == 'Output:':
            Label(fr_l, text=ref, bg=col.c3, font='15').grid(
                row=irow, column=0, columnspan=2, pady=5, padx=5, sticky='we')
            irow += 1
            for elem in ids_merge_param[ref]:

                Label(fr_l, text=elem, bg=col.c3).grid(
                    row=irow,  column=0, padx=2, pady=2, sticky='w')
                if elem in ['HDF5_1', 'HDF5_2', 'HDF5_out']:
                    entrystring = StringVar()
                    entrystring.set(ids_merge_param[ref][elem][0])
                    c = Checkbutton(fr_l, variable=entrystring)
                    c.grid(row=irow, column=1, padx=3, pady=2, sticky='e')
                    CreateToolTip(c, text=ids_merge_param[ref][elem][1])
                    entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                      ref=ref: update_xml_param_wf(ids_merge_param, ref, elem, entrystring.get()))
                    irow += 1
                else:
                    entrystring = StringVar()
                    entrystring.set(ids_merge_param[ref][elem][0])
                    entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                      ref=ref: update_xml_param_wf(ids_merge_param, ref, elem, entrystring.get()))
                    Entry(fr_l, textvariable=entrystring, bg=col.c1).grid(
                        row=irow, column=1, padx=3, pady=2, sticky='e')
                    irow += 1
        else:
            irow = 0
            Label(fr_l_settings, text=ref, bg=col.c3, font='15').grid(
                row=irow, column=1, columnspan=2, pady=5, padx=5, sticky='we')
            irow += 1

            for elem in ids_merge_param[ref]:

                Label(fr_l_settings, text=elem, bg=col.c3).grid(
                    row=irow,  column=0, padx=2, pady=2, sticky='w')
                if elem == 'itime':
                    entrystring = StringVar()
                    entrystring.set(ids_merge_param[ref][elem][0])
                    entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                      ref=ref: update_xml_param_wf(ids_merge_param, ref, elem, entrystring.get()))
                    Entry(fr_l_settings, textvariable=entrystring, bg=col.c1).grid(
                        row=irow, column=1, padx=3, pady=2, sticky='e')
                    irow += 1
                else:
                    entrystring = StringVar()
                    entrystring.set(ids_merge_param[ref][elem][0])
                    c = Checkbutton(fr_l_settings, variable=entrystring)
                    c.grid(row=irow, column=1, padx=3, pady=2, sticky='e')
                    CreateToolTip(c, text=ids_merge_param[ref][elem][1])
                    entrystring.trace('w', lambda name, index, mode, elem=elem, entrystring=entrystring,
                                      ref=ref: update_xml_param_wf(ids_merge_param, ref, elem, entrystring.get()))
                    irow += 1

    button_saveconfig = Button(
        fr_l, text='Save IDS_MERGE Configuration', bg=col.c2)
    button_saveconfig.grid(row=52, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(command=lambda: save_xml_param_to_file_multiple(
        ids_merge_param, wf_param_folder+'/ids_merge.xml'))

    button_saveconfig = Button(
        fr_l, text='Run IDS_MERGE', bg=col.c2)
    button_saveconfig.grid(row=53, column=0, padx=5, pady=5, sticky='ew')
    button_saveconfig.configure(command=lambda: ids_compare(ids_merge_param))
