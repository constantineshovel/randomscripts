# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
#RANDOMSCRIPTS 4 GEOSCIENCES by ConstantineShovel
#https://github.com/constantineshovel/randomscripts
# Created on: October 2024
# Author: Costantino Pala, PhD student at Cagliari State University (Sardinia) 
# Contact: costantino.pala.geo@proton.me
#This script works on ArcMAP10.8.2 and should be tested on ArcGIS Pro
#
# Usage:
#   INUE - Post Fire Erosion Susceptibility Assessment Tool
#   Available functions and commands:
#     PFES() - Calculates Post-Fire Erosion Susceptibility using IC and reclassified burn severity (rBS)
#     IC(dem_units, algorithm) - Calculates the Sediment Connectivity Index with chosen DEM units and hydrology algorithm
#     ARBURES(threshold) - Calculates NDVI and reclassifies it using a specified threshold (e.g., 0.25)
#     FOGU() - Generates NBR, dNBR, and burn severity classification, and drafts the wildfire perimeter
#     DI() - Evaluates effects of disconnection structures, like terraces or post-fire emergency works
#     RIU(algorithm) - Drafts watersheds and river networks, accepting a DEM input (algorithms: D8, MFD, DINF)
#     INUE(command, dem_units, algorithm, threshold) - Full analysis with options: "postfire", "postfire disconnected", "vegetation recovery", "vegetation recovery disconnected"
#
# Description:
#   This tool is designed to assess erosion susceptibility in post-fire landscapes. It calculates:
#     - Sediment Connectivity Index (IC) as proposed by Borselli et al. (2008), with roughness index modification from Cavalli et al. (2013)
#     - Post-fire erosion susceptibility based on reclassified burn severity (rBS)
#     - The effects of vegetation recovery on erosion susceptibility, using NDVI from Sentinel-2 L2A images
#   Outputs a susceptibility map.
#
# Required Inputs:
#   <elevation_tif> - DEM raster file (Digital Elevation Model)
#   <roadmask_tif> - raster for roads and urban areas (look at Borselli et al. 2008)
#   <reclassified_Burn_Severity> - rBS raster layer
#   <Disconnecting_Index> - Disconnected Areas raster layer
#   <Sentinel_2_L2A_images> - Sentinel-2 L2A imagery for NDVI calculation
#
# References:
#   Borselli, L., Cassi, P., & Torri, D. (2008). Prolegomena to sediment and flow connectivity in the landscape. Catena, 75(3), 268–277. DOI: 10.1016/j.catena.2008.07.006
#   Cavalli, M., Trevisani, S., Comiti, F., & Marchi, L. (2013). Geomorphometric assessment of spatial sediment connectivity. Geomorphology, 188, 31–41. DOI: 10.1016/j.geomorph.2012.05.007
#   Key, C. H., & Benson, N. C. (2006). Landscape assessment: Ground measure of severity, the Composite Burn Index. USDA Forest Service.
#   Keeley, J. E. (2009). Fire intensity, fire severity and burn severity. Int. J. Wildland Fire, 18(1), 116–126. DOI: 10.1071/WF07049
#   Rouse, J. W., Haas, R. H., Schell, J. A., & Deering, D. W. (1974). Monitoring vegetation systems with ERTS. NASA, ERTS Symposium, 1, 309–317
#   European Space Agency (ESA). (2016 - present). Sentinel-2 L2A imagery. Retrieved from Copernicus Open Access Hub
# ---------------------------------------------------------------------------



#_______________________________________________________________________________________________


#Import arcpy, arcpy.sa, arcpy.mapping and tkinter.filedialog modules
import arcpy #arcgis
import arcpy.sa as sa #statistical analysis toolbox
import arcpy.mapping as map 
import tkinter as tk
import tkinter.filedialog as d #to open input files with graphical interface

#______________________WELCOME MESSAGE_______________

print("Welcome to INUE - Post Fire Erosion Susceptibility Assessment tool - v.1.0.0.")

#____________________________________________________ 

root = tk.Tk()
root.withdraw()
print("Select the folder where to save the files")
arcpy.env.workspace =  d.askdirectory(title="Select Folder to Save Files") #assetat su tretu pro triballiare
arcpy.env.workspace.replace('/', '\\') #mudat su tretu in d-una manera chi a Python andet bene
arcpy.env.overwriteOutput = True #permitit de iscriere unu file subra de s'ateru
prj = arcpy.mapping.MapDocument("CURRENT") #assetat su progetu
mxd = map.MapDocument("CURRENT") #assetat sa mapa che a destinu de sos documentos chi faghet
adf = mxd.activeDataFrame
outdir = arcpy.env.workspace + "\\" #agiunghet unu slash a su tretu de tribagliu. Serbit pro s'ammentare sos file.
print('Now call one of the modules. Type help("commands") to discover all the available modules')

#_________________________CHANGING OUTPUT FOLDER___________________________________________________________

def ammenta():
	print("Select the folder where you want to save the files")
	arcpy.env.workspace =  d.askdirectory(title="Select Folder to Save Files") 
	arcpy.env.workspace.replace('/', '\\') 
	outdir = arcpy.env.workspace + "\\"
	print("The new output folder is:", outdir)
	print("Now call one of the modules and go to take a coffe, you deserve it, really.")



#_________________________OUTPUT PATHS______________________________________________________________________

