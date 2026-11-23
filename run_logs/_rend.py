import pymupdf
d=pymupdf.open(r"final_runs_pessimistic_ccs\NLBE_resolution_and_scope.pdf")
for p in (12,15,17): d[p-1].get_pixmap(dpi=90).save(rf"run_logs\_pg{p}.png")
print([b[4][:90] for b in d[16].get_text("blocks")])
