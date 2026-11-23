import pandas as pd, pickle
U=pd.read_pickle(r"run_logs\_use_elec_h2_all.pkl"); DM=pd.read_pickle(r"run_logs\_elec_dem_xb_all.pkl")
print(U.head(3).to_string()); print(U.columns.tolist(), U.run.unique()); print(DM.head(3).to_string()); print(DM.tech.unique()[:20])
X=pd.read_pickle(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl"); print(X.keys() if hasattr(X,"keys") else type(X)); print(X["xb"].head(3).to_string(), X["xb"].car.unique())