# Local variables:
Output_drop_raster = ""
oFLOWDIR = outdir + "FlowDir.tif"
oDIRMASK = outdir + "dirmask.tif"
oACCMASK = outdir + "accmask.tif"
oRIVERMASK = outdir + "rivermask.tif"
oDIRFINAL = outdir + "dirfinal.tif"
oMEANDEM = outdir + "meandem.tif"
oRESTOPO = outdir + "restopo.tif"
oW = outdir + "W.tif"
oACCSEMIFINAL = outdir + "accsemifinal.tif"
oACCFinal = outdir + "accfinal.tif"
oWMean = outdir + "wmean.tif"
oSLOPE = outdir + "slope.tif"
oS = outdir + "S.tif"
oSMean = outdir + "smean.tif"
oDup = outdir + "DUP.tif"
oinv_WS = outdir + "invws.tif"
oX = outdir + "x.tif"
oDdn = outdir + "DDN.tif"
oIC = outdir + "SedimentConnectivityIndex.tif"
oPost_Fire_Erosion_Susceptibility_Map = outdir + "PFES.tif"
oWemiMean = outdir + "WemiMean.tif"
oWFMean = outdir + "WFMean.tif"
oSemiMean = outdir + "SemiMean.tif"
oSFMean = outdir + "SFMean.tif"
oslopezero = outdir + "oslopezero.tif"
osz05 = outdir + "osz05.tif"
oWSMeans = outdir + "WSMeans.tif"
oACCFinal25 = outdir + "ACCFinal25.tif"
oX0 = outdir + "X0.tif"
oXinvWS = outdir + "XinvWS.tif"
onormalizedIC = outdir + "normalizedIC.tif"
oPFESmap = outdir + "POSTFIRESUSCEPTIBILITYMAP.tif"
odupddn = outdir + "dupddn.tif"
onbrpre = outdir +"nbrprefire.tif"
onbrpost = outdir + "nbrpostfire.tif"
odnbr = outdir + "dNBR.tif"
obs = outdir + "BURNSEVERITY.tif"
owfp = outdir + "WILDFIREPERIMETER.tif"
owfpsh = outdir + "burntscarshapefile.shp"
oFILLED = outdir + "oFILLED.tif"
oFLOWDIRE = outdir + "oFLOWDIRE.tif"
oACCFLOW = outdir + "oACCFLOW.tif"
oRIVNET = outdir + "oRIVNET.tif"
oBASIN = outdir + "oBASIN.tif"
obasinshape = outdir + "obasinshape.tif"
ondvi = outdir + "NDVI.tif"
oBJ4T = outdir + "bj4t.tif"
oBJ8T = outdir + "bj8t.tif"
oBJ12T = outdir + "bj12t.tif"
obr8pre = outdir + "br8pre.tif"
obr8post = outdir + "br8post.tif"
obr12pre = outdir + "br12pre.tif"
obr12post = outdir + "br12post.tif"
ovr = outdir + "vr.tif"
othr = outdir + "ndvithr.tif"
oreclassBS = outdir + "BURNSEVERITYCLASSESPFES.tif"
orivershape = outdir + "RIVERNETWORK.shp"
oresdem = outdir + "resampledem.tif"
oWS16 = outdir + "ws16.tif"
icfilldem = outdir + "oicfilldem.tif"
odmap = outdir + "PFESDISCONNECTED.tif"
PWIndex = outdir + "PersonalWindex.tif"
orr = outdir + "rr.tif"
nodtif = outdir + "nodtif.tif"
conodtif = outdir + "conodtif.tif"
norgtif = outdir + "norgtif.tif"



# _________________________USER GUIDE______________________________________________________________________

def help(module):
    """
    Available commands: 
    PFES(), 
    IC(), 
    ARBURES(threshold), threshold is comprised in the range [-1, +1]
    FOGU(), 
    DI(), 
    RIU(),
    INUE(commands), commands are: postfire - postfire disconnected - vegetation recovery - vegetation recovery disconnected
    help(module), modules are: "PFES" - "IC" - "ARBURES" - "FOGU" - "DI" - "RIU" - "INUE" -"ammenta"
    ammenta()
    """
    if module == "IC":
        print('Welcome to the IC User Guide. IC allows you to easily calculate the sediment connectivity index, following the procedure proposed by Borselli et al. (2008), with the modification proposed in Cavalli et al. (2013). Using IC you need to specify the DEM units and the algorithm for flow direction and flow accumulation. Available DEM units: Example: If you want to calculate IC on a dem with foot units using the D infinity algorithm you need to type IC("FOOT", "DINF") then press enter. DEM UNITS: "INCH", "FOOT", "YARD", "MILE_US", "NAUTICAL_MILE", "MILLIMETER", "CENTIMETER", "METER", "KILOMETER", "DECIMETER". Algorithms: "D8", "DINF"')
    
    elif module == "PFES":
        print("Welcome to the PFES User Guide. PFES stands for Post Fire Erosion Susceptibility, and it calculates susceptibility to erosion using the sediment connectivity index (IC) from Borselli et al. (2008) and Cavalli et al. (2013), coupled with reclassified burn severity classes (rBS).")
        print("You can calculate IC and rBS by calling the functions ic() and rbs(), respectively. Once calculated, call PFES() to create the post-fire erosion susceptibility map. Low-risk areas = 0, High-risk areas = max. Call the function using PFES().")
    
    elif module == "ARBURES":
        print("Welcome to the ARBURES Vegetation Tool User Guide. ARBURES calculates NDVI for the selected period and reclassifies it using a specified threshold.")
        print("You can call ARBURES by typing ARBURES(x), where x is the threshold (a decimal number, like 0.25). ARBURES output should be multiplied by PFES output to model the effects of post-fire vegetation recovery.")
        print("Low-risk areas = 0, High-risk areas = max. Input values are Sentinel-2 L2A Band 04 and Band 08 images. The threshold values are crucial for assessing the effects of vegetation recovery and range between -1 and 1.")
        print("To call the function, type ARBURES(threshold). Example: ARBURES(0.33)")
    
    elif module == "DI":
        print("Welcome to the Sediment Disconnection Tool User Guide. DI evaluates the effects of natural or human-made landforms that disconnect sediments, such as terraces, slopes shaped by lava flows, and post-fire emergency works.")
        print("Prepare the input raster before using DI. The input values are a raster for Disconnected Areas, where areas with maximum sediment connectivity are set to 1. Other areas can be evaluated with 2, but experimentation is encouraged.")
        print("Call the function using DI().")
    
    elif module == "RIU":
        print("Welcome to RIU, the Watershed Tool User Guide. RIU allows drafting of watersheds and river networks. The tool accepts a Digital Elevation Model as input. Call the function using RIU().")
    
    elif module == "FOGU":
        print("Welcome to the FOGU User Guide! FOGU calculates NBR, dNBR, and classifies burn scars into severity classes. It also calculates and drafts the wildfire perimeter. Call the function using FOGU().")
    
    elif module == "commands":
        print("Available commands: PFES(), IC(dem_units, alg), ARBURES(threshold), FOGU(), DI(), RIU(), INUE(commands, dem_units, algo, threshold), help(module)")
    
    elif module == "INUE4ArcPY":
        print("Welcome to the INUE User Guide. INUE performs a full analysis of the burned area immediately after fire or after vegetation recovery. Call INUE by writing INUE(command, dem_units, hydrology algorithm, NDVI threshold). The available commands are:")
        print('"postfire" - assess erosion susceptibility immediately after the wildfire')
        print('"postfire disconnected" - assess erosion susceptibility immediately after the wildfire in areas where sediment can be both connected or disconnected by natural or anthropogenic landforms')
        print('"vegetation recovery" - assess erosion susceptibility after vegetation recovery. NDVI threshold is 0.25 but can be modified in the code.')
        print('"vegetation recovery disconnected" - assess erosion susceptibility after vegetation recovery in areas that are naturally or anthropically disconnected.')
        print('Example: INUE("postfire", "METER", "DINF", 0.25)')
        print("You need to specify also dem units, hydrology algorithm and NDVI threshold for the IC and ARBURES modules. If you need some help about take a look at the User Guide of IC and ARBURES.")
    
    elif module == "ABOUT":
        """
        Borselli, L., Cassi, P., & Torri, D. (2008). Prolegomena to sediment and flow connectivity in the landscape. Catena, 75(3), 268–277.\n
        Cavalli, M., Tarolli, P., Marchi, L., & Dalla Fontana, G. (2008). The effectiveness of airborne LiDAR data in the recognition of channel-bed morphology. CATENA, 73(3), 249–260. https://doi.org/10.1016/j.catena.2007.11.001\n
        Cavalli, M., Trevisani, S., Comiti, F., & Marchi, L. (2013). Geomorphometric assessment of spatial sediment connectivity. Geomorphology, 188, 31–41.\n
        Key, C. H., & Benson, N. C. (2006). Landscape assessment: Ground measure of severity, the Composite Burn Index. USDA Forest Service.\n
        Keeley, J. E. (2009). Fire intensity, fire severity and burn severity. Int. J. Wildland Fire, 18(1), 116–126.\n
        Martini, L., Faes, L., Picco, L., Iroumé, A., Lingua, E., Garbarino, M., & Cavalli, M. (2020). Assessing the effect of fire severity on sediment connectivity in central Chile. Science of The Total Environment, 728, 139006. https://doi.org/10.1016/j.scitotenv.2020.139006\n
        Rouse, J. W., Haas, R. H., Schell, J. A., & Deering, D. W. (1974). Monitoring vegetation systems with ERTS. NASA, ERTS Symposium.\n
        """
    elif module == "ammenta":
        print("Do you want to change the output folder? Call ammenta() and change it!")
		


	
