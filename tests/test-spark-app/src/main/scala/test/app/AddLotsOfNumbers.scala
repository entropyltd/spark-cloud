package test.app

import java.io.File

import org.apache.spark.{SparkContext, SparkConf}

object AddLotsOfNumbers {

  def main(args: Array[String]): Unit = {

    val fullPathToFile: String = args(0)

    val sc: SparkContext = new SparkContext(new SparkConf().setAppName("Add lots of numbers"))

    val numPartitions: Int = 100
    val doSomethingNum: Int = 2000

    val count: Int =
      sc.makeRDD(1 to 1000000)
      .repartition(numPartitions)
      .map(_ =>
        (1 to doSomethingNum).map(_.toString.length)
        .sum)
      .reduce(_ + _)

    val pw = new java.io.PrintWriter(new File(fullPathToFile))
    try pw.write(count.toString + "\n") finally pw.close()

  }
}