from PIL import Image
import glob,os
ps=sorted(glob.glob(r"plot_scripts\presentation\out_vre15\*.png"))
for p in ps:
    im=Image.open(p); ex=im.convert("L").getextrema()
    flag="" if ex[1]-ex[0]>100 else "  <-- SUSPECT BLANK"
    print(f"{os.path.basename(p):34} {im.size[0]}x{im.size[1]} {ex}{flag}")
print("count",len(ps))