#_____________________________________W_index raster generator____________________________________________________________

def WINDEX(newmin = 0.05, newmax = 1, nodatavalue= 1):
	"""
	Welcome to the W module reclassifier! If you want to use a different W index to properly model the roughness characteristics of the watershed you can reclassy 	it here, as you prefer. The W module accepts two mandatory values which are the new minimum and maximum values to be rescaled. By default the values are setted 	to 0 and 1. As you start the module the program will ask you for a raster file to be reclassified. You can use the W Index to calculate the Index of 	Connectivity as you wish. The No Data is settled by default to 0 but you can specify another number. Higher W correspond to maximum roughness. 
	W(newmin, newmax, nodatavalue) W(0,1,0)
	"""
	arcpy.env.overwriteOutput = True
	l = d.askopenfilename(title="Select the Raster to be reclassified")
	arcpy.MakeRasterLayer_management(l, "Raster to be reclassified")

	print("W Module 1: nodata reclassifier")
	rr = sa.Con(sa.IsNull("Raster to be reclassified"), nodatavalue, "Raster to be reclassified")
	rr.save(PWIndex)
	arcpy.MakeRasterLayer_management(PWIndex, "W8")
	print("W Module 1 - Finished")

	#print("W Module 2: W index creator")
	#min_W = arcpy.GetRasterProperties_management("Raster without No Data","MINIMUM", "Band_1")
	#max_W = arcpy.GetRasterProperties_management("Raster without No Data","MAXIMUM", "Band_1")
	#rescaled_W = sa.RescaleByFunction(orr, sa.TfLinear(max_W, min_W), newmin , newmax)
	#rescaled_W.save(PWIndex)
	#arcpy.MakeRasterLayer_management(PWIndex, "W")
	#print("W Module 2- Finished")


#________________________________________IC TOOL__________________________________________________________________________________


