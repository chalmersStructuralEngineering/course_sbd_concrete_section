import pickle        #imports the neccesary functions for writing and reading files
import csv             #imports the necessary functions for creating cvs (excel) files

priceconcrete=1000         #price of concrete per m3
pricesteel=10000           #price of steel per tonne

StirrupDiam=12                  # stirrups diameter (mm)
steeldensity=7.8                # reinforcing steel density (tonne/m3)    

optimethod= 0   #0 means only considering ONE rebar diameter for the whole bridge, 1 means cheapest bridge no matters whether the beams have the same rebar diameter
numberofruns=5 #Number of jobs the loop is divided in

#CO2
CO2SteelW=830     #Kg CO2 per tonne
CO2ConcreteV=360    #Kg C02 per m3


#################################################  Which output data do you want ?     1 MEANS YES           #######################################################

InputsEXCEL=1                                  #Table containing information about the input parameters of every bridge
GlobalEXCEL=1                                  #Table containing  full information about  every bridge
CheckedGlobalEXCEL=1                            #Table containing  full information about  every bridge which has been selected as feasible
CostEXCEL=1                                     #Table containing  beam costs for every feasible diameter

###################################################################################################################################
    
Position=[]                 #Initialized matrix to store the different fragments of Position [TAG of the bridge | TAG og the beam | Number of feasible reinforcement designs within that beam]
for run in xrange(0,numberofruns):
    Positiontemp=pickle.load(open('Position%s.p'%(run)))
    for i in range (len(Positiontemp)):                               #Merges the different fragments of Position
        Position.append(Positiontemp[i][:])
          
print ('Position Matrix succesfully imported')   
Reinforc=[]             #Initialized matrix to store the different fragments of Reinforc

for run in xrange(0,numberofruns):
    Reinforctemp=pickle.load(open('Reinforc%s.p'%(run)))
    for i in range (len(Reinforctemp)):                                #Merges the different fragments of Reinforc
        Reinforc.append(Reinforctemp[i][:])
   
print ('Reinforc Matrix succesfully imported')
Inputs=[]                   #Initialized matrix to store the different fragments of Inputs

for run in xrange(0,numberofruns):
    Jobparttemp=pickle.load(open('Inputspart%s.p'%(run)))
    for i in range (len(Jobparttemp)):                                     #Merges the different fragments of Inputs
        Inputs.append(Jobparttemp[i][:])

print ('Geometry Matrix succesfully imported')  

Sortedinputs=[]                                 # for computing issues, having the TAGs of bridges in their corresponding position is prefered (TAG=45 i=45)
inputspos=0
for i in xrange (0,Inputs[-1][0]+1):            # for doing that, the positions where there are not bridges are filled with zeros-rows
    if Inputs[inputspos][0]==i:
        
        Sortedinputs.append(Inputs[inputspos])
        inputspos=inputspos+1
    else:
        Sortedinputs.append([0,0,0,0,0,0,0])
   
    
