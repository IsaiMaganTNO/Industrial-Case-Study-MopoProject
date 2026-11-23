import zipfile, os
F = [
 ("A_NL+BE_regional_clusters", r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\output\Investment_Results.3day_nb_ccslow_ccu_cap16_dac0.sqlite"),
 ("A_NL+BE_country_level", r"final_runs_pessimistic_ccs\2_CountryLevel_NLBE\output\Investment_Results.3day_nb_ctry_ccslow_ccu_cap16_dac0.sqlite"),
 ("A-B_Mixed_resolution", r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\Investment_Results.3day_mr_ccslow_ccu_cap16_dac0.sqlite"),
 ("B_National_CO2_caps", r"final_runs_pessimistic_ccs\5_MixedRes_CountryCO2caps_emitter_credit\output\Investment_Results.ctryco2B_mr_ccslow_ccu_cap16_dac0.sqlite"),
 ("B_10_repr_days", r"runs\rp10_mr_noblend\output\Investment_Results.10day_noblend_mr_ccslow_ccu_cap16_dac0.sqlite"),
 ("B_Optimistic_CCS", r"final_runs_pessimistic_ccs\6_MixedRes_OptimisticCCS\output\Investment_Results.mr_ccsopt_ccu_dac0.sqlite"),
 ("B_With_FR_LU", r"xpress_server_v4\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.v4.xpress.sqlite"),
]
out = "IndustrialCase_report_output_databases.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for n, p in F:
        assert os.path.getsize(p) > 0, p
        z.write(p, f"{n}.sqlite")
with zipfile.ZipFile(out) as z:
    print(z.testzip()); [print(i.filename, round(i.file_size/2**20), "MB") for i in z.infolist()]
print(round(os.path.getsize(out)/2**20), "MB zip")