def IC(dem_unit="METER", alg="D8", Wsett="Default", newmin = 0.05, newmax = 1, nodatavalue= 1): #dem_unit = "FOOT", "METER".... alg = "D8", "DINF" . Eg: IC("DINF", "METER") 
    	""" #sa ghia lestra de Python incumintzat inoghe
    	Welcome to the IC User Guide. 
    	The IC module enables you to calculate the Sediment Connectivity Index (IC), which is essential for understanding sediment transport dynamics. 
    	This module follows the methodology proposed by Borselli et al. (2008). 
	Weighting factor W: you can put every input you want but, since INUE is built for erosion susceptibility assessment in burnt areas a surface rougess index is 	calculated with a 5x5 cell moving window calculating standard deviatio  of the elevation raster. The weighting factor to be used is specified after the 	algorithm (see examples below) and 4 options are available. "Cavalli2013" calculates the weighting factor for Alpine areas as discussed in Cavalli et al. 2013. 	If you type "personalized" te program opens a select file window which allows you to load a raster file generated before with other Weighting factors. "Windex" 	allows you to load a raster file which final output will be a rescaled inverted raster. It is useful if you have the maximum values in the channel areas and is 	specifically thought to be used with STONE2 outputs. TRI is the topographic roughness index.
	newmin, newmax and nodatavalue are the input values of Windex, so if you plan to use other W factors feel free to ignore this parameters. 
	    
    	The resulting index is a fundamental output, along with burn severity, for drafting the Post Fire Erosion Susceptibility (PFES) map.
	IC module needs to define the Digital Elevation Model units (eg: foot, meter, kilometer) and to choose between D8, MFD and DINF algorithms for flow direction 	and flow accumulation. 
	DEM UNITS: INCH, FOOT, YARD, MILE_US, NAUTICAL_MILE, MILLIMETER, CENTIMETER, METER, KILOMETER, DECIMETER
	Algorithms: D8, DINF
	Roughness indexes: "default", "Cavalli2013", "WINDEX", "TRI", "personalized"
	Examples: IC(METER, D8)  IC(FOOT, D8) IC(MILLIMETER, DINF), IC(METER, D8, Cavalli2013), IC(METER, DINF, personalized, 2, 4, -9999)
	Take note that D8 is the faster algorithm. DINF performs beautiful outputs but has higher computational costs.

    	""" #sa ghia lestra de python s'acabat inoghe	

	arcpy.env.overwriteOutput = True 
	#LOAD RASTERS
	print("Select Digital Elevation Model in TIF format")
	a = d.askopenfilename(title="Select Digital Elevation Model")
	a1 = "r'"+a+"'"
	ELEVATION = arcpy.MakeRasterLayer_management(a, "DEM")
	print("Select ROADMASK in TIF format")
	b = d.askopenfilename(title="Select ROADMASK")
	ROADMASK = arcpy.MakeRasterLayer_management(b, "ROADMASK")

	#0 DEM RESAMPLE
	#RESAMPLEDEM = arcpy.management.Resample(ELEVATION, oresdem, cellsize, "BILINEAR")
	#RESAMPLEDEM.save(oresdem)
	#arcpy.MakeRasterLayer_management(oresdem, "RESAMPLEDEM")
	#RESAMPLEDEM1 = arcpy.Raster(oresdem)
	#print("FINISHED - 0 RESAMPLE DEM")

    	# 0. FILL DEM
    	filled_dem = sa.Fill("DEM") #est s'algoritmu chi serbit a prenare sas cheas de su dem. su chi nde bessit benit asegnadu a filled_dem
    	filled_dem.save(icfilldem) #s'ammentat filled_dem che a file tif in su tretu ispetzificadu
    	arcpy.MakeRasterLayer_management(icfilldem, "FILLDEM") #leghet su file filled_dem dae sa memoria de s'elaboradore e nche lu carrigat in su progetu che a layer file. Serbit pro lu donare a sos algoritmos chi sighent
    	print("FINISHED - FILL DEM") #narat ebbia chi custu modulu s'est acabadu e chi at fatu totu su chi depiat faghere

	#1 FLOW DIRECTION

	FLOWDIR = sa.FlowDirection("FILLDEM", "NORMAL", "", alg)  #Calculat a in-ue nche calant sas currentes
	FLOWDIR.save(oFLOWDIR)  #S'ammentat su raster
	arcpy.MakeRasterLayer_management(oFLOWDIR, "FLOWDIR1")  #Nche carrigat su Raster che a Raster layer
	print("FINISHED - 1 FLOW DIRECTION")

	#2 DIRMASK

	DIRMASK = sa.Times("FLOWDIR1", "ROADMASK") #Calculat a DIRMASK
	DIRMASK.save(oDIRMASK)
	arcpy.MakeRasterLayer_management(oDIRMASK, "DIRMASK2")
	print("FINISHED - 2 DIRMASK")

	#3 ACCMASK

	ACCMASK = sa.FlowAccumulation("DIRMASK2", "", "FLOAT", alg)
	ACCMASK.save(oACCMASK)
	arcpy.MakeRasterLayer_management(oACCMASK, "ACCMASK3")
	print("FINISHED - 3 ACCMASK")

	#4 RIVERMASK

	RIVERMASK = sa.LessThan("ACCMASK3", 1000)
	RIVERMASK.save(oRIVERMASK)
	arcpy.MakeRasterLayer_management(oRIVERMASK, "RIVERMASK4")
	print("FINISHED - 4 RIVERMASK")

	#5 DIRFINAL

	DIRFINAL = sa.Times("DIRMASK2", "RIVERMASK4")
	DIRFINAL.save(oDIRFINAL)
	arcpy.MakeRasterLayer_management(oDIRFINAL, "DIRFINAL5")
	print("FINISHED - 5 DIRFINAL")

	if Wsett == "Cavalli2013":

		#6a mean elevation

		MEANDEM = sa.FocalStatistics("DEM", arcpy.sa.NbrRectangle(5,5, "CELL"),"MEAN", "DATA", 90)
		MEANDEM.save(oMEANDEM)
		arcpy.MakeRasterLayer_management(oMEANDEM, "MEANDEM6")
		print("FINISHED - 6a Mean Elevation")

		#6b residual topography
		RESTOPO = sa.Minus("DEM", "MEANDEM6")
		RESTOPO.save(oRESTOPO)
		arcpy.MakeRasterLayer_management(oRESTOPO, "RESTOPO7")
		print("FINISHED - 6b Residual Topography")

		#6 Focal Statistics W roughness index
		W = sa.FocalStatistics("RESTOPO7", arcpy.sa.NbrRectangle(5,5, "CELL"),"STD", "DATA", 90)
		W.save(oW)
		arcpy.MakeRasterLayer_management(oW, "W6")
		print("FINISHED - 6 W roughness index: Cavalli et al. 2013")
	
	elif Wsett == "WINDEX":
		WINDEX(newmin = 0.05, newmax = 1, nodatavalue= 1)
		print("FINISHED - 6 Windex")

	elif Wsett == "Default":
		#6 Focal Statistics W roughness index
		print("This module calculates a Roughness index based on your dem with a 5x5 moving window, using the Standard Deviation")
		W = sa.FocalStatistics("DEM", arcpy.sa.NbrRectangle(5,5, "CELL"),"STD", "DATA", 90)
		W.save(oW)
		arcpy.MakeRasterLayer_management(oW, "W6")
		print("FINISHED 6 - Default W roughness index")
	elif Wsett == "personalized":
		print("Select your own W Index")
		icwper = d.askopenfilename(title="Select Raster for W Index")
		ROADMASK = arcpy.MakeRasterLayer_management(icwper, "W6")
		print("FINISHED - 6 Personalized W Index is successfully loaded")
	elif Wsett == "TRIRiley1999":
    		print("Calculating the Topographic Roughness Index (TRI) following Riley et al., 1999")
    		focal_mean = sa.FocalStatistics("DEM", sa.NbrRectangle(3, 3, "CELL"), "MEAN", "DATA")
		r9fm = outdir + "r9fm.tif"
		focal_mean.save(r9fm) 
    		abs_diff = sa.Abs(sa.Minus("DEM", focal_mean))
		abspa = outdir+"abspa.tif"
		abs_diff.save(abspa)
    		TRI = sa.FocalStatistics(abspa, sa.NbrRectangle(3, 3, "CELL"), "SUM", "DATA")
    		TRIsavepath = outdir + "TRIriley99.tif"
    		TRI.save(TRIsavepath)
    		arcpy.MakeRasterLayer_management(TRIsavepath, "W6")
		print("FINISHED - 6 Topographic Roughness Index by Riley et al. 1999")


	elif Wsett == "TRI2":
		print("Lets calculate the Toprographic Roughness Index starting from your DEM")
		for i in range(0,3):
			parFS = ["MEAN", "MAXIMUM", "MINIMUM"]
			outFSa = ["FSmean.tif", "FSmax.tif", "FSmin.tif"]
			FSnames = ["FSmean", "FSmax", "FSmin"]
			FSo = sa.FocalStatistics("DEM", arcpy.sa.NbrRectangle(5,5, "CELL"),parFS[i], "DATA", 90)
			savepathFS = outdir + outFSa[i]
			FSo.save(savepathFS)
			arcpy.MakeRasterLayer_management(savepathFS, FSnames[i])
		TRI = sa.Divide(sa.Minus("FSmean", "FSmin"), sa.Minus("FSmax", "FSmin"))
		TRIsave = outdir + "TRI.tif"
		TRI.save(TRIsave)
		arcpy.MakeRasterLayer_management(TRIsave, "W6")
		print("FINISHED - 6 Topographic Roughness Index")



	#7 accsemifinal
	ACCSEMIFINAL = sa.FlowAccumulation("DIRFINAL5", "", "FLOAT", alg)
	ACCSEMIFINAL.save(oACCSEMIFINAL)
	arcpy.MakeRasterLayer_management(oACCSEMIFINAL, "ACCSEMIFINAL7")
	print("FINISHED - 7 ACCSEMIFINAL")


	#8 ACCFinal
	ACCFinal = sa.Plus("ACCSEMIFINAL7", 1)
	ACCFinal.save(oACCFinal)
	arcpy.MakeRasterLayer_management(oACCFinal, "ACCFINAL8")
	print("FINISHED - 8 ACCFINAL")


	#9 Process: Wmean
	WFMean = sa.FlowAccumulation("DIRFINAL5", "W6", "FLOAT", alg)
	WFMean.save(oWFMean)
	arcpy.MakeRasterLayer_management(oWFMean, "9a WFMean")

	WemiMean = sa.Plus("9a WFMean", "W6")
	WemiMean.save(oWemiMean)
	arcpy.MakeRasterLayer_management(oWemiMean, "9b WemiMean")
	b11 = arcpy.Raster(oWemiMean)

	WMean = sa.Divide("9b WemiMean", "ACCFinal8")
	WMean.save(oWMean)
	arcpy.MakeRasterLayer_management(oWMean, "9 WMean")
	print("FINISHED - 9 WMean")


	#10 Process: Slope
	SLOPE = sa.Slope("DEM", "DEGREE", "1", "PLANAR", dem_unit)
	SLOPE.save(oSLOPE)
	arcpy.MakeRasterLayer_management(oSLOPE, "10 SLOPE")
	print("FINISHED - 10 SLOPE") 

	#11 Process: S
	
	S = S = sa.Con("10 SLOPE", 0.005, "10 SLOPE", "value = 0")
	S = S.save(oS)
	arcpy.MakeRasterLayer_management(oS, "11 S")
	print("FINISHED - 11 S")

	#12 Process: Smean
	SFMean = sa.FlowAccumulation("DIRFINAL5", "11 S", "FLOAT", alg)
	SFMean.save(oSFMean)
	arcpy.MakeRasterLayer_management(oSFMean, "12a SFMean")
	a14 = arcpy.Raster(oSFMean)

	SemiMean = sa.Plus("12a SFMean", "11 S")
	SemiMean.save(oSemiMean)
	arcpy.MakeRasterLayer_management(oSemiMean, "12b SemiMean")

	SMean = sa.Divide("12b SemiMean", "ACCFinal8")
	SMean.save(oSMean)
	arcpy.MakeRasterLayer_management(oSMean, "12 SMean")
	print("FINISHED - 12 SMean") 

	print("Input files for IC calculation are ready. Let's move on with the calculation of Dup and Ddn")
	#13 Process: Dup
	WSMeans = sa.Times("9 WMean", "12 SMean")
	WSMeans.save(oWSMeans)
	arcpy.MakeRasterLayer_management(oWSMeans, "13a WSMeans")
	a15 = arcpy.Raster(oWSMeans)

	ACCFinal25 = sa.Times("ACCFinal8", 25)
	ACCFinal25.save(oACCFinal25)
	arcpy.MakeRasterLayer_management(oACCFinal25, "13b ACCFinal25")
	b15 = arcpy.Raster(oACCFinal25)

	Dup = sa.Times("13a WSMeans", sa.SquareRoot("13b ACCFinal25"))
	Dup.save(oDup)
	arcpy.MakeRasterLayer_management(oDup, "13 Dup")
	Dup15 = arcpy.Raster(oDup)
	print("FINISHED - 13 Dup")

	#14 Process: inv_WS
	
	WSinv = sa.Times("W6", "11 S")
	WSinv.save(oWS16)
	arcpy.MakeRasterLayer_management(oWS16, "14 a WSinv")
	
	inv_WS = sa.Divide(1, "14 a WSinv")
	inv_WS.save(oinv_WS)
	arcpy.MakeRasterLayer_management(oinv_WS, "14 inv_WS")
	print("FINISHED - 14 inv_WS")	

	#15 Process X

	X = sa.FlowLength("DIRFINAL5", "DOWNSTREAM", "14 inv_WS")
	X.save(oX)
	arcpy.MakeRasterLayer_management(oX, "15 X")
	print("FINISHED - 15 X")

	#16 Process: Ddn 
	X0 = sa.Con("15 X", "14 inv_WS" , "15 X", "value = 0")
	X0.save(oX0)
	arcpy.MakeRasterLayer_management(oX0, "15a X0")
	a18 = arcpy.Raster(oX0)
 
	Ddn = sa.Plus("15a X0", "15 X")
	Ddn.save(oDdn)
	arcpy.MakeRasterLayer_management(oDdn, "16 Ddn")
	Ddn18 = arcpy.Raster(oDdn)
	print("FINISHED - 16 Ddn")
	
	print("I am calculating the Sediment Connectivity Index IC (Borselli et al. 2008)")

	#17 Process: Index of Connectivity 
	dupddn = sa.Divide("13 Dup", "16 Ddn")
	dupddn.save(odupddn)
	arcpy.MakeRasterLayer_management(odupddn, "DupDdn")
	IC = sa.Log10("DupDdn")
	IC.save(oIC)
	arcpy.MakeRasterLayer_management(oIC, "17 Index of Connectivity")
	print("FINISHED - 17 Sediment Connectivity Index (IC) - Borselli et al. 2008")

	#18 Process: calculates the normalized IC
	min_IC = arcpy.GetRasterProperties_management("17 Index of Connectivity","MINIMUM", "Band_1")
	max_IC = arcpy.GetRasterProperties_management("17 Index of Connectivity","MAXIMUM", "Band_1")
	normalized_IC = sa.RescaleByFunction(oIC,sa.TfLinear(min_IC, max_IC),0 , 1)
	normalized_IC.save(onormalizedIC)
	arcpy.MakeRasterLayer_management(onormalizedIC, "18 normalized Index of Connectivity")
	print("FINISHED - 18 normalized IC")

