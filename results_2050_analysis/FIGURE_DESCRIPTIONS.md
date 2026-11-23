# Figure descriptions for the report (NL+BE)

Figures are in `figures/` (PNG at 400 dpi and SVG; `_vertical` = NL above BE); the data behind each figure is in `data/` under the same name. Figures have no titles, so the captions below are meant as figure captions. Numbers quoted in the text are per country (NL panel or BE panel) in TWh/yr unless stated otherwise.

**Scenarios.** *NL+BE regional clusters* and *NL+BE country level* model only the Netherlands and Belgium, with 17 zones or one node per country respectively. *Mixed resolution* keeps NL+BE in 17 zones and adds DE, DK, NO and UK at country level with one shared CO2 cap; it is the reference for the four sensitivities: *National CO2 caps* (a separate cap per country), *10 repr. days* (10 instead of 3 representative days), *Optimistic CCS* (higher CO2 storage limits, lower CO2 transport and injection costs) and *With FR + LU* (France and Luxembourg added). Except in Optimistic CCS, NL can store at most 2.5 / 10.5 / 16 Mt CO2 per year in 2030 / 2040 / 2050, and BE has no storage.

---

## A1 - Electricity generation

*Caption: Electricity generation in NL and BE by technology in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution.*

In all three scenarios the power system shifts from gas to offshore wind, but how far it goes depends strongly on whether NL and BE are modelled on their own. In the two NL+BE-only scenarios, Dutch offshore wind grows steeply to roughly 370-380 TWh in 2050, and BE adds hydrogen turbines as firm back-up; in Regional clusters NL also builds new nuclear. In Mixed resolution, Dutch offshore wind grows much less (about 207 TWh in 2050, some 45% lower), no hydrogen turbines are built, and BE instead keeps biomass power and some gas power in 2040. Belgian nuclear is similar in 2030 and 2050 in all scenarios, but in 2040 Mixed resolution relies less on it. Solar and onshore wind are nearly identical everywhere, as they are close to their potential. The reason for the gap is the industry (see A5): without access to CO2 storage abroad, NL and BE must decarbonise industry with electricity and hydrogen, and the hydrogen comes from electrolysis powered by offshore wind. With neighbours, industry can use gas with carbon capture and export the CO2, so far less electricity is needed, and the neighbouring countries provide the flexibility that hydrogen turbines otherwise supply.

## A2 - Hydrogen supply

*Caption: Hydrogen supply in NL and BE by source in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution (hydrogen made and used inside refineries excluded).*

The LH2 import terminals in both countries are used at or near their limit from 2040 onwards in every scenario: imported liquid hydrogen is the cheapest low-carbon hydrogen available, so the model always takes it first. What differs is how much additional hydrogen is produced. In the NL+BE-only scenarios, electrolysis in NL grows strongly after 2040 (to 130 TWh in Regional clusters and 73 TWh in Country level by 2050), while in Mixed resolution it only appears in 2050 at a much lower level; in 2030 and 2040 Mixed resolution covers the gap with a small amount of gas reforming with capture. All electrolysis is located in NL, close to the offshore wind landing points, and BE receives a large share of its hydrogen by pipeline from NL in the NL+BE-only scenarios. This pipeline flow is internal to NL+BE: the two countries together have no net hydrogen trade with other countries in those scenarios.

## A3 - Electricity consumption

*Caption: Electricity use in NL and BE by category in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution.*

Fixed demand from buildings, transport and other sectors is the same in all scenarios, so the differences come from industry, electrolysis and trade. Industrial electricity use roughly doubles to triples between 2030 and 2050 in the NL+BE-only scenarios, and electrolysis in NL becomes the largest single new consumer by 2050, especially in Regional clusters. In Mixed resolution both grow far less, and NL becomes a net exporter of electricity to its neighbours instead. Building heat and storage also grow over time but remain small. This mirrors A1 and A5: when industry cannot rely on CO2 export, it electrifies directly or indirectly through hydrogen; when it can, gas with capture takes over and the surplus offshore wind is sold abroad.

## A4 - Hydrogen consumption

*Caption: Hydrogen use in NL and BE by category in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution (hydrogen made and used inside refineries excluded).*

Industrial hydrogen use starts after 2030 and grows strongly in the NL+BE-only scenarios, in both NL and BE, because hydrogen replaces fossil fuels in ammonia, glass and part of steel production. Hydrogen turbines are also used in these scenarios, mainly in 2030 and again in 2050, to provide firm power. In Mixed resolution, industrial hydrogen only appears in 2050 and at a much lower level, and no hydrogen is burned for power. Instead NL passes a steady 30-36 TWh per year on to its neighbours, mainly imported LH2, acting as a hydrogen transit hub. The "net pipeline export" from NL in the NL+BE-only scenarios is hydrogen sent to BE, not export out of the region.

## A5 - Industry production routes

