@echo off
echo ==================================
echo Starting Jenkins
echo ==================================
cd jenkins
echo.
echo Starting Jenkins on port 8080...
echo This will take about 60 seconds...
echo.
"C:\Program Files\Microsoft\jdk-17.0.17.10-hotspot\bin\java.exe" -jar jenkins.war --httpPort=8080
pause
