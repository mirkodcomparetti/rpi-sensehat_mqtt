echo on
for /f "tokens=3,2,4 delims=/- " %%x in ("%date%") do set d=%%y%%x%%z
set data=%d%
Echo zipping...
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\rpideploy_%d%.zip" ".\setconfiguration.sh"
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\rpideploy_%d%.zip" ".\rpi_sensehat_mqtt.logrotate"
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\rpideploy_%d%.zip" ".\rpi_sensehat_mqtt.service"
"C:\Program Files\7-Zip\7z.exe" a -tzip ".\rpideploy_%d%.zip" ".\rpi_sensehat_mqtt.py"
echo Done!