Global =[[0]*40 for i in range(len(Reinforc))]                  #Matrix containing information about Inputs, Reinforcement Design and Unit costs
for i in xrange (0,len(Reinforc)):
    Global[i][0]=Reinforc[i][0]                                              # TAG of the Bridge
    Global[i][1]=Sortedinputs[Reinforc[i][0]][6]                             # BC (m)
    Global[i][2]=Sortedinputs[Reinforc[i][0]][1]                             # Plate thickness (m)
    Global[i][3]=Sortedinputs[Reinforc[i][0]][2]                             # Beam thickness (width) (m)
    Global[i][4]=Sortedinputs[Reinforc[i][0]][3]                             # Beam height (m)
    Global[i][5]=Sortedinputs[Reinforc[i][0]][4]                             # Cantilever distance (m)
    Global[i][6]=Reinforc[i][20]                                             # Width T section (m)
    Global[i][7]=Reinforc[i][21]                                             # Effective width T section (m)
    Global[i][8]=Sortedinputs[Reinforc[i][0]][5]                             # Number of beams
    Global[i][9]=Reinforc[i][1]                                              # TAG of the beam (0=cantilever beam, 1, 2..)
    Global[i][10]=Reinforc[i][2]                                             # TAG of the region (1=support, 2,3,..)
    Global[i][11]=Reinforc[i][3]                                             # Starting longitudinal position of the region (m)
    Global[i][12]=Reinforc[i][4]                                             # Final longitudinal position of the region (m)
    Global[i][13]=Reinforc[i][5]                                             # Length of the region (m)
    Global[i][14]=Reinforc[i][6]                                             # Number of rebars needed for carrying the bending moment within that region
    Global[i][15]=Reinforc[i][7]                                             # Diameter of those rebars
    Global[i][16]=Reinforc[i][8]                                             # Number of layers of rebars
    Global[i][17]=Reinforc[i][9]                                             # Yielding check (0=No, 1=Yes)
    Global[i][18]=Reinforc[i][10]                                            # Design effect bending moment in ULS(MNm)
    Global[i][19]=Reinforc[i][11]                                            # Design resistant bending moment (MNm)
    Global[i][20]=Reinforc[i][12]                                            # Utilisation ratio for bending moment
    Global[i][21]=Reinforc[i][13]                                            # Ductility ratio
    Global[i][22]=Reinforc[i][14]                                            # Design effect normal force in ULS (MN)
    Global[i][23]=Reinforc[i][15]                                            # Design effect shear force in ULS (MN) (abs)
    Global[i][24]=Reinforc[i][16]                                            # Design resistant shear force considering only the concrete shear strength (MN) 
    Global[i][25]=Reinforc[i][17]                                            # Separation of stirrups in case they are needed (mm)
    Global[i][26]=Reinforc[i][18]                                            # Design resistant shear force of the shear reinforcement (MN)
    Global[i][27]=Reinforc[i][19]                                            # Utilisation ratio for shear force
    Global[i][28]=Reinforc[i][24]                                            # Design effect bending moment in SLS(MNm) (MNm) 
    Global[i][29]=Reinforc[i][22]                                            # Crack width (mm) 
    Global[i][30]=Reinforc[i][23]                                            # Crack width check 
    if Global[i][25]=='No stirrups needed':
        Global[i][31]=Global[i][13]*(Global[i][6]*Global[i][2]+Global[i][3]*Global[i][4]-pi*Global[i][14]*Global[i][15]*Global[i][15]/float(4000000))    #Concrete volume per region (m3)
        Global[i][32]=Global[i][13]*pi*Global[i][14]*Global[i][15]*Global[i][15]/float(4000000)                                                          #Steel volume per region (m3)  
    else:    
        Global[i][31]=Global[i][13]*(Global[i][6]*Global[i][2]+Global[i][3]*Global[i][4]-pi*Global[i][14]*Global[i][15]*Global[i][15]/float(4000000))-(Global[i][13]*1000/Global[i][25])*(2*Global[i][3]+2*Global[i][4])*(StirrupDiam*StirrupDiam/float(4000000))    #Concrete volume per region (m3)
        Global[i][32]=Global[i][13]*pi*Global[i][14]*Global[i][15]*Global[i][15]/float(4000000)+(Global[i][13]*1000/Global[i][25])*(2*Global[i][3]+2*Global[i][4])*(StirrupDiam*StirrupDiam/float(4000000)) #Steel volume per region (m3)  
    Global[i][33]=Global[i][32]*steeldensity                      #Steel weigth per region (tonne)
    Global[i][34]=Global[i][31]*priceconcrete                   # Concrete cost per region (SEK)
    Global[i][35]=Global[i][33]*pricesteel                          # Steel cost per region (SEK)
    Global[i][36]=Global[i][34]+Global[i][35]                    # Total cost per region (SEK)
    Global[i][37]=Reinforc[i][25]                               #Volume of steel from slab reinforcement
    Global[i][38]=Global[i][33]*CO2SteelW+Global[i][31]*CO2ConcreteV
    Global[i][39]=Sortedinputs[Reinforc[i][0]][7] #Span
print ('Global Matrix succesfully Built')

############################################################################################################################################
# As happened before with Inputs,since some bridges are dismissed in the analysis file, the Position matrix needs to be assessed in terms of TAGS
# This subprogramme stores in the matrix PosPosition, the i-position when the Position matrix switches to a different bridge


PosPositionv=[Position[0][0],0]         # The first position is introduced by hand
PosPosition=[]                          
PosPosition.append(PosPositionv[:])


for i in xrange(1,len(Position)):

    if Position[i][0]!=Position[i-1][0] :    # Every time the TAG changes in the matrix Position, the i-position is stored in PosPosition as well as the TAG of the bridge
        PosPositionv[0]=Position[i][0]
        PosPositionv[1]=i        
        PosPosition.append(PosPositionv[:])