*Caption: Share of production per industrial sector in NL and BE by route type in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution.*

In 2030 most sectors still run on fossil fuels without capture in all scenarios, and by 2050 every sector is decarbonised, but along very different routes. Some choices are the same everywhere: chlorine is electric; paper, pulp, aluminium and secondary steel use biomass or scrap; and refineries use gas reforming with capture. The main difference is between the NL+BE-only scenarios and Mixed resolution. On their own, NL and BE make ammonia and float glass with hydrogen, electrify primary steel (fully in Country level, mostly in Regional clusters) and container glass, and make part of their olefins from methanol produced with captured CO2. In Mixed resolution, ammonia, primary steel, olefins and float glass all switch to gas with carbon capture, and cement is mostly fired with biomass. The reason is the CO2 storage limit: on their own, NL and BE can store only 16 Mt CO2 per year in 2050, so any extra captured CO2 has to be used (for methanol), and the model prefers routes that avoid CO2 altogether. With neighbours, captured CO2 can be exported to storage in NO, UK and DK, which makes gas with capture the cheapest route for most heavy industry.

---

## B1 - Electricity generation, sensitivities

*Caption: Electricity generation in NL and BE by technology in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU.*

National CO2 caps give almost the same power mix as Mixed resolution, so the way the CO2 cap is split between countries hardly affects electricity generation. The other three sensitivities do change the mix. With 10 repr. days, NL builds more offshore wind and more nuclear, and BE more solar, plus some gas and hydrogen turbines as back-up; with more varied weather days the model sees longer low-wind periods and values firm capacity and storage more (see B3). Optimistic CCS gives the largest change: nuclear disappears in both countries and is replaced by gas power with capture, mainly in BE (88 TWh), while offshore wind falls clearly; cheap CO2 storage makes gas with capture cheaper than new nuclear. With FR + LU, NL builds no nuclear, BE halves its nuclear output and replaces it with biomass power (47 TWh). This is likely because adding France enlarges the shared CO2 and biofuel caps, while France itself offers little firm power because its existing nuclear plants are assumed to retire after 40 years.

## B2 - Hydrogen supply, sensitivities

*Caption: Hydrogen supply in NL and BE by source in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU (refinery hydrogen excluded).*

The LH2 terminals run at their limit in every sensitivity, so differences come only from electrolysis in NL and from pipeline imports into BE. Electrolysis is highest with 10 repr. days, where the more varied weather gives more hours with surplus wind and solar to run electrolysers, and lowest with Optimistic CCS, where industry uses gas with capture instead of hydrogen. With FR + LU, BE imports noticeably more hydrogen by pipeline, in line with the higher hydrogen use in Belgian industry in that scenario (see B4 and B5). National CO2 caps is again close to Mixed resolution.

## B3 - Electricity consumption, sensitivities

*Caption: Electricity use in NL and BE by category in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU.*

Fixed demand and industrial electricity use are almost the same in all sensitivities, so the differences lie in electrolysis, storage, heat and exports. The 10 repr. days scenario stands out: NL charges around 120 TWh into storage, mostly multi-day iron-air batteries, compared with at most about 20 TWh in the other scenarios. With only 3 representative days, the model cannot see weather events lasting several days, so long-duration storage has no value; with 10 days it does. The same scenario also uses more electricity for electrolysis and building heat (the latter not yet analysed) and none for refineries, because the NL+BE refineries are not used (see B5). Optimistic CCS uses the least electricity for electrolysis and exports the least, reflecting its shift to gas with capture. NL is a net exporter of electricity in all sensitivities.

## B4 - Hydrogen consumption, sensitivities

*Caption: Hydrogen use in NL and BE by category in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU (refinery hydrogen excluded).*

In most sensitivities a large share of the hydrogen arriving in NL is passed on to neighbouring countries, and only a moderate amount is used by industry. Two scenarios deviate. In Optimistic CCS, industry uses no hydrogen at all, because gas with capture becomes cheaper everywhere, so both NL and BE export their imported hydrogen. With FR + LU, Belgian industry roughly doubles its hydrogen use, mainly in glass, so more hydrogen stays inside NL+BE and NL exports less. Hydrogen turbines are used only in BE, mostly in 10 repr. days, as back-up power during longer low-wind periods.

## B5 - Industry production routes, sensitivities

*Caption: Share of production per industrial sector in NL and BE by route type in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU.*

The core of the industrial transition is robust across all sensitivities: primary steel and olefins use gas with capture, chlorine is electric, and paper, pulp, aluminium and secondary steel use biomass or scrap. The sensitivities mainly change the marginal sectors: glass, cement and ammonia. Optimistic CCS pushes glass furthest towards gas with capture, as CO2 storage is cheap. National CO2 caps and With FR + LU move part of the glass to hydrogen. With FR + LU, ammonia moves largely to biomass and cement from biomass to gas with capture, probably because the larger shared biofuel cap makes biomass available to other uses. The most striking result is in 10 repr. days: the NL+BE refineries are not used in 2050, and the same demand for refinery products is met by imports from Denmark. The refinery units are available in the model, so this is a cost-driven choice; the exact reason (full NL CO2 storage or cheaper capture and storage in Denmark) has not yet been confirmed.


