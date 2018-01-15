<%
  OutputLayers = ["{name:s}Output".format(name=name.title()) for name in NETINFO['target'].values()]
  UpdatesPerCall = CONFIG['UpdatesPerCall']
  weightDecay = CONFIG['weightDecay']
  batchSize = CONFIG['batchSize']
  learningRate = CONFIG['learningRate']
  momentum = CONFIG['momentum']
  reportInterval = CONFIG['reportInterval']
  SpikeThreshold = CONFIG['SpikeThreshold']
  SpikeThresholdStepSize = CONFIG['SpikeThresholdStepSize']
  TestEpoch = CONFIG['TestEpoch']
  ErrorCriterion = CONFIG['ErrorCriterion']

  if 'testGroupCrit' in CONFIG:
    testGroupCrit = CONFIG['testGroupCrit']
  else:
    testGroupCrit = 0.5

  if 'targetRadius' in CONFIG:
    targetRadius = CONFIG['targetRadius']
  else:
    targetRadius = 0

  if 'zeroErrorRadius' in CONFIG:
    zeroErrorRadius = CONFIG['zeroErrorRadius']
  else:
    zeroErrorRadius = 0

  if 'InitialWeights' in CONFIG:
    InitialWeights = CONFIG['InitialWeights']
  else:
    InitialWeights = 'init.wt'

  if 'ProcFiles' in CONFIG:
    ProcFiles = CONFIG['ProcFiles']
  else:
    ProcFiles = []
%>
proc main {} {
  global env
  global Test
  if {![ info exists env(PATH) ]} {
    set env(PATH) "/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/crcox/bin"
  }

  source "network.in"
% if ProcFiles:
  % for procfile in ProcFiles:
  source ${procfile}
  % endfor
% endif
  setObject testGroupCrit ${testGroupCrit}
  setObject targetRadius ${targetRadius}
  setObject numUpdates ${UpdatesPerCall}
  setObject weightDecay ${weightDecay}
  setObject batchSize ${batchSize}
  setObject zeroErrorRadius ${zeroErrorRadius}
  setObject learningRate ${learningRate}
  setObject momentum ${momentum}
  setObject reportInterval ${reportInterval}
  set SpikeThreshold ${SpikeThreshold}
  set SpikeThresholdStepSize ${SpikeThresholdStepSize}
  set TestEpoch ${TestEpoch}
  set ErrorCriterion ${ErrorCriterion}

  set WeightDir "./wt"
  if { ![file exists $WeightDir]} {
    file mkdir $WeightDir
  }

  resetNet
  set wtfile ${InitialWeights}
  if {[file exists $wtfile]} {
    puts "Loading ${InitialWeights}..."
    loadWeights $wtfile
  } else {
    puts "Saving ${InitialWeights}..."
    saveWeights $wtfile
  }

  loadExamples [file join "ex" "train.ex"] -exmode PERMUTED
  useTrainingSet train
  set numTrainingExamples [getObj trainingSet.numExamples]
  loadExamples [file join "ex" "test.ex"] -exmode ORDERED
  useTestingSet test
  set numTestingExamples [getObj testingSet.numExamples]
  set errlog [open [file join "error.log"] w]
  set MFHCcsv [open [file join "MFHC.csv"] w]
  set errList [errorInUnits $MFHCcsv {${' '.join(OutputLayers)}}]
  set PError [summarizeError $errList 0]
  set err [getObj error]
  set errHistory [list]
  set i 0
  while {$PError <%text>></%text> $ErrorCriterion} {
    saveWeights "prev.wt"
    set objective "infinity"
    for {set i 0} {$i <%text><</%text> $numTrainingExamples } {incr i} {
      loadWeights "prev.wt"
      doExample $i -set train -train
      set returnCode [test $numTestingExamples -return]
      if { $Test(totalError) <%text><</%text> $objective } {
        saveWeights "next.wt"
        set objective $Test(totalError)
      }
    }
    loadWeights "next.wt"

    # Log the (cross-entropy) error.
    puts $errlog [format "%.2f" $Test(totalError)]

    # Save the model weights. Periodically save to a persistent archive.
    incr i 1
    if { [expr {$i % $TestEpoch}] == 0 } {
      # Compute the (unit-wise) error
      set errList [errorInUnits $MFHCcsv {${' '.join(OutputLayers)}}]
      set PError [summarizeError $errList 0]
      set wtfile [file join $WeightDir [format "%d.wt" [getObj totalUpdates]]]
    }
  }
  saveWeights "final.wt"
  close $errlog
  close $MFHCcsv
  exit 0
}

if { [catch {main} msg] } {
  puts stderr "unexpected script error: $msg"
  exit 1
}

<%def name="join(x)" filter="trim">
  <%
    output = ' '.join(str(i) for i in x)
  %>
  output
</%def>
