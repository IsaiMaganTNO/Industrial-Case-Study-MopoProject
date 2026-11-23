# Proposed additions: technical capabilities emphasised in the industrial case

The Pan-EU section describes the shared architecture (data pipelines, Model Builder, INES, the transformation to SpineOpt, Spine Toolbox scenarios, multi-year investment, and blended representative periods). The industrial case uses the same architecture. The proposals below describe what this case adds or uses differently. Each item can become one or two paragraphs in the industrial-case chapter.

## 1. Mixed spatial resolution within one model
The industrial case represents NL and BE with 17 sub-national regional clusters. In the mixed-resolution set-up, the neighbouring countries (DE, DK, NO, UK and, in a sensitivity, FR and LU) are added as single country nodes. Both resolutions are combined in one optimisation problem. The three spatial set-ups (regional clusters, country level and mixed resolution) are generated from the same data-pipeline databases. Only the spatial mapping and the user configuration change; importers and source data are not modified. This shows in practice the claim in Section 2.2 that several model instances can be built from the same databases by changing the configuration. It also allows a controlled test of how much the results depend on spatial resolution and on the system boundary.

Suggested text: "The industrial case extends the common workflow with a mixed-resolution configuration, in which the region of interest (NL+BE) is represented by 17 sub-national clusters while surrounding countries are represented at national level. Because the spatial mapping is applied during model construction, the regional-cluster, country-level and mixed-resolution instances are generated from identical data-pipeline databases, isolating the effect of spatial resolution and system boundary on the results."

## 2. Explicit industrial process routes as competing technologies
Industry is represented by competing production routes, not by an exogenous energy demand. For each sector, a reference route and one or more low-carbon alternatives can meet a demand for material output: primary and secondary steel, ammonia, olefins, cement, three types of glass, chlorine, aluminium, paper, pulp and refineries. The model chooses the mix of routes endogenously, which makes the industrial use of electricity, hydrogen, natural gas, biomass and CO2 an outcome of the optimisation. Examples are electric or hydrogen-based steel versus gas-based direct reduction with capture, and olefins from methanol made with captured CO2. Capture is modelled as separate route variants, not as a retrofit of existing plants.

Suggested text: "Industrial demand is expressed in physical output per sector, and each sector can be supplied by a reference route or by low-carbon alternatives (electrification, hydrogen, carbon capture, CO2 utilisation, biomass). The choice of route is therefore endogenous and directly coupled to the electricity, hydrogen and CO2 systems."

## 3. A full CO2 value chain with alternative accounting rules
The case models the full CO2 chain: capture at industrial plants and power plants, a CO2 pipeline network (including cross-border links), geological storage sites with capacity limits, utilisation in methanol production, and an atmosphere node for emissions. Two policy rules are implemented and compared. The first is one shared emission cap for all modelled countries. The second is a set of national caps in which CO2 exported for storage is credited to the exporting country. The national caps use the user-constraint mechanism described in Section 2.4. This makes the industrial case the main application of SpineOpt for carbon-capture-and-storage infrastructure and for emission accounting between countries.

## 4. Consistent scaling of annual budgets with representative periods
When the year is represented by a small number of representative days, annual (cumulative) limits must be scaled consistently with the period weights. Examples are biomass availability and CO2 storage injection limits. During the industrial case we found that limits which are not scaled can be wrong by a factor of up to 365 without causing any error, because the model still solves. We introduced a consistent rescaling as a standard model patch. This is a general methodological point for every SpineOpt application that uses representative periods.

## 5. Sensitivity to temporal resolution and long-duration storage
The case compares 3 and 10 representative days. With 10 days, the model values multi-day flexibility and builds iron-air (long-duration) storage, which it does not build with 3 days. The industrial routes and the location of refining also change. This shows that the number of representative periods is not only a computational setting; it can change investment decisions qualitatively.

## 6. Verification and traceability in practice
The case used a small test model (few regions, short time horizon) to check the full chain quickly before large runs. It also used systematic checks between the stages of the pipeline. For example, these checks revealed that CO2 emission factors were lost between the commodity database and the INES database, and that the CO2 pipeline network in the source data allowed flow in only one direction. These examples show the value of the intermediate databases and the input/output separation described in Sections 2.2 and 2.3: errors could be traced to a specific stage and corrected there.

## 7. Solving at scale (optional)
The mixed-resolution and FR+LU instances are large linear programmes that were solved with open-source (HiGHS) and commercial (Xpress) solvers. If relevant to the report, mention problem size and solve time here.

## Summary: same or different?
The architecture, INES, the transformation to SpineOpt, scenario management and the core SpineOpt features (multi-year investment, sector coupling, representative periods) are the same as in the Pan-EU case. The industrial case is different in:
- mixed spatial resolution;
- endogenous industrial route choice;
- the full CO2 chain with alternative accounting rules;
- the methodological lessons on budget scaling and temporal resolution.

These four points are its main additional technical contribution.