PosPositionv[0]=Position[-1][0]              # The last position is also introduced by hand
PosPositionv[1]=len(Position)
PosPosition.append(PosPositionv[:])   

###############################################################################################################################################
#TAGPOS stores information about the boundary positions of the different bridges (TAGs) within the matrix Global.
#[ TAG of the Bridge | starting position | final position | Number of beams | No of combinations  beam-regions]
         
                                                     

numTAG=len(set([row[0] for row in Global]))-1       #No of Bridges (TAGs), the -1 is due to lists start in 0

TAGPOS=[[0]*5 for i in range(numTAG+1)]             #Initialised TAGPOS according to number of bridges, in this case the range has to be increased one position

TAGPOS[0][0]=Global[0][0]                           #The first and last positions are included manually
TAGPOS[0][1]=0

TAGPOS[numTAG][2]=len(Global)-1
TAGPOS[numTAG][0]=Global[-1][0]
TAGPOS[numTAG][3]=Global[len(Global)-1][8]
contTAG=0


for i in xrange(1,len(Global)):                                         #Loop to assign the corresponding values to TAGPOS
                if Global[i][0]!=Global[i-1][0]:
                    
                    TAGPOS[contTAG][2]=i-1
                    TAGPOS[contTAG][3]=Global[i-1][8]
                    TAGPOS[contTAG+1][0]=Global[i][0]
                    TAGPOS[contTAG+1][1]=i
                    contTAG=contTAG+1



                 

###############################################################################################################################################
# Loop for storing the different combinations of Beam-Region used later on for completing the matrix TAGPOS

RegBeam=[0]*len(Global)
for i in xrange(0,len(Global)):
    RegBeamA=[Global[i][9], Global[i][10]]
    RegBeam[i]=RegBeamA

###############################################################################################################################################
#This subprogramme decides which bridges are feasible and stores their data and the boundary position of them as
#in TAGPOS but only for the chosen ones. A feasible bridge means it has possible designs in every region.    
#CheckedGlobal has the same structure as Global. (It might happen that a bridge passes this filter but then some of the regions is not designed for a certain diameter, however there is a final check in BridgeCost)
#CheckedPosition has the same structure as Position  [TAG of the Bridge | Tag of the beam | No of feasible reinforcement designs]
                    
numreg=len(set([row[10] for row in Global]))                #Number of analised regions

CheckedGlobal=[]                                            #Initialised matrix for feasible bridges
CheckedPosition=[]                                          #Initialised matrix for position of feasible bridges 

for i in xrange(0,len(TAGPOS)):

    IniPosT=PosPosition[i][1]                               # This variables define the boundaries of each TAG bridge in the matrix Position, using the new matrix PosPosition
    FinPosT=PosPosition[i+1][1]
                                           
   
    TAGPOS[i][4]=len([list(x) for x in set(tuple(x) for x in RegBeam[TAGPOS[i][1]:TAGPOS[i][2]+1])])   #Stores in TAGPOS the No of combinations  beam-regions per Bridge
    
    if TAGPOS[i][4]==numreg*((TAGPOS[i][3]+1)/2):                           #Checks if the No of combinations beam-region is the minimum and hence there are feasible designs for every region
        for j in xrange(TAGPOS[i][1],TAGPOS[i][2]+1):
            CheckedGlobal.append(Global[j])                                 #Stores the data of the feasible bridge
        
        for k in xrange(IniPosT,FinPosT):
            
            CheckedPosition.append(Position[k])                             #Stores the position of the feasible bridge
    else:
        print('Bridge Discarded')
        print(TAGPOS[i][0])
                                                       # For each bridge, IniPosT is updated with the previous final position                                                    
    
   
   
print ('Unfeasible bridges succesfully Discarded')

###############################################################################################################################################
#This subprogramme calculates the cost of the different beams by combining the costs of the different regions within each beam considering same rebar diameter within each beam
#Cost [TAG of the Bridge | TAG of the beam | Rebar diameter | Cost of the beam]

Cost=[]                                 # Initialised Cost matrix
Costv=[0,0,0,0,0,0]                         # This list (vector) contains the local data which is then stored in Cost 
IniPosB=0                               # Initial beam position


