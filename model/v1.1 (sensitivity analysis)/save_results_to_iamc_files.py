import pandas as pd
import numpy as np
import pyomo.environ as py
import os


def write_iamc(output_df, model, scenario, region, variable, unit, time, values):
    if isinstance(values, list):
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": time,
                "value": values,
            }
        )
    else:
        _df = pd.DataFrame(
            {
                "model": model,
                "scenario": scenario,
                "region": region,
                "variable": variable,
                "unit": unit,
                "year": time,
                "value": values,
            },
            index=[0],
        )

    # output_df = output_df.append(_df)
    output_df = pd.concat([output_df, _df], ignore_index=True)
    return output_df


def write_results_to_ext_iamc_format(m, res_dir):

    input_iamc = pd.DataFrame()
    _scenario = m.scenario
    _model = 'Material-Recycling'
    _time = m.years

    # ADD TO SAVE INPUTS TO EXCEL FILE HERE!!!
    ##########################################

    output_iamc = pd.DataFrame()

    # # (2A)
    # for e in m.set_exporter:
    #     for i in m.set_importer:
    #         _value = m.var_q[e, i]()
    #         if _value > 0:
    #             output_iamc = write_iamc(
    #                 output_iamc, _model, _scenario, e + '>' + i, "LNG|Trade", "MMBtu", m.year, _value
    #             )
    #         else:
    #             pass

    # # (2B)
    # for c in m.set_importer_europe:
    #     _value = m.var_q_dom_europe[c]()
    #     if _value > 0:
    #         output_iamc = write_iamc(
    #             output_iamc, _model, _scenario, c, "EDP|NG", "MMBtu", m.year, _value
    #         )
    #     else:
    #         pass

    # # (2C)
    # for i in m.set_importer:
    #     _v = m.var_demand_not_covered[i]()
    #     if _v > 0:
    #         output_iamc = write_iamc(
    #             output_iamc, _model, _scenario, c, "LNG|Unsupplied", "MMBtu", m.year, _v
    #         )
    #     else:
    #         pass

    # # (2D) average supply costs per importer
    # for i in m.set_importer:
    #     if i in m.set_importer_europe:
    #         _demand_covered = m.par_demand[i] - m.var_demand_not_covered[i]() - m.var_q_dom_europe[i]()
    #     else:
    #         _demand_covered = m.par_demand[i] - m.var_demand_not_covered[i]()

    #     _value = np.around(m.var_cost_market_clearing[i]() / _demand_covered, 2)

    #     output_iamc = write_iamc(
    #         output_iamc, _model, _scenario, i, "LNG|Cost|Average", "$/MMBtu", m.year, _value
    #     )
    #     output_iamc = write_iamc(
    #         output_iamc, _model, _scenario, i, "LNG|Cost|Total", "$", m.year, m.var_cost_market_clearing[i]()
    #     )

    # # (2E) 
    # output_iamc = write_iamc(
    #     output_iamc, _model, _scenario, 'Europe', "LNG|Cost|EDP", "$", m.year, m.var_cost_edp()
    # )

    # # (2F)
    # output_iamc = write_iamc(
    #     output_iamc, _model, _scenario, 'Europe', "LNG|Cost|CCS", "$", m.year, m.var_cost_ccs()
    # )

    # # (2G)
    # for i in m.set_importer:
    #     _v = m.var_demand_not_covered[i]()
    #     if _v > 0:
    #         output_iamc = write_iamc(
    #             output_iamc, _model, _scenario, i, "LNG|Cost|Unsupplied", "$", m.year, _v * 10e10
    #         )
    #     else:
    #         pass

    # # (2H) objective function value
    # output_iamc = write_iamc(
    #     output_iamc, _model, _scenario, 'World', "Objective value", "$", m.year, m.objective()
    # )

    # # (2G) utilization rate (i.e., use of gasification capacity per exporter)
    # for e in m.set_exporter:
    #     _total_export = sum(m.var_q[e, _importer]() for _importer in m.set_importer)
    #     _utilization = (_total_export / m.par_gasification[e]) * 100
    #     output_iamc = write_iamc(
    #         output_iamc, _model, _scenario, e, "LNG|Gasification|Utilization", "%", m.year, np.around(_utilization, 1)
    #     )

    # #
    # #
    # #
    # # ------------------------------------------------------------------------------------------------------------------

    # output_iamc.to_excel(
    #     os.path.join(res_dir, "1_primal solution.xlsx"), index=False
    # )
    return output_iamc


# def write_iamc_with_marginal_exporter(output_df, model, scenario, region, variable, unit, time, values, exporter):
#     if isinstance(values, list):
#         _df = pd.DataFrame(
#             {
#                 "model": model,
#                 "scenario": scenario,
#                 "region": region,
#                 "variable": variable,
#                 "unit": unit,
#                 "year": time,
#                 "value": values,
#                 "marginal exporter": exporter
#             }
#         )
#     else:
#         _df = pd.DataFrame(
#             {
#                 "model": model,
#                 "scenario": scenario,
#                 "region": region,
#                 "variable": variable,
#                 "unit": unit,
#                 "year": time,
#                 "value": values,
#                 "marginal exporter": exporter
#             },
#             index=[0],
#         )

#     # output_df = output_df.append(_df)
#     output_df = pd.concat([output_df, _df], ignore_index=True)
#     return output_df


# def write_dual_variables_to_output_files(m, res_dir):
#     _df = pd.DataFrame()
#     _scenario = m.scenario
#     _model = 'LNG model'
#     _time = m.year

#     for importer in m.set_importer:
#         _check = 0
#         _price = 0
#         _value = m.dual[m.con_demand_balance[importer]]  # dual variable of importer's balance constraint
#         for exporter in m.set_exporter:
#             _des = m.par_des[exporter, importer]

#             if (_value <= _des * 1.05) and (_value >= _des * 0.95):
#                 _marginal_exporter = exporter  # find marginal exporter per import country
#                 _check = 1
#             else:
#                 pass
#         if _check == 0:
#             _marginal_exporter = 'NOT AVAILABLE'
#         else:
#             pass

#         _df = write_iamc_with_marginal_exporter(
#             _df, _model, _scenario, importer, "LNG|Cost|Marginal", "$/MMBtu", m.year, _value, _marginal_exporter
#         )

#         _df.to_excel(
#             os.path.join(res_dir, "2_dual solution.xlsx"), index=False
#         )
#     return
