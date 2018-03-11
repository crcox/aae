proc candide_optimization() {
  # This is not actually implemented properly to run as a proc, but it's a start...
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
}