for i in xrange(0,len(CheckedPosition)):
    
        
                for diam in list(set([row[15] for row in CheckedGlobal])):          # Loop for all the different diameters included in the analysis
                    contRegD=0                                                      # Counter for checking whether is possible to design a whole beam with the same rebar diameter 
                    costBeam=0                                                      # Initialising the beam cost every time the loop switches to a new diameter  
                    CO2Beam=0
                    
                    for diamReg in xrange(0,CheckedPosition[i][2]):                     # Loop to consider the data of bridges within a particular beam

                         if CheckedGlobal[diamReg+IniPosB][15]==diam:                   # If the rebar diameter considered is equal to the rebar diameter of that data...

                            costBeam=costBeam+CheckedGlobal[diamReg+IniPosB][36]        # The cost of that region is added to the beam cost
                            CO2Beam=CO2Beam+CheckedGlobal[diamReg+IniPosB][38]
                            contRegD=contRegD+1                                         # The counter is increased
                            span=CheckedGlobal[diamReg+IniPosB][39]
        
                    if contRegD==len(set([row[10] for row in CheckedGlobal])):          # If the counter is equal to the number of analised regions, which means there is a feasible design with that diameter for the whole beam...
            
                        
                        Costv[0]=CheckedPosition[i][0]                                              # Includes the TAG of the bridge
                        Costv[1]=CheckedPosition[i][1]                                              # Includes the Tag of the beam
                        Costv[2]=diam                                                               # Includes the considered diameter
                        Costv[3]=costBeam                                                           # Includes the cost of that beam for that diameter
                        Costv[4]=CO2Beam
                        Costv[5]=span    #Span length
                        Cost.append(Costv[:])                                                       # Adds the local data to the global Cost matrix
                        
    
                IniPosB=IniPosB+CheckedPosition[i][2]                         # The initial beam position is updated

print ('Cost calculation of beams by combination of region costs with same rebar diameter succefully completed')                            

###############################################################################################################################################
#Calculation of bridge costs by two different methods, first considering same rebar diameter for all beams, second considering cheapest beam regardless rebar diameter of the other beams