#__________________________________POST FIRE EROSION SUSCEPTIBILITY MAP_______________________________________________________

def PFES():
    	"""
    	Welcome to the PFES module! This module is designed to draft the base map for assessing post-wildfire erosion susceptibility.
    
    	The PFES module utilizes the normalized Index of Connectivity and the Reclassified Burn Severity maps to calculate the Post Fire Susceptibility to Erosion Map. 
    	This output is crucial for understanding areas at risk of erosion following a wildfire, providing valuable information for land management and restoration efforts.
    
    	After generating the susceptibility map, users are guided on how to further analyze disconnected areas using the DI module or simulate vegetation recovery effects with the ARBURES() function.
    	"""


	arcpy.env.overwriteOutput = True #consente di sovrascrivere
	print("Welcome to PFES, the module to draft the base map for post wildfire erosion susceptibility")
	c1 = d.askopenfilename(title="Select the normalized Sediment Connectivity Index map")
	ici = arcpy.MakeRasterLayer_management(c1, "normalized Index of Connectivity")
	c2 = d.askopenfilename(title="Select the reclassified Burn Severity Map. You can calculate the map with the FOGU() module")
	reclassified_Burn_Severity = arcpy.MakeRasterLayer_management(c2, "Reclassified Burn Severity")
	#1 Process: calculates the susceptibility to erosion map
	print("I am drafting the Post Fire Susceptibility to Erosion Map")
	PFESmap = sa.Times("normalized Index of Connectivity", "Reclassified Burn Severity")
	PFESmap.save(oPFESmap)
	arcpy.MakeRasterLayer_management(oPFESmap, "Post Fire Susceptibility to Erosion Map")
	print("Finished. If you want to add the disconnected areas call the disconnecting module with the DI() function. Else, if you want to simulate the effects of 	vegetation recovery type ARBURES().")


