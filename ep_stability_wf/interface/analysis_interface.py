from tkinter import *
from tkinter import ttk
import ep_stability_wf.interface.colour_definitions as col
from ep_stability_wf.interface.create_workflow_param import (
    save_xml_param_to_file,
    update_xml_param,
    create_xml_param_from_file,
)
from ep_stability_wf.workflow.analysis_modes import run_analysis
from ep_stability_wf.workflow.functions_wf import parameters_workflow
import os
from shutil import copy2
from stat import *


def save_analysis_open_window(analysis_param, wf_param_folder, label):
    save_xml_param_to_file(analysis_param, wf_param_folder + "/analysis.xml")
    if label == "Frequency and Damping":
        return window_frequency_damping(wf_param_folder)
    elif label == "Mode Structure":
        return window_mode_structure(wf_param_folder)


# FUNCTION NEW ANALYSIS WINDOW
def analysis_window(ana_ref, analysis_param, wf_param_folder):
    options_to_diplay = ["user", "database", "backend", "version", "shot_number", "run"]
    # create analysis directory if none exists
    analysis_dir = "./Analysis_EP_WF"
    analysis_dir_check = os.path.isdir(analysis_dir)

    if not analysis_dir_check:
        os.makedirs(analysis_dir)
        print("Analysis folder was created")

    window_an = Toplevel()
    window_an.title("EP Analysis")
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
    fr_ana.grid(row=0, column=0, rowspan=2, sticky="nwes", padx=3, pady=3)

    # LEFT SIDE
    irow = 0
    for ref in [ana_ref]:
        Label(fr_ana, text=ref, bg=col.c3, font="15").grid(
            row=irow, column=0, columnspan=3, pady=10, padx=5, sticky="we"
        )
        irow += 1

        for elem in analysis_param[ref]:
            if elem in options_to_diplay:
                Label(fr_ana, text=elem, bg=col.c3).grid(
                    row=irow, column=0, padx=3, pady=3, sticky="w"
                )
                if elem == "backend":
                    entrystring = StringVar()
                    entrystring.set(analysis_param[ref][elem])
                    Label(fr_ana, text=elem, bg=col.c3).grid(
                        row=irow, column=0, padx=3, pady=3, sticky="w"
                    )
                    combobox = ttk.Combobox(fr_ana, textvariable=entrystring)
                    combobox.grid(row=irow, column=1, padx=3, pady=3, sticky="e")
                    combobox.config(values=("HDF5", "MDSPlus"))
                    entrystring.trace(
                        "w",
                        lambda name, index, mode, elem=elem, entrystring=entrystring, ref=ref: update_xml_param(
                            analysis_param, ref, elem, entrystring.get()
                        ),
                    )
                    irow += 1
                else:
                    entrystring = StringVar()
                    entrystring.set(analysis_param[ref][elem])
                    # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
                    entrystring.trace(
                        "w",
                        lambda name, index, mode, elem=elem, entrystring=entrystring, ref=ref: update_xml_param(
                            analysis_param, ref, elem, entrystring.get()
                        ),
                    )
                    Entry(fr_ana, textvariable=entrystring, bg=col.c1).grid(
                        row=irow, column=1, padx=3, pady=3, sticky="e"
                    )
                    irow += 1

    # RIGHT SIDE TOP
    button_analysis = Button(
        fr_ana, text="Frequency, Damping or Radial Location", bg=col.c2
    )
    button_analysis.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
    button_analysis.configure(
        command=lambda: save_analysis_open_window(
            analysis_param, wf_param_folder, label="Frequency and Damping"
        )
    )

    # button_analysis = Button(fr_ana, text='Radial Position', bg=col.c2)
    # button_analysis.grid(row=3, column=3, padx=5, pady=5, sticky='ew')
    # button_analysis.configure(
    #     command=lambda: Plot(3, wf_param_folder))

    button_analysis = Button(fr_ana, text="Mode Structure", bg=col.c2)
    button_analysis.grid(row=4, column=3, padx=5, pady=5, sticky="ew")
    button_analysis.configure(
        command=lambda: save_analysis_open_window(
            analysis_param, wf_param_folder, label="Mode Structure"
        )
    )


