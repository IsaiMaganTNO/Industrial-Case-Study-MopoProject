from PIL import Image
import glob,os
for p in sorted(glob.glob(r"reports_v2_vre15\*.png")):
    im=Image.open(p); ex=im.convert("L").getextrema()
    print(f"{os.path.basename(p):58} {im.size[0]}x{im.size[1]} grey{ex}")