#_____________________________________SEDIMENT DISCONNECTING INDEX______________________________________________________

def DI():
    	"""
    	Welcome to the DI module! This module is designed for assessing sediment disconnection linked with prefire or postfire natural and anthropic landforms.
    
    	Users are prompted to select the DI and PFES raster files, which are then processed to calculate a map indicating areas of sediment disconnection.
    
    	This output helps in understanding the dynamics of sediment transport and erosion risk in post-wildfire landscapes, aiding in effective land management and 	restoration efforts.
    	"""

	arcpy.env.overwriteOutput = True #consente di sovrascrivere
	print("Welcome to DI, the module for sediment disconnection assessment")
	print("Select the Post Fire Susceptibility to Erosion Map")
	d1 = d.askopenfilename(title="Select the Post Fire Susceptibility to Erosion Map")
	print("Select the Disconnecting Sediment Index map")
	d2 = d.askopenfilename(title = "Select the Sediment Disconnecting Index map")
	arcpy.MakeRasterLayer_management(d1, "Post Fire Susceptibility to Erosion Map")
	arcpy.MakeRasterLayer_management(d2, "Disconnecting Index")
	DMAP = sa.Divide("Post Fire Susceptibility to Erosion Map", "Disconnecting Index")
	DMAP.save(odmap)
	arcpy.MakeRasterLayer_management(odmap, "PFES map with disconnected areas")
	print("Finished")


#_____________________________________ARBURES: Vegetation Recovery Tool__________________________________________________________

def ARBURES(threshold):
    """
    Welcome to the ARBURES module! This module simulates the effects of vegetation recovery following a wildfire.

    The process involves selecting Sentinel 2 L2A imagery for Band 04 (Red) and Band 08 (Near Infrared) to calculate the Normalized Difference Vegetation Index (NDVI). 
    The NDVI values are then reclassified based on the user-defined threshold to create a Vegetation Recovery map.

    Additionally, the module incorporates a Post Fire Susceptibility to Erosion map to assess the combined effects of vegetation recovery on erosion risk.
    The final output is a map indicating the susceptibility to erosion, factoring in vegetation recovery, aiding in post-wildfire management and recovery planning.
    """
    
    arcpy.env.overwriteOutput = True  # consente di sovrascrivere
    print("Select the Band04 Sentinel 2 L2A image")
    e = d.askopenfilename(title = "Select the Band 04 Sentinel 2 L2A image")
    print("Select the Band08 Sentinel 2 L2A image")
    f = d.askopenfilename(title = "Select the Band 08 Sentinel 2 L2A image")
    arcpy.MakeRasterLayer_management(e, "Band 04 JP2")
    arcpy.MakeRasterLayer_management(f, "Band 08 JP2")
    b4r = arcpy.CopyRaster_management("Band 04 JP2", oBJ4T, "", "", "", "", "", "64_BIT", "", "", "TIFF", "")
    arcpy.MakeRasterLayer_management(oBJ4T, "Band 04 TIF")
    b8r = arcpy.CopyRaster_management("Band 08 JP2", oBJ8T, "", "", "", "", "", "64_BIT", "", "", "TIFF", "")
    arcpy.MakeRasterLayer_management(oBJ8T, "Band 08 TIF")
    
    NDVI = sa.Divide(sa.Minus("Band 08 TIF", "Band 04 TIF"), sa.Plus("Band 08 TIF", "Band 04 TIF"))
    NDVI.save(ondvi)
    arcpy.MakeRasterLayer_management(ondvi, "NDVI")
    
    thrfl = sa.Float(threshold)
    min_NDVI = arcpy.GetRasterProperties_management("NDVI", "MINIMUM", "Band_1")
    max_NDVI = arcpy.GetRasterProperties_management("NDVI", "MAXIMUM", "Band_1")
    
    TNDVI = sa.Reclassify("NDVI", "Value", sa.RemapRange([[min_NDVI, thrfl, 1], [0.25, max_NDVI, 0]]), "NODATA")
    TNDVI.save(othr)
    TN = arcpy.MakeRasterLayer_management(othr, "Vegetation Recovery")
    
    print("Select the Post Fire Susceptibility to Erosion Map")
    g = d.askopenfilename(title = "Select the PostFire Susceptibility to Erosion Map")
    arcpy.MakeRasterLayer_management(g, "Post Fire Susceptibility to Erosion Map")
    
    VR = sa.Times("Post Fire Susceptibility to Erosion Map", "Vegetation Recovery")
    VR.save(ovr)
    arcpy.MakeRasterLayer_management(ovr, "Post Fire Erosion Susceptibility with Vegetation Recovery")
    
    print("Arbures: map for vegetation recovery index is successfully drafted!")
	
#__________________________________FOGU: NBR, dNBR, Burn Severity, Burnt Scar Perimeter____________________________________________________