def window_frequency_damping(wf_param_folder):
    options_to_diplay = [
        "n_min",
        "n_max",
        "m_min",
        "m_max",
        "r_min",
        "r_max",
        "model",
        "compare_modes",
        "itime",
        "save_plots",
        "interactivePlots",
        "label_scaler",
        "line_scaler",
    ]
    analysis_param = create_xml_param_from_file(wf_param_folder + "/analysis.xml")
    ana_ref = list(analysis_param.keys())[0]

    window_an = Toplevel()
    window_an.title("Frequency, Damping & Radial Location Analysis")
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
    fr_ana.grid(row=0, column=0, rowspan=2, sticky="nwes", padx=3, pady=3)

    # LEFT SIDE
    irow = 0
    for ref in [ana_ref]:
        Label(fr_ana, text=ref, bg=col.c3, font="15").grid(
            row=irow, column=0, columnspan=3, pady=10, padx=5, sticky="we"
        )
        irow += 1

        for elem in analysis_param[ref]:
            if elem in options_to_diplay:
                Label(fr_ana, text=elem, bg=col.c3).grid(
                    row=irow, column=0, padx=3, pady=3, sticky="w"
                )
                if elem == "model":
                    entrystring = StringVar()
                    entrystring.set(analysis_param[ref][elem])
                    Label(fr_ana, text=elem, bg=col.c3).grid(
                        row=irow, column=0, padx=3, pady=2, sticky="w"
                    )
                    combobox = ttk.Combobox(fr_ana, textvariable=entrystring)
                    combobox.grid(row=irow, column=1, padx=3, pady=3, sticky="e")
                    combobox.config(values=("5", "4", "1", "2"))
                    entrystring.trace(
                        "w",
                        lambda name, index, mode, elem=elem, entrystring=entrystring, ref=ref: update_xml_param(
                            analysis_param, ref, elem, entrystring.get()
                        ),
                    )
                    irow += 1
                elif elem in ["compare_modes", "save_plots", "interactivePlots"]:
                    entrystring = StringVar()
                    entrystring.set(analysis_param[ref][elem])
                    c = Checkbutton(fr_ana, variable=entrystring)
                    c.grid(row=irow, column=1, padx=3, pady=3, sticky="e")
                    entrystring.trace(
                        "w",
                        lambda name, index, mode, elem=elem, entrystring=entrystring, ref=ref: update_xml_param(
                            analysis_param, ref, elem, entrystring.get()
                        ),
                    )
                    irow += 1
                else:
                    entrystring = StringVar()
                    entrystring.set(analysis_param[ref][elem])
                    # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
                    entrystring.trace(
                        "w",
                        lambda name, index, mode, elem=elem, entrystring=entrystring, ref=ref: update_xml_param(
                            analysis_param, ref, elem, entrystring.get()
                        ),
                    )
                    Entry(fr_ana, textvariable=entrystring, bg=col.c1).grid(
                        row=irow, column=1, padx=3, pady=3, sticky="e"
                    )
                    irow += 1

    # LEFT SIDE BOTTOM
    button_saveconfig = Button(fr_ana, text="Save Analysis Configuration", bg=col.c2)
    button_saveconfig.grid(row=51, column=0, padx=5, pady=5, sticky="ew")
    button_saveconfig.configure(
        command=lambda: save_xml_param_to_file(
            analysis_param, wf_param_folder + "/analysis.xml"
        )
    )

    button_run_freq = Button(fr_ana, text="Run Frequency", bg=col.c2)
    button_run_freq.grid(row=52, column=0, padx=5, pady=5, sticky="ew")
    button_run_freq.configure(command=lambda: run_analysis(wf_param_folder, 0))

    button_run_damping = Button(fr_ana, text="Run Damping", bg=col.c2)
    button_run_damping.grid(row=53, column=0, padx=5, pady=5, sticky="ew")
    button_run_damping.configure(command=lambda: run_analysis(wf_param_folder, 1))

    button_run_damping = Button(fr_ana, text="Run Radial Location", bg=col.c2)
    button_run_damping.grid(row=54, column=0, padx=5, pady=5, sticky="ew")
    button_run_damping.configure(command=lambda: run_analysis(wf_param_folder, 2))


