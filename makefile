default:
	echo Hello world

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

RunSequence: RunSequencePart0 RunSequencePart1 RunSequencePart2

RunSequencePart0:
	python3 MakeSmallCovarianceMatrixPlot.py
	python3 MakeSmallDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

RunSequencePart1:
	python3 CleanPastFiles.py
	python3 RunEmulator.py
	python3 MakePCAPercentagePlot.py
	python3 MakePCAParameterPlot.py
	python3 MakeSmallDesignPredictedObservablePlot.py

RunExtraCheck:
	python3 MakePCACheckPlot.py

RunHoldoutCheck:
	python3 MakeHoldoutCheckPlot.py

RunSequencePart2:
	python3 RunMCMC.py
	python3 MakeMCMCSamplingPlot.py
	python3 MakePosteriorCorrelationPlot.py
	python3 MakeSmallPosteriorObservablePlot.py
	python3 MakeQHatPlot.py
	# python3 WriteToText.py
	# python3 WritePosteriorToText.py


