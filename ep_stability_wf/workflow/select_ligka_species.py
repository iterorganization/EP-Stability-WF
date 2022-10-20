#!/usr/bin/env python

import numpy as np
import warnings

# Dictionary of mappings between (Z,A) and the Ligka species string
# Non-implemented species should return None
# A is optional, can be set to None, in which case all A will match
LIGKA_ZA_STRINGS = {
    (1, 1): "hh",
    (1, 2): "dd",
    (1, 3): "tt",
    # (2, 3): "h3",
    (2, 3): None,
    (2, 4): "he",
    (4, None): "be",
    (5, None): None,
    # (5, None): "bo",
    (6, None): "ca",
    # (7, None): "ni",
    (7, None): None,
    (10, None): "ne",
    # (18, None): None,
    (18, None): "ar",
    (74, None): "tu",
}

# Dictionary of mappings between (Z,A) and the Ligka /fast/ species string
# Non-implemented species should return None
LIGKA_FAST_ZA_STRINGS = {
    (1, 1): "fh",
    (1, 2): "fd",
    #(1, 3): "ft",
    (1, 3): None,
    (2, 4): "al",
}

def get_density_thermal_fast(species_obj:object, modify_ids:bool=False):
    if len(species_obj.density_thermal) > 0:
        density_thermal = species_obj.density_thermal.copy()
    else:
        if len(species_obj.density) > 0:
            dd = species_obj.density
        else:
            dd = None
        if len(species_obj.density_fast) > 0:
            df = species_obj.density_fast
        else:
            df = None

        if dd is None:
            # Only density_fast provided, denisty = density_fast
            dd = df.copy()
        if df is None:
            # Only density provided, denisty_fast = 0
            df = np.zeros_like(dd)

        density_thermal = dd - df

    if len(species_obj.density_fast) == 0:
        if len(species_obj.density > 0):
            density_fast = species_obj.density[:] - density_thermal[:]
        else:
            density_fast = np.zeros_like(density_thermal)
    else:
        density_fast = species_obj.density_fast[:].copy()

    # Set density_fast floor = 0
    density_fast[density_fast<0] = 0.0

    if (density_fast < 0.0).any() or (density_thermal < 0.0).any():
        print(f"""negative density. debug info:
            (z,a): ({species_obj.element[0].z_n}, {species_obj.element[0].a})
            {density_thermal=}
            {density_fast=}
            {species_obj.density[0]=}
            {species_obj.density_thermal[0]=}
            {species_obj.density_fast[0]=}
        """)

    # For debugging a single species
    if (species_obj.element[0].z_n, species_obj.element[0].a) == (10,20) and False:
        print(f"""
            (z,a): ({species_obj.element[0].z_n}, {species_obj.element[0].a})
            {species_obj.density=}
            {species_obj.density_thermal=}
            {species_obj.density_fast=}

            {density_thermal=}
            {density_fast=}
        """)

    return density_thermal, density_fast

