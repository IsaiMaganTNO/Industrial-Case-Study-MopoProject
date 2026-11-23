s=open("tools/make_deck_final3.py",encoding="utf8").read()
s=s.replace('''M.plot_slide(pdf, "How each industrial sector decarbonises", f_decarb(), [], section=SEC, imgw=.9,
                     cap=''','''M.wide_slide(pdf, "How each industrial sector decarbonises", f_decarb(), section=SEC,
                     cap=''',1)
a='''        M.plot_slide(pdf, "CO2 captured per sector"'''
txt='''        M.text_slide(pdf, "CO2 captured per sector: what is behind it", [
            ("NL+BE alone (2050)", ["Baseline 32 Mt / lower resolution 27 Mt captured",
                "Refinery hydrogen (gas reforming with capture, NL): 15 Mt in both - the largest source",
                "Steam crackers for plastics with capture: 6-9 Mt",
                "Biogas upgrading with capture (NL, baseline only): 6.5 Mt - negative emissions",
                "Cement oxy-fuel with capture: 2.5 Mt (mostly BE)",
                "Steel gas DRI with capture (BE, baseline only): 1 Mt",
                "Most other sectors switch to electricity or hydrogen and have nothing to capture"]),
            ("With neighbours (2050, NL+BE)", ["51 Mt captured - storage abroad makes capture cheaper than switching fuel",
                "Refinery hydrogen: 14 Mt",
                "Steam crackers: 11 Mt; gas-based plastics with capture: 7 Mt",
                "Steel gas DRI with capture: 7 Mt (NL 4.1, BE 3.1)",
                "Ammonia from gas with capture: 6 Mt (NL 4.5, BE 1.8)",
                "Cement oxy-fuel with capture (incl. biomass): 4.5 Mt",
                "Glass: below 0.3 Mt in all set-ups"])], section=SEC)
'''
s=s.replace(a, txt+a,1)
open("tools/make_deck_final3.py","w",encoding="utf8").write(s)
