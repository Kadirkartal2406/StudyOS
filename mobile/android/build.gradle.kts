allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

// Build output redirected to C:\FlutterBuild to avoid impellerc failing on paths
// with non-ASCII characters (OneDrive\Masaüstü).
val flutterBuildRoot = File("C:/FlutterBuild")
rootProject.layout.buildDirectory.set(flutterBuildRoot)

subprojects {
    layout.buildDirectory.set(File("C:/FlutterBuild/${project.name}"))
}
subprojects {
    project.evaluationDependsOn(":app")
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
