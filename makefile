default:
	echo Hello world

RunBaseline: SetupBaseline RunSequence

RunHoldoutTest20: SetupHoldoutTest20 RunSequence

RunHoldoutTest22: SetupHoldoutTest22 RunSequence

RunHoldoutTest64: SetupHoldoutTest64 RunSequence

SetupBaseline:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N5.yaml
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupTestAnalysis:
	python3 SetupAnalysis.py --Config yaml/TestAnalysis.yaml
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupHadronOnly:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_HadronOnly.yaml
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupHadronOnlyDefaultSys:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_HadronOnlyDefaultSys.yaml
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupHadronOnlyFullyCorrelated:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_HadronOnlyDefaultSys.yaml --DefaultSysLength 9999 --TagSuffix FullyCorrelated
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupHadronOnlyNonCorrelated:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012Matern_HadronOnlyDefaultSys.yaml --DefaultSysLength 0 --TagSuffix NonCorrelated
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupHadronOnlyFirst60:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_HadronOnlyFirst60.yaml
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupBaselineCentral:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --CentralityMax 10
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupSmoothedCentral:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --CentralityMax 10 --DoSmoothing
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupHoldoutTest20:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --Holdout 20 --CentralityMax 10
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupHoldoutTest22:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --Holdout 22 --CentralityMax 10
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

SetupHoldoutTest64:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF.yaml --Holdout 64 --CentralityMax 10
	python3 MakeCovarianceMatrixPlot.py
	python3 MakeDesignObservablePlot.py
	python3 MakeDesignSpacePlot.py

RunSequence: RunSequencePart1 RunSequencePart2

RunSequencePart1:
	python3 CleanPastFiles.py
	python3 RunEmulator.py
	python3 MakePCAPercentagePlot.py
	python3 MakeDesignPredictedObservablePlot.py

RunExtraCheck:
	python3 MakePCACheckPlot.py

RunHoldoutCheck:
	python3 MakeHoldoutCheckPlot.py

RunSequencePart2:
	python3 RunMCMC.py
	python3 MakeMCMCSamplingPlot.py
	python3 MakePosteriorCorrelationPlot.py
	python3 MakePosteriorObservablePlot.py
	python3 WriteToText.py
	python3 WritePosteriorToText.py