def window_mode_structure(wf_param_folder):
    options_to_diplay = ["model", "itime", "save_plots", "interactivePlots"]
    analysis_param = create_xml_param_from_file(wf_param_folder + "/analysis.xml")
    ana_ref = list(analysis_param.keys())[0]

    window_an = Toplevel()
    window_an.title("Mode Structure Analysis")
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
    fr_ana.grid(row=0, column=0, rowspan=2, sticky="nwes", padx=3, pady=3)

    # LEFT SIDE
    irow = 0
    for ref in [ana_ref]:
        Label(fr_ana, text=ref, bg=col.c3, font="15").grid(
            row=irow, column=0, columnspan=3, pady=10, padx=5, sticky="we"
        )
        irow += 1

        for elem in analysis_param[ref]:
            if elem in options_to_diplay:
                Label(fr_ana, text=elem, bg=col.c3).grid(
                    row=irow, column=0, padx=3, pady=3, sticky="w"
                )
                if elem == "model":
                    entrystring = StringVar()
                    entrystring.set(analysis_param[ref][elem])
                    Label(fr_ana, text=elem, bg=col.c3).grid(
                        row=irow, column=0, padx=3, pady=3, sticky="w"
                    )
                    combobox = ttk.Combobox(fr_ana, textvariable=entrystring)
                    combobox.grid(row=irow, column=1, padx=3, pady=3, sticky="e")
                    combobox.config(values=("5", "4", "1", "2"))
                    entrystring.trace(
                        "w",
                        lambda name, index, mode, elem=elem, entrystring=entrystring, ref=ref: update_xml_param(
                            analysis_param, ref, elem, entrystring.get()
                        ),
                    )
                    irow += 1
                elif elem in ["save_plots", "interactivePlots"]:
                    entrystring = StringVar()
                    entrystring.set(analysis_param[ref][elem])
                    c = Checkbutton(fr_ana, variable=entrystring)
                    c.grid(row=irow, column=1, padx=3, pady=3, sticky="e")
                    entrystring.trace(
                        "w",
                        lambda name, index, mode, elem=elem, entrystring=entrystring, ref=ref: update_xml_param(
                            analysis_param, ref, elem, entrystring.get()
                        ),
                    )
                    irow += 1
                else:
                    entrystring = StringVar()
                    entrystring.set(analysis_param[ref][elem])
                    # if an entry is changed, the new values should immediately be changed in the workflow_param dictionary
                    entrystring.trace(
                        "w",
                        lambda name, index, mode, elem=elem, entrystring=entrystring, ref=ref: update_xml_param(
                            analysis_param, ref, elem, entrystring.get()
                        ),
                    )
                    Entry(fr_ana, textvariable=entrystring, bg=col.c1).grid(
                        row=irow, column=1, padx=3, pady=3, sticky="e"
                    )
                    irow += 1

    # LEFT SIDE BOTTOM

    button_saveconfig = Button(fr_ana, text="Save Analysis Configuration", bg=col.c2)
    button_saveconfig.grid(row=51, column=0, padx=5, pady=5, sticky="ew")
    button_saveconfig.configure(
        command=lambda: save_xml_param_to_file(
            analysis_param, wf_param_folder + "/analysis.xml"
        )
    )

    button_run_freq = Button(fr_ana, text="Run Mode Structure", bg=col.c2)
    button_run_freq.grid(row=52, column=0, padx=5, pady=5, sticky="ew")
    button_run_freq.configure(command=lambda: run_analysis(wf_param_folder, 3))
