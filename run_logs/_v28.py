import pandas as pd
area={"NSBE01":3490.060068,"NSNL011":13072.298108,"NSNL012":20874.523573,
      "NSNL031":12615.611310,"NSNL032":6343.347802,"NSNL033":4437.287798}
fb={"NSBE01":5.235,"NSNL011":9.8048,"NSNL012":6.1267,"NSNL031":17.4689,"NSNL032":3.6596,"NSNL033":5.8237}
fo={"NSBE01":5.235,"NSNL011":9.8048,"NSNL012":28.5913,"NSNL031":17.4689,"NSNL032":9.5149,"NSNL033":5.8237}
print(f"{'zone':9}{'area_km2':>12}{'FB_cap':>9}{'FO_cap':>9}{'FB==FO':>8}{'FB/area*1000':>14}")
for z in area:
    print(f"{z:9}{area[z]:12.1f}{fb[z]:9.3f}{fo[z]:9.3f}{str(fb[z]==fo[z]):>8}{fb[z]/area[z]*1000:14.3f}")
