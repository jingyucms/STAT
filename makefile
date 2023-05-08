# DeployBase = ~/Dropbox/Temp/Meow
DeployBase = ~/Dropbox/Presentations/20230328_HardBayesianResult_HardProbes2023_YiChen/Plots/

default:
	echo Hello world

now:
	python3 DumpAllData.py --Key tag

RunBaseline: SetupBaseline RunSequence

RunHoldoutTest20: SetupHoldoutTest20 RunSequence

RunHoldoutTest22: SetupHoldoutTest22 RunSequence

RunHoldoutTest64: SetupHoldoutTest64 RunSequence

SetupBaseline:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N15.yaml

SetupBaselineN5:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N5.yaml

SetupBaselineN10:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N10.yaml

SetupBaselineGoodPCAN10:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_GoodPCAN10.yaml

SetupBaselineN20:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N20.yaml

SetupBaselineMatern:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_N10.yaml

SetupTestAnalysis:
	python3 SetupAnalysis.py --Config yaml/TestAnalysis.yaml

SetupHadronOnly:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_HadronOnly.yaml

SetupHadronOnlyDefaultSys:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_HadronOnlyDefaultSys.yaml

SetupHadronOnlyFullyCorrelated:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_HadronOnlyDefaultSys.yaml --DefaultSysLength 9999 --TagSuffix FullyCorrelated

SetupHadronOnlyNonCorrelated:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_HadronOnlyDefaultSys.yaml --DefaultSysLength 0 --TagSuffix NonCorrelated

SetupHadronOnlyFirst60:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_HadronOnlyFirst60.yaml

SetupBaselineCentral:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --CentralityMax 10

SetupSmoothedCentral:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --CentralityMax 10 --DoSmoothing

SetupHoldoutTest20:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --Holdout 20 --CentralityMax 10

SetupHoldoutTest22:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --Holdout 22 --CentralityMax 10

SetupHoldoutTest64:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --Holdout 64 --CentralityMax 10

RunSequence: RunSequencePart0 RunEmulator RunSequencePart1 RunMCMC RunSequencePart2

RunSequencePlotOnly: RunSequencePart0 RunSequencePart1 RunSequencePart2

RunSequencePart0:
	python3 MakeSmallCovarianceMatrixPlot.py
	python3 MakeSmallDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

RunEmulator:
	python3 CleanPastFiles.py
	python3 RunEmulator.py

RunSequencePart1:
	python3 MakePCAPercentagePlot.py
	python3 MakePCAParameterPlot.py
	python3 MakeSmallDesignPredictedObservablePlot.py

RunExtraCheck:
	python3 MakePCACheckPlot.py

RunHoldoutCheck:
	python3 MakeHoldoutCheckPlot.py

RunMCMC:
	python3 RunMCMC.py

RunSequencePart2:
	python3 MakeMCMCSamplingPlot.py
	# python3 MakePosteriorCorrelationPlot.py
	python3 MakePosteriorCorrelationPlot.py --Config yaml/CorrelationExponentialConfig.yaml
	python3 MakePosteriorCorrelationPlot.py --Config yaml/CorrelationExponentialConfigSmall.yaml
	python3 MakeSmallPosteriorObservablePlot.py
	python3 MakePosteriorObservablePlot.py
	python3 MakeQHatPlot.py
	python3 MakeFPlot.py
	# python3 WriteToText.py
	# python3 WritePosteriorToText.py

RunSlice:
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron \
		--Label Jet Hadron \
		--Suffix JetVsHadron_T02E200 --DoKSTest True \
		--T 0.2 --E 200
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron \
		--Label Jet Hadron \
		--Suffix JetVsHadron_T02E100 --DoKSTest True \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4 \
		--Label Jet Hadron Both \
		--Suffix JetVsHadronVsAll \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableJet \
		--Label Jet Jet \
		--Suffix JetVsJet --DoKSTest True
	cp result/QHatSliceComparison*.pdf ~/Dropbox/Temp/Meow/

RunSlice20230223:
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEJet_ObservableJet STAT20221012ExponentialRBF_N4_OnlyATLASJet_ObservableJet STAT20221012ExponentialRBF_N4_OnlyCMSJet_ObservableJet \
		--Label Jet Hadron "ALICE jet" "ATLAS jet" "CMS jet" \
		--Suffix JetSeparateVsHadron_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_OnlySmallJet_ObservableJet STAT20221012ExponentialRBF_N4_OnlySmallJet \
		--Label Jet Hadron "Small jet" "Small jet + hadron" \
		--Suffix SmallJet_T02E100 \
		--T 0.2 --E 100
	cp result/QHatSliceComparison*.pdf ~/Dropbox/Temp/Meow/

