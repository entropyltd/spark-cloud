val companyName = "app"

val domain = "test"

val projectName = "spark-cluster-launch-test"

name := projectName

scalaVersion := "2.10.4"

val sparkVersion = "1.5.1"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % sparkVersion % "provided" withSources() withJavadoc()
)

organization := domain + "." + companyName