def select_species_by_density(core_profiles:object, param:dict=None, scenario_param:dict=None, dens_func:callable=None, dens_func_choice:str="axis", density_cutoff:"dict[str, float]"={}, debug:bool=False):
    if param is None:
        if debug:
            print("No parameter dict provided, taking default (EPs on)")
        param = {"fast_particles": 1}
    if scenario_param is None:
        scenario_param = {}
    if dens_func is None:
        if dens_func_choice.lower() in ["radial", "line"]:
            # Calculate cutoff based on radial mean (distinct from volume average density)
            dens_func = lambda x: np.sum(x * np.ones_like(x)) / np.sum(np.ones_like(x))
        else:
            # Calculate cutoff based on axis value
            dens_func = lambda x: x[0]

    # Prepare list of species [(isp, n_thermal, n_fast)]
    species_list = [
        (isp, *[dens_func(x) for x in get_density_thermal_fast(species_obj)])
        for isp, species_obj in enumerate(core_profiles.profiles_1d[0].ion)
    ]
    # Reverse sort species by thermal density
    species_list.sort(key=lambda x: x[1], reverse=True)
    if debug:
        print(species_list)
    total_ion_density = sum([x[1] + x[2] for x in species_list])

    curr_str = ["el"]
    curr_str_fast = []

    # Round A and Z to integers? What about 2.5
    za_func = lambda x: round(x)
    for iisp, (isp, thermal_density_val, fast_density_val) in enumerate(species_list):
        species_obj = core_profiles.profiles_1d[0].ion[isp]

        z_sp = za_func(species_obj.element[0].z_n)
        a_sp = za_func(species_obj.element[0].a)
        ligka_string = LIGKA_ZA_STRINGS.get((z_sp, a_sp), None)
        if ligka_string is None:
            ligka_string = LIGKA_ZA_STRINGS.get((z_sp, None), None)
            if ligka_string is None:
                print(f"Skipping species: {isp} with (Z,A): ({z_sp}, {a_sp})")
                continue

        # density cutoff is a dict of ligka strings to floats describing the fraction of total ion density
        if thermal_density_val >= density_cutoff.get(ligka_string, np.inf) * total_ion_density:
            curr_str.append(ligka_string)

        ligka_fast_string = LIGKA_FAST_ZA_STRINGS.get((z_sp, a_sp), None)
        if fast_density_val >= density_cutoff.get(ligka_fast_string, np.inf) * total_ion_density:
            if ligka_fast_string is not None:
                curr_str_fast.append(ligka_fast_string)
            else:
                print(f"Skipping unknown fast species: {isp} with (Z,A): ({z_sp}, {a_sp})")

    # Optionally replace "dd" and/or "tt" with "dt" for Ligka to treat as $^2.5$H hybrid species
    if int(scenario_param.get("DT", 0)):
        if not ("dd" in curr_str and "tt" in curr_str):
            warnings.warn("Not both D and T are present, looking for either to replace with 'DT'.")
        if "dd" in curr_str or "tt" in curr_str:
            for ligka_string in ["dd", "tt"]:
                if ligka_string in curr_str:
                    curr_str.remove(ligka_string)
            curr_str.insert(1, "dt")
        else:
            warnings.warn("'DT' option selected, but neither D nor T present in IDS.")

    nback = len(curr_str)
    nhot = len(curr_str_fast) * int(param.get("fast_particles", 1))
    nspec = nback + nhot

    ligka_species_str = "".join(curr_str) + "".join(curr_str_fast) * int(param.get("fast_particles", 1))

    return ligka_species_str, nspec, nback, nhot


def test():
    class fake_element(object):
        def __init__(self, z, a):
            self.z_n = z
            self.a = a

    class fake_ion_species(object):
        def __init__(self, density_thermal, density_fast, density, z, a):
            self.density_thermal = density_thermal
            self.density_fast = density_fast
            self.density = density
            self.element = [fake_element(z, a)]

    class fake_profiles_1d(object):
        def __init__(self, nr=3):
            self.ion = [
                fake_ion_species(ni_th, ni_fast, ni, z, a)
                for isp, (ni_th, ni_fast, ni, z, a) in enumerate([
                    # Ne (below 1% threshold), ni_th missing
                    [np.zeros(0), 0.0*np.ones(nr), 0.001*np.ones(nr), 10, 20],
                    # H: ni missing, ni_thermal present
                    [1.01* np.ones(nr), 0.0*np.ones(nr), np.zeros(0), 1, 1],
                    # D: ni_thermal missing, ni present
                    [np.zeros(0), 0.0*np.ones(nr), np.ones(nr), 1, 2],
                    # He (below 1% threshold), but alpha present. ni missing
                    [0.001*np.ones(nr), 0.005*np.ones(nr), 0.0*np.ones(nr), 2, 4],
                ])
            ]

    class fake_core_profs(object):
        def __init__(self):
            self.profiles_1d = [fake_profiles_1d()]

    fake_obj = fake_core_profs()

    if False:
        print()
        print(fake_obj.profiles_1d[0].ion[1].density)
        print(fake_obj.profiles_1d[0].ion[1].density_thermal)
        print(fake_obj.profiles_1d[0].ion[1].density_fast)
        print()

    density_cutoff = {v:val for (mydict, val) in zip([LIGKA_ZA_STRINGS, LIGKA_FAST_ZA_STRINGS], [0.02, 0.001]) for k,v in mydict.items()}
    print(density_cutoff)

    ligka_species_str, nspec, nback, nhot = select_species_by_density(fake_obj, param={"fast_particles": 1}, density_cutoff=density_cutoff, debug=True)
    print(ligka_species_str, nspec, nback, nhot)
    if ligka_species_str == "elhhddal" and nspec==4 and nback==3 and nhot==1:
        print("ligka_species_str is correct")
    else:
        raise ValueError(ligka_species_str, nspec, nback, nhot)

    print()
    ligka_species_str, nspec, nback, nhot = select_species_by_density(fake_obj, param={"fast_particles": 0}, scenario_param={"DT": 1}, density_cutoff=density_cutoff, debug=True)
    print(ligka_species_str, nspec, nback, nhot)
    if ligka_species_str == "eldthh" and nspec==3 and nback==3 and nhot==0:
        print("ligka_species_str is correct")
    else:
        raise ValueError(ligka_species_str, nspec, nback, nhot)


if __name__ == "__main__":
    test()