if optimethod==0:                                           # This subprogramme calculates the bridge cost by considering same rebar diameter for all beams of the bridge
    
            CostPosition=[]                                 # This matrix contains the bridge TAG and initial position for the data related with that TAG in the matrix Cost, this allows assessing the bridges separetly [TAG of the bridge | Initial position of the data in Cost related to this TAG]
            CostPositionv=[Cost[0][0],0]                    # Local values of CostPosition
            CostPosition.append(CostPositionv[:])


            for i in xrange(1,len(Cost)):

                if Cost[i][0]!=Cost[i-1][0]:
                    CostPositionv[0]=Cost[i][0]
                    CostPositionv[1]=i
                    CostPosition.append(CostPositionv[:])

            CostPositionv[0]=Cost[-1][0]
            CostPositionv[1]=len(Cost)
            CostPosition.append(CostPositionv[:])



            CostDiam=[]    #This matrix contains the beam cost for the different feasible diameters used for reinforcing the bridge [TAG of the bridge | TAG of the beam | Rebar Diameter | Beam cost]
                                      # Feasible diameter means it can be used for all the beams

            for i in xrange(0,len(CostPosition)-1):
                for diam in list(set([row[15] for row in CheckedGlobal])):

                        contdiam=0                                                # Counter for checking whether this diameter can be used for all the beams of the bridge or not
                        Costauxpos=[]                                             # Stores the i-position of the rows in Cost for that diameter
                        
                        for j in xrange(CostPosition[i][1],CostPosition[i+1][1]):

                            if  Cost[j][2]==diam:                               #If the loop finds a row in Cost for that bridge which that diameter, the counter increases
                                contdiam=contdiam+1
                                Costauxpos.append(j)

                        if contdiam==(Sortedinputs[CostPosition[i][0]][5]+1)/2:           #If the counter is equal to the number of beams of the bridge, the diameter is considered as feasible and the cost for all those beams stored in CostDiam
                            for k in Costauxpos:
                                CostDiam.append(Cost[k])

            print ('Optimal Cost calculation at beam level succefully completed')
                            
            CostDiamPosition=[]     #This matrix contains the position of the bridges for a particular diameter, it works as the previous ones for storing positions [TAG of the bridge | Rebar Diameter | Initial position for that bridge and diameter]
            CostDiamPositionv=[CostDiam[0][0],CostDiam[0][2],0]
            CostDiamPosition.append(CostDiamPositionv[:])


            for i in xrange(1,len(CostDiam)):

                if CostDiam[i][2]!=CostDiam[i-1][2] or CostDiam[i][0]!=CostDiam[i-1][0]:
                    CostDiamPositionv[0]=CostDiam[i][0]
                    CostDiamPositionv[1]=CostDiam[i][2]
                    CostDiamPositionv[2]=i        
                    CostDiamPosition.append(CostDiamPositionv[:])

            CostDiamPositionv[0]=CostDiam[-1][0]
            CostDiamPositionv[1]=CostDiam[-1][2]
            CostDiamPositionv[2]=len(CostDiam)
            CostDiamPosition.append(CostDiamPositionv[:])
            
                



            CostBridgeDiam=[]      ################# This is the final matrix containing the bridge costs for different bridges and different diameters  [TAG of the bridge | Rebar diameter | Bridge cost]
                                   ################# Since the bridge is considered symmetric in both longitudinal and transversal directions, and so the regions, the cost for a beam is twice the beam cost,
                                   ################# and for considering all the bridge they have to be considered twice again.

            for i in xrange(0,len(CostDiamPosition)-1):
                
                CostBridgeDiamv=[0,0,0,0,0]
                if Sortedinputs[CostDiamPosition[i][0]][5]%2!=0:                             # If the bridge contains an odd number of beams, the one in the middle has to be considered only once
                    for j in xrange(CostDiamPosition[i][2],CostDiamPosition[i+1][2]-1):
                        CostBridgeDiamv[2]=CostBridgeDiamv[2]+4*CostDiam[j][3]               # The non-mid beam is multiplied by four to considered the total length and its symmetrical beam in the transversal direction
                        CostBridgeDiamv[3]=CostBridgeDiamv[3]+4*CostDiam[j][4]
                    CostBridgeDiamv[2]=CostBridgeDiamv[2]+2*CostDiam[j+1][3]                 # The mid beam is multiplied by two to considered the total length but not its symmetrical beam in the transversal direction
                    CostBridgeDiamv[3]=CostBridgeDiamv[3]+2*CostDiam[j+1][4]
                    CostBridgeDiamv[0]=CostDiamPosition[i][0]
                    CostBridgeDiamv[1]=CostDiamPosition[i][1]
                    CostBridgeDiamv[4]=CostDiam[j][5]
                    CostBridgeDiam.append(CostBridgeDiamv[:])
               
                else:   
                    for j in xrange(CostDiamPosition[i][2],CostDiamPosition[i+1][2]):
                        CostBridgeDiamv[2]=CostBridgeDiamv[2]+4*CostDiam[j][3]
                        CostBridgeDiamv[3]=CostBridgeDiamv[3]+4*CostDiam[j][4]
                    CostBridgeDiamv[0]=CostDiamPosition[i][0]
                    CostBridgeDiamv[1]=CostDiamPosition[i][1]
                    CostBridgeDiamv[4]=CostDiam[j][5]
                    CostBridgeDiam.append(CostBridgeDiamv[:])
            
            #Loop that checks every bridge priced and adds the cost of slab reinforcement
            
            for i in xrange(0,len(CostBridgeDiam)):
                for j in xrange(0,len(Global)):
                    if Global[j][0]==CostBridgeDiam[i][0]: #If tag found in global is the same tag as the bridge checked add its slab reinforcement cost and go for the next bridge.
                        CostBridgeDiam[i][2]=CostBridgeDiam[i][2]+(Global[j][37]*steeldensity*pricesteel)-(Global[j][37]*priceconcrete)
                        CostBridgeDiam[i][3]=CostBridgeDiam[i][3]+(Global[j][37]*steeldensity*CO2SteelW)-(Global[j][37]*CO2ConcreteV)
                        break
                        
                
            CostDiam.insert(0,['TAG Bridge',' TAG Beam','Diameter (mm)','Beam cost (SEK)', 'kg C02 per beam'])      #These commands add titles to the matrix and convert them into Excel spreadsheets.

            resultFile = open("CostDiam.csv",'wb')
            wr = csv.writer(resultFile, dialect='excel')
            wr.writerows(CostDiam)

            CostBridgeDiam.insert(0,['TAG Bridge','Diameter (mm)','Bridge cost (SEK)', 'kg C02'])

            resultFile = open("CostBridgeDiam.csv",'wb')
            wr = csv.writer(resultFile, dialect='excel')
            wr.writerows(CostBridgeDiam)

        