def FOGU():
    """
    Welcome to the FOGU module. Let's calculate NBR, dNBR, and draft maps for Burn Severity,
    reclassified Burn Severity (PFES), and Wildfire perimeter. FOGU works only with 
    Sentinel 2 L2A images! BANDS: 04, 08, 12
    """
    arcpy.env.overwriteOutput = True  # consente di sovrascrivere

    # IMPORT SENTINEL IMAGES
    print("Select the Prefire Band08 Sentinel 2 L2A image")
    h = d.askopenfilename(title="Select the Prefire Band08 Sentinel 2 L2A image")
    print("Select the Prefire Band12 Sentinel 2 L2A image")
    i = d.askopenfilename(title="Select the Prefire Band12 Sentinel 2 L2A image")
    print("Select the Postfire Band08 Sentinel 2 L2A image")
    j = d.askopenfilename(title="Select the Postfire Band08 Sentinel 2 L2A image")
    print("Select the Postfire Band12 Sentinel 2 L2A image")
    k = d.askopenfilename(title="Select the Postfire Band12 Sentinel 2 L2A image")
    arcpy.MakeRasterLayer_management(h, "Band 08 PREFIRE JP2")
    b8rpre = arcpy.CopyRaster_management("Band 08 PREFIRE JP2", obr8pre, "", "", "", "", "", "64_BIT", "", "", "TIFF", "")
    arcpy.MakeRasterLayer_management(obr8pre, "Band 08 PREFIRE TIF")
    arcpy.MakeRasterLayer_management(i, "Band 12 PREFIRE JP2")
    b12rpre = arcpy.CopyRaster_management("Band 12 PREFIRE JP2", obr12pre, "", "", "", "", "", "64_BIT", "", "", "TIFF", "")
    arcpy.MakeRasterLayer_management(obr12pre, "Band 12 PREFIRE TIF")
    arcpy.MakeRasterLayer_management(j, "Band 08 POSTFIRE JP2")
    b8rpost = arcpy.CopyRaster_management("Band 08 POSTFIRE JP2", obr8post, "", "", "", "", "", "64_BIT", "", "", "TIFF", "")
    arcpy.MakeRasterLayer_management(obr8post, "Band 08 POSTFIRE TIF")
    arcpy.MakeRasterLayer_management(k, "Band 12 POSTFIRE JP2")
    b12rpost = arcpy.CopyRaster_management("Band 12 POSTFIRE JP2", obr12post, "", "", "", "", "", "64_BIT", "", "", "TIFF", "")
    arcpy.MakeRasterLayer_management(obr12post, "Band 12 POSTFIRE TIF")

    #PREFIRE

    NBRpre = sa.Divide(sa.Minus("Band 08 PREFIRE TIF", "Band 12 PREFIRE TIF"), sa.Plus("Band 08 PREFIRE TIF", "Band 12 PREFIRE TIF"))
    NBRpre.save(onbrpre)
    arcpy.MakeRasterLayer_management(onbrpre, "NBR PREFIRE")
    print("FOGU: FINISHED - 1 PREFIRE NBR")

    # POSTFIRE
    

    NBRpost = sa.Divide(sa.Minus("Band 08 POSTFIRE TIF", "Band 12 POSTFIRE TIF"), sa.Plus("Band 08 POSTFIRE TIF", "Band 12 POSTFIRE TIF"))
    NBRpost.save(onbrpost)
    arcpy.MakeRasterLayer_management(onbrpost, "NBR POSTFIRE")
    print("FOGU: FINISHED - 2 POSTFIRE NBR")

    # dNBR
    dNBR = sa.Minus("NBR PREFIRE", "NBR POSTFIRE")
    dNBR.save(odnbr)
    arcpy.MakeRasterLayer_management(odnbr, "dNBR")
    print("FOGU: FINISHED - 3 dNBR")
    
    # Burn Severity
    min_dNBR = arcpy.GetRasterProperties_management("dNBR", "MINIMUM", "Band_1")
    max_dNBR = arcpy.GetRasterProperties_management("dNBR", "MAXIMUM", "Band_1")
    # 1 = high postfire regrowth, 2 = low postfire regrowth, 3 = unburnt, 4 = low severity, 
    # 5 = moderate low severity, 6 = moderate high severity, 7 = high severity
    BS = sa.Reclassify("dNBR", "Value", sa.RemapRange([[min_dNBR, -0.25, 1], [-0.25, -0.1, 2], 
                                                          [-0.1, 0.1, 3], [0.1, 0.27, 4], 
                                                          [0.27, 0.44, 5], [0.44, 0.66, 6], 
                                                          [0.66, max_dNBR, 7]]), "NODATA")  # funziona
    BS.save(obs)
    arcpy.MakeRasterLayer_management(obs, "Burn Severity Classes")
    print("FOGU: FINISHED - 4 Burn Severity map drafting")

    # reclassified Burn Severity for PFES map drafting
    reclassBS = sa.Reclassify("Burn Severity Classes", "Value", sa.RemapRange([[1, 3, 1], [4, 4, 2], 
                                                                                   [5, 5, 3], [6, 6, 4], 
                                                                                   [7, 7, 5]]), "NODATA")  # funziona
    reclassBS.save(oreclassBS)
    arcpy.MakeRasterLayer_management(oreclassBS, "Reclassified Burn Severity")
    print("FOGU: FINISHED - 5 Burn Severity for PFES")

    # Wildfire perimeter
    WFP = sa.Reclassify("Burn Severity Classes", "Value", sa.RemapRange([[1, 3, 0], [4, 7, 1]]), "NODATA")  # funziona
    WFP.save(owfp)
    arcpy.MakeRasterLayer_management(owfp, "Wildfire Perimeter")
    print("FOGU: FINISHED - 6 Wildfire Perimeter drafting")

#__________________________________RIU - WATERSHED DRAFTING TOOL____________________________________________________
	
def RIU():
    """
    Welcome to RIU! This tool calculates flow direction, flow accumulation, 
    and draws river networks and watersheds. You can select the algorithm 
    for flow direction and flow accumulation by writing:
    
    Select a DEM and go with the flow!
    """
    
    arcpy.env.overwriteOutput = True  # Allow overwriting of existing files

    # Prompt user to select a DEM file
    dem_file = d.askopenfilename(title="Select a Digital Elevation Model")  
    if not dem_file:
        print("No file selected. Exiting.")
        return

    # Create raster layer from selected DEM
    riu_dem = arcpy.MakeRasterLayer_management(dem_file, "RIUDEM")

    # 1. FILL DEM
    filled_dem = sa.Fill("RIUDEM")
    filled_dem.save(oFILLED)
    arcpy.MakeRasterLayer_management(oFILLED, "RIU 1 - FILLED DEM")
    print("RIU, module 1 finished: filled DEM")

    # 2. FLOW DIRECTION
    flow_direction = sa.FlowDirection("RIU 1 - FILLED DEM", "NORMAL", "", "D8")  # Calculate flow direction
    flow_direction.save(oFLOWDIRE)  # Save the output raster
    arcpy.MakeRasterLayer_management(oFLOWDIRE, "RIU 2 - FLOW DIRECTION")
    print("RIU, module 2 finished: flow direction")

    # 3. FLOW ACCUMULATION
    flow_accumulation = sa.FlowAccumulation("RIU 2 - FLOW DIRECTION", "", "FLOAT", "D8")
    flow_accumulation.save(oACCFLOW)
    arcpy.MakeRasterLayer_management(oACCFLOW, "RIU 3 - FLOW ACCUMULATION")
    print("RIU, module 3 finished: flow accumulation")

    # 4. RIVER NETWORK
    #maxacc= arcpy.GetRasterProperties_management("RIU 3 - FLOW ACCUMULATION", "MAXIMUM", "Value")#gets max value
    #mac = float(maxacc.getOutput(0))#extract the value from the result
    #thr = mac*0.001#applies thresholding for riv network extraction. modify 0.001 as you wish
    river_network = sa.LessThan("RIU 3 - FLOW ACCUMULATION", 1000.00)
    river_network.save(oRIVNET)
    arcpy.MakeRasterLayer_management(oRIVNET, "RIU 4 - RIVER NETWORK")
    print("RIU, module 4 finished: river network")

    #5. POURPOINT PATHFINDER
    nodes = sa.FocalStatistics("RIU 4 - RIVER NETWORK", arcpy.sa.NbrRectangle(3,3, "CELL"), "MAJORITY", "DATA", 90)
    nodes.save(nodtif)
    arcpy.MakeRasterLayer_management(nodtif, "NODES")
    conodes = sa.Con("NODES", "NODES" , "", "value = 0")
    conodes.save(conodtif)
    arcpy.MakeRasterLayer_management(conodtif, "CONODES")
    norg = sa.RegionGroup("CONODES", "EIGHT", "WITHIN", "ADD_LINK", "")
    norg.save(norgtif)
    arcpy.MakeRasterLayer_management(norgtif, "Pour Points")

    # 6. BASIN
    basin = sa.Watershed("RIU 2 - FLOW DIRECTION", "Pour Points", "Value")
    basin.save(oBASIN)
    arcpy.MakeRasterLayer_management(oBASIN, "RIU 6 - WATERSHEDS")
    print("RIU, module 6 finished: watershed delineation")

    # 7. SHAPEFILE CONVERSION
    obasinshape = "basin_shapefile_output.shp"  # Define the output shapefile path
    arcpy.RasterToPolygon_conversion("RIU 6 - WATERSHEDS", obasinshape, "NO_SIMPLIFY", "Value")
    arcpy.RasterToPolyline_conversion("RIU 4 - RIVER NETWORK", orivershape, "NO_SIMPLIFY", "Value")
    print("RIU: module 7 finished: Watershed and River network shapefiles")