## Comparison with the European (EU case) baseline

The European case baseline gives a broadly similar picture for NL+BE, but with a different balance between technologies. In 2050 it relies much more on nuclear power (BE 145 TWh, NL 113 TWh, against 0-53 TWh per country in our runs) and on less offshore wind (NL 163 TWh, BE 5 TWh, against 207-380 TWh in NL and about 40 TWh in BE in our runs). Electrolysis is also spread over both countries in the EU case (NL 95 TWh, BE 20 TWh), whereas our runs place all electrolysis in NL and supply BE by pipeline. Liquid-hydrogen imports are of the same size (BE 20 TWh, NL 23-30 TWh). For industry, the EU baseline matches our runs with neighbouring countries more than the NL+BE-only runs: primary steel moves to gas-based direct reduction with capture, cement to oxy-fuel with capture, olefins to methanol with capture, and refinery output falls by about three quarters. Our NL+BE-only runs instead rely on green hydrogen and electric routes.

The differences come mainly from how the two models are set up. First, the EU case models every country as a single node inside a fully connected European system. NL+BE can therefore import electricity, hydrogen, methanol and other fuels from the rest of Europe; in 2050 they are net importers of electricity (about 30 TWh) and hydrogen (about 46 TWh) and import large volumes of methanol. Our NL+BE-only runs have to meet their demand internally, which leads to more offshore wind and electrolysis in NL. Second, our runs represent NL+BE with regional clusters and hourly weather data per cluster, which raises the value of offshore wind in NL and lowers the value of building it in BE. The EU case uses country averages. Third, the cost and potential assumptions differ. These include the nuclear investment cost and allowed new-build capacity, the offshore-wind potential per country, CO2 storage capacity and transport tariffs (our runs use pessimistic CCS assumptions), and the industrial demand data and route options. The large nuclear share in the EU case points to lower nuclear costs or tighter limits on renewables there; we have not yet checked this against its input data.

Overall, both models agree that NL+BE decarbonise through a mix of large-scale clean electricity, imported and domestic hydrogen, and carbon capture in heavy industry. The difference lies in the mix: whether this electricity comes from nuclear or offshore wind, and whether industry uses capture or hydrogen. The EU case represents the European-optimal solution with free trade. Our NL+BE-only runs show what is needed when the region must be self-sufficient, and the mixed-resolution runs fall between the two. This shows that the national outcome depends strongly on the system boundary and on how much the region can rely on its neighbours for energy and CO2 storage.


### Why the EU case has more hydrogen supply

The main reason for the higher hydrogen supply in the EU case is a demand that our model does not contain: ammonia as fuel for international shipping. In the EU baseline, NL+BE use about 194 TWh of hydrogen in 2050 for new Haber-Bosch ammonia plants (NL 111, BE 82 TWh). Almost all of this ammonia (about 163 TWh) is used as fuel for international maritime bunkering in the ports of Rotterdam and Antwerp. Hydrogen for road transport adds another 16 TWh. To meet this demand, NL+BE build 115 TWh of electrolysis and import 46 TWh of hydrogen by pipeline from other countries. Our model only covers hydrogen demand from industry, power generation and the power system. Ammonia for fertiliser is already produced in our runs, but there is no demand for ammonia as shipping fuel. Our total hydrogen use in NL+BE is therefore lower, about 37-116 TWh in 2050 depending on the scenario.

### Industrial decarbonisation compared with the EU case

In both models, NL+BE heavy industry decarbonises mainly through carbon capture and switching to cleaner fuels, but the EU baseline has fewer options than our NL+BE-only runs. In the EU baseline, primary steel moves from blast furnaces to gas-based direct reduction with capture, cement moves to oxy-fuel kilns with capture, and olefins move to the methanol route with capture. Existing ammonia plants keep running on natural gas with capture, and glass continues to use unabated natural gas. Refinery output falls by about three quarters as fuel demand declines. This pattern is very close to our Mixed resolution run, where NL+BE can export CO2 to neighbouring countries for storage and gas with capture is the cheapest route. Our NL+BE-only runs reach a different outcome. Because CO2 storage is limited to the Dutch storage site and CO2 cannot be exported, the model switches ammonia to green hydrogen, primary steel largely to electric routes, glass to electricity and hydrogen, and part of the olefins to methanol made from captured CO2. The comparison shows that the choice between hydrogen and electric routes on one side and carbon capture on the other depends mainly on how much CO2 storage the region can access. With good access to storage, as in the EU case and our Mixed resolution run, capture on gas-based routes is preferred.