RunSlice20230302:
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEJet_ObservableJet STAT20221012ExponentialRBF_N4_OnlyATLASJet_ObservableJet STAT20221012ExponentialRBF_N4_OnlyCMSJet_ObservableJet STAT20221012ExponentialRBF_N4_OnlyALICEHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyATLASHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyCMSHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyRHICHadron_ObservableHadron \
		--Label Jet Hadron "ALICE jet" "ATLAS jet" "CMS jet" "ALICE hadron" "ATLAS hadron" "CMS hadron" "RHIC hadron" \
		--Suffix JetSeparateVsHadronSeperate_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyATLASHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyCMSHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyRHICHadron_ObservableHadron \
		--Label Jet Hadron "ALICE hadron" "ATLAS hadron" "CMS hadron" "RHIC hadron" \
		--Suffix JetVsHadronSeparate_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyATLASHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyCMSHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyRHICHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEHadron_EnergyMax3000_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEHadron_EnergyMin3000_ObservableHadron \
		--Label Jet Hadron "ALICE hadron" "ATLAS hadron" "CMS hadron" "RHIC hadron" "ALICE hadron 2.76 TeV" "ALICE hadron 5.02 TeV" \
		--Suffix JetVsHadronSeparateV2_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEHadron_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEHadron_EnergyMax3000_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEHadron_EnergyMin3000_ObservableHadron \
		--Label Jet Hadron "ALICE hadron" "ALICE hadron 2.76 TeV" "ALICE hadron 5.02 TeV" \
		--Suffix JetVsHadronSeparateALICE_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_PTCut30_ObservableHadron STAT20221012ExponentialRBF_N4_PTUpTo30_ObservableHadron \
		--Label Jet Hadron "Hadron PT > 30" "Hadron PT up to 30" \
		--Suffix HadronCut_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEJet_EnergyMax3000_ObservableJet STAT20221012ExponentialRBF_N4_OnlyATLASJet_EnergyMax3000_ObservableJet STAT20221012ExponentialRBF_N4_OnlyCMSJet_EnergyMax3000_ObservableJet \
		--Label Jet Hadron "ALICE jet" "ATLAS jet" "CMS jet" \
		--Suffix JetSeparate2760VsHadron_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron STAT20221012ExponentialRBF_N4_OnlyALICEJet_EnergyMin3000_ObservableJet STAT20221012ExponentialRBF_N4_OnlyATLASJet_EnergyMin3000_ObservableJet STAT20221012ExponentialRBF_N4_OnlyCMSJet_EnergyMin3000_ObservableJet \
		--Label Jet Hadron "ALICE jet" "ATLAS jet" "CMS jet" \
		--Suffix JetSeparate5020VsHadron_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_PTUpTo100_ObservableJet STAT20221012ExponentialRBF_N4_PTCut100_ObservableJet \
		--Label Jet "Jet PT < 100" "Jet PT > 100" \
		--Suffix JetPT100_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_PTUpTo250_ObservableJet STAT20221012ExponentialRBF_N4_PTCut250_ObservableJet \
		--Label Jet "Jet PT < 250" "Jet PT > 250" \
		--Suffix JetPT250_T02E100 \
		--T 0.2 --E 100
	cp result/QHatSliceComparison*.pdf ~/Dropbox/Temp/Meow/

RunSlice20230303:
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut10_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut12_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut14_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut16_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut18_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut20_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut22_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut24_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut26_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut28_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut30_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut40_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut50_ObservableHadron \
		--Label Jet Hadron \
			"Hadron PT > 10" "Hadron PT > 12" "Hadron PT > 14" "Hadron PT > 16" "Hadron PT > 18" \
			"Hadron PT > 20" "Hadron PT > 22" "Hadron PT > 24" "Hadron PT > 26" "Hadron PT > 28" \
			"Hadron PT > 30" "Hadron PT > 40" "Hadron PT > 50" \
		--Suffix HadronScan_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut10_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut14_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut18_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut22_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut26_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut30_ObservableHadron \
		--Label Jet Hadron \
			"Hadron PT > 10" "Hadron PT > 14" "Hadron PT > 18" "Hadron PT > 22" "Hadron PT > 26" "Hadron PT > 30" \
		--Suffix HadronScanV2_T02E100 \
		--T 0.2 --E 100
	cp result/QHatSliceComparison*.pdf ~/Dropbox/Temp/Meow/

RunSlice20230305:
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20221012ExponentialRBF_N4_ObservableJet STAT20221012ExponentialRBF_N4_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut30_OnlyALICEHadron_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut30_OnlyATLASHadron_ObservableHadron \
			STAT20221012ExponentialRBF_N4_PTCut30_OnlyCMSHadron_ObservableHadron \
		--Label Jet Hadron "ALICE hadron PT > 30" "ATLAS hadron PT > 30" "CMS hadron PT > 30" \
		--Suffix JetVsHadronSeparatePT30_T02E100 \
		--T 0.2 --E 100
	cp result/QHatSliceComparison*.pdf ~/Dropbox/Temp/Meow/

