# --------------------------------------------
# Analysis componenet for Python EP workflow
# --------------------------------------------


# NEEDED MODULES
from ep_stability_wf.interface.create_workflow_param import create_xml_param_from_file
import subprocess


def run_analysis(wf_param_folder, l):
    analysis_param = create_xml_param_from_file(wf_param_folder+'/analysis.xml')
    ana_ref = list(analysis_param.keys())[0]
    if analysis_param[ana_ref]['model'] == '5':
        occurrence = 0
    elif analysis_param[ana_ref]['model'] == '4':
        occurrence = 1
    elif analysis_param[ana_ref]['model'] == '1':
        occurrence = 2
    elif analysis_param[ana_ref]['model'] == '2':
        occurrence = 6
    if l == 0:
        print('Running Frequency Plot')
        result = subprocess.run(["general_plots_ids.py", f"-user={analysis_param[ana_ref]['user']}", f"-database={analysis_param[ana_ref]['database']}", f"-shot={analysis_param[ana_ref]['shot_number']}", f"-run={analysis_param[ana_ref]['run']}", f"-occurrence={occurrence}", f"-type=frequency", f"-interactivePlots=0", f"-compare_modes={analysis_param[ana_ref]['compare_modes']}" ], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    if l == 1:
        print('Running Damping Plot')
        result = subprocess.run(["general_plots_ids.py", f"-user={analysis_param[ana_ref]['user']}", f"-database={analysis_param[ana_ref]['database']}", f"-shot={analysis_param[ana_ref]['shot_number']}", f"-run={analysis_param[ana_ref]['run']}", f"-occurrence={occurrence}", f"-type=damping", f"-interactivePlots=0", f"-compare_modes={analysis_param[ana_ref]['compare_modes']}"], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    if l == 2:
        print('Running Radial Location Plot')
        result = subprocess.run(["general_plots_ids.py", f"-user={analysis_param[ana_ref]['user']}", f"-database={analysis_param[ana_ref]['database']}", f"-shot={analysis_param[ana_ref]['shot_number']}", f"-run={analysis_param[ana_ref]['run']}", f"-occurrence={occurrence}", f"-type=radial_location", f"-interactivePlots=0", f"-compare_modes={analysis_param[ana_ref]['compare_modes']}"], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
    if l == 3:
        print(f'Running Mode Structure: {analysis_param}')
        result = subprocess.run(["plot_EF_ids.py", f"-user={analysis_param[ana_ref]['user']}", f"-database={analysis_param[ana_ref]['database']}", f"-shot={analysis_param[ana_ref]['shot_number']}", f"-run={analysis_param[ana_ref]['run']}", f"-occurrence={occurrence}", f"-interactivePlots=0"], capture_output=True, text=True)
        print(result.stdout)

    print('Done, please check the results!')
