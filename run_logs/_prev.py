import fitz
d=fitz.open(r'runs\3day_mr_fix\SLIDES_nb_v2_vs_mr_fix.pdf')
for i in [0,2,3,4,9,12,15]: d[i].get_pixmap(dpi=60).save(rf'run_logs\_slide_tmp\p{i+1}.png')
