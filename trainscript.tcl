proc main {} {
  global env
  global Test
  if {![ info exists env(PATH) ]} {
    set env(PATH) "/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/crcox/bin"
  }

  source "network.in"
  setObject testGroupCrit 0.5
  setObject targetRadius 0
  setObject numUpdates 20
  setObject weightDecay 0
  setObject batchSize 25
  setObject zeroErrorRadius 0
  setObject learningRate 0.005
  setObject momentum 0
  setObject reportInterval 20
  set SpikeThreshold 5.0
  set SpikeThresholdStepSize 1.5
  set TestEpoch 50
  set ErrorCriterion 0.2

  set WeightDir "./wt"
  if { ![file exists $WeightDir]} {
    file mkdir $WeightDir
  }

  resetNet
  set wtfile init.wt
  if {[file exists $wtfile]} {
    puts "Loading init.wt..."
    loadWeights $wtfile
  } else {
    puts "Saving init.wt..."
    saveWeights $wtfile
  }

  loadExamples [file join "ex" "train.ex"] -exmode PERMUTED
  useTrainingSet train
  loadExamples [file join "ex" "test.ex"] -exmode ORDERED
  useTestingSet test
  set errlog [open [file join "error.log"] w]
  set MFHCcsv [open [file join "MFHC.csv"] w]
  set errList [errorInUnits $MFHCcsv {['SemOutput', 'PhonOutput']}]
  set PError [summarizeError $errList 0]
  set err [getObj error]
  set errHistory [list]
  set i 0
  while {$PError > $ErrorCriterion} {
    train -a steepest
    set err [getObj error]
    if { [llength $errHistory] == 10 } {
      set spike [detectSpike $errHistory $err $SpikeThreshold]
      if { $spike } {
        # Revert to the prior weight state and half the learning rate.
        puts "Spike!"
        loadWeights "oneBack.wt"
        setObject learningRate [expr {[getObj learningRate] / 2}]
        set SpikeThreshold [expr {$SpikeThreshold * $SpikeThresholdStepSize}]
        continue
      }
    }
    # Update and maintain the (cross-entropy) error history.
    lappend errHistory $err
    if {[llength $errHistory] > 10} {
      set errHistory [lrange $errHistory 1 end]
    }

    # Log the (cross-entropy) error.
    puts $errlog [format "%.2f" $err]

    # Save the model weights. Periodically save to a persistent archive.
    saveWeights "oneBack.wt"
    incr i 1
    if { [expr {$i % $TestEpoch}] == 0 } {
      # Compute the (unit-wise) error
      set errList [errorInUnits $MFHCcsv {['SemOutput', 'PhonOutput']}]
      set PError [summarizeError $errList 0]
      set wtfile [file join $WeightDir [format "%d.wt" [getObj totalUpdates]]]
      file copy "oneBack.wt" $wtfile
    }
  }
  file delete "oneBack.wt"
  close $errlog
  close $MFHCcsv
  exit 0
}

if { [catch {main} msg] } {
  puts stderr "unexpected script error: $msg"
  exit 1
}