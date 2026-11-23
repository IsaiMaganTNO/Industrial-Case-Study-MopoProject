crf=lambda r,n: r/(1-(1+r)**-n)
gas=0.015
# marginal electricity: CCGT+CC is the price-setter in 2050
ccgtcc = gas/0.4857 + 0.01035 + 1150*crf(0.09,25)/(8760*0.5)
print(f"marginal elec (CCGT+CC, eta 0.4857) ~ {ccgtcc:.4f} /MWh")
pem_f = ccgtcc/0.622
pem_c = 613.71*crf(0.08,25)/(8760*0.9)
print(f"PEM     fuel {pem_f:.4f} + capex {pem_c:.4f} = {pem_f+pem_c:.4f}")
sm_f = gas/0.69; sm_c = 1057.32*crf(0.09,30)/(8760*0.9) + 0.00445*8760/(8760*0.9)
print(f"SMR+CC  fuel {sm_f:.4f} + capex {sm_c:.4f} = {sm_f+sm_c:.4f}")
print(f"ratio PEM/SMR+CC = {(pem_f+pem_c)/(sm_f+sm_c):.2f}x")
