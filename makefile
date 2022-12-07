default:
	echo Hello world

RunBaseline: SetupBaseline RunSequence

RunHoldoutTest20: SetupHoldoutTest20 RunSequence

RunHoldoutTest22: SetupHoldoutTest22 RunSequence

RunHoldoutTest64: SetupHoldoutTest64 RunSequence

SetupBaseline:
	python3 SetupAnalysis.py --Config yaml/Exponential20221012RBF_N10.yaml
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