#_____________________________________OPTIONAL input applier_____________________________________________________________
def optional(optional_inputs = 1, min = 0, max = 1):
	"""
	Welcome to the optional module which is useful to personalize your PFES map with all the input you want. The input has to be loaded as raster file (.tif), 	then will be reclassified from a minimum to a maximum values, as you specified calling the module. Optional accepts three parameters which have to be 	specified when calling the function, in the form: optional(optional_inputs = 1, min = 0, max = 1) where optional_inputs is the number of the input values you 	want to apply, min and max are the minimum and maximum values for reclassification. Optional will ask for the PFES map for every optional input, in case you 	want, allowing you to overlap or not overlap the optional inputs.
	"""
	arcpy.env.overwriteOutput = True

	for i in range(0, optional_inputs, 1):
		o = d.askopenfilename(title="Select the Raster for optional input number" + str(i+1))
		arcpy.MakeRasterLayer_management(o, "Optional raster number" + str(i+1))
		min_op = arcpy.GetRasterProperties_management("Optional raster number"+str(i+1),"MINIMUM", "Band_1")
		max_op = arcpy.GetRasterProperties_management("Optional raster number"+str(i+1),"MAXIMUM", "Band_1")
		rescaled_op = sa.RescaleByFunction("Optional raster number"+str(i+1), sa.TfLinear(min_op, max_op), min , max)
		savingpathop = outdir + ("optionalinputN_" + str(i+1)+".tif")
		rescaled_op.save(savingpathop)
		arcpy.MakeRasterLayer_management(savingpathop, ("PFESmap"+"optionalinput"+str(i+1)))
		PFESmap = d.askopenfilename(title="Load the Post Fire Erosion Susceptibility map")
		arcpy.MakeRasterLayer_management(PFESmap, "Post Fire Erosion Susceptibility map")
		pfesop = sa.Times("Post Fire Erosion Susceptibility map", ("optionalinputN_" + str(i+1)+".tif"))
		savingpath = outdir + ("pfesmap"+"optional_input"+str(i+1)+".tif")
		pfesop.save(savingpath)

		arcpy.MakeRasterLayer_management(savingpath, ("PFESmap with optional input number"+str(i+1)))
		print("Optional: optional input number", str(i+1), "succesfully added and loaded")

#______________________________________PFES full procedure___________________________________

def INUE(conditions, dem_unit, alg, Wsett="Default", newmin = 0.05, newmax = 1, nodatavalue= 1, threshold=None):
    """
    Welcome to the INUE module!
    
    This tool performs a full analysis of the erosion susceptibility after a wildfire, 
    assessing the effects of vegetation recovery and terraces. The module calculates 
    the Sediment Connectivity Index (Borselli et al., 2008; Cavalli et al., 2013), 
    fire parameters such as wildfire perimeter and burn severity, and applies the 
    Disconnecting Index along with the effects of vegetation recovery. 
    The module will prompt you for input files as needed.
    INUE exists also a software! Find it @ https://zenodo.org/records/18429446

    

    
    Parameters:
    conditions (str): The condition to assess, options are:
        - "postfire"
        - "postfire disconnected"
        - "vegetation recovery"
        - "vegetation recovery disconnected"

    dem_units: "INCH", "FOOT", "YARD", "MILE_US", "NAUTICAL_MILE", "MILLIMETER", "CENTIMETER", "METER", "KILOMETER", "DECIMETER"
    algo: "D8", "DINF"
    threshold = an NDVI value ranging between -1 and +1. In the Montiferru Fire Burnt Scar the value is 0.25. Threshold is optional and has only to be setted for    "vegetation recovery" and "vegetation recovery disconnected"

    Examples: 
	INUE("postfire", "METER", "5", "DINF") 
        INUE("postfire disconnected", "FOOT", "3", "D8") 
        INUE("vegetation recovery", "MILLIMETER", "10", "D8", 0.25) 
        INUE("vegetation recovery disconnected", "CENTIMETER", "1", "DINF", 0.25)

	If DINF algorith takes a lot of time or generates loop try with D8 which has less computational cost.

    """
    
    if conditions == "postfire":
        IC(dem_unit, alg, Wsett="Default", newmin = 0.05, newmax = 1, nodatavalue= 1)
        FOGU()
        PFES()
    elif conditions == "postfire disconnected":
        IC(dem_unit, alg, Wsett="Default", newmin = 0.05, newmax = 1, nodatavalue= 1)
        FOGU()
        PFES()
        DI()
    elif conditions == "vegetation recovery":
        IC(dem_unit, alg, Wsett="Default", newmin = 0.05, newmax = 1, nodatavalue= 1)
        FOGU()
        PFES()
        ARBURES(threshold)
    elif conditions == "vegetation recovery disconnected":
        IC(dem_unit, alg, Wsett="Default", newmin = 0.05, newmax = 1, nodatavalue= 1)
        FOGU()
        PFES()
        DI()
        ARBURES(threshold)
    else:
        print('Error: Unsupported condition. Please choose from "postfire", "postfire disconnected", "vegetation recovery", or "vegetation recovery disconnected"')
