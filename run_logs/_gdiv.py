nat={"LNG-terminal":{"BE":669.0,"NL":860.3},"gas-extraction":{"NL":284.547945},"bio-diges-up":{"NL":8.518997}}
ic1={"LNG-terminal":{"BE":83.625,"NL":95.588889},"gas-extraction":{"NL":31.616438},"bio-diges-up":{"NL":0.946555}}
n={"BE":8,"NL":9}
print(f"{'tech':16s} {'ctry':5s} {'national':>11s} {'/nreg':>11s} {'IC1 value':>11s} {'ratio':>8s}")
for t in nat:
    for ctry,v in nat[t].items():
        per=v/n[ctry]; got=ic1[t][ctry]
        print(f"{t:16s} {ctry:5s} {v:11.4f} {per:11.4f} {got:11.4f} {got/per:8.4f}")
