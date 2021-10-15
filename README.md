# Project GP: Network Analysis
To identify the best path and effectively automate the process using QGIS Python to create and reiterate evacuation paths during the flooding to save time and lives.

**How to run the codes**
1. Open QGIS and open the code.py file using QGIS Scripts
![image](https://user-images.githubusercontent.com/80443493/137457987-38bdd4da-ce5e-4514-8abe-0661a9cf565b.png)

2. Run the script                                   
![image](https://user-images.githubusercontent.com/80443493/137458045-f55cde87-6888-4749-b781-664f4e4d6079.png)

3. Input path to all the files (shapefile and qml) and provide the following details: <br/>
  a. Buffer distance value <br/>
  b. Selected safety point name <br/>
  c. Selected safety point latitude and longitude                                             
![image](https://user-images.githubusercontent.com/80443493/137458213-41af22e8-dfb5-4f3f-88ab-f726765e1cfa.png)

4. Once the desired layers are loaded, run the export_image.py code using the Python Console
![image](https://user-images.githubusercontent.com/80443493/137458312-9fb413d9-c716-40bf-af63-7589e1802d66.png)

5. Once the code is executed the map will be zoomed to the extent of either:
  a. Final path - address points to the safety location
  b. Entire study area
  Additionally, the view on the QGIS Map Canvas is also exported as an image in the output folder
![image](https://user-images.githubusercontent.com/80443493/137458386-f89b5f60-569c-443f-9f1a-78c0fbb5b4cd.png)

