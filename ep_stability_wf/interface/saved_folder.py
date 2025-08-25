from ep_stability_wf.interface.extra_functions import save

class saved_folder_name(object):
    def __init__(self):
        self.value = None

    def NoAction(self):
        self.value = self.value

    def Save(self, chosen_folder, init_folder, wf_param_folder_default, workflow_param, wfp_ref, fur_ref, act_ref):
        previous_folder = init_folder
        if chosen_folder == init_folder:
            if self.value is None:# Very first SAVE, or SAVE after a SAVE_AS
                self.value = save(
                    chosen_folder,
                    previous_folder,
                    wf_param_folder_default,
                    workflow_param,
                    wfp_ref,
                    fur_ref,
                    act_ref,
                    0,
                )
        else:
            if chosen_folder is None:
                if self.value is None:  # 1st SAVE after a LOAD
                    self.value = save(
                        init_folder,
                        previous_folder,
                        wf_param_folder_default,
                        workflow_param,
                        wfp_ref,
                        fur_ref,
                        act_ref,
                        0,
                    )
                else:  # Next SAVEs after a LOAD; SAVE after a SAVE AS which is after a LOAD;
                    self.value = save(
                        self.value,
                        previous_folder,
                        wf_param_folder_default,
                        workflow_param,
                        wfp_ref,
                        fur_ref,
                        act_ref,
                        0,
                    )
            else:  # SAVE AS
                if_cancelled = self.value
                self.value = save(
                    chosen_folder,
                    previous_folder,
                    wf_param_folder_default,
                    workflow_param,
                    wfp_ref,
                    fur_ref,
                    act_ref,
                    1,
                )
                if self.value is None:
                    self.value = if_cancelled
        return self.value