else:               #This subprogramme calculates the bridge cost by considering the cheapest beam (in terms of diameter) regardless the rebar diameter of other beams in the same bridge

            
            CostB=[]                                  # This matrix contains the cost of the cheapest beam of a certain bridge [TAG of the Bridge | TAG of the Beam | Rebar diameter | Beam cost]
            CostBv=[0,0,0,0,0]                          # This list contains the local data which is included in CostB
            Price=max([row[3] for row in Cost])       # Inital beam cost taken as the most expensive one, then it is updated in order to find the cheapest beam

            for i in xrange(0,len(Cost)):
                            
                                if i<len(Cost)-1:                                   #For being able to access the position i+1 to check whether we are in a new beam or not, the last position is treated separetly
                                    
                                    if Cost[i][1]!=Cost[i+1][1] or Cost[i][0]!=Cost[i+1][0]:            #If next postion corresponds to another beam or bridge...
                                        if Cost[i][3]<=Price:                                           #If the cost of the beam for the current diameter is cheaper than the beam cost with the previous diameter, the cost of the cheapest beam is updated in its diameter stored
                                            Price=Cost[i][3]
                                            diam=Cost[i][2]
                                            CO2=Cost[i][4]
                                        
                                        CostBv[0]=Cost[i][0]                 # Since the next i-position correspons to a new beam, it is time to store the cheapest beam
                                        CostBv[1]=Cost[i][1]
                                        CostBv[2]=diam
                                        CostBv[3]=Price
                                        CostBv[4]=CO2
                                        CostB.append(CostBv[:])
                                        Price=max([row[3] for row in Cost])                 #The initial cost is resetted to the most expensive case
                                        
                                    else:                                                   #If the next i-position still corresponds to the same beam, only the cost is updated but no storage is done
                                           if Cost[i][3]<=Price:
                                                Price=Cost[i][3]
                                                diam=Cost[i][2]
                                                CO2=Cost[i][4]
                                            
                                else:                                                       #Same proccedure but for last i-position
                                    
                                        if Cost[i][3]<=Price:
                                            Price=Cost[i][3]
                                            diam=Cost[i][2]
                                            CO2=Cost[i][4]
                                        
                                        CostBv[0]=Cost[i][0]
                                        CostBv[1]=Cost[i][1]
                                        CostBv[2]=diam
                                        CostBv[3]=Price
                                        CostBv[4]=CO2
                                        CostB.append(CostBv[:])
                                        Price=max([row[3] for row in Cost])
                                        
            

            print ('Optimal Cost calculation at beam level succefully completed')


            CostCheapPositionv=[CostB[0][0],0]          #This matrix contains the position of the bridges as included in CostB, it works as the previous ones for storing positions [TAG of the bridge| Initial position for that bridge ]
            CostCheapPosition=[]
            CostCheapPosition.append(CostCheapPositionv[:])


            for i in xrange(1,len(CostB)):

                if CostB[i][0]!=CostB[i-1][0] :
                    CostCheapPositionv[0]=CostB[i][0]
                    CostCheapPositionv[1]=i        
                    CostCheapPosition.append(CostCheapPositionv[:])

            CostCheapPositionv[0]=CostB[-1][0]
            CostCheapPositionv[1]=len(CostB)
            CostCheapPosition.append(CostCheapPositionv[:])


            CostBridgeCheap=[]    ################# This is the final matrix containing the cheapest bridges  [TAG of the bridge | Bridge cost]
                                                    ################# Since the bridge is considered symmetric in both longitudinal and transversal directions, and so the regions, the cost for a beam is twice the beam cost,
                                                    ################# and for considering all the bridge they have to be considered twice again.

            for i in xrange(0,len(CostCheapPosition)-1):        #It works exactly as the previous one
                
                if len(set([row for row in xrange(CostCheapPosition[i][1],CostCheapPosition[i+1][1])]))==(Sortedinputs[CostCheapPosition[i][0]][5]+1)/2:   #Discard those ones with some beams not designed that passed the filter of checkedglobal
                    CostBridgeCheapv=[0,0,0]
                    if Sortedinputs[CostCheapPosition[i][0]][5]%2!=0:
                        for j in xrange(CostCheapPosition[i][1],CostCheapPosition[i+1][1]-1):
                            CostBridgeCheapv[1]=CostBridgeCheapv[1]+4*CostB[j][3]
                            CostBridgeCheapv[2]=CostBridgeCheapv[2]+4*CostB[j][4]
                        CostBridgeCheapv[1]=CostBridgeCheapv[1]+2*CostB[j+1][3]
                        CostBridgeCheapv[2]=CostBridgeCheapv[2]+2*CostB[j+1][4]
                        CostBridgeCheapv[0]=CostCheapPosition[i][0]
                        CostBridgeCheap.append(CostBridgeCheapv[:])
                   
                    else:   
                        for j in xrange(CostCheapPosition[i][1],CostCheapPosition[i+1][1]):
                            CostBridgeCheapv[1]=CostBridgeCheapv[1]+4*CostB[j][3]
                            CostBridgeCheapv[2]=CostBridgeCheapv[2]+4*CostB[j][4]
                        CostBridgeCheapv[0]=CostCheapPosition[i][0]
                        CostBridgeCheap.append(CostBridgeCheapv[:])
                        
            #Loop that checks every bridge priced and adds the cost of slab reinforcement
            
            for i in xrange(0,len(CostBridgeCheap)):
                for j in xrange(0,len(Global)):
                    if Global[j][0]==CostBridgeCheap[i][0]: #If tag found in global is the same tag as the bridge checked add its slab reinforcement cost and go for the next bridge.
                        CostBridgeCheap[i][1]=CostBridgeCheap[i][1]+(Global[j][37]*steeldensity*pricesteel)-(Global[j][37]*priceconcrete)
                        CostBridgeCheap[i][2]=CostBridgeCheap[i][2]+(Global[j][37]*steeldensity*CO2SteelW)-(Global[j][37]*CO2ConcreteV)
                        break


            CostB.insert(0,['TAG Bridge',' TAG Beam','Diameter (mm)','Beam cost (SEK)','kg C02 per beam'])        #These commands add titles to the matrix and convert them into Excel spreadsheets.
            resultFile = open("CostB.csv",'wb')                
            wr = csv.writer(resultFile, dialect='excel')
            wr.writerows(CostB)
                        
            CostBridgeCheap.insert(0,['TAG bridge',' Bridge Cost (SEK)','kg C02'])

            resultFile = open("CostBridgeCheap.csv",'wb')
            wr = csv.writer(resultFile, dialect='excel')
            wr.writerows(CostBridgeCheap)

    
    
