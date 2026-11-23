# Routes to participant-level data

Checked 2026-11-23. Facts only. No participant-level data from any of these trials is public.
RepairSplit has not been run on real trial data.

"Verified" means the statement was read in this check, in the source named. "Not verified" means
the source could not be reached and the entry rests on the earlier survey or on a secondary source.

## Clemastine crossover trial (ReBUILD)

Lancet 2017;390:2481-2489. PMID 29029896. doi:10.1016/S0140-6736(17)32346-2. Registry NCT02040298.

| Item | Finding | Status |
|---|---|---|
| Route | On request to the authors. | From secondary papers, see below. |
| Registry | Record updated 2025-09-17. Summary results are posted. The record has no individual-participant-data sharing section. | Verified (ClinicalTrials.gov API). |
| Primary paper's own data-sharing statement | Not read. The publisher's page returned HTTP 403 to an automated request and the paper is not in PubMed Central. Whether the 2017 paper has a data-sharing statement at all is unknown. | Not verified. |
| Secondary paper, J Neurol Neurosurg Psychiatry 2022 (doi:10.1136/jnnp-2022-329221, PMC9984688) | "Data are available upon reasonable request." | Verified (full text). |
| Secondary paper, PNAS 2023 (doi:10.1073/pnas.2217635120, PMC10193980) | States that data tables, analysis code and scripts "have been deposited in the public repository Dryad", except information that could compromise anonymisation. The reference is a Dryad share link, deposited 2023-04-30, titled "MWF of the corpus callosum: Results from the ReBUILD trial". | Verified (full text). |
| That Dryad link | Resolves. The page says the dataset "is currently Private for Peer Review" and lists three files: `mwf_data.csv`, `mwf_pnas_code.do`, `README.md`. | Verified that the page loads and lists the files. Files were not downloaded or opened. |
| Does the Dryad deposit hold VEP latency per participant? | By its title it holds myelin water fraction data, not VEP. | Not verified; contents not opened. |
| Summary numbers usable without participant data | Registry results give mean and SD of VEP change per eye for clemastine and placebo periods (93 eyes). | Verified. Used in `docs/VALIDATION.md`. |

## Bexarotene phase 2a (CCMR One)

Lancet Neurol 2021;20:709-720. PMID 34418398. doi:10.1016/S1474-4422(21)00179-4. Registry ISRCTN14265371.

| Item | Finding | Status |
|---|---|---|
| Route | On request to the chief investigator, with a signed data access agreement. | Verified in a secondary paper, see below. |
| Registry | Record last updated 2023-11-07. Individual-participant-data sharing statement: "Not provided at time of registration". Sharing plan field: "No". | Verified (ISRCTN API). |
| Primary paper's own data-sharing statement | Not read. The publisher's page returned HTTP 403 and the paper is not in PubMed Central. The survey's wording for this paper could not be checked against the paper itself. | Not verified. |
| Secondary paper, Brain Commun 2025 (doi:10.1093/braincomms/fcaf032, PMC11852336) | Lists de-identified participant data, the primary efficacy endpoint data set, the visual evoked potentials data set and the lesional magnetisation transfer ratio data set, with data dictionaries, as "available for researchers from our website". Access requests go to the chief investigator. "A signed data access agreement will be required and investigator support might be provided if part of an academic collaboration." | Verified (full text). |
| Follow-up paper, Mult Scler 2024 (doi:10.1177/13524585241233177, PMC11290016) | "Deidentified participant data will be made available online on publication" at a department web address. | Verified (full text). |
| That department web address | Redirects to the department home page. No dataset page is reached. | Verified (HTTP redirect followed). |
| Group website named in the CCMR Two protocol | Home page loads. Its menu has research, news and outreach pages and no data or dataset page. | Verified for the home page menu only; inner pages not read. |
| Primary endpoint data on the EudraCT site | Stated by the survey. | Not verified in this check. |
| Summary numbers usable without participant data | The abstract gives the SD of MTR change per arm (0.98 and 0.84 percentage units, 26 randomised per arm). | Verified. Used in `docs/VALIDATION.md`. |

## Metformin plus clemastine phase 2a (CCMR Two)

Protocol: Trials 2025;26:562. PMID 41361285. doi:10.1186/s13063-025-09254-2. Registry NCT05131828.

| Item | Finding | Status |
|---|---|---|
| Route | On request to the chief investigator, with a signed data access agreement, once the results are published. | Verified in the protocol paper. |
| Registry | Record updated 2025-12-11. Plan to share individual participant data: "No". No results posted. Enrolment 70. | Verified (ClinicalTrials.gov API). |
| Protocol paper's statement | "The protocol, statistical analysis plan and the deidentified dataset for the primary and secondary outcomes (with corresponding statistical codes) will be made available with publication" from the research group's website. "A signed data access agreement will be required, and investigator support might be provided if part of an academic collaboration." | Verified (full text, PMC12683890). |
| Registry and protocol paper | They disagree: the registry says no sharing, the paper describes sharing on request. | Verified, both read. |
| Results paper | None found. A PubMed search for the trial on 2026-11-23 returned only the protocol. Results were presented at ECTRIMS 2025 (abstract 152/O133) and are known here only from conference reports. | Verified that the search returned nothing else. A paper indexed under different terms could have been missed. |
| Data available now | None. The stated route opens "with publication". | Follows from the rows above. |

## Not checked

- Whether any of the three groups currently answers data requests, how long it takes, or what the
  agreement requires. Nobody was contacted.
- Sponsor platforms (Vivli, ClinicalStudyDataRequest, YODA). None of these three trials names one.
  They are academic trials; the survey found a sponsor platform route only for the opicinumab trials.
- The data-sharing statements inside the two Lancet-family primary papers, as noted above.
