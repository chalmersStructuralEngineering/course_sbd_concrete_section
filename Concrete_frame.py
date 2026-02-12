#####################################################################################
##Frame bridge optimization WSP bridge concept.
##Cluster version.
##Authors: Jon Difs, Fredrik Karlsson.
##Based on work by: Santiago Luis Fernandez, David Tarazona Ramos.
##Last update:
##
####################################################################################



##""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
##                                                       TYPE OF ANALYSIS 
##If true, traffic load module will be activated.
##"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

##Data for traffic load 
TrafficAnalysis=True
CarPlacement=2      ##0 means Parallel cars, 1 means all combinations, 2 means combinations Support-Midspan
numlanes=2
widthlane=3

thickTraffic=0.01
htraffic=0.5						##Height traffic plate loops


Lane1Pressure=0.009
Lane2Pressure=0.0025
Lane3Pressure=0.0025
RemainingPressure=0.0025
Lane1Car=300
Lane2Car=200
Lane3Car=100
wheelwidth=0.4


########################################
##MODIFIABLE PARAMETERS

##Bridge Geometry

##Wings


##Cantilevers
Cantileverwidth=0.4
Cantileverheight=0.5
cantiliverOffset=0.3

##Barrier load

barrierload=0.0005                             #MN/m

##Pressure over the deck
loadmagnitude=0.05                           #Magnitude of the pressure of the bridge [MPa]

##Diameter values considered in reinforcement design
diamrange=[0.01, 0.014,0.016,0.020,0.025,0.028,0.032] #[m]


##ANALYSIS PARAMETERS

Ncores=16                                   ##Number of computational cores available (Check if license allows as many cores as included here) CHANGE WHEN RUNNING ON GLENN TO 16
elementsize=0.5
elementsizetraffic=0.5
delta=1e-4


##Load combination factors

##ULS
gammaULSP=1.35
gammaULSV=1.5

##Quasi-permanent state
gammaSLSP=1                                 #For Quasi-permanent load combination
gammaSLSV=0.3


g=9.81                                      #[m/s^2)Gravity value 


##Material properties

##Concrete
Ecm=35.E3
fck=40 #MPa
fctm=3.5 #MPa
poissonconcrete= 0.15
rhoconcrete=0.0024
gammac=1.5
alphacc=1
fcd=(alphacc*fck)/float(gammac)
epscu=0.0035
alphar=0.81
bethar=0.416
c=0.035 #m  <---------------- Concrete cover
dg=0.032  #m biggest size of aggregate 

##Reinforcement steel B500B
fyk=500 #MPa
gammas=1.15
fyd=fyk/float(gammas) #MPa

Es=200000 #MPa
diamstirrups=0.012 #m
cover=0.02+diamstirrups

diamslab=0.016 #m  <------------------ Diameter of reinforcement in slab
#################################################################################

##import necessary modules


from caeModules import *
from abaqus import *
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True,
    reportDeprecated=False)
import time
import sketch
import math
import part
import material
import section
import regionToolset
import assembly
import step
import load
import mesh
import job
import visualization
import xyPlot
from visualization import ELEMENT_NODAL
import displayGroupMdbToolset as dgn
import displayGroupOdbToolset as dgo
import odbAccess
import csv


#####################################################################################


starting_point_total = time.time()                      ##Start point for the time counter

##initialize vectors used for data storage
Reinforct=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] ##23 zeros

Failmatrix=[]
Position=[]
Positionv=[0,0,0]
Reinforc=[]
##Convergence vectors
ConvMEd=[]
Convdef=[]
Convelements=[]

jobnumber=0
numberofjobs=len(looplist)

print '---------------------------------------------Submitted %s jobs-----------------------------------------' %(numberofjobs)	#Print number of jobs that will be done in the loop.


for loop in xrange(0,numberofjobs):
        ##Assign for each bridge the correspondent parameters 
        thicknesslab=looplist[loop][1]
        thicknessleg=looplist[loop][2]
        height=looplist[loop][3]
        platewidth=looplist[loop][4]
        L=looplist[loop][5]
        diam=looplist[loop][6]
        starting_point_loop = time.time()	                                    #Loop time counter starts here
        jobnumber=jobnumber+1								                    #Take into account the current job
        jobsremaining=numberofjobs-jobnumber                                    #Remaining jobs calculation

###########################################################################################
        ##Calculations used for soilpressure

        ##Soilpressure MANY IMPROVEMTS ARE POSSIBLE
        wingOffset=0.5 ##m from ground
        wingWidness=2
        heightWing=height-wingOffset

        ##Soil Constants according to #Geoteknik- Goran Sallfors"

        weight=0.018                    ##MN/m^3 in our case FYLLNADSMATERIAL
        c=0                                  ##MPa cohesive number 0 for fyllnadsmaterial (friction soil) (also tfu)
        alpha = math.radians(45)                     ##fracture angle convert to radians
        OCR=1                             ##Fyllnadsmaterial
        pw=0.01                           ##MN/m^3 water weight
        verticalload=0.015             ## accordning to wsp calculations page 1529                ## If it exsist in MN/m^2
        subsoilwaterheight=0        ##if subsoilwater not for our case
        ##safety factors
        Fc=1.3
        Falpha=1.3

        ##Dimension values

        cdim=c/float(Fc)
        alphadim=math.atan(tan(alpha)/float(Falpha))



        ##Soil pressure coefficients

        Ka  = math.tan((math.pi/4-(alphadim/float(2))))**2                  ##Active side
        Kac=math.tan(math.pi/4-(alphadim/float(2)))*2
        Kp  = math.tan((math.pi/4+(alphadim/float(2))))**2                 ##Passive side
        Kpc=math.tan(math.pi/4+(alphadim/float(2)))*2
        Ko=(1-math.sin(alpha))*math.sqrt(OCR)
        #print Ka
        #print Kac
        #print Kp
        #print Kpc
        #print Ko

        ##Soilpressure at height according to geometry


        SoilpressureActiveMax=(verticalload+weight*(height-subsoilwaterheight)+(weight-pw)*subsoilwaterheight)*Ka+subsoilwaterheight*pw
        SoilpressureActiveEdgeMax=(verticalload+weight*(heightWing-subsoilwaterheight)+(weight-pw)*subsoilwaterheight)*Ka+subsoilwaterheight*pw
        SoilpressureRestMax=(verticalload+weight*(height-subsoilwaterheight)+(weight-pw)*subsoilwaterheight)*Ko+subsoilwaterheight*pw 
        SoilpressureRestEdgeMax=(verticalload+weight*(heightWing-subsoilwaterheight)+(weight-pw)*subsoilwaterheight)*Ko+subsoilwaterheight*pw 

        ##To get it linear (has to be done incase of subsoilwater) [kn/m/m]

        SoilpressureActive=SoilpressureActiveMax/float(height)
        SoilpressureActiveEdge=SoilpressureActiveEdgeMax/float(heightWing)
        SoilpressureRest=SoilpressureRestMax/float(height)
        SoilpressureRestEdge=SoilpressureRestEdgeMax/float(heightWing)

        ##ULS max of active or re
        SoilpressureSLS=SoilpressureRest
        SoilpressureULS=max(SoilpressureActive,SoilpressureRest)
        SoilpressureSLSedge=SoilpressureRestEdge
        SoilpressureULSedge=max(SoilpressureActiveEdge,SoilpressureRestEdge)

        if SoilpressureSLS==():
            if SoilpressureULS==():
                if SoilpressureSLSedge==():
                    if SoilpressureULSedge==():
                        print 'Soilpressure not correctly introduced or does not exist'
        ##################################################################################################

        ##Moment from wings

        ##EDGE MOMENT FRAME LEG

        ##SLS

        ##Load Equation


        edgemomentSLS=(SoilpressureSLSedge*wingWidness**2)/float(2)


        ##ULS

        ##Load Equation

        ##Equation for edge moment
        edgemomentULS=(SoilpressureULSedge*wingWidness**2)/float(2)