print ('Optimal Cost calculation at Bridge level succefully completed')    
    


FIRSTI=['TAG','Plate Thickness','Beam Thickness','Beam height','Cantilever distance','Number of beams','BC 1=Supp 2=PoiFix 3=EdgeFix','Length (m)']
FIRSTG=['TAG','BC 1=Supp 2=PoiFix 3=EdgeFix','Plate Thickness (m)','Beam Thickness (m)','Beam height (m)','Cantilever distance (m)','Width Tsection (m)','Effective width Tsection (m)',
       'Number of beams','Tag Beam','Region','Region starting section (m)','Region final section (m)','Length of the region (m)','Number of rebars','Rebar diameter (mm)','Number of Layers','Yielding?','MEd (MN.m)','MRd(MN.m)'
       ,'URm','Ductility','NEd(MN)','|VEd|(MN)','VRdc(MN)','s (mm)','VRds(MN)','URv','MEdSLS','Crack width (mm)','Crack check','Concrete volume (m3)','Steel volume (m3)','Steel weigth (tonne)','Concrete cost (SEK)','Steel cost (SEK)','Cost of region (SEK)', 'As slab', 'C02 per region']


if InputsEXCEL==1:
    Inputs.insert(0,FIRSTI)

    resultFile = open("Inputs.csv",'wb')
    wr = csv.writer(resultFile, dialect='excel')
    wr.writerows(Inputs)

if GlobalEXCEL==1:
    Global.insert(0,FIRSTG)

    resultFile = open("Global.csv",'wb')
    wr = csv.writer(resultFile, dialect='excel')
    wr.writerows(Global)

if CheckedGlobalEXCEL==1:
    CheckedGlobal.insert(0,FIRSTG)

    resultFile = open("CheckedGlobal.csv",'wb')
    wr = csv.writer(resultFile, dialect='excel')
    wr.writerows(CheckedGlobal)

if CostEXCEL==1:
    Cost.insert(0,['TAG bridge','TAG beam','diam','Cost','kg C02 per beam'])

    resultFile = open("Cost.csv",'wb')
    wr = csv.writer(resultFile, dialect='excel')
    wr.writerows(Cost)







