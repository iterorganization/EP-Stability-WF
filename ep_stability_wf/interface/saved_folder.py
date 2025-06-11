from ep_stability_wf.interface.extra_functions import save

class saved_folder_name(object):
    def __init__(self):
        self.value = None

    def NoAction(self):
        self.value = self.value

    def Save(self, chosen_folder, init_folder, wf_param_folder_default, workflow_param, wfp_ref, fur_ref, act_ref):
        previous_folder = init_folder
        
        # If chosen_folder is the same as current folder, treat it as a regular save
        if chosen_folder is not None and self.value is not None:
            if chosen_folder == self.value:
                # If it's the same folder, perform a regular save in the current folder
                self.value = save(
                    self.value,
                    previous_folder,
                    wf_param_folder_default,
                    workflow_param,
                    wfp_ref,
                    fur_ref,
                    act_ref,
                    0,  # Use 0 to indicate regular save
                )
                return self.value
        
        if chosen_folder == init_folder:  # Very first SAVE, or SAVE after a SAVE_AS
            self.value = save(
                self.value,
                previous_folder,
                wf_param_folder_default,
                workflow_param,
                wfp_ref,
                fur_ref,
                act_ref,
                1,
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