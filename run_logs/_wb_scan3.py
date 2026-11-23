import openpyxl
wb=openpyxl.load_workbook(r"verification\global_constraints_industry_case_study.xlsx")
print(wb["scenario_config.yaml"]["A3"].comment.text); print(wb["scenario_config.yaml"]["A15"].value)
