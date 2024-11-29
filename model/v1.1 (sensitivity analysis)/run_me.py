import utils
import numpy as np
import pyomo.environ as py
from datetime import datetime
import pandas as pd
import os

# import save_results_to_iamc_files as report
from itertools import islice
import plot_results_with_pyam as plot

# TODO: Add here something.

_INPUT_DATA = [
    "scalars.xlsx",
    "vectors_costs.xlsx",
    "vectors_capacity.xlsx",
    "vectors_manufacturing.xlsx",
]

# SOURCES:

# - Embodied energy analysis of photovoltaic (PV) system based on macro- and micro-level
#           https://doi.org/10.1016/j.enpol.2005.06.018

_SCENARIO = "Solar Modules"
# _SCENARIO = "Wind Turbines"

# Wind Turbines ... Onshore

# EXPECTATIONS
# (0) ... Optimistic Price
# (1) ... Pesimistic Price
# (2) ... GENeSYS-MOD

_data = utils.get_input_data_from_excel_sheets(_INPUT_DATA)
scalars = _data[0]
vector_costs = _data[1]
vector_capacity = _data[2]
vector_manufacturing = _data[3]


for _choice in [1]:
    # Pi_Bar_total_t_n_y
    _exo_installed = dict()
    for _index, _row in vector_capacity.iterrows():
        if _row.Technology == _SCENARIO:
            _exo_installed[_SCENARIO, _row.Year] = _row["Value [MW]"]
        else:
            pass

    # c_prim_t_y
    _exo_costs = dict()
    for _index, _row in vector_costs.iterrows():
        if _row.Technology == _SCENARIO:
            _exo_costs[_SCENARIO, _row.Year] = _row["Value [EUR/MW]"]
        else:
            pass

    if _choice == 0:
        pass
    elif _choice == 1:
        for _key in _exo_costs.keys():
            if _key[1] < 2030:
                pass
            elif _key[1] < 2040:
                _exo_costs[_SCENARIO, _key[1]] += (
                    _exo_costs[_SCENARIO, _key[1] - 10] * (2040 - _key[1]) / 10
                )
            elif _key[1] >= 2040:
                pass
        # _list = _exo_costs.values()
        # _values = {'Price [EUR/MW]': _list}
        # _df = pd.DataFrame(_values)
        # _df.to_excel('modified prices.xlsx', index=False)
    elif _choice == 2:
        for _key in _exo_costs.keys():
            # please check GENeSYS-MOD data
            _exo_costs[_SCENARIO, _key[1]] *= 1.74

    else:
        print("ERROR IN CHOICE!")
        break

    # ...............
    # ...c_sec_t_y...
    # ...............

    # "vectors_manufacturing.xlsx"
    # ...assuming 25% of total manufacturing cost in the EU from the materials!
    # 0.75 * 295 320 EUR/MW for SOLAR MODULES (constant over time)
    # WIND TURBINES IMPORT COSTS * (1 - 0.25/1.4)
    _exo_manu = dict()
    utils.fetch_data(_exo_manu, vector_manufacturing, _SCENARIO, "Value [EUR/MW]")

    # nodes = list(['EU27'])
    years = sorted(list(set(vector_capacity.Year)))
    technology = list([_SCENARIO])
    model = py.ConcreteModel()
    model.scenario = _SCENARIO
    model.technology = py.Set(initialize=technology)
    model.years = py.Set(initialize=years)

    model.dual = py.Suffix(direction=py.Suffix.IMPORT)
    
    model.choice = _choice

    model.par_pi_bar = py.Param(
        model.technology,
        model.years,
        doc="PI-Bar^total_t_n_y [MW]",
        initialize=_exo_installed,
    )

    model.par_c_prim = py.Param(
        model.technology, model.years, doc="c^prim_t_y [EUR/MW]", initialize=_exo_costs
    )

    model.par_c_sec = py.Param(
        model.technology,
        model.years,
        doc="c^sec_t_y [EUR/MW] (manufacturing)",
        initialize=_exo_manu,
    )

    # Technical lifetime
    model.par_lifetime = py.Param(
        initialize=scalars.loc[scalars.Variable == "TechLife|" + _SCENARIO].Value.item()
    )

    # Scrap available from previous years (exogenous parameter)
    # model.scrap_previous = scalars.loc[scalars.Variable=='Scrap|'+_SCENARIO].Value.item()

    # f_scrap_t_MW (amount of scrap per installed capacity)
    model.scrap_specific = py.Param(
        initialize=scalars.loc[
            scalars.Variable == "f_scrap_t_MW|" + _SCENARIO
        ].Value.item()
    )

    # f_mining_t_MW (amount of materials needed per installed capacity)
    model.f_mining = py.Param(
        initialize=scalars.loc[
            scalars.Variable == "f_mining_t_MW|" + _SCENARIO
        ].Value.item()
    )

    # Q^mining_y
    model.Q_mining = py.Param(
        initialize=scalars.loc[
            scalars.Variable == "Q_mining_t|" + _SCENARIO
        ].Value.item()
    )

    # f_recycling
    _factor = 0.05/0.85
    model.f_recycling = py.Param(
        initialize=scalars.loc[
        scalars.Variable == "f_recycling|" + _SCENARIO
    ].Value.item() * _factor)
    print("Recycling efficiency (i.e., quality) %: {:.1f}".format(model.f_recycling()*100))
    
    # f_scrap_rec
    _factor = 0.25
    model.f_scrap_rec = py.Param(
        initialize=scalars.loc[
            scalars.Variable == "f_scrap_rec|" + _SCENARIO
        ].Value.item()
        * _factor
    )
    print(model.f_scrap_rec())

    # installed capacity of technology in y_start
    model.par_pi_total_y0 = scalars.loc[
        scalars.Variable == "Pi_Total_y0|" + _SCENARIO
    ].Value.item()

    # print("CHECK OF INPUT PARAMETERS:")
    # print("")

    # _formatted_number = "{:,}".format(model.par_gasification["Australia"])
    # print("Gasification|Capacity|Australia (MMBtu): ", _formatted_number)

    # VARIABLES & CONSTRAINTS

    model.var_pi_total = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        name="PI_Total",
        doc="Total installed capacity per technology, node, and year.",
    )

    model.var_pi_new = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        name="PI_Total",
        doc="Newly installed capacity per technology, node, and year.",
    )

    model.var_pi_dec = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        name="PI_Total",
        doc="Decommissioned installed capacity per technology, node, and year.",
    )

    def con_installed_capacity(model, tech, year):
        if year == model.years.first():
            return (
                model.var_pi_total[tech, year]
                == model.par_pi_total_y0
                + model.var_pi_new[tech, year]
                - model.var_pi_dec[tech, year]
            )
        else:
            return (
                model.var_pi_total[tech, year]
                == model.var_pi_total[tech, year - 1]
                + model.var_pi_new[tech, year]
                - model.var_pi_dec[tech, year]
            )

    model.con_installed_capacity = py.Constraint(
        model.technology,
        model.years,
        rule=con_installed_capacity,
        doc="Constraint (1) - checked.",
    )

    def con_decommissioned_capacity(model, tech, year):
        if tech == "Solar Modules":
            # https://www.takomabattery.com/european-solar-pv-industry-report-different-market-segments/
            _exogenous = 7.5 * 1000  # in MW
        else:
            # https://windeurope.org/about-wind/reports/wind-energy-in-europe-outlook-to-2023/
            _exogenous = 12.5 * 1000  # in MW

        if year - model.par_lifetime >= model.years.first():
            return (
                model.var_pi_dec[tech, year]
                == model.var_pi_new[tech, year - model.par_lifetime]
            )
        else:
            return (
                model.var_pi_dec[tech, year]
                == _exogenous + 0.15 * model.var_pi_new[tech, year]
            )

    model.con_decommissioned_capacity = py.Constraint(
        model.technology,
        model.years,
        rule=con_decommissioned_capacity,
        doc="Constraint (2)+(3) - checked.",
    )

    model.var_q_scrap_dec = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        doc="Amount of scrap/waste due to decommissioning of capacity.",
    )

    def con_scrap_available(model, tech, year):
        return (
            model.var_q_scrap_dec[tech, year]
            == model.scrap_specific * model.var_pi_dec[tech, year]
        )

    model.con_scrap_available = py.Constraint(
        model.technology,
        model.years,
        rule=con_scrap_available,
        doc="Constraint (4) - checked.",
    )

    model.var_pi_new_primary = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        doc="Newly installed capacitiy from primary mineral supply.",
    )

    model.var_pi_new_secondary = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        doc="Newly installed capacitiy from secondary mineral supply.",
    )

    def con_newly_installed_capacity(model, tech, year):
        return (
            model.var_pi_new[tech, year]
            == model.var_pi_new_primary[tech, year]
            + model.var_pi_new_secondary[tech, year]
        )

    model.con_newly_installed_capacity = py.Constraint(
        model.technology,
        model.years,
        rule=con_newly_installed_capacity,
        doc="Constraint (5) - checked.",
    )

    model.var_q_primary = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        doc="Amount of primary material supply needed.",
    )

    ###############################################################################

    def con_material_needs_primary(model, tech, year):
        return (
            model.var_q_primary[tech, year]
            == model.var_pi_new_primary[tech, year] * model.f_mining
        )

    model.con_material_needs_primary = py.Constraint(
        model.technology,
        model.years,
        rule=con_material_needs_primary,
        doc="Constraint (6) - checked.",
    )

    ###############################################################################

    model.var_share_of_today_s_mining = py.Var(
        model.technology,
        model.years,
        within=py.NonNegativeReals,
        doc="EUs share on todays total global proudction.",
    )

    def con_bound_of_mining(model, tech, year):
        return model.var_q_primary[tech, year] <= model.Q_mining

    model.con_bound_of_mining = py.Constraint(
        model.technology,
        model.years,
        rule=con_bound_of_mining,
        doc="Constraint (7) - checked",
    )

    def con_import_share_eu(model, tech, year):
        return (
            model.var_share_of_today_s_mining[tech, year]
            == model.var_q_primary[tech, year] / model.Q_mining
        )

    model.con_import_share_eu = py.Constraint(
        model.technology, model.years, rule=con_import_share_eu
    )

    _import = 0.5

    def con_limit_import_share_eu(model, tech, year):
        # 0.5 is a result of the model run with optimistic price assumptions.
        return model.var_share_of_today_s_mining[tech, year] <= _import

    model.con_limit_import_share_eu = py.Constraint(
        model.technology,
        model.years,
        rule=con_limit_import_share_eu,
        doc="Constraint (x) - checked.",
    )
    ###############################################################################

    model.var_q_scrap_rec = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        doc="Amount of scrap recycled and used in the material secondary supply",
    )

    def con_scrap_recycling_efficiency(model, tech, year):
        return (
            model.f_mining * model.var_pi_new_secondary[tech, year]
            == model.f_recycling * model.var_q_scrap_rec[tech, year]
        )

    model.con_scrap_recycling_efficiency = py.Constraint(
        model.technology,
        model.years,
        rule=con_scrap_recycling_efficiency,
        doc="Constraint (8) - checked.",
    )

    ###############################################################################

    model.var_q_scrap_total = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        doc="Amount of total available scarp/waste",
    )

    def con_amount_of_scrap(model, tech, year):
        if year == model.years.first():
            return (
                model.var_q_scrap_total[tech, year]
                == model.var_q_scrap_dec[tech, year] - model.var_q_scrap_rec[tech, year]
            )
        else:
            return (
                model.var_q_scrap_total[tech, year]
                == model.var_q_scrap_total[tech, year - 1]
                + model.var_q_scrap_dec[tech, year]
                - model.var_q_scrap_rec[tech, year]
            )

    model.con_amount_of_scrap = py.Constraint(
        model.technology,
        model.years,
        rule=con_amount_of_scrap,
        doc="Constraint (9) - checked...?",
    )

    ###############################################################################

    model.var_cost_prim = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        doc="Cost for material primary supply",
    )
    model.var_cost_sec = py.Var(
        model.technology,
        model.years,
        domain=py.NonNegativeReals,
        doc="Cost for material secondary supply",
    )

    def con_cost_primary(model, tech, year):
        return (
            model.var_cost_prim[tech, year]
            == model.var_pi_new_primary[tech, year] * model.par_c_prim[tech, year]
        )

    model.con_cost_primary = py.Constraint(
        model.technology,
        model.years,
        rule=con_cost_primary,
        doc="Constraint (10) - checked.",
    )

    ###############################################################################

    model.var_cost_scrap = py.Var(
        model.technology,
        model.years,
        domain=py.Reals,
        doc="Cost of recycling scrap/waste",
    )

    def con_cost_secondary(model, tech, year):
        return (
            model.var_cost_sec[tech, year]
            == model.var_pi_new_secondary[tech, year] * model.par_c_sec[tech, year]
            + model.var_cost_scrap[tech, year]
        )

    model.con_cost_secondary = py.Constraint(
        model.technology,
        model.years,
        rule=con_cost_secondary,
        doc="Constraint (11) - checked.",
    )

    ###############################################################################

    def con_cost_scrap_recycling(model, tech, year):
        return (
            model.var_cost_scrap[tech, year]
            == model.var_q_scrap_rec[tech, year] * model.f_scrap_rec
        )

    model.con_cost_scrap_recycling = py.Constraint(
        model.technology,
        model.years,
        rule=con_cost_scrap_recycling,
        doc="Constraint (12) - checked.",
    )

    ###############################################################################

    model.var_slack_scrap = py.Var(
        model.technology,
        model.years,
        within=py.NonNegativeReals,
        doc="Ensure that scrap/waste is continously reduced from 2035 onwards.",
    )

    def con_reduce_scrap_produced_from_20xx(model, tech, year):
        if year < 2035:
            return py.Constraint.Skip
        else:
            return (
                model.var_q_scrap_total[tech, year - 1]
                - model.var_q_scrap_total[tech, year]
                == model.var_slack_scrap[tech, year]
            )

    # model.con_reduce_scrap_produced_from_20xx = py.Constraint(
    #     model.technology,
    #     model.years,
    #     rule=con_reduce_scrap_produced_from_20xx,
    #     doc="Constraint (13) - checked.",
    # )

    ###############################################################################

    def con_total_capacity_as_expected(model, tech, year):
        return model.var_pi_total[tech, year] == model.par_pi_bar[tech, year]

    model.con_total_capacity_as_expected = py.Constraint(
        model.technology,
        model.years,
        rule=con_total_capacity_as_expected,
        doc="Constraint (14) - checked.",
    )

    ###############################################################################

    model.var_slack_rec = py.Var(
        model.technology,
        model.years,
        within=py.NonNegativeReals,
        doc="Recycled scrap additions in tons.",
    )

    def con_recycling_rate_increase(model, tech, year):
        if year == model.years.first():
            return py.Constraint.Skip
        else:
            return (
                model.var_q_scrap_rec[tech, year]
                - model.var_q_scrap_rec[tech, year - 1]
                <= model.var_slack_rec[tech, year]
            )

    model.con_recycling_rate_increase = py.Constraint(
        model.technology,
        model.years,
        rule=con_recycling_rate_increase,
        doc="Constraint (15)",
    )

    def con_recycling_rate_speed(model, tech, year):
        if year < 2030:
            return model.var_slack_rec[tech, 2025] == model.var_slack_rec[tech, year]
        elif year < 2035:
            return model.var_slack_rec[tech, 2030] == model.var_slack_rec[tech, year]
        elif year < 2040:
            return model.var_slack_rec[tech, 2035] == model.var_slack_rec[tech, year]
        elif year < 2045:
            return model.var_slack_rec[tech, 2040] == model.var_slack_rec[tech, year]
        else:
            return model.var_slack_rec[tech, 2045] == model.var_slack_rec[tech, year]

    model.con_recycling_rate_speed = py.Constraint(
        model.technology,
        model.years,
        rule=con_recycling_rate_speed,
        doc="Constraint (14a) - checked.",
    )

    # DYNAMICS OF THE RECYCLING INDUSTRY
    #
    #
    #
    #

    def con_restrict_max_recycling_capacity(model, tech, year):
        return model.var_pi_new_secondary[tech, year] <= 40000

    # model.con_restrict_max_recycling_capacity = py.Constraint(model.technology, model.years, rule=con_restrict_max_recycling_capacity)

    # OBJECTIVE FUNCTION
    def objective_function(m):
        return sum(
            model.var_cost_prim[tech, year] + model.var_cost_sec[tech, year]
            for tech in model.technology
            for year in model.years
        )

    model.objective = py.Objective(expr=objective_function, sense=py.minimize)

    solver = py.SolverFactory("gurobi")
    solution = solver.solve(model)

    print("OBJECTIVE VALUE: {:,.0f} MEUR".format(model.objective() / 1000000))

    # REPORT THE MODEL RESULTS TO OUTPUT FILES
    _now = datetime.now().strftime("%Y%m%d_%H")
    if _choice == 0:
        _str_add = "optimistic_price"
    elif _choice == 1:
        _str_add = "pessimistic_price"
    elif _choice == 2:
        _str_add = "GENeSYS-MOD"

    result_dir = os.path.join(
        "result",
        "{}_{}_{}_{}_{}".format(
            _now, model.scenario, _str_add, str(_factor), str(_import)
        ),
    )
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    _years = list(model.years)

    _par_expansion_plan = [
        np.around(model.par_pi_bar[model.technology.first(), year], 0)
        for year in model.years
    ]
    _var_total = [
        np.around(model.var_pi_total[model.technology.first(), year](), 0)
        for year in model.years
    ]
    _overcapacity = [
        np.around(
            model.var_pi_total[model.technology.first(), year]()
            - model.par_pi_bar[model.technology.first(), year],
            0,
        )
        for year in model.years
    ]

    _var_total_reduced = list(islice(_var_total, len(_var_total) - 1))
    _list = [model.par_pi_total_y0]
    _previous_capacity = _list + _var_total_reduced
    _new_prim = [
        np.around(model.var_pi_new_primary[model.technology.first(), year](), 0)
        for year in model.years
    ]
    _new_sec = [
        np.around(model.var_pi_new_secondary[model.technology.first(), year](), 0)
        for year in model.years
    ]
    _dec = [
        (-1) * np.around(model.var_pi_dec[model.technology.first(), year](), 0)
        for year in model.years
    ]
    _total_scrap = [
        np.around(model.var_q_scrap_total[model.technology.first(), year](), 0)
        for year in model.years
    ]
    _scrap_rec = [
        np.around(model.var_q_scrap_rec[model.technology.first(), year](), 0)
        for year in model.years
    ]
    _new_scrap = [
        np.around(model.var_q_scrap_dec[model.technology.first(), year](), 0)
        for year in model.years
    ]
    _imp_share = [
        100
        * np.around(
            model.var_share_of_today_s_mining[model.technology.first(), year](), 3
        )
        for year in model.years
    ]

    _df = pd.DataFrame(
        {
            "Year": _years,
            "Expansion plan [MW]": _par_expansion_plan,
            "Total capacity [MW]": _var_total,
            "Overcapacity [MW]": _overcapacity,
            "Current capacity [MW]": _previous_capacity,
            "Newly|Primary [MW]": _new_prim,
            "Newly|Secondary [MW]": _new_sec,
            "Decommissioned [MW]": _dec,
            "Import share global production [%]": _imp_share,
            "Total scrap [tons]": _total_scrap,
            "Scrap recycled [tons]": _scrap_rec,
            "Scrap additions [tons]": _new_scrap,
        }
    )

    _df.to_excel(os.path.join(result_dir, "solution.xlsx"), index=False)

    plot.run(model, _df, result_dir)
    print("MINING-BASED TOTAL ADDITIONS: {} GW".format(sum(_new_prim)))
    print("RECYCLING-BASED TOTAL ADDITIONS: {} GW".format(sum(_new_sec)))
    print("In %: {:.1f}".format(sum(_new_sec) / (sum(_new_prim) + sum(_new_sec)) * 100))
    print("TOTAL SCRAP: {} Mt".format(_total_scrap[-1] / 1000))
    print("__________________________")
    print("")