RunAlternate:
	# python3 MakeSmallPosteriorObservablePlot.py
	python3 MakeSmallPosteriorObservablePlot.py \
		--Alternate STAT20221012ExponentialRBF_N4_CentralityMin10 \
		--AlternateLabel "Peripheral only" \
		--Suffix PeripheralOnly
	python3 MakeSmallPosteriorObservablePlot.py \
		--Alternate STAT20221012ExponentialRBF_N4_CentralityMax10 \
		--AlternateLabel "Central only" \
		--Suffix CentralOnly
	# python3 MakeAlternateChi2Plot.py \
	# 	--Alternate STAT20221012ExponentialRBF_N4_CentralityMax10 \
	# 	--AlternateLabel "Central only" \
	# 	--Suffix CentralOnly
	# python3 MakeAlternateChi2Plot.py \
	# 	--Alternate STAT20221012ExponentialRBF_N4_CentralityMin10 \
	# 	--AlternateLabel "Peripheral only" \
	# 	--Suffix PeripheralOnly

RunAlternate20230223:
	python3 MakeSmallPosteriorObservablePlot.py \
		--Alternate STAT20221012ExponentialRBF_N4_OnlySmallJet \
		--AlternateLabel "Small jet + hadron" \
		--Suffix SmallJetOnly

RunSlice20230321:
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20230320ExponentialRBF_N4_ObservableJet STAT20230320ExponentialRBF_N4_ObservableHadron \
		--Label Jet Hadron \
		--Suffix JetVsHadron_T02E100 \
		--T 0.2 --E 100
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20230320ExponentialRBF_N4_ObservableJet STAT20230320ExponentialRBF_N4_ObservableHadron STAT20230320ExponentialRBF_N4_PTCut30_ObservableHadron STAT20230320ExponentialRBF_N4_PTUpTo30_ObservableHadron \
		--Label Jet Hadron "Had. $$ p_{T} > 30$$ GeV" "Had. $$ p_{T} \leq 30$$ GeV"\
		--Suffix JetVsHadronPTSplit_T02E100 \
		--T 0.2 --E 100

RunAlternate20230321:
	python3 MakeSmallPosteriorObservablePlot.py \
		--Alternate STAT20230320ExponentialRBF_N4_PTCut30_ObservableHadron \
		--AlternateLabel "Hadron $$ p_{T} > 30$$ GeV" \
		--Suffix HadronPTCut30
	python3 MakeSmallPosteriorObservablePlot.py \
		--Alternate STAT20230320ExponentialRBF_N4_OnlySmallJet \
		--AlternateLabel "Small jet + hadron" \
		--Suffix SmallJetOnly
	python3 MakePosteriorObservablePlot.py \
		--Alternate STAT20230320ExponentialRBF_N4_PTCut30_ObservableHadron \
		--AlternateLabel "Hadron $$ p_{T} > 30$$ GeV" \
		--Suffix HadronPTCut30
	
RunSlice20230325:
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20230320ExponentialRBF_N4_ObservableJet STAT20230320ExponentialRBF_N4_ObservableHadron \
		--Label Jet Hadron \
		--Suffix JetVsHadron_T02E100 \
		--T 0.2 --E 100 --DoOverlapArea True
	python3 MakeQHatSlicePlot.py \
		--Plot STAT20230320ExponentialRBF_N4_ObservableJet STAT20230320ExponentialRBF_N4_ObservableHadron STAT20230320ExponentialRBF_N4 \
		--Label Jet Hadron Both \
		--Suffix JetVsHadronVsAll \
		--T 0.2 --E 100
	cp result/QHatSliceComparison*.pdf ~/Dropbox/Temp/Meow/

RunAlternate20230325:
	python3 MakeSmallPosteriorObservablePlot.py 
	python3 MakeSmallPosteriorObservablePlot.py \
		--Alternate STAT20230320ExponentialRBF_N4_PTCut30_ObservableHadron \
		--AlternateLabel "Hadron $$ p_{T} > 30$$ GeV" \
		--Suffix HadronPTCut30
	python3 MakeSmallPosteriorObservablePlot.py \
		--Alternate STAT20230320ExponentialRBF_N4_OnlySmallJet \
		--AlternateLabel "Small jet + hadron" \
		--Suffix SmallJetOnly


Deploy:
	mkdir -p $(DeployBase)
	# cp result/STAT20221012ExponentialRBF_N4/plots/* ~/Dropbox/Temp/Meow/
	# rsync -rvv result/STAT2023* $(DeployBase)/
	rsync -rvv result/*pdf $(DeployBase)/