#####################################################################################################
        
        ##initilazie export vector

        Reinforc1=[] 



        ##Create Model
        myModel = mdb.Model(name='ModelBridge')


        ##Simple Geometry 

        ##slab
        mySketchPlate = myModel.ConstrainedSketch(name='Sketch Plate', sheetSize=
          200.0)

        mySketchPlate.rectangle(point1=(0, 0), point2=(L, platewidth))	

        myPlate = myModel.Part(name='slab', dimensionality=THREE_D, 
                type=DEFORMABLE_BODY)

        myPlate.BaseShell(sketch=mySketchPlate) 										##Will be a Shell element

        ##leg1
        mySketchLeg = myModel.ConstrainedSketch(name='Sketch Leg1', sheetSize=200.0)
        mySketchLeg.rectangle(point1=(0,0), point2=(height, platewidth))
        myLeg1 = myModel.Part(name='Leg1', dimensionality=THREE_D,type=DEFORMABLE_BODY)
        myLeg1.BaseShell(sketch=mySketchLeg) 											##Will be a Shell element

        ##leg2
        mySketchLeg = myModel.ConstrainedSketch(name='Sketch Leg2', sheetSize=200.0)
        mySketchLeg.rectangle(point1=(0,0), point2=(height, platewidth))
        myLeg2 = myModel.Part(name='Leg2', dimensionality=THREE_D,type=DEFORMABLE_BODY)
        myLeg2.BaseShell(sketch=mySketchLeg) 											##Will be a Shell element

        ##Cantilever1
        mySketchCantilever = myModel.ConstrainedSketch(name='Sketch Cantilever-1',sheetSize=200.0)				    
        mySketchCantilever.Line(point1=(0, 0), point2=(L, 0))			        
        myCantilever1 = myModel.Part(name='Cantilever1', dimensionality=THREE_D,type=DEFORMABLE_BODY)
        myCantilever1.BaseWire(sketch=mySketchCantilever)								##Will be a wire element

        ##Cantilever2
        mySketchCantilever = myModel.ConstrainedSketch(name='Sketch Cantilever-2',sheetSize=200.0)				    
        mySketchCantilever.Line(point1=(0, 0), point2=(L,0))			        
        myCantilever2 = myModel.Part(name='Cantilever2', dimensionality=THREE_D,type=DEFORMABLE_BODY)
        myCantilever2.BaseWire(sketch=mySketchCantilever)								##Will be a wire element

        ##Create Material

        ##frame bridge
        myConcrete = myModel.Material (name='concrete')
        elasticProperties = (Ecm, poissonconcrete)
        myConcrete.Density(table=((rhoconcrete, ), ))
        myConcrete.Elastic(table=(elasticProperties, ) )

        ##Cantilever low E modulus 
        myConcrete = myModel.Material (name='Cantilever Concrete')
        elasticProperties= (Ecm/float(1000000000), poissonconcrete)
        myConcrete.Density(table=((rhoconcrete, ), ))
        myConcrete.Elastic(table=(elasticProperties, ) )

        ##Create Sections

        ##slab
        myPlateSection = myModel.HomogeneousShellSection(name='plate', 
        preIntegrate=OFF, material='concrete', thicknessType=UNIFORM, 
        thickness=thicknesslab, thicknessField='', idealization=NO_IDEALIZATION, 
        poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
        useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)

        ##legs
        myLegSection  = myModel.HomogeneousShellSection(name='leg', 
        preIntegrate=OFF, material='concrete', thicknessType=UNIFORM, 
        thickness=thicknessleg, thicknessField='', idealization=NO_IDEALIZATION, 
        poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
        useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)

        ##Cantilever
        #myCantileverSection = myModel.HomogeneousShellSection (idealization=NO_IDEALIZATION,	    #Create the section for the plate, with shell elements, 5 integration points and thickness according to the given paramenters
        #integrationRule=SIMPSON, material='Cantilever Concrete', name='Cantilever Section',			
        #numIntPts=5, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=
        #GRADIENT, thickness=Cantileverwidth, thicknessField='', thicknessModulus=None,
        #thicknessType=UNIFORM, useDensity=OFF)

        ##Beam element
        myModel.RectangularProfile(name='Cantilever geometry', a=Cantileverwidth, b=Cantileverheight)
        myModel.BeamSection(name='Beam Element Cantilever', 												#Beam element!
                integration=DURING_ANALYSIS, poissonRatio=0.15, profile='Cantilever geometry', 
                material='Cantilever Concrete', temperatureVar=LINEAR, 
                consistentMassMatrix=False)
                

        ##Assembly

        myAssembly=myModel.rootAssembly 

        ##leg1
        myInstanceLeg = myAssembly.Instance(name='Leg1Instance', part=myLeg1, dependent=OFF)	
        myAssembly.rotate(angle=90, axisDirection=(height, 0, 0.0), axisPoint=(0.0,0, 0.0), instanceList=('Leg1Instance', )) 						#Leg1 rotering
        myAssembly.rotate(angle=90, axisDirection=(0.0,0, -platewidth), axisPoint=(0.0, 0.0, platewidth), instanceList=('Leg1Instance', )) 			#Leg1 rotering

        ##leg2
        myInstanceLeg2 = myAssembly.Instance(name='Leg2Instance', part=myLeg2, dependent=OFF)
        myAssembly.translate(instanceList=('Leg2Instance', ), vector=(L, 0.0, 0.0))  #Rotate and move leg2
        myAssembly.rotate(angle=90, axisDirection=(height, 0, 0.0), axisPoint=(L, 0.0, 0.0), instanceList=('Leg2Instance', )) 

        myAssembly.rotate(angle=90, axisDirection=(0, 0, -platewidth), axisPoint=(L, 0.0, 0.0), instanceList=('Leg2Instance', ))
        myAssembly.rotate(angle=180, axisPoint=(L, 0 , platewidth/float(2)), axisDirection= (0, -height, 0), instanceList=('Leg2Instance', )) 		#rotate 180 degrees for mesh symmetry

        ##plate
        myInstancePlate = myAssembly.Instance(name='PlateInstance', part=myPlate, dependent=OFF)	
        myAssembly.rotate(angle=90.0, axisDirection=(L, 0, 0), axisPoint=(0, 0.0, 0.0), instanceList=('PlateInstance', )) 

        ##Cantilever1
        myInstanceCantilever1= myAssembly.Instance(name='Cantilever 1', part=myCantilever1, dependent=OFF)	
        myAssembly.translate(instanceList=('Cantilever 1', ), vector=(0.0, 0.3, 0))

        ##Cantilever2
        myInstanceCantilever2= myAssembly.Instance(name='Cantilever 2', part=myCantilever2, dependent=OFF)	
        myAssembly.translate(instanceList=('Cantilever 2', ), vector=(0.0, 0.3, platewidth))


        Instance=(myInstanceLeg, myInstanceLeg2, myInstancePlate, )    ##For convenience
        Cantilivers=(myInstanceCantilever1,myInstanceCantilever2, )         ##For convenience

        ##Merge to make one part
        mergedinstance=myAssembly.InstanceFromBooleanMerge(name='Merged Bridge', instances = Instance, originalInstances=SUPPRESS, domain=GEOMETRY)


        ##Assign Sections

        myBridge=myModel.parts['Merged Bridge']	#New path for merged part
        session.viewports['Viewport: 1'].setValues(displayedObject=myBridge)	# Show bridge in viewport


        ##Plate
        regionPlate=regionToolset.Region(faces=myBridge.faces.findAt(((L/float(2),0,platewidth/float(2)),)))
        myBridge.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=regionPlate, sectionName='plate', thicknessAssignment=FROM_SECTION)	    #Assignment for the plate region
        #myBridge.flipNormal(regions=regionPlate) ##Thickness offset


        ##Legs1
        regionLeg1=regionToolset.Region(faces=myBridge.faces.findAt(((0,-height,platewidth),)))
        myBridge.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=regionLeg1, sectionName='leg', thicknessAssignment=FROM_SECTION)	    #Assignment for leg1 region
        #myBridge.flipNormal(regions=regionLeg1)

        ##Legs2
        regionLeg2=regionToolset.Region(faces=myBridge.faces.findAt(((L, -height, platewidth),)))
        myBridge.SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=regionLeg2, sectionName='leg', thicknessAssignment=FROM_SECTION)	    #Assignment for leg2 region
        #myBridge.flipNormal(regions=regionLeg2)

        ##Cantilever1
        regionCantilever1=regionToolset.Region(edges=myCantilever1.edges.findAt(((L/float(2),0,0),)))
        myCantilever1.SectionAssignment(offset=0.0, offsetField='',offsetType=MIDDLE_SURFACE, region=regionCantilever1, sectionName='Beam Element Cantilever', thicknessAssignment=FROM_SECTION)


        ##Cantilever2
        regionCantilever2=regionToolset.Region(edges=myCantilever2.edges.findAt(((L/float(2),0,0),)))
        myCantilever2.SectionAssignment(offset=0.0, offsetField='',offsetType=MIDDLE_SURFACE, region=regionCantilever2, sectionName='Beam Element Cantilever', thicknessAssignment=FROM_SECTION)


        myAssembly.makeIndependent(instances=(mergedinstance, ))	##Make the instance of the whole bridge independent. (Avoid problems when meshing).
        session.viewports['Viewport: 1'].setValues(displayedObject=myAssembly)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(renderShellThickness=OFF) ##Toggle on/off


        ##Assign Beam Orientation ##CORRECT??

        regionCantilever1=regionToolset.Region(edges=myCantilever1.edges.findAt(((L/float(2),0,0),)))
        regionCantilever2=regionToolset.Region(edges=myCantilever2.edges.findAt(((L/float(2),0,0),)))
        myCantilever1.assignBeamSectionOrientation(region=regionCantilever1, method=N1_COSINES, n1=(0.0, 0.0, -1-0))
        myCantilever2.assignBeamSectionOrientation(region=regionCantilever2, method=N1_COSINES, n1=(0.0, 0.0, -1-0))



        ##BC


        for i in range (0,2):

         edgeleg=myAssembly.instances['Merged Bridge-1'].edges.findAt(((L*i,-height,0+delta),),((L*i,-height,platewidth/float(2)),))
         regionBC=regionToolset.Region(edges=edgeleg)
          #region = myAssembly.Set(edges=edges1, name='Set-1')
         myModel.DisplacementBC(name='BC-%s' %(i), createStepName='Initial',region=regionBC, u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET,amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)


        ##partitions for wings Shell edge load
        for i in range(0,2):
            LegFace=mergedinstance.faces.getByBoundingBox(L*i-delta,-height-delta,0-delta,L*i+delta,0+delta,platewidth+delta)

            DatumLegLoad=myAssembly.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=-height+wingOffset).id
            Datums=myAssembly.datums
            myAssembly.PartitionFaceByDatumPlane(datumPlane=Datums[DatumLegLoad], faces=LegFace)


        ##Partitions L/2 to get path L/2
        PlateFace=mergedinstance.faces.getByBoundingBox(0-delta,0-delta,0-delta,L+delta,0+delta,platewidth+delta)
        DatumPlate=myAssembly.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=L/float(2)).id
        Datums=myAssembly.datums
        myAssembly.PartitionFaceByDatumPlane(datumPlane=Datums[DatumPlate], faces=PlateFace)

        ##Tie cantilevers to deck OR TO EDGE????

        for i in range (0,2):

         SurfPlateCant=mergedinstance.faces.getByBoundingBox(0-delta,0-delta,0-delta,L+delta,platewidth+delta)
         regionSurfPlateBridge=regionToolset.Region(side2Faces=SurfPlateCant)
         Cantedge = Cantilivers[i].edges.findAt(((L/float(2),0.3,i*platewidth),))
         c1=myAssembly.Surface(circumEdges=Cantedge, name='circumcant%s' %(i))


         myModel.Tie(name='Cantilerver ties%s' %(i), master=regionSurfPlateBridge, slave=c1, positionToleranceMethod=SPECIFIED, positionTolerance=1, adjust=ON, tieRotations=ON, thickness=ON)



        if TrafficAnalysis==False:      ##Just an approximation of the traffic load for faster analysis


                   ##Step 

            myModel.StaticStep(name='SLS', previous='Initial',								        #Create the loading step for the analysis.
                                                   timePeriod=1.0, initialInc=1,
                                                  description='Pressure on slab SLS.')
            myModel.StaticStep(name='ULS', previous='SLS',								            #Create the loading step for the analysis.
                       timePeriod=1.0, initialInc=1,
                      description='Pressure on slab ULS.')          

                    ##Loads
                    
                    ##Pressure over the deck 
                    
            
            SurfacePlate=mergedinstance.faces.getByBoundingBox(0-delta, 0-delta, 0-delta,L+delta, 0, platewidth+delta)
            
            topSurfacePlate= ((SurfacePlate,SIDE2),)										                        #Select which side (SIDE 2, downwards)
            myModel.Pressure(name='PressurePlate SLS', createStepName='SLS', 
                                                region=topSurfacePlate, magnitude=loadmagnitude*gammaSLSV)							        #Create the load in the regions previously found according to the load magnitude set at the beginning

            myModel.loads['PressurePlate SLS'].deactivate('ULS')    
            myModel.Pressure(name='PressurePlate ULS', createStepName='ULS', 
                                                region=topSurfacePlate, magnitude=loadmagnitude*gammaULSV)							        #Create the load in the regions previously found according to the load magnitude set at the beginning

            ##gravity Load
            wholemodel= faces=mergedinstance.faces.getByBoundingBox(0-delta, -height-delta, 0-delta, L+delta, 0+delta, platewidth+delta)
            cantiliver1=Cantilivers[0].edges.findAt(((L/float(2),0.3,0),))
            cantiliver2=Cantilivers[1].edges.findAt(((L/float(2),0.3,platewidth),))
            regionCant=myAssembly.Set(edges=cantiliver1+cantiliver2, faces=wholemodel, name='set')
            #regionBridg=regionToolset.Region(faces=wholemodel)
            #print regionBridge
            #regionb=((regionBridg),(regionCant))
            
            myModel.Gravity(name='Self-weight SLS', createStepName='SLS', region=regionCant, comp2=-g*gammaSLSP, distributionType=UNIFORM, field='')
            myModel.loads['Self-weight SLS'].deactivate('ULS')
            myModel.Gravity(name='Self-weight ULS', createStepName='ULS', region=regionCant, comp2=-g*gammaULSP, distributionType=UNIFORM, field='')

            ##soilpressure

            ##apply loads
            myModel.ExpressionField(name='AnalyticalField', localCsys=None, description='', expression='Y*(1) ')

            legface0=mergedinstance.faces.getByBoundingBox(0-delta,-height-delta,0-delta,0+delta,0+delta,platewidth+delta)
            legface1=mergedinstance.faces.getByBoundingBox(L-delta,-height-delta,0-delta,L+delta,0+delta,platewidth+delta)

            mySurface=((legface0, SIDE1), (legface1, SIDE1),)

            myModel.Pressure(name='Triangle Load SLS', createStepName='SLS', region=mySurface, distributionType=FIELD, field='AnalyticalField', magnitude=-SoilpressureSLS*gammaSLSP, amplitude=UNSET)
            myModel.loads['Triangle Load SLS'].deactivate('ULS')
            myModel.Pressure(name='Triangle Load ULS', createStepName='ULS', region=mySurface, distributionType=FIELD, field='AnalyticalField', magnitude=-SoilpressureULS*gammaULSP, amplitude=UNSET)

            edge1=regionToolset.Region(side1Edges=mergedinstance.edges.findAt(((0,-height/float(2),0),),((0,-height/float(2),platewidth),),((L,-height/float(2),0),),((L,-height/float(2),platewidth),)))

            myModel.ShellEdgeLoad(name='Wing moment SLS', createStepName='SLS', 
                region=edge1, magnitude=-edgemomentSLS*gammaSLSP, distributionType=FIELD, 
                field='AnalyticalField', localCsys=None, traction=MOMENT, resultant=ON)
            myModel.loads['Wing moment SLS'].deactivate('ULS')
            myModel.ShellEdgeLoad(name='Wing moment ULS', createStepName='SLS', 
                region=edge1, magnitude=-edgemomentULS*gammaULSP, distributionType=FIELD, 
                field='AnalyticalField', localCsys=None, traction=MOMENT, resultant=ON)

        else: ##TRAFIC LOAD FROM COMPOSITE BRIDGE
            
            num=1            ##NUM OF BEAMS 1??
            
            thickTraffic=0.01
            
            posadj=0
            delta=1E-4
            MagLanes=[Lane1Pressure,RemainingPressure] # Lane2Pressure,Lane3Pressure,RemainingPressure equal
            numCases=(num+1)/2
            LaneCut=[[0,0,0,0,0,0] for i in xrange(0,numCases)]
            

            remaining=(platewidth-3*numlanes)/float(2)
            if remaining <0:
                print('--------------------------------ERROR:The number of lanes introduced can not fit into the bridge according to regulations. Reduce number of lanes or design a wider bridge.---------------------------------------')
                quit()
            
            
           
                  
                 
            postrafficLongCar=[]                    
            postrafficLong1Car=[0.5,2.5]
            postrafficLongCar.extend(postrafficLong1Car[:])
            for i in xrange(0,numlanes-1):
                postrafficLong1Car=[postrafficLongCar[-1]+1,postrafficLongCar[-1]+3]
                postrafficLongCar.extend(postrafficLong1Car[:])


            postrafficLong=[] #List storing all the longitudinal partitions for traffic plate
             
            postrafficlong1lane= [0.3+posadj,0.7+posadj,2.3+posadj, 2.7+posadj,3+posadj] 
            postrafficLong.extend(postrafficlong1lane[:])
            
            ##Position of beams partitions
            
            for i in xrange(0,numlanes-1):   
                postrafficlong1lane=[0.3+postrafficlong1lane[-1],0.7+postrafficlong1lane[-1],2.3+postrafficlong1lane[-1],2.7+postrafficlong1lane[-1],3+postrafficlong1lane[-1]]
                postrafficLong.extend(postrafficlong1lane[:])  
                


            
            postrafficLong=list(set(postrafficLong)) #Remove repeated values (To avoid collisions between partitions of different nature 
            postrafficLong.sort() #Sort values in order to avoid problems while partitioning  (Insert influence lines partition in correct position)

            if postrafficLong[-1]==platewidth+posadj:
                postrafficLong.pop(-1)
            if postrafficLong[0]==posadj:
                postrafficLong.pop(0)
            ##Modelling of the traffic plate

            mySketchPlate = myModel.ConstrainedSketch(name='Sketch Plate',sheetSize=200.0)				    #Initialize skecth plate
            mySketchPlate.rectangle(point1=(0, 0), point2=(L, platewidth))			        #Draw the sketch depending on the values given
            myTraffic = myModel.Part(name='Traffic', dimensionality=THREE_D,type=DEFORMABLE_BODY)	#Create the part from the previous sketch

            myTraffic.BaseShell(sketch=mySketchPlate)						#This part will be shell type

            ##Material traffic plate
            
            myConcrete = myModel.Material (name='Traffic Concrete')						            #Create a new material (Concrete)

            elasticProperties = (Ecm/float(1000000000), poissonconcrete)							        #Assign mechanical properties (E modulus,Poisson coef) Very small E because no stiffness desired.
            myConcrete.Elastic(table=(elasticProperties, ) )					                    #Assign previous properties to the material

            ##Plate Traffic

            myPlateSection = myModel.HomogeneousShellSection (idealization=NO_IDEALIZATION,	    #Create the section for the plate, with shell elements, 5 integration points and thickness according to the given paramenters
                    integrationRule=SIMPSON, material='Traffic Concrete', name='Traffic Section',			
                    numIntPts=5, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=
                    GRADIENT, thickness=thickTraffic, thicknessField='', thicknessModulus=None,
                    thicknessType=UNIFORM, useDensity=OFF)


            ##Assembly Traffic
            myAssembly = myModel.rootAssembly
            myInstanceTraffic = myAssembly.Instance(name='TrafficInstance', part=myTraffic, dependent=OFF)	
            myAssembly.rotate(angle=90.0, axisDirection=(L,0,0), axisPoint=(0,0,0), instanceList=('TrafficInstance',))
            myAssembly.translate(instanceList=('TrafficInstance', ), vector=(0.0, htraffic, 0))
            myAssembly.translate(instanceList=('TrafficInstance', ), vector=(0.0, 0.0, posadj))

            regionTraffic=regionToolset.Region(faces=myTraffic.faces.findAt(((L/float(2),platewidth/float(2),0),)))     #Find the faces in the part, XY object
            myTraffic.flipNormal(regions=regionTraffic)
            myTraffic.SectionAssignment(offset=0.0, offsetField=''
                        , offsetType=BOTTOM_SURFACE, region=regionTraffic, sectionName='Traffic Section', thicknessAssignment=		  
                        FROM_SECTION)


            ## Partitions Traffic

            if CarPlacement!=2:

                postrafficaxle=[x*0.1 for x in xrange(0,5*L+12,12)]    #Mid span plus one extra position to be sure it is crossed

                DatumTrafficLong=[]

            else:
                
                postrafficaxle=[0,1.2,L/float(4)-0.8,L/float(4)+0.4,L/float(2)-0.8,L/float(2)+0.4]    #0.8=1.2/2 + 0.4/2

                DatumTrafficLong=[]


            for i in postrafficLong:
                    DatumTrafficLongv=myAssembly.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=i).id
                    DatumTrafficLong.append(DatumTrafficLongv)

                    
            DatumTrafficTrans=[]

            for i in postrafficaxle:
                    DatumTrafficTransAxlPos=myAssembly.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=i).id
                    DatumTrafficTransAxlFro=myAssembly.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=i+0.4).id
                    DatumTrafficTrans.append([DatumTrafficTransAxlPos,DatumTrafficTransAxlFro])

            Datums=myAssembly.datums


            for i in DatumTrafficLong:
                SurfaceTrafficLong=myInstanceTraffic.faces.findAt(((L/float(2),htraffic,platewidth+posadj-delta),))
                myAssembly.PartitionFaceByDatumPlane(datumPlane=Datums[i], faces=SurfaceTrafficLong)

            
            postrafficLongCarLane1=[0.5,2.5]
            postrafficLongCarLane2=[3+0.5,3+2.5]
            postrafficCar=postrafficLongCarLane1+postrafficLongCarLane2
            if numlanes==3:
                postrafficLongCarLane3=[6+0.5,6+2.5]
                postrafficCar=postrafficLongCarLane1+postrafficLongCarLane2+postrafficLongCarLane3
            
                            
            for i in xrange(0,len(DatumTrafficTrans)):
                for j in DatumTrafficTrans[i]:
                    if j!=DatumTrafficTrans[0][0]:
                        for pos in postrafficCar:
                            SurfaceCar=myInstanceTraffic.faces.getByBoundingBox(0-delta,htraffic-delta,pos+posadj-0.2-delta,L+delta,htraffic+delta,pos+posadj+0.2+delta)
                            myAssembly.PartitionFaceByDatumPlane(datumPlane=Datums[j], faces=SurfaceCar)

            ##Step 

            myModel.StaticLinearPerturbationStep(name='Traffic Load', previous='Initial',								        #Create the loading step for the analysis.
                description='Pressure on slab Traffic')

            ########### LOADS

            ####Gravity load ASK WHY region didnt exist IT LOOK WIERD

            wholemodel= faces=mergedinstance.faces.getByBoundingBox(0-delta, -height-delta, 0-delta, L+delta, 0+delta, platewidth+delta)
            cantiliver1=Cantilivers[0].edges.findAt(((L/float(2),0.3,0),))
            cantiliver2=Cantilivers[1].edges.findAt(((L/float(2),0.3,platewidth),))
            regionCant=myAssembly.Set(edges=cantiliver1+cantiliver2, faces=wholemodel, name='set2')

            myModel.Gravity(name='Self-weight', createStepName='Traffic Load', comp2=-g, region=regionCant, distributionType=UNIFORM, field='')

            ##Soil pressure
            myModel.ExpressionField(name='AnalyticalField', localCsys=None, description='', expression='Y*(1) ')

            legface0=mergedinstance.faces.getByBoundingBox(0-delta,-height-delta,0-delta,0+delta,0+delta,platewidth+delta)
            legface1=mergedinstance.faces.getByBoundingBox(L-delta,-height-delta,0-delta,L+delta,0+delta,platewidth+delta)

            mySurface=((legface0, SIDE1), (legface1, SIDE1),)

            myModel.Pressure(name='SoilSLS', createStepName='Traffic Load', region=mySurface, distributionType=FIELD, field='AnalyticalField', magnitude=-SoilpressureSLS, amplitude=UNSET)
            myModel.Pressure(name='SoilULS', createStepName='Traffic Load', region=mySurface, distributionType=FIELD, field='AnalyticalField', magnitude=-SoilpressureULS, amplitude=UNSET)
            ##Edgemoment from wings

            edge1=regionToolset.Region(side1Edges=mergedinstance.edges.findAt(((0,-height/float(2),0),),((0,-height/float(2),platewidth),),((L,-height/float(2),0),),((L,-height/float(2),platewidth),)))

            myModel.ShellEdgeLoad(name='WingSLS', createStepName='Traffic Load', 
                region=edge1, magnitude=-edgemomentSLS, distributionType=FIELD, 
                field='AnalyticalField', localCsys=None, traction=MOMENT, resultant=ON)

            myModel.ShellEdgeLoad(name='WingULS', createStepName='Traffic Load', 
                region=edge1, magnitude=-edgemomentULS, distributionType=FIELD, 
                field='AnalyticalField', localCsys=None, traction=MOMENT, resultant=ON)



            ##Traffic Loads

            postrafficaxlemid=[x+0.2 for x in postrafficaxle]

            if CarPlacement==2:
                rangeLoad=xrange(0,len(postrafficaxlemid)-1,2)
            else:
                rangeLoad=xrange(0,len(postrafficaxlemid)-1)

            for i in rangeLoad:
                    
                    Axlel11Lane1=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i]-0.2-delta,htraffic-delta,postrafficLongCarLane1[0]+posadj-0.2-delta,postrafficaxlemid[i]+0.2+delta,htraffic+delta,postrafficLongCarLane1[0]+posadj+0.2+delta)
                    Axlel12Lane1=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i]-0.2-delta,htraffic-delta,postrafficLongCarLane1[1]+posadj-0.2-delta,postrafficaxlemid[i]+0.2+delta,htraffic+delta,postrafficLongCarLane1[1]+posadj+0.2+delta)
                    Axlel21Lane1=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i+1]-0.2-delta,htraffic-delta,postrafficLongCarLane1[0]+posadj-0.2-delta,postrafficaxlemid[i+1]+0.2+delta,htraffic+delta,postrafficLongCarLane1[0]+posadj+0.2+delta)
                    Axlel22Lane1=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i+1]-0.2-delta,htraffic-delta,postrafficLongCarLane1[1]+posadj-0.2-delta,postrafficaxlemid[i+1]+0.2+delta,htraffic+delta,postrafficLongCarLane1[1]+posadj+0.2+delta)

                    Axlel11Lane2=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i]-0.2-delta,htraffic-delta,postrafficLongCarLane2[0]+posadj-0.2-delta,postrafficaxlemid[i]+0.2+delta,htraffic+delta,postrafficLongCarLane2[0]+posadj+0.2+delta)
                    Axlel12Lane2=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i]-0.2-delta,htraffic-delta,postrafficLongCarLane2[1]+posadj-0.2-delta,postrafficaxlemid[i]+0.2+delta,htraffic+delta,postrafficLongCarLane2[1]+posadj+0.2+delta)
                    Axlel21Lane2=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i+1]-0.2-delta,htraffic-delta,postrafficLongCarLane2[0]+posadj-0.2-delta,postrafficaxlemid[i+1]+0.2+delta,htraffic+delta,postrafficLongCarLane2[0]+posadj+0.2+delta)
                    Axlel22Lane2=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i+1]-0.2-delta,htraffic-delta,postrafficLongCarLane2[1]+posadj-0.2-delta,postrafficaxlemid[i+1]+0.2+delta,htraffic+delta,postrafficLongCarLane2[1]+posadj+0.2+delta)

                    TopSurfaceCarLane1=((Axlel11Lane1,SIDE2),(Axlel12Lane1,SIDE2),(Axlel21Lane1,SIDE2),(Axlel22Lane1,SIDE2))
                    TopSurfaceCarLane2=((Axlel11Lane2,SIDE2),(Axlel12Lane2,SIDE2),(Axlel21Lane2,SIDE2),(Axlel22Lane2,SIDE2))
                    myModel.Pressure(name='Car%s Lane1' %(i), createStepName='Traffic Load', region=TopSurfaceCarLane1, magnitude=(0.5*Lane1Car/float(1000))/float(wheelwidth*wheelwidth))
                    myModel.Pressure(name='Car%s Lane2' %(i), createStepName='Traffic Load', region=TopSurfaceCarLane2, magnitude=(0.5*Lane2Car/float(1000))/float(wheelwidth*wheelwidth))
                    
                    if numlanes==3:
                       
                        Axlel11Lane3=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i]-0.2-delta,htraffic-delta,postrafficLongCarLane3[0]+posadj-0.2-delta,postrafficaxlemid[i]+0.2+delta,htraffic+delta,postrafficLongCarLane3[0]+posadj+0.2+delta)
                        Axlel12Lane3=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i]-0.2-delta,htraffic-delta,postrafficLongCarLane3[1]+posadj-0.2-delta,postrafficaxlemid[i]+0.2+delta,htraffic+delta,postrafficLongCarLane3[1]+posadj+0.2+delta)
                        Axlel21Lane3=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i+1]-0.2-delta,htraffic-delta,postrafficLongCarLane3[0]+posadj-0.2-delta,postrafficaxlemid[i+1]+0.2+delta,htraffic+delta,postrafficLongCarLane3[0]+posadj+0.2+delta)
                        Axlel22Lane3=myInstanceTraffic.faces.getByBoundingBox(postrafficaxlemid[i+1]-0.2-delta,htraffic-delta,postrafficLongCarLane3[1]+posadj-0.2-delta,postrafficaxlemid[i+1]+0.2+delta,htraffic+delta,postrafficLongCarLane3[1]+posadj+0.2+delta)

                        TopSurfaceCarLane3=((Axlel11Lane3,SIDE2),(Axlel12Lane3,SIDE2),(Axlel21Lane3,SIDE2),(Axlel22Lane3,SIDE2))
                        myModel.Pressure(name='Car%s Lane3' %(i), createStepName='Traffic Load', region=TopSurfaceCarLane3, magnitude=(Lane3Car/float(1000))/float(wheelwidth*wheelwidth))
                

            SurfaceLane1=myInstanceTraffic.faces.getByBoundingBox(0,htraffic-delta,-delta+posadj,L+delta,htraffic+delta,3+delta+posadj)
            SurfaceLane2=myInstanceTraffic.faces.getByBoundingBox(0,htraffic-delta,3-delta+posadj,L+delta,htraffic+delta,6+delta+posadj)
            TopSurfaceLane1=((SurfaceLane1,SIDE2),)
            TopSurfaceLane2=((SurfaceLane2,SIDE2),)

            myModel.Pressure(name='UDL Lane1', createStepName='Traffic Load', region=TopSurfaceLane1, magnitude=Lane1Pressure)
            myModel.Pressure(name='UDL Lane2', createStepName='Traffic Load', region=TopSurfaceLane2, magnitude=Lane2Pressure)
            
            if remaining!=0:
                if numlanes==2:
                    SurfaceRemaining=myInstanceTraffic.faces.getByBoundingBox(0,htraffic-delta,6-delta+posadj,L+delta,htraffic+delta,platewidth+delta+posadj)
                    TopSurfaceRemaining=((SurfaceRemaining,SIDE2),)
                    myModel.Pressure(name='UDL Remaining', createStepName='Traffic Load', region=TopSurfaceRemaining, magnitude=RemainingPressure)
                else:
                    SurfaceRemaining=myInstanceTraffic.faces.getByBoundingBox(0,htraffic-delta,9-delta+posadj,L+delta,htraffic+delta,platewidth+delta+posadj)
                    TopSurfaceRemaining=((SurfaceRemaining,SIDE2),)
                    myModel.Pressure(name='UDL Remaining', createStepName='Traffic Load', region=TopSurfaceRemaining, magnitude=RemainingPressure)
                
                    SurfaceLane3=myInstanceTraffic.faces.getByBoundingBox(0,htraffic-delta,6-delta+posadj,L+delta,htraffic+delta,9+delta+posadj)
                    TopSurfaceLane3=((SurfaceLane3,SIDE2),)
                    myModel.Pressure(name='UDL Lane3', createStepName='Traffic Load', region=TopSurfaceLane3, magnitude=Lane3Pressure)
            else:
                if numlanes!=2:
                    SurfaceLane3=myInstanceTraffic.faces.getByBoundingBox(0,htraffic-delta,6-delta+posadj,L+delta,htraffic+delta,9+delta+posadj)
                    TopSurfaceLane3=((SurfaceLane3,SIDE2),)
                    myModel.Pressure(name='UDL Lane3', createStepName='Traffic Load', region=TopSurfaceLane3, magnitude=Lane3Pressure)

            
            if CarPlacement==0:
                LoadCombinations=len(postrafficaxlemid)-1
            elif CarPlacement==1:
                if numlanes==2:
                        LoadCombinations=(len(postrafficaxlemid)-1)**2
                else:
                        LoadCombinations=(len(postrafficaxlemid)-1)**3
            elif CarPlacement==2:
                if numlanes==2:
                        LoadCombinations=3**2
                else:
                        LoadCombinations=3**3
            
            
            Names=[()*i for i in xrange(0,2*LoadCombinations)]
            cNames=0
            
            if CarPlacement==2:
                rangeLoad=xrange(0,len(postrafficaxlemid)-1,2)
            else:
                rangeLoad=xrange(0,len(postrafficaxlemid)-1)
            
            
            if remaining!=0:
                if CarPlacement!=0:
                    if numlanes==2:
                        for i in rangeLoad:
                            for j in rangeLoad:
                                        Names[cNames]+=(('Car%s Lane1' %(i), gammaSLSV), ('Car%s Lane2' %(j), gammaSLSV),('UDL Lane1', gammaSLSV),('UDL Lane2', gammaSLSV),('UDL Remaining', gammaSLSV),('Self-weight', gammaSLSP),('SoilSLS',gammaSLSP),('WingSLS', gammaSLSP),)
                                        Names[cNames+1]+=(('Car%s Lane1' %(i), gammaULSV), ('Car%s Lane2' %(j), gammaULSV),('UDL Lane1', gammaULSV),('UDL Lane2', gammaULSV),('UDL Remaining', gammaULSV),('Self-weight', gammaULSP),('SoilULS',gammaULSP),('WingULS',gammaULSP),)
                                        cNames+=2
                    if numlanes==3:
                                    for i in rangeLoad:
                                        for j in rangeLoad:
                                            for k in rangeLoad:
                                                Names[cNames]+=(('Car%s Lane1' %(i), gammaSLSV), ('Car%s Lane2' %(j), gammaSLSV),('Car%s Lane3' %(k), gammaSLSV),('UDL Lane1', gammaSLSV),('UDL Lane2', gammaSLSV),('UDL Lane3', gammaSLSV),('UDL Remaining', gammaSLSV),('Self-weight', gammaSLSP),('SoilSLS', gammaSLSP),('WingSLS', gammaSLSP),)
                                                Names[cNames+1]+=(('Car%s Lane1' %(i), gammaULSV), ('Car%s Lane2' %(j), gammaULSV),('Car%s Lane3' %(k), gammaULSV),('UDL Lane1', gammaULSV),('UDL Lane2', gammaULSV),('UDL Lane3', gammaULSV),('UDL Remaining', gammaULSV),('Self-weight', gammaULSP),('SoilULS', gammaULSP),('WingULS',gammaULSP),)
                                                cNames+=2
                
                
                
                else:
                        for i in xrange(0,len(postrafficaxlemid)-1):
                    
                            if numlanes==2:
                            
                                Names[cNames]+=(('Car%s Lane1' %(i), gammaSLSV), ('Car%s Lane2' %(i), gammaSLSV),('UDL Lane1', gammaSLSV),('UDL Lane2', gammaSLSV),('UDL Remaining', gammaSLSV),('Self-weight', gammaSLSP),('SoilSLS', gammaSLSP),('WingSLS', gammaSLSP),)
                                Names[cNames+1]+=(('Car%s Lane1' %(i), gammaULSV), ('Car%s Lane2' %(i), gammaULSV),('UDL Lane1', gammaULSV),('UDL Lane2', gammaULSV),('UDL Remaining', gammaULSV),('Self-weight', gammaULSP),('SoilULS', gammaULSP),('WingULS',gammaULSP),)
                                cNames+=2
                            if numlanes==3:
                            
                                Names[cNames]+=(('Car%s Lane1' %(i), gammaSLSV), ('Car%s Lane2' %(i), gammaSLSV),('Car%s Lane3' %(i), gammaSLSV),('UDL Lane1', gammaSLSV),('UDL Lane2', gammaSLSV),('UDL Lane3', gammaSLSV),('UDL Remaining', gammaSLSV),('Self-weight', gammaSLSP),('SoilSLS', gammaSLSP),('WingSLS', gammaSLSP),)
                                Names[cNames+1]+=(('Car%s Lane1' %(i), gammaULSV), ('Car%s Lane2' %(i), gammaULSV),('Car%s Lane3' %(i), gammaULSV),('UDL Lane1', gammaULSV),('UDL Lane2', gammaULSV),('UDL Lane3', gammaULSV),('UDL Remaining', gammaULSV),('Self-weight', gammaULSP),('SoilULS', gammaULSP),('WingULS',gammaULSP),)
                                cNames+=2   
                                
            else:
                if CarPlacement!=0:
                    if numlanes==2:
                        for i in rangeLoad:
                            for j in rangeLoad:
                                        Names[cNames]+=(('Car%s Lane1' %(i), gammaSLSV), ('Car%s Lane2' %(j), gammaSLSV),('UDL Lane1', gammaSLSV),('UDL Lane2', gammaSLSV),('Self-weight', gammaSLSP),('SoilSLS', gammaSLSP),('WingSLS', gammaSLSP),)
                                        Names[cNames+1]+=(('Car%s Lane1' %(i), gammaULSV), ('Car%s Lane2' %(j), gammaULSV),('UDL Lane1', gammaULSV),('UDL Lane2', gammaULSV),('Self-weight', gammaULSP),('SoilULS', gammaULSP),('WingULS',gammaULSP),)
                                        cNames+=2
                    if numlanes==3:
                                    for i in rangeLoad:
                                        for j in rangeLoad:
                                            for k in rangeLoad:
                                                Names[cNames]+=(('Car%s Lane1' %(i), gammaSLSV), ('Car%s Lane2' %(j), gammaSLSV),('Car%s Lane3' %(k), gammaSLSV),('UDL Lane1', gammaSLSV),('UDL Lane2', gammaSLSV),('UDL Lane3', gammaSLSV),('Self-weight', gammaSLSP),('SoilSLS', gammaSLSP),('WingSLS', gammaSLSP),)
                                                Names[cNames+1]+=(('Car%s Lane1' %(i), gammaULSV), ('Car%s Lane2' %(j), gammaULSV),('Car%s Lane3' %(k), gammaULSV),('UDL Lane1', gammaULSV),('UDL Lane2', gammaULSV),('UDL Lane3', gammaULSV),('Self-weight', gammaULSP),('SoilULS', gammaULSP),('WingULS',gammaULSP),)
                                                cNames+=2
                
                
                
                else:
                        for i in xrange(0,len(postrafficaxlemid)-1):
                    
                            if numlanes==2:
                            
                                Names[cNames]+=(('Car%s Lane1' %(i), gammaSLSV), ('Car%s Lane2' %(i), gammaSLSV),('UDL Lane1', gammaSLSV),('UDL Lane2', gammaSLSV),('Self-weight', gammaSLSP),('SoilSLS', gammaSLSP),('WingSLS', gammaSLSP),)
                                Names[cNames+1]+=(('Car%s Lane1' %(i), gammaULSV), ('Car%s Lane2' %(i), gammaULSV),('UDL Lane1', gammaULSV),('UDL Lane2', gammaULSV),('Self-weight', gammaULSP),('SoilULS', gammaULSP),('WingULS',gammaULSP),)
                                cNames+=2
                            if numlanes==3:
                            
                                Names[cNames]+=(('Car%s Lane1' %(i), gammaSLSV), ('Car%s Lane2' %(i), gammaSLSV),('Car%s Lane3' %(i), gammaSLSV),('UDL Lane1', gammaSLSV),('UDL Lane2', gammaSLSV),('UDL Lane3', gammaSLSV),('Self-weight', gammaSLSP),('SoilSLS', gammaSLSP),('WingSLS', gammaSLSP),)
                                Names[cNames+1]+=(('Car%s Lane1' %(i), gammaULSV), ('Car%s Lane2' %(i), gammaULSV),('Car%s Lane3' %(i), gammaULSV),('UDL Lane1', gammaULSV),('UDL Lane2', gammaULSV),('UDL Lane3', gammaULSV),('Self-weight', gammaULSP),('SoilULS', gammaULSP),('WingULS',gammaULSP),)
                                cNames+=2

            
            
            
            NameCases=[()*i for i in xrange(0,2*numCases)]      #first half SLS then ULS

        ##lots of stuff removed here correct or not????????????????????????
             

            NameFinal=[()*i for i in xrange(0,2*LoadCombinations*numCases)]    #First half SLS, then ULS
            
            cNameFinal=0
            for i in xrange(0,len(Names),2):
                for j in xrange(0,len(NameCases)/2):
                    NameFinal[cNameFinal]+=Names[i]
                    NameFinal[cNameFinal]+=NameCases[j]
                    cNameFinal+=1
            
            for i in xrange(1,len(Names),2):
                for j in xrange(len(NameCases)/2,len(NameCases)):
                    NameFinal[cNameFinal]+=Names[i]
                    NameFinal[cNameFinal]+=NameCases[j]
                    cNameFinal+=1

                    
            for i in xrange(0,len(NameFinal)/2):
                myModel.steps['Traffic Load'].LoadCase(name='LoadCase SLS %s'%(i), loads=NameFinal[i])
                myModel.steps['Traffic Load'].LoadCase(name='LoadCase ULS %s'%(i), loads=NameFinal[i+len(NameFinal)/2])


            ##Traffic tie to deck 
            SurfPlateBridge=mergedinstance.faces.getByBoundingBox(0-delta,0-delta,0-delta,L+delta,0+delta,platewidth+delta)#+posadj)
            SurfPlateTraffic=myInstanceTraffic.faces.getByBoundingBox(0-delta,htraffic-delta,0-delta+posadj,L+delta,htraffic+delta,platewidth+delta+posadj)
            regionSurfPlateBridge=regionToolset.Region(side2Faces=SurfPlateBridge)
            regionSurfPlateTraffic=regionToolset.Region(side1Faces=SurfPlateTraffic)

            myModel.Tie(name='Constraint Traffic', master=regionSurfPlateBridge, slave=regionSurfPlateTraffic, positionToleranceMethod=SPECIFIED, positionTolerance=1, adjust=ON, tieRotations=ON, thickness=ON)

        ##Traffic mesh
            myAssembly.seedPartInstance(deviationFactor=0.1, minSizeFactor=0.1, regions=(myInstanceTraffic,), size=elementsizetraffic)
            myAssembly.generateMesh(regions=(myInstanceTraffic,))
            
            ##see shell thickness
        session.viewports['Viewport: 1'].setValues(displayedObject=myAssembly)
        session.viewports['Viewport: 1'].assemblyDisplay.setValues(renderShellThickness=OFF) #Toggle on/off
        ##Mesh of bridge

        myAssembly.seedPartInstance(deviationFactor=0.1, minSizeFactor=0.1, regions=(mergedinstance,), size=elementsize)
        myAssembly.generateMesh(regions=( mergedinstance, ))

        myAssembly.seedPartInstance(deviationFactor=0.1, minSizeFactor=0.1, regions=(Cantilivers), size=elementsize)
        myAssembly.generateMesh(regions=(Cantilivers[0],Cantilivers[1], ))                      ##Cantilivers

        numofe=mergedinstance.elements###############element counter for convergence study
        numofelements=len(numofe)

        ##Field Output

        myModel.fieldOutputRequests['F-Output-1'].setValues(
                            variables=('S','PE', 'PEEQ', 'PEMAG', 'LE', 'U', 'RF', 'CF', 'SF',                              ##Variables requested to show in the calculations 
                            'CSTRESS', 'CDISP','NFORC'))


                        ##Create the job
        jobName = 'Pressure_on_top%s'%(portionnumber)                        
        myJob=mdb.Job(name=jobName, model='ModelBridge', description='Pressure on top of a bridge deck', type=ANALYSIS, 
                atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
                memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
                scratch='', multiprocessingMode=DEFAULT, numCpus=Ncores, numDomains=Ncores)



        myJob.submit()                              ##Submit the job
        myJob.waitForCompletion()             ##Script waits for job to complete

        ################################################################################

        ##ANALYSIS RUNNING HERE

        ################################################################################
        failcause=''

        ##DEFLECTION CHECK

        odb = visualization.openOdb('Pressure_on_top%s.odb'%(portionnumber))
        deflection=[]                                                                                   ##create deflection vector
        if TrafficAnalysis==True:

            deflectionaux=[]

            LoadCombinations=LoadCombinations*numCases
            for i in xrange(1,LoadCombinations+1):                                          ##Checked in SLS
                frame = odb.steps['Traffic Load'].frames[i] 
                dispField = frame.fieldOutputs['U']                                             ##Give a name to frame for displacements
                dispFieldSM=frame.fieldOutputs['SM']	                                    ##Give a name to frame for sectional moments
                        
                disp=[]                                                                                   ##Initialize a vector for displacements
                for i in range(0,len(dispField.values)):                                        ##Loop that check the deflection in every node and append them to the vector.
                            a=dispField.values[i].data[1]    ##0,1,2                         ##Get every displacement U2 
                            disp.append(a)	                                                        ##Append them to the vector previously defined
                deflength=min(disp)                                                                ##Get the smallest one (most negative, biggest deflection)
                deflectionaux.append(deflength)

            if deflectionaux<L/float(400):
                            failcause+='Deflection '
            deflection.append(min(deflectionaux))                                          ##Append it to the deflections vector.





        if TrafficAnalysis==False:
                frame = odb.steps['SLS'].frames[-1]                                          ##check deflection in SLS
                dispField = frame.fieldOutputs['U']                                            ##Give a name to frame for displacements
                dispFieldSM=frame.fieldOutputs['SM']                                      ##Give a name to frame for sectional moments
                disp=[]                                                                                  ##Initialize a vector for displacements
                for i in range(0,len(dispField.values)):                                       ##Loop that check the deflection in every node and append them to the vector.
                    a=dispField.values[i].data[1]    ##0,1,2                                ##Get every displacement U2 
                    disp.append(a)                                                                  ##Append them to the vector previously defined
                deflength=min(disp)                                                               ##Get the smallest one (most negative, biggest deflection)

                deflection.append(deflength)                                                  ##Append it to the deflections vector.

                if abs(deflection)>L/float(400):
                    failcause+= 'Deflection'
                    print 'Deflection exceeded'
        print 'The maximum deflection is:',deflection


        myOdb = visualization.openOdb(path='Pressure_on_top%s.odb'%(portionnumber))
        myViewport=session.viewports['Viewport: 1']
        myViewport.setValues(displayedObject=myOdb)
        myViewport.odbDisplay.setPrimaryVariable(variableLabel='SM', outputPosition=INTEGRATION_POINT, refinement=(COMPONENT, 'SM2'))           
        ODBFI7=session.odbs['Pressure_on_top%s.odb'%(portionnumber)]
        myViewport.setValues(displayedObject=ODBFI7)
        odbName=session.viewports[session.currentViewportName].odbDisplay.name
        if TrafficAnalysis==False:
            session.odbData[odbName].setValues(activeFrames=(('SLS', (-1, )), ('ULS', (-1, )), ))

        ##X path creation

        ##plate
        xmin=elementsize-delta
        xmax=elementsize+delta
        ymin=0-delta
        ymax=0+delta
        zmin=platewidth/float(2)-delta
        zmax=platewidth/float(2)+delta
        node1=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        xmin=L/float(2)-delta
        xmax=L/float(2)+delta
        node2=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        #session.Path(name='Path Long Mid', type=NODE_LIST, expression=(('Merged Bridge-1', (node1[0].label, node2[0].label, )), ))
        ##leg
        xmin=0-delta
        xmax=0+delta
        ymin=-height-delta
        ymax=-height+delta
        zmin=platewidth/float(2)-delta
        zmax=platewidth/float(2)+delta
        node1=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        ymin=0-delta
        ymax=0+delta
        node2=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        #session.Path(name='Path Long Leg', type=NODE_LIST, expression=(('Merged Bridge-1', (node1[0].label, node2[0].label, )), ))


        ##Z paths creation 

        ##L/2

        xmin=L/float(2)-delta
        xmax=L/float(2)+delta
        ymin=0-delta
        ymax=0+delta
        zmin=platewidth-delta
        zmax=platewidth+delta
        node1=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        zmin=-0-delta
        zmax=0+delta
        node2=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        session.Path(name='Path Trans L/2', type=NODE_LIST, expression=(('Merged Bridge-1', (node2[0].label, node1[0].label, )), ))

        ##0

        xmin=elementsize-elementsize/float(2)
        xmax=elementsize+elementsize/float(2)
        ymin=0-delta
        ymax=0+delta
        zmin=platewidth-delta
        zmax=platewidth+delta
        node1=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        zmin=-0-delta
        zmax=0+delta
        node2=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        session.Path(name='Path Trans 0', type=NODE_LIST, expression=(('Merged Bridge-1', (node2[0].label, node1[0].label, )), ))


        ##L/4

        xmin=L/float(4)-delta
        xmax=L/float(4)+delta
        ymin=0-delta
        ymax=0+delta
        zmin=platewidth-delta
        zmax=platewidth+delta
        node1=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        zmin=-0-delta
        zmax=0+delta
        node2=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        #session.Path(name='Path Trans L/4', type=NODE_LIST, expression=(('Merged Bridge-1', (node2[0].label, node1[0].label, )), ))

        ##h-elementsize
        delta=1e-4
        xmin=0-delta
        xmax=0+delta
        ymin=-elementsize-elementsize/float(2)
        ymax=-elementsize+elementsize/float(2)
        zmin=platewidth-delta
        zmax=platewidth+delta
        node1=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        zmin=-0-delta
        zmax=0+delta
        node2=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        session.Path(name='Path Trans -0', type=NODE_LIST, expression=(('Merged Bridge-1', (node2[0].label, node1[0].label, )), ))



        ##h=-height

        delta=1e-4
        xmin=0-delta
        xmax=0+delta
        ymin=-height-delta
        ymax=-height+delta
        zmin=platewidth-delta
        zmax=platewidth+delta
        node1=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        zmin=-0-delta
        zmax=0+delta
        node2=mergedinstance.nodes.getByBoundingBox(xmin, ymin, zmin, xmax, ymax, zmax)
        session.Path(name='Path Trans -height', type=NODE_LIST, expression=(('Merged Bridge-1', (node2[0].label, node1[0].label, )), ))

        myViewport.odbDisplay.setPrimaryVariable(variableLabel='SM', outputPosition=INTEGRATION_POINT, refinement=(COMPONENT, 'SM2'))           

        #####################################

        ##data extraction TRANSVERSAL DIRECTION for longitudinal reinforcement

        ## Bug might occur here with thickness of shells =0.3, its because the length of the dataSF vector is longer then there are number of elements
        ## i.e multiple forces are extracted from the same element and the diagram looks wierd, not yet solved.
        #####################################

        if TrafficAnalysis==True: ##this only works if traffic analysis is run


        #################################################################
                    
                    ##moment ULS
        ############################################################

            SMlocal1=[]
                                                                                ###Midspan
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1): ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude1' , path=session.paths['Path Trans L/2'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM1' ), ), ), labelType=TRUE_DISTANCE_Z)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude1' , path=session.paths['Path Trans L/2'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSM2)):
                    SMlocal1.append(dataSM2[i][1]+abs(dataSM3[i][1]))             ## Bjorn Engstrom, Mario Plos mu=1

                del session.xyDataObjects['Path Trans SM2 magnitude1'], session.xyDataObjects['Path Trans SM3 magnitude1']

            SMmid=max(SMlocal1)

            SMlocal2=[]
        ####################################################corner slab
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1): ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MIN_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude2' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM1' ), ), ), labelType=TRUE_DISTANCE_Z)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude2' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSM2)):
                    SMlocal2.append(dataSM2[i][1]-abs(dataSM3[i][1]))             ##Mario Plos mu=1 - = Top reinforcement 

                del session.xyDataObjects['Path Trans SM2 magnitude2'], session.xyDataObjects['Path Trans SM3 magnitude2']

            SMslab=min(SMlocal2)

            SMlocal22=[]
        ####################################################corner leg
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1): ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude2' , path=session.paths['Path Trans -0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM2' ), ), ), labelType=TRUE_DISTANCE_Z)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude2' , path=session.paths['Path Trans -0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSM2)):
                    SMlocal22.append(dataSM2[i][1]+abs(dataSM3[i][1]))          ##SM2 is positive here

                del session.xyDataObjects['Path Trans SM2 magnitude2'], session.xyDataObjects['Path Trans SM3 magnitude2']

            SMleg=max(SMlocal22)

            SMlocal3=[]
                                                                                    ##foot
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1): ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude3' , path=session.paths['Path Trans -height'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM2' ), ), ), labelType=TRUE_DISTANCE_Z)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude3' , path=session.paths['Path Trans -height'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSM2)):
                    SMlocal3.append(dataSM2[i][1]-abs(dataSM3[i][1]))             ## Negative moment here

                del session.xyDataObjects['Path Trans SM2 magnitude3'], session.xyDataObjects['Path Trans SM3 magnitude3']

            SMfoot=min(SMlocal3)
        ########################################################################


        ##############shear force


        ###########################################################
            SFlocal1=[]
                                                                                                        ##midspan
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF4=session.XYDataFromPath(name='Path Trans SF4 magnitude1' , path=session.paths['Path Trans L/2'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF4' ), ), ), labelType=TRUE_DISTANCE_Z)

                dataSF5=session.XYDataFromPath(name='Path Trans SF5 magnitude1' , path=session.paths['Path Trans L/2'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF5' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSF4)):
                    SFlocal1.append(sqrt((dataSF4[i][1])**2+(dataSF5[i][1])**2))##ACCORDING TO WSP CALCULATIONS

                del session.xyDataObjects['Path Trans SF4 magnitude1'], session.xyDataObjects['Path Trans SF5 magnitude1']

            SFmid=max(SFlocal1)
                                                                                                           ##corner slab
            SFlocal2=[]
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF4=session.XYDataFromPath(name='Path Trans SF4 magnitude2' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF4' ), ), ), labelType=TRUE_DISTANCE_Z)

                dataSF5=session.XYDataFromPath(name='Path Trans SF5 magnitude2' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF5' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSF4)):
                    SFlocal2.append(sqrt((dataSF4[i][1])**2+(dataSF5[i][1])**2))##ACCORDING TO WSP CALCULATIONS

                del session.xyDataObjects['Path Trans SF4 magnitude2'], session.xyDataObjects['Path Trans SF5 magnitude2']
            SFslab=max(SFlocal2)

            
                                                                                ##corner leg
            SFlocal3=[]
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF4=session.XYDataFromPath(name='Path Trans SF4 magnitude2' , path=session.paths['Path Trans -0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF4' ), ), ), labelType=TRUE_DISTANCE_Z)

                dataSF5=session.XYDataFromPath(name='Path Trans SF5 magnitude2' , path=session.paths['Path Trans -0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF5' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSF5)):
                    SFlocal3.append(sqrt((dataSF4[i][1])**2+(dataSF5[i][1])**2))##ACCORDING TO WSP CALCULATIONS ##solving bug in dataSF4

                del session.xyDataObjects['Path Trans SF4 magnitude2'], session.xyDataObjects['Path Trans SF5 magnitude2']
            SFleg=max(SFlocal3)



            SFlocal4=[]
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF4=session.XYDataFromPath(name='Path Trans SF4 magnitude' , path=session.paths['Path Trans -height'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF4' ), ), ), labelType=TRUE_DISTANCE_Z)

                dataSF5=session.XYDataFromPath(name='Path Trans SF5 magnitude' , path=session.paths['Path Trans -height'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF5' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSF4)):
                    SFlocal4.append(sqrt((dataSF4[i][1])**2+(dataSF5[i][1])**2))##ACCORDING TO WSP CALCULATIONS

                del session.xyDataObjects['Path Trans SF4 magnitude'], session.xyDataObjects['Path Trans SF5 magnitude']
            SFfoot=max(SFlocal4)
        ###########################################################
        ##moment SLS

        #########################################################


                                                                                            ##midspan
            SMSLSlocal1=[]
                                                            
            for i in xrange(0,LoadCombinations+1): ##SLS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude1' , path=session.paths['Path Trans L/2'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM1' ), ), ), labelType=TRUE_DISTANCE_Z)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude1' , path=session.paths['Path Trans L/2'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSM2)):
                    SMSLSlocal1.append(dataSM2[i][1]+abs(dataSM3[i][1]))             #Mario Plos mu=1

                del session.xyDataObjects['Path Trans SM2 magnitude1'], session.xyDataObjects['Path Trans SM3 magnitude1']

            SMSLSmid=max(SMSLSlocal1)

                                                                                    ##corner slab
            SMSLSlocal2=[]

            for i in xrange(0,LoadCombinations+1): ##SLS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude3' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM1' ), ), ), labelType=TRUE_DISTANCE_Z)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude3' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSM2)):
                    SMSLSlocal2.append(dataSM2[i][1]-abs(dataSM3[i][1]))             #Mario Plos mu=1

                del session.xyDataObjects['Path Trans SM2 magnitude3'], session.xyDataObjects['Path Trans SM3 magnitude3']

            SMSLSslab=min(SMSLSlocal2)



                                                                                        ##corner leg
            SMSLSlocal3=[]

            for i in xrange(0,LoadCombinations+1): ##SLS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude3' , path=session.paths['Path Trans -0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM1' ), ), ), labelType=TRUE_DISTANCE_Z)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude3' , path=session.paths['Path Trans -0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSM2)):
                    SMSLSlocal3.append(dataSM2[i][1]+abs(dataSM3[i][1]))             #Mario Plos mu=1

                del session.xyDataObjects['Path Trans SM2 magnitude3'], session.xyDataObjects['Path Trans SM3 magnitude3']

            SMSLSleg=max(SMSLSlocal3)


                                                                                   ##foot
            SMSLSlocal4=[]


            for i in xrange(0,LoadCombinations+1): ##SLS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude3' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM2' ), ), ), labelType=TRUE_DISTANCE_Z)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude3' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSM2)):
                    SMSLSlocal4.append(dataSM2[i][1]-abs(dataSM3[i][1]))             #Mario Plos mu=1

                del session.xyDataObjects['Path Trans SM2 magnitude3'], session.xyDataObjects['Path Trans SM3 magnitude3']

            SMSLSfoot=min(SMSLSlocal4)

        #########################################

        ########Normal force

        ########################################
                                                                                                    ##midspan

            SFNmaxlocal=[]

            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF1=session.XYDataFromPath(name='Path Trans SF1 mid' , path=session.paths['Path Trans L/2'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF1' ), ), ), labelType=TRUE_DISTANCE_Z)

                dataSF3=session.XYDataFromPath(name='Path Trans SF3 mid' , path=session.paths['Path Trans L/2'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSF1)):
                    SFNmaxlocal.append(dataSF1[i][1])#+dataSF3[i][1]) ##K=1

                del session.xyDataObjects['Path Trans SF1 mid'], session.xyDataObjects['Path Trans SF3 mid']
            SFNmid=min(SFNmaxlocal)


                                                                                    ##corner slab
            SFNmaxlocal=[]

            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF1=session.XYDataFromPath(name='Path Trans SF1 0' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF1' ), ), ), labelType=TRUE_DISTANCE_Z)

                dataSF3=session.XYDataFromPath(name='Path Trans SF3 0' , path=session.paths['Path Trans 0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSF1)):
                    SFNmaxlocal.append(dataSF1[i][1])#+dataSF3[i][1]) ##K=1

                del session.xyDataObjects['Path Trans SF1 mid'], session.xyDataObjects['Path Trans SF3 mid']
            SFNslab=min(SFNmaxlocal)

                                                                    ##corner leg

            SFNmaxlocal=[]

            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF2=session.XYDataFromPath(name='Path Trans SF2 -0' , path=session.paths['Path Trans -0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF2' ), ), ), labelType=TRUE_DISTANCE_Z)

                dataSF3=session.XYDataFromPath(name='Path Trans SF3 mid' , path=session.paths['Path Trans -0'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSF2)):
                    SFNmaxlocal.append(dataSF2[i][1])#+dataSF3[i][1]) ##K=1

                del session.xyDataObjects['Path Trans SF1 mid'], session.xyDataObjects['Path Trans SF3 mid']
            SFNleg=min(SFNmaxlocal)


                                                    ##foot
            SFNmaxlocal=[]

            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF2=session.XYDataFromPath(name='Path Trans SF2 -0' , path=session.paths['Path Trans -height'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF2' ), ), ), labelType=TRUE_DISTANCE_Z)

                dataSF3=session.XYDataFromPath(name='Path Trans SF3 mid' , path=session.paths['Path Trans -height'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF3' ), ), ), labelType=TRUE_DISTANCE_Z)

                for i in xrange (0,len(dataSF2)):
                    SFNmaxlocal.append(dataSF2[i][1])#+dataSF3[i][1]) ##K=1

                del session.xyDataObjects['Path Trans SF1 mid'], session.xyDataObjects['Path Trans SF3 mid']
            SFNfoot=min(SFNmaxlocal)




            ################################################


            ##data extraction longitudinal direction 


            ################################################
            """"
            SMlocal1=[]

            for i in xrange(LoadCombinations+1,2*LoadCombinations+1): ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSM2=session.XYDataFromPath(name='Path Trans SM2 magnitude1' , path=session.paths['Path Long Mid'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM2' ), ), ), labelType=TRUE_DISTANCE_Y)
                    
                dataSM3=session.XYDataFromPath(name='Path Trans SM3 magnitude1' , path=session.paths['Path Long Mid'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SM',INTEGRATION_POINT, ( (COMPONENT, 'SM3' ), ), ), labelType=TRUE_DISTANCE_Y)

                for i in xrange (0,len(dataSM2)):
                    SMlocal1.append(dataSM2[i][1]+dataSM3[i][1])             #Mario Plos mu=1
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        ##shear force

            SFmaxlocal=[]
            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF4=session.XYDataFromPath(name='Path Long SF4 magnitude' , path=session.paths['Path Long Mid'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF4' ), ), ), labelType=TRUE_DISTANCE_X)

                dataSF5=session.XYDataFromPath(name='Path Long SF5 magnitude' , path=session.paths['Path Long Mid'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF5' ), ), ), labelType=TRUE_DISTANCE_X)

                for i in xrange (0,len(dataSF4)):
                    SFmaxlocal.append(sqrt((dataSF4[i][1])**2+(dataSF5[i][1])**2))##ACCORDING TO WSP CALCULATIONS

                del session.xyDataObjects['Path Long SF4 magnitude'], session.xyDataObjects['Path Long SF5 magnitude']


            SF=(min(SFmaxlocal),max(SFmaxlocal))

            #########################NORMAL FORCE

            SFNmaxlocal=[]

            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF1=session.XYDataFromPath(name='Path Long SF1 magnitude' , path=session.paths['Path Long Mid'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF1' ), ), ), labelType=TRUE_DISTANCE_X)

                dataSF3=session.XYDataFromPath(name='Path Long SF3 magnitude' , path=session.paths['Path Long Mid'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF3' ), ), ), labelType=TRUE_DISTANCE_X)

                for i in xrange (0,len(dataSF1)):
                    SFNmaxlocal.append(dataSF1[i][1]+dataSF3[i][1]) ##K=1

                del session.xyDataObjects['Path Long SF1 magnitude'], session.xyDataObjects['Path Long SF3 magnitude']
            SFN=min(SFNmaxlocal)


        ##normal force leg

            SFNlocal=[]

            for i in xrange(LoadCombinations+1,2*LoadCombinations+1):           ##ULS
                session.viewports['Viewport: 1'].odbDisplay.basicOptions.setValues(sectionResults=USE_ENVELOPE, envelopeCriteria=MAX_VALUE)
                
                dataSF1=session.XYDataFromPath(name='Path LongLeg SF1 magnitude' , path=session.paths['Path Long Leg'], includeIntersections=True, 
                    shape=UNDEFORMED,frame=i,variable=('SF',INTEGRATION_POINT, ( (COMPONENT, 'SF2' ), ), ), labelType=TRUE_DISTANCE_Y)

                for i in xrange (0,len(dataSF1)):
                    SFNlocal.append(dataSF1[i][1])

                del session.xyDataObjects['Path LongLeg SF1 magnitude'], session.xyDataObjects['Path LongLeg SF3 magnitude']
            SFNleg=min(SFNlocal)

            """
            ##design of transversal reinforcement
            dtrans=thicknesslab-cover-diamslab/float(2)
            As_min_trans=max((0.26*fctm/float(fyk))*1*dtrans, 0.0013*1*dtrans) ##Values per meter
            As_trans_slab=As_min_trans*L*platewidth
            
            dtrans=thicknessleg-cover-diamslab/float(2)
            As_min_trans=max((0.26*fctm/float(fyk))*1*dtrans, 0.0013*1*dtrans) ##Values per meter
            As_trans_leg=As_min_trans*height*platewidth*2 ##two legs
            
            
            
            ##volume calculation for cost
            Vslab=thicknesslab*L*platewidth
            Vlegs=thicknesslab*height*2*platewidth
            Vbridge=Vslab+Vlegs
            contReg=0
            for r in range (1,5): ##four cutpostions
                insertpos=False 


                contdiam=0
                ##Bottom reinforcement design

                if r==1:                                                ##midspan
                    MEdSLS=SMSLSmid
                    MEd=SMmid
                    VEd=SFmid
                    NEd=-SFNmid## minus in abaqus is compression but compression is + in EC2
                    hbeam=thicknesslab
                    length=L/float(4)

                if r==2:                                                ##corner slab
                    MEdSLS=abs(SMSLSslab)
                    MEd=abs(SMslab)
                    VEd=SFslab
                    NEd=-SFNslab##compression
                    hbeam=thicknesslab
                    length=L/float(4)

                if r==3:                                             ##corner leg
                    MEdSLS=abs(SMSLSleg)
                    MEd=SMleg
                    VEd=SFleg
                    hbeam=thicknessleg
                    NEd=-SFNleg##compression
                    length=height/float(2)

                if r==4:                                                ##foot
                    MEdSLS=abs(SMSLSfoot)
                    MEd=abs(SMfoot)
                    VEd=SFfoot
                    NEd=-SFNfoot##compression
                    hbeam=thicknessleg
                    length=height/float(2)

                print('NEd= %s' %(NEd))
                print('MEd= %s' %(MEd))
                print('MEdSLS= %s' %(MEdSLS))
                print('VEd= %s' %(VEd))

                ##In case of more spans, negative moments might be detected and top reinforcement needed
                if MEd<0:
                    print('------------------------------------Negative moment has been detected, top reinforcement is needed------------------------------------------------------------')

                ###Variable extraction

                print('Effect moment%s'%(MEd))
                Reinforct[10]=NEd
                Reinforct[11]=VEd
                Reinforct[6]=MEd
                Reinforct[19]=MEdSLS

                    ##values used in export matrix

                Reinforct[0]=looplist[loop][0]
                Reinforct[1]=r   ##region where cut is done
                Reinforct[20]=As_trans_slab
                Reinforct[21]=As_trans_leg
                Reinforct[22]=length


                

                b=1 ## beam is calculated in 1 meter length
                effwidth=b-2*cover          ##diam stirrups included in cover

                alphaR=0.810 #=alpaSimplified stress-strain relationship C12/16-C50/60. Concrete Structures Compendium 2007:3, page 49
                betaR=0.416		#shrinkage factor
                epscu=0.0035	#sB126 ecu

                epsy=fyd/float(Es)	#sB60

                CRdc=0.18/float(gammac)

                k1v=0.15

                alphacw=1  #for non-prestressed structures

                ni1=0.6*(1-fck/float(250))
                Ac=b*hbeam

                alpha=pi/2
                theta=pi/4   #assumed a crack angle of 45

                rhowmin=0.08*sqrt(fcd)/float(fyd)    #Minimum ratio of shear reinforcement SS-EN 1992-1-1:2005 (E)
                Aswmin=1*rhowmin
                Asw=4*pi*diamstirrups*diamstirrups/4            ##possible with 4? two stirrups /m

                smin=Asw/float(Aswmin)

                ##calculations for beam
              #  for diam in diamrange:
                barspacing=max(diam*1,dg+0.05,0.02)##EC2 B121
                UR=101
                diammm=diam*1000
                Reinforct[3]=diammm
                print('Diameter of bars = %s mm' %(diammm))

                z=0.9*(hbeam-diam/float(2)-cover)			#???? thick=thickness of plate hei=height of beams (=0), botdist=cover+diamstirrups
                As= MEd*1.0/float(fyd*z)			#s.B115
                numbar=int(As/(pi*diam*diam/4))+1	#numbar = number of rebars
                As=numbar*pi*diam*diam/4				#Total area of rebars
                Asprim=max(numbar/4*pi*diam*diam/4,2*pi*diam*diam/4) ##atleast t
                calc=0

                while UR>100:
                   if calc>0:
                       print('One bar has been added!<-------------------------------------------------------')
                   numbar=numbar+calc
                   if diam*(((int((MEd/float(fyd*0.9*((hbeam-diam/float(2)-cover)-1.5*diam-barspacing)))/(pi*diam*diam/4))+1)+2)/3)+barspacing*(((int((MEd/float(fyd*0.9*((hbeam-diam/float(2)-cover)-1.5*diam-barspacing)))/(pi*diam*diam/4))+1)+2)/3-1)<effwidth: 	#barspacing=0,02	effwidth=witdh of partition (=2a+h)
                                                                                              
                       if diam*numbar+barspacing*(numbar-1)<effwidth:          ##If bars fit
                           ##1 LAYER
                                       print('One layer layout')
                                       layers=1
                                       Reinforct[4]=layers
                                       d=hbeam-cover-diam/float(2)
                                       dprim=cover+diam/float(2)
                                       As=numbar*pi*diam*diam/4
                                       print('As = %s' %(As))

                                       print('Number of bars = %s' %(numbar))

                                       x=(fyd*As-fyd*Asprim+NEd)/float(alphaR*fcd*b)
                                       print 'x=%s' %(x)
                                       if x < dprim:
                                            print 'x<dprim'
                                            failcause+='Tension in Top layer'
                                            break
                                       epss=((d-x)/float(x))*epscu	#s.B127 epscu=0.0035
                                       epssprim=((x-dprim/float(x))*epscu)
                                       ##Yielding check 
                                       if epss <epsy:
                                               print('Yielding assumption bottom layer not OK <-------------------------- ')	#epsy=sB60, epss=sB60
                                               yielding=0
                                               Reinforct[5]=yielding
                                               numbar=numbar-1
                                               As=numbar*pi*diam*diam/4
                                               Asprim=max(numbar/4*pi*diam*diam/4,2*pi*diam*diam/4)

                                               x=(fyd*As-fyd*Asprim+NEd)/float(alphaR*fcd*b)		#sB130, widthTsection=2a+h

                                               MRd=alphaR*fcd*b*x*(d-betaR*x)+fyd*Asprim*(d-dprim)-NEd(d-hbeam/float(2))
                                               Reinforct[2]=numbar+numbar/4
                                               Reinforct[7]=MRd
                                               ##If yielding is not happening, try to reduce one bar and see what happens
                                               print('Design moment (After reducing one bar) = %s MN.m' %(str(MRd)[:5]))
                                               UR=(MEd/MRd)*100
                                               Reinforct[8]=UR
                                               print('Utilization ratio (After reducing one bar) = %s%%' %(str(UR)[:4]))
                                               Asl=(numbar-1)*pi*diam*diam/4
                                               if UR>100:
                                                   
                                                   print('Reinforcement configuration is not suitable after reducing one bar <-------------------------')
                                                   break
                                                   
                                       ##check top layer not yielding
                                       elif epssprim<epsy:
                                               print 'Top layer not yieldning'
                                               x1=-((Es*epscu*Asprim-fyd*As-NEd)/float(alphaR*fcd*b))/float(2)+sqrt((((Es*epscu*Asprim-fyd*As-NEd)/float(alphaR*fcd*b))/float(2))**2-(-Es*epscu*Asprim*dprim)/float(alphaR*fcd*b))
                                               x2=-((Es*epscu*Asprim-fyd*As-NEd)/float(alphaR*fcd*b))/float(2)-sqrt((((Es*epscu*Asprim-fyd*As-NEd)/float(alphaR*fcd*b))/float(2))**2-(-Es*epscu*Asprim*dprim)/float(alphaR*fcd*b))
                                               
                                               x=max(x1,x2)
                                               print ('x=%s  ######################################################################' %(x))
                                               if x<dprim:
                                                 failcause+= 'Tension in top layer'
                                                 print 'x<dprim tension in top layer'
                                                 break
                                               epss=((d-x)/float(x))*epscu	#s.B127 epscu=0.0035
                                               epssprim=((x-dprim/float(x))*epscu)
                                               if epss > epsy and epssprim < epsy:
                                                    MRd=alphaR*fcd*b*x*(d-betaR*x)+(Es*(x-dprim)/float(x))*(epscu)*Asprim*(d-dprim)-NEd*(d-hbeam/float(2))	#sB112
                                                    Reinforct[7]=MRd
                                                    print('Yielding assumption OK after new equation were top layer not yielding')
                                                    yielding=1
                                                    Reinforct[5]=yielding
                                                    print('Design moment = %s MN.m' %(str(MRd)[:5]))
                                                    UR=(MEd/MRd)*100
                                                    Reinforct[8]=UR
                                                    Reinforct[2]=numbar+numbar/4
                                                    print('Utilization ratio = %s%%' %(str(UR)[:4]))
                                                    Asl=numbar*pi*diam*diam/4
                                                    if Asl<max((0.26*fctm/float(fyk))*b*d,0.0013*b*d):
                                                            print 'Reinforcment less then minimum accordning to EC'
                                                            break
                                               else:
                                                    print'design not suitable wth regards to yieldning'
                                                    failcause+='Not yielding'
                                                    yielding=0
                                                    Reinforct[5]=yielding
                                                    break
                                                    ##otherwise yielding happens
                                       elif epssprim>epsy and epss>epsy:
                                                    MRd=alphaR*fcd*b*x*(d-betaR*x)+fyd*Asprim*(d-dprim)-NEd*(d-hbeam/float(2))	#sB112
                                                    Reinforct[7]=MRd
                                                    print('Yielding assumption OK ---------------------------------')
                                                    yielding=1
                                                    Reinforct[5]=yielding
                                                    print('Design moment = %s MN.m' %(str(MRd)[:5]))
                                                    UR=(MEd/MRd)*100
                                                    Reinforct[8]=UR
                                                    Reinforct[2]=numbar+numbar/4
                                                    print('Utilization ratio = %s%%' %(str(UR)[:4]))
                                                    Asl=numbar*pi*diam*diam/4
                                                    if Asl<max((0.26*fctm/float(fyk))*b*d,0.0013*b*d):
                                                            print 'Reinforcment less then minimum accordning to EC'
                                                            break
                                                
                                       else:
                                            print'nothing yielding dont bother'
                                            failcause+='Not yielding'
                                            break
                                                
                                                
                                                ##crack width check, part 2 b293
                                       Fs=MEdSLS/(d-betaR*x)       ##Crack width is checked for SLS 
                                       sigmas=Fs/Asl
                                       kt=0.4                      ##For long term (0.6 for short term)
                                       fcteff=fctm
                                       h=hbeam
                                       alphae=Es/float(Ecm)
                                       hcef=min(2.5*(h-d),(h-x)/float(3),h/float(2))
                                       Acef=b*hcef
                                       rhopeff=Asl/Acef
                                       DeltaEps=max((sigmas-kt*(fcteff/float(rhopeff))*(1+alphae*rhopeff))/float(Es),0.6*(sigmas/float(Es)))
                                       k3=3.4     
                                       k1=0.8
                                       k2=0.5##h0.5 vid ren bojning har vi??
                                       k4=0.425
                                       srmax=k3*cover+k1*k2*k4*(diam/float(rhopeff))
                                       wk=srmax*DeltaEps
                                       wmax=0.0003
                                       checkCrack=(wk<wmax)
                                       Reinforct[17]=wk*1000   #in mm
                                       Reinforct[18]=checkCrack
                                       if checkCrack==False:
                                               print 'failed cause of crackwidth'
                                               failcause+='Crack '
                                       print(wk,checkCrack)
                                       k=min(1+sqrt(200/float(d*1000)),2)
                                       k=min(1+sqrt(200/float(d*1000)),2)
                                       rhol=min(Asl/(float(b*d)),0.02)
                                       sigmacp=min(NEd/float(Ac),0.2*fcd)

                                #######SHEAR CALCULATIONS livtryckbrott sB194


                                       VRdc=(CRdc*k*(100*rhol*fck)**(1/float(3))+k1v*sigmacp)*b*d
                                       vmin=0.035*k**(3/float(2))*fck**(1/float(2))
                                       VRdcmin=(vmin+k1v*sigmacp)*b*d
                                       VRdc=max(VRdc,VRdcmin)
                                       Reinforct[12]=VRdc
                                       

                                       
                                       if VRdc<VEd:
                                           VRdmax=alphacw*b*0.9*d*ni1*fcd/float(tan(theta)+1/float(tan(theta)))
                                           s=Asw*fyd*0.9*d*1/float((tan(theta)*VEd))            ##b203
                                           
                                                                            
                                           s=min(s,smin)

                                           smax=0.75*d*(1+1/float(tan(theta)))

                                           s=min(s,smax)*1000                                             #In mm
                                           s=int(s/100)*100                                               # In 100,200,300mm....
                                           if s<100:
                                                   failcause+='Stirrups separation '
                                           Reinforct[13]=s
                                           if s!=0:
                                               VRds=Asw*0.9*d*fyd*(1/float(tan(theta)))/float(s/float(1000))
                                               VRds=min(VRds,VRdmax)
                                               URv=VEd/VRds
                                           else:
                                               VRds=0
                                               URv=VEd/VRdc
                                           Reinforct[14]=VRds
                                           
                                           
                                           Reinforct[15]=URv
                                           print('Shear reinforcement is required at this section')
                                           print('Spacing between bars is %s and diameter of bars=%s'%(s,diamstirrups))
                                           
                                       else:
                                           s=100
                                           VRds=0
                                           Reinforct[14]=VRds
                                           Reinforct[13]='No stirrups needed'
                                           URv=VEd/VRdc
                                           Reinforct[15]=URv
                                           print('Shear reinforcement is not required at this section')
                       else:
                       
                       #################################################
                       ##                   Two layer layout
                       ###############################################
                       
                       
                       
                           #if diam*(((int((MEd/float(fyd*0.9*(dprov-diam-barspacing/float(2))))/(pi*diam*diam/4))+1+calc)+1)/2)+barspacing*(((int((MEd/float(fyd*0.9*(dprov-diam-barspacing/float(2))))/(pi*diam*diam/4))+1+calc)+1)/2-1)<effwidth:
                               ##2 LAYERS
                               
                               d1=hbeam-cover-diam/float(2)
                               d2=d1-barspacing-diam
                               d=(d1+d2)/float(2)
                               dprim=cover+diam/float(2)
                               
                                                                                       
                               print('Two layer layout')
                               layers=2
                               Reinforct[4]=layers
                               #z=0.9*(thicknesslab-diam/float(2)-cover)			#???? thick=thickness of plate hei=height of beams (=0), botdist=cover+diamstirrups
                               As= MEd*1.0/float(fyd*0.9*d)			#s.B115
                               numbar=int(As/(pi*diam*diam/4))+calc+1	#numbar = number of rebars
                               As=numbar*pi*diam*diam/4				#Total area of rebars
                               Asprim=max(numbar/4*pi*diam*diam/4,2*pi*diam*diam/4)
                               print('Number of bars = %s' %(numbar))
                               print('As = %s' %(As))

                               x=(fyd*As-fyd*Asprim+NEd)/float(alphaR*fcd*b)
                               print 'x=%s' %(x)
                               if x < dprim:
                                    print 'x<dprim'
                                    failcause+= 'Tension in top layer'
                                    break
                               epss=((d2-x)/float(x))*epscu	 #s.B127 epscu=0.0035
                               epssprim=((x-dprim/float(x))*epscu)



                               if epss <epsy and epssprim>epsy: ##top layer yielding bottom doesnt
                                       print('Yielding assumption bottom layer not OK <-------------------------- ')	#epsy=sB60, epss=sB60
                                       yielding=0
                                       Reinforct[5]=yielding
                                       numbar=numbar-1
                                       As=numbar*pi*diam*diam/4
                                       Asprim=max(numbar/4*pi*diam*diam/4,2*pi*diam*diam/4)
                                       x=(fyd*As-fyd*Asprim+NEd)/float(alphaR*fcd*b)		#sB130, widthTsection=2a+h
                                       MRd=alphaR*fcd*b*x*(d-betaR*x)+fyd*Asprim*(d-dprim)-NEd(d-hbeam/float(2))
                                       Reinforct[2]=numbar+numbar/4
                                       Reinforct[7]=MRd
                                       ##If yielding is not happening, try to reduce one bar and see what happens
                                       print('Design moment (After reducing one bar) = %s MN.m' %(str(MRd)[:5]))
                                       UR=(MEd/MRd)*100
                                       Reinforct[8]=UR
                                       print('Utilization ratio (After reducing one bar) = %s%%' %(str(UR)[:4]))
                                       Asl=(numbar-1)*pi*diam*diam/4
                                       if UR>100:
                                           
                                           print('Reinforcement configuration is not suitable after reducing one bar <-------------------------')
                                           break
                               elif epssprim<epsy and epss>epsy: ##bottom layer yieldin top doesnt
                                               print 'Top layer not yielding'
                                               x1=-((Es*epscu*Asprim-fyd*As-NEd)/float(alphaR*fcd*b))/float(2)+sqrt((((Es*epscu*Asprim-fyd*As-NEd)/float(alphaR*fcd*b))/float(2))**2-(-Es*epscu*Asprim*dprim)/float(alphaR*fcd*b)) ##new equation for x
                                               x2=-((Es*epscu*Asprim-fyd*As-NEd)/float(alphaR*fcd*b))/float(2)-sqrt((((Es*epscu*Asprim-fyd*As-NEd)/float(alphaR*fcd*b))/float(2))**2-(-Es*epscu*Asprim*dprim)/float(alphaR*fcd*b))
                                               
                                               x=max(x1,x2)
                                               print ('x=%s  ######################################################################' %(x))
                                               if x<dprim:
                                                 print 'x<dprim tension in top layer'
                                                 failcause+= 'Tension in top layer'
                                                 break
                                               epss=((d-x)/float(x))*epscu	#s.B127 epscu=0.0035
                                               epssprim=((x-dprim/float(x))*epscu)
                                               if epss > epsy and epssprim < epsy:
                                                    MRd=alphaR*fcd*b*x*(d-betaR*x)+(Es*(x-dprim)/float(x))*(epscu)*Asprim*(d-dprim)-NEd*(d-hbeam/float(2))	#sB112
                                                    Reinforct[7]=MRd
                                                    print('Yielding assumption OK')
                                                    yielding=1
                                                    Reinforct[5]=yielding
                                                    print('Design moment = %s MN.m' %(str(MRd)[:5]))
                                                    UR=(MEd/MRd)*100
                                                    Reinforct[8]=UR
                                                    Reinforct[2]=numbar+numbar/4
                                                    print('Utilization ratio = %s%%' %(str(UR)[:4]))
                                                    Asl=numbar*pi*diam*diam/4
                                                    if Asl<max((0.26*fctm/float(fyk))*b*d,0.0013*b*d):
                                                            print 'Reinforcment less then minimum accordning to EC'
                                                            break
                                               else:
                                                    print'design not suitable with regards to yielding'
                                                    failcause+='Not yielding'
                                                    break
                               elif epssprim>epsy and epss>epsy:
                                                    MRd=alphaR*fcd*b*x*(d-betaR*x)+fyd*Asprim*(d-dprim)-NEd*(d-hbeam/float(2))	#sB112
                                                    Reinforct[8]=MRd
                                                    print('Yielding assumption OK ---------------------------------')
                                                    yielding=1
                                                    Reinforct[5]=yielding
                                                    print('Design moment = %s MN.m' %(str(MRd)[:5]))
                                                    UR=(MEd/MRd)*100
                                                    Reinforct[8]=UR
                                                    Reinforct[2]=numbar+numbar/4
                                                    print('Utilization ratio = %s%%' %(str(UR)[:4]))
                                                    Asl=numbar*pi*diam*diam/4
                                                    if Asl<max((0.26*fctm/float(fyk))*b*d,0.0013*b*d):
                                                            print 'Reinforcment less then minimum accordning to EC'
                                                            break
                               
                               else:
                                    print'nothing yielding dont bother'
                                    failcause+='Not yielding'
                                    break
                               ## Crack width check 
                               Fs=MEdSLS/(d-betaR*x)       ##Crack width is checked for SLS 
                               sigmas=Fs/Asl
                               kt=0.4                      ##For long term (0.6 for short term)
                               fcteff=fctm
                               h=hbeam
                               alphae=Es/float(Ecm)
                               hcef=min(2.5*(h-d),(h-x)/float(3),h/float(2))
                               Acef=b*hcef
                               rhopeff=Asl/Acef
                               DeltaEps=max((sigmas-kt*(fcteff/float(rhopeff))*(1+alphae*rhopeff))/float(Es),0.6*(sigmas/float(Es)))
                               k3=3.4     
                               k1=0.8
                               k2=0.5##h0.5 vid ren bojning har vi??
                               k4=0.425
                               srmax=k3*cover+k1*k2*k4*(diam/float(rhopeff))
                               wk=srmax*DeltaEps
                               wmax=0.0003
                               checkCrack=(wk<wmax)
                               Reinforct[17]=wk*1000   #in mm
                               Reinforct[18]=checkCrack
                               if checkCrack==False:
                                       print 'failed cause of crackwidth'
                                       failcause+='Crack '
                               print(wk,checkCrack)
                               k=min(1+sqrt(200/float(d*1000)),2)
                               k=min(1+sqrt(200/float(d*1000)),2)
                               rhol=min(Asl/(float(b*d)),0.02)
                               sigmacp=min(NEd/float(Ac),0.2*fcd)

                        #######SHEAR CALCULATIONS livtryckbrott sB194


                               VRdc=(CRdc*k*(100*rhol*fck)**(1/float(3))+k1v*sigmacp)*b*d
                               vmin=0.035*k**(3/float(2))*fck**(1/float(2))
                               VRdcmin=(vmin+k1v*sigmacp)*b*d
                               VRdc=max(VRdc,VRdcmin)
                               Reinforct[12]=VRdc
                               

                               
                               if VRdc<VEd:
                                   VRdmax=alphacw*b*0.9*d*ni1*fcd/float(tan(theta)+1/float(tan(theta)))
                                   s=Asw*fyd*0.9*d*1/float((tan(theta)*VEd))
                                   
                                                                    
                                   s=min(s,smin)

                                   smax=0.75*d*(1+1/float(tan(theta)))

                                   s=min(s,smax)*1000                                             #In mm
                                   s=int(s/100)*100                                               # In 100,200,300mm....
                                   if s<100:
                                           failcause+= 'Stirrups separation '
                                   Reinforct[13]=s
                                   if s!=0:
                                       VRds=Asw*0.9*d*fyd*(1/float(tan(theta)))/float(s/float(1000))
                                       VRds=min(VRds,VRdmax)
                                       URv=VEd/VRds
                                   else:
                                       VRds=0
                                       URv=VEd/VRdc
                                   Reinforct[14]=VRds
                                   
                                   
                                   Reinforct[15]=URv
                                   print('Shear reinforcement is required at this section')
                                   print('Spacing between bars is %s and diameter of bars=%s'%(s,diamstirrups))
                                   
                               else:
                                   s=100
                                   VRds=0
                                   Reinforct[14]=VRds
                                   Reinforct[13]='No stirrups needed'
                                   URv=VEd/VRdc
                                   Reinforct[15]=URv
                                   print('Shear reinforcement is not required at this section')
                                                              #After the design,  store only if UR<100, s>100mm and crack witdh is acceptable
                       if UR<=100 and s>=100 and checkCrack==True:
                           duct=x/float(d)
                           Reinforct[9]=duct
                           
                       ##Check ductility as well   
                           if fck>=55:
                               if duct<=0.35:
                                   contReg=contReg+1
                                   insertpos=True
                                   Reinforct[20]=(max(Asl/float(5),(0.26*fctm/float(fyk))*1*d, 0.0013*1*d))*platewidth*L ##EN-1992-1-1:2005 section 9.3.1.1 states that 20% of main reinforcement should be put in secondary reinforccment
                                   Reinforct[21]=max(Asl/(5),(0.26*fctm/float(fyk))*1*d, 0.0013*1*d)*platewidth*height
                                   Reinforc1.append(Reinforct[:])
                                   
                               else:
                                   failcause+='Ductibility '
                                   print('Not enough ductibility')
                           else:
                               if duct<=0.45:
                                   contReg=contReg+1
                                   insertpos=True
                                   Reinforct[20]=max(Asl/float(5),(0.26*fctm/float(fyk))*1*d, 0.0013*1*d)*platewidth*L
                                   Reinforct[21]=max(Asl/float(5),(0.26*fctm/float(fyk))*1*d, 0.0013*1*d)*platewidth*L
                                   Reinforc1.append(Reinforct[:])
                                   
                               else:
                                   failcause+='Ductibility '
                                   print('Not enough ductibility')

                   else:  ##Otherwise, reject the analysis   
                       MRd=0
                       duct=0
                       print('Reinforcement configuration is not suitable')
                       contdiam+=1
                       #if contdiam==len(diamrange):
                       failcause+='Fitting of bars '
                       if UR!=101:
                           print('Tried with more bars but they dont fit')
                       break
                       
                   calc=calc+1
                    
        Failmatrixv=[looplist[loop][0],failcause,diam]
        Failmatrix.append(Failmatrixv)
                ##Create a matrix to assist optimization process

        if contReg==4:
                print ' sutiable' ##remove
                Reinforc.extend(Reinforc1)
                Positionv[0]=looplist[loop][0]
                Positionv[1]=diam
                Positionv[2]=contReg
                Position.append(Positionv[:])


        ##data for convergence
        ConvMEd.append(MEd)
        Convdef.append(deflection)
        Convelements.append(numofelements)


        odb.close() ##to avoid lock file error
        del myModel
        elapsed_time_loop = time.time () - starting_point_loop
        elapsed_time_sofar = time.time () - starting_point_total
        estimationtime=(elapsed_time_sofar/float(jobnumber))*jobsremaining
        print '---------------------------------------------Time elapsed in last bridge t=%ss--------------------------------------------------------------' %(int(elapsed_time_loop))    
        print '---------------------------------------------Total time elapsed so far t=%ss--------------------------------------------------------------' %(int(elapsed_time_sofar))
        print '---------------------------------------------Estimated remaining time t=%ss--------------------------------------------------------------' %(int(estimationtime))










elapsed_time = time.time () - starting_point_total	                                             ##Compute the time that took the whole process
totaltime = int(elapsed_time)                                                                           ##Number of seconds
totaltimemin = totaltime / 60                                                                               ##Time in minutes

FIRSTC=['TAG','Reason','Diam']
Failmatrix.insert(0,FIRSTC)
resultFile = open("Failmatrix%s.csv"  %(portionnumber),'wb')
wr = csv.writer(resultFile, dialect='excel')
wr.writerows(Failmatrix)

##Save results into files to be loaded during the optimization process
pickle.dump(looplist[:], open('Inputspart%s.p' %(portionnumber),'wb'))
pickle.dump(Reinforc[:], open('Reinforc%s.p' %(portionnumber),'wb'))
pickle.dump(Position[:], open('Position%s.p' %(portionnumber),'wb'))


