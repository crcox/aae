# function in the aae module. This script should be run from the root
# This script was automatically generated using the json2trainScript
# of an experiment folder, which will have sub-folders for individual
# runs of the experiment (00/, 01/, etc) and a folder for example
# files (ex/). Lens .in files should be in the root directory, as
# well. The subfolder for each run should have a folder for weights.
# Error, accuracy, and activation values will be written into separate
# files within the directory for each run.
proc main {} {
  global env
  global Test
  if {![ info exists env(PATH) ]} {
    set env(PATH) "/usr/lib64/qt-3.3/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin:/home/crcox/bin"
  }

  source "network.in"
  source bin/tcl/errorInUnits.tcl
  source bin/tcl/summarizeError.tcl
  source bin/tcl/detectSpike.tcl

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

  set WeightDir "./"

  resetNet
  set wtfile [file join $WeightDir [format "init_%d.wt" [getObj totalUpdates]]]
  if {[file exists $wtfile]} {
    loadWeights $wtfile
  } else {
    saveWeights $wtfile
  }

  ################################################################################
  #                                Start Phase 1                                 #
  ################################################################################
  loadExamples [file join "ex" "train_sae.ex"] -set "train_sae" -exmode PERMUTED
  loadExamples [file join "ex" "train_sae_aw.ex"] -set "train_sae_aw" -exmode PERMUTED
  loadExamples [file join "ex" "test.ex"] -exmode ORDERED
  if {[expr {rand()}] > 0.5} {
    set trainToggle 0
    useTrainingSet "train_sae"
  } else {
    set trainToggle 1
    useTrainingSet "train_sae_aw"
  }
  useTestingSet test
  set errlog [open [file join "phase01_err.log"] w]
  set MFHCcsv [open [file join "phase01_MFHC.csv"] w]
  set errList [errorInUnits $MFHCcsv {PhonOutput SemOutput}]
  set PError [summarizeError $errList 0]
  set err [getObj error]
  set errHistory [list]
  set i 0
  while {$PError > 0.15} {
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
      set errList [errorInUnits $MFHCcsv {PhonOutput SemOutput}]
      set PError [summarizeError $errList 0]
      set wtfile [file join $WeightDir [format "phase01_%d.wt" [getObj totalUpdates]]]
      file copy "oneBack.wt" $wtfile

      incr trainToggle 1
      if { [expr {$trainToggle % 2}] == 0 } {
        useTrainingSet "train_sae"
      } else {
        useTrainingSet "train_sae_aw"
      }
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
