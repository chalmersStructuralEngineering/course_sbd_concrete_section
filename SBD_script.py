from abaqus import*
from abaqusConstants import*
from caeModules import *
from odbAccess import *
from visualization import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import numpy as np

def combination_multy():
    Manual_control = ''             #If no manual control, subsitute number with ''. Can either be 12 or 16 [m], 12 is open 16 is closed
    no_tracks = [2]                   #Number of tracks on the bridge deck. Can be either 1 or 2

    Width = 12750                    #Bridge width [mm]
    Height = [3600, 5600]                   #Bridge Heigth [mm]

    Span = np.arange(6000,8001,2000)                  #Free span length [mm], 500
    #Span = np.arange(8000,16001,500)                  #Free span length [mm]

    #Bridge deck parameters
    thickness_deck = np.arange(300,851,500)          #thickness of the bridge deck [mm], 50
    #thickness_deck = np.arange(400,901,50)          #thickness of the bridge deck [mm]                          

    radius = [3, 3.5] #Radius of the bottom side of the slab. Shall be multiplied with the span_length. [mm]
    #radius = [3, 3.5, 4, 4.5, 5, 5.5, 6, 11]
    #radius = [11, 16, 21 ,26] #Radius of the bottom side of the slab. Shall be multiplied with the span_length. [mm]

    Leg_thickness = np.arange(300,801,500) #50
    #Leg_thickness = np.arange(400,901,50)
    Foundation_thickness = np.arange(400,901,500)    #Foundations thickneses 400 to 900 mm with an increase of 100mm [mm], 100
    Foundation_length = 0.3*Span        #Foundation length beneath either leg for the 16m version [mm]
    Foundation_extrusion = 600     #extrusion of the base plate on the inside of either leg for the 16m version [mm] 

    Foundation_length_12 = Span    #Foundation length beneath either leg for the 12m version [mm]
    Foundation_extrusion_12 = 100   #extrusion of the base plate on the outside of either leg for the 12m version [mm] 

    Edge_beam_height = 800
    Edge_beam_width = 300

    Ecm = 33e+3                     #Elasticity of concrete [MPa]
    density_concrete = 2500         #kg/m^3
    density_steel = 7800            #kg/m^3
    exp_coef = 1e-5                 #expantion coefficient of steel and concrete
    max_temp = 35                   #max exposure tempterature  
    min_temp = -29                  #min exposure temperature
    
    Soil_weight = 20                #Soil weight at retaning structure [kN/m^3]
    friction_angle = 45             #friction angle of fill material [degrees]

    r_rails = 1500                  #rail spacing [mm]
    Concrete_class = 'C35/45'
    # Foundation_type_12 = ['Foundation on bedrock','Foundation on clay']
    # E_modulus_foundation_12 = [50,4] #In MPA for 12 m

    Foundation_type_12 = ['Foundation on bedrock', 'Foundation on hard friction soil', 'Foundation on soft friction soil']
    E_modulus_foundation_12 = [15.E+03, 60, 10] #In MPA for 12 m

    # Foundation_type_16 = ['Foundation on bedrock','Foundation on clay']
    # E_modulus_foundation_16 =[50, 20]
    Foundation_type_16 = ['Foundation on bedrock', 'Foundation on hard friction soil', 'Foundation on soft friction soil']
    E_modulus_foundation_16 =[15.E+03, 60, 10]
    
    Id = 1
    model_name = 'Slab_bridge-'
    indata=[]                     
    for n_Span in Span:
        if Manual_control !='':
            n_span = Manual_control*1000
        else:
            n_span = n_Span

        if n_span == 12000:
            Foundation_type = Foundation_type_12
            E_modulus_foundation = E_modulus_foundation_12
        else:
            Foundation_type = Foundation_type_16
            E_modulus_foundation = E_modulus_foundation_16       

        for n_thickness_b_deck in thickness_deck:
            for n_found in range(len(E_modulus_foundation)):
                n_E_foundation = E_modulus_foundation[n_found]
                Found_type = Foundation_type[n_found]

                for n_thickness_legs in Leg_thickness:
                    if n_span != 12000:
                        Leg_thickness_top = [n_legs for n_legs in Leg_thickness if n_legs >= n_thickness_legs]
                    else:
                        Leg_thickness_top = [n_thickness_legs]
                    for n_thickness_legs_top in Leg_thickness_top:

                        for n_radius in radius:
                            for n_height in Height:
                                for n_track in no_tracks:
                                    for n_Foundation_thickness in Foundation_thickness:   
                                
                                        this_model = model_name + ( ('{0:0'+str(len(str(2)))+'d}').format(Id) )
                                        this_model_name = str(this_model)
                                        if Manual_control !='':
                                            n_span = Manual_control*1000
                                        else:
                                            n_span = n_Span
                                        if n_span ==  12000:
                                            Found_Len = n_Span
                                            Found_extrustion = Foundation_extrusion_12   
                                        else:
                                            Found_Len = Foundation_length
                                            Found_extrustion = Foundation_extrusion + n_thickness_legs/2
                                            tapering = (n_thickness_legs_top-n_thickness_legs)/Height   #tapering increase of legs
                                ## Placerar all indata i dictionary: 'my_indata'
                                        my_indata={'Model name':this_model_name,'Manual control':Manual_control, 'Free span':n_Span, 'Width':Width, 'Density concrete':density_concrete, 
                                                   'Density steel': density_steel,'Edge beam width':Edge_beam_width,'Edge beam height':Edge_beam_height,'no tracks':n_track,
                                                   'Foudnation length':Found_Len,'Foundation extrustion':Found_extrustion,'Foundation thickness':n_Foundation_thickness,'Radius':n_radius*n_Span,
                                                   'max temp':max_temp,'min temp':min_temp,'exp coef':exp_coef, 'Foundation length':Found_Len, 'Foundation extrusion':Found_extrustion,
                                                   'Leg thickness bottom':n_thickness_legs,'Leg thickness top':n_thickness_legs_top, 'Height legs':Height, 'Deck thickness':n_thickness_b_deck,
                                                   'Foundation E-modulus':n_E_foundation,'E-modulus abaqus':Ecm,'Tapering legs':tapering,'Soil weight':Soil_weight,'Rail spacing':r_rails,
                                                   'Friction angle':friction_angle,'Concrete class':Concrete_class,'Foundation type':Found_type} 
                                        indata.append(my_indata)
                                        Id += 1
    return(indata)

def combination_single():
    Manual_control = ''           #If no manual control, subsitute number with ''. Can either be 12 or 16 [m]
    no_tracks = 1                  #Number of tracks on the bridge deck. Can be either 1 or 2

    Width = 7200                    #Bridge width [mm]
    Height = 7500                   #Bridge Heigth [mm]

    Span = [16000]                  #Span length [mm]
    #Bridge deck parameters
    thickness_deck = [950]          #thickness of the bridge deck [mm]
    radius = [3.8]               #Radius of the bottom side of the slab. it is multiplied with the span_length later. [mm]

    #Concrete class
    Concrete_class = 'C35/45'

    #leg thickenss bot governs the thickness of the 12 m bridge variant. It represent the uniform thickness of the legs
    Leg_thickness_bot = [700]       #Leg thickness in the bottom of the legs [mm]

    leg_thickness_top = [1350]      #Leg thickness in the top of the legs [mm]

    Foundation_thickness = [900]    #Foundations thickneses 400 to 900 mm with an increase of 50mm [mm]
    Foundation_length = 4700        #Foundation length beneath either leg for the 16m version [mm]
    Foundation_extrusion = 1150     #extrusion of the base plate on the inside of either leg for the 16m version [mm] 

    Foundation_length_12 = Span    #Foundation length between either leg for the 12m version [mm]
    Foundation_extrusion_12 = 100   #extrusion of the base plate on the outside of either leg for the 12m version [mm] 

    Edge_beam_height = 800
    Edge_beam_width = 300

    Ecm = 33e+3                     #Elasticity of concrete [MPa]
    density_concrete = 2500         #kg/m^3
    density_steel = 7800            #kg/m^3
    exp_coef = 1e-5                 #expantion coefficient of steel and concrete
    max_temp = 40                   #max exposure tempterature  
    min_temp = -48                  #min exposure temperature
    
    Soil_weight = 20                #Soil weight at retaning structure [kN/m^3]
    friction_angle = 45             #friction angle of fill material [degrees]

    r_rails = 1500                  #rail spacing [mm]
    Foundation_type = ['Foundation on clay']
    # Foundation_type = ['Foundation clay']
    # E_modulus_foundation = [50,4] #In MPA for 12 m
    # E_modulus_foundation =[50, 20]
    E_modulus_foundation = [20]
    Id = 1
    model_name = 'Slab_bridge-'
    indata=[]
    for n_Span in Span:
        for n_thickness_b_deck in thickness_deck:
            for n_found_stiff in range(len(E_modulus_foundation)):
                n_E_foundation = E_modulus_foundation[n_found_stiff]
                n_E_foundation_type = Foundation_type[n_found_stiff]
                for n_thickness_legs in Leg_thickness_bot:
                    if Manual_control !='':
                        n_span = Manual_control*1000
                    else:
                        n_span = n_Span
                    if n_span >= 16000:
                        Leg_thickness_top = leg_thickness_top
                    else:
                        Leg_thickness_top = [n_thickness_legs]
                    for n_thickness_legs_top in Leg_thickness_top:
                        for n_radius in radius:
                            for n_Foundation_thickness in Foundation_thickness:   
                            
                                this_model = model_name + ( ('{0:0'+str(len(str(2)))+'d}').format(Id) )
                                this_model_name = str(this_model)
                                if Manual_control !='':
                                    n_span = Manual_control*1000
                                else:
                                    n_span = n_Span
                                if n_span ==  12000:
                                    Found_Len =n_Span
                                    Found_extrustion = Foundation_extrusion_12  
                                else:
                                    Found_Len = Foundation_length
                                    Found_extrustion = Foundation_extrusion + n_thickness_legs/2
                                tapering = (n_thickness_legs_top-n_thickness_legs)/Height   #tapering increase of legs
                                ## Placerar all indata i dictionary: 'my_indata'
                                my_indata={'Model name':this_model_name,'Manual control':Manual_control, 'Free span':n_Span, 'Width':Width, 'Density concrete':density_concrete, 
                                        'Density steel': density_steel,'Edge beam width':Edge_beam_width,'Edge beam height':Edge_beam_height,'no tracks':no_tracks,
                                        'Foudnation length':Found_Len,'Foundation extrustion':Found_extrustion,'Foundation thickness':n_Foundation_thickness,'Radius':n_radius*n_Span,
                                        'max temp':max_temp,'min temp':min_temp,'exp coef':exp_coef, 'Foundation length':Found_Len, 'Foundation extrusion':Found_extrustion,
                                        'Leg thickness bottom':n_thickness_legs,'Leg thickness top':n_thickness_legs_top, 'Height legs':Height, 'Deck thickness':n_thickness_b_deck,
                                        'Foundation E-modulus':n_E_foundation,'E-modulus abaqus':Ecm,'Tapering legs':tapering,'Soil weight':Soil_weight,'Rail spacing':r_rails,
                                        'Friction angle':friction_angle,'Concrete class':Concrete_class,'Foundation type':n_E_foundation_type} 
                                indata.append(my_indata)
                                Id += 1
    return(indata)

def Concrete_classes(concrete_class):
    #Capacities in MPa
    import numpy as np
    if concrete_class == 'C12/15':
        fck = 12.0                  
        fck_cube = 15.0              
    elif concrete_class == 'C16/20':
        fck = 16.
        fck_cube = 20.
    elif concrete_class == 'C20/25':
        fck = 20.
        fck_cube = 25.
                    
    elif concrete_class == 'C25/30':
        fck = 25.
        fck_cube = 30.
                    
    elif concrete_class == 'C30/37':
        fck = 30.
        fck_cube = 37.
    elif concrete_class == 'C32/40':
        fck = 32.
        fck_cube = 40.
    elif concrete_class == 'C35/45':
        fck = 35.
        fck_cube = 45.
                    
    elif concrete_class == 'C40/50':
        fck = 40.
        fck_cube = 50.
    elif concrete_class == 'C45/55':
        fck = 45.
        fck_cube = 55.
    elif concrete_class == 'C50/60':
        fck = 50.
        fck_cube = 60.
    elif concrete_class == 'C55/67':
        fck = 55.
        fck_cube = 67.
    elif concrete_class == 'C60/75':
        fck = 60.
        fck_cube = 75.
    elif concrete_class == 'C70/85':
        fck = 70.
        fck_cube = 85.
    elif concrete_class == 'C80/95':
        fck = 80.
        fck_cube = 95.
    elif concrete_class == 'C90/105':
        fck = 90.
        fck_cube = 105.

    fcm = fck + 8.
    
    if fck <= 50.:
        fctm = 0.30 * (fck) ** (2. / 3.)
    else:
        fctm = 2.12 * np.log((1. + fcm/10.), np.exp(1))

    fctk005 = 0.7 * fctm
    Ecm = 22. * (fcm / 10.) ** (0.3) * 1000                 #SS-EN 1992-1-1 table 3.1                     

    if fck<=50:
        alpha_R = 0.810
        Beta_R =0.416
    elif fck==55:
        alpha_R =0.742
        Beta_R =0.392
    elif fck==60:
        alpha_R =0.695
        Beta_R =0.377
    elif fck==70:
        alpha_R =0.637
        Beta_R =0.362
    elif fck==80:
        alpha_R =0.599
        Beta_R =0.355
    elif fck==90:
        alpha_R =0.583
        Beta_R =0.353


    concrete_properties = {'fck': fck, 'fck_cube': fck_cube, 'fcm': fcm, 'fctm': fctm, 'fctk005': fctk005, 'Ecm': Ecm,'alpha R':alpha_R,'Beta R':Beta_R}

    return concrete_properties

def model_create(indata):
    import numpy as np
    Mdb()
    #Manually controlling which typ of frame bridge should be applied. Can be changed in def combination()
    if indata['Manual control'] !='':
        control_span = indata['Manual control']*1000
    else:
        control_span = indata['Free span']

    #The thickness of legs needs to be added to the free span lenghts since the shell thicknes extrudes equally much on either side of the shell.
    l = indata['Free span']
    x =np.linspace(l/2,l/100-1)
    r = indata['Radius']
    t_d = indata['Deck thickness']
    thicknesses = t_d - np.sqrt(r**2-(x)**2)+r  
    t_end_deck = thicknesses[0]
    tapering_legs = (float(indata['Leg thickness top'])-float(indata['Leg thickness bottom']))/float(indata['Height legs'])
    l = int(l + (indata['Leg thickness top']-(t_end_deck/2)*tapering_legs))
    indata.update({'Span':l})
    # indata.update({'Span':indata['Free span']})
    print(indata['Span'])
    #Creating the model
    mdb.Model(modelType=STANDARD_EXPLICIT, name=indata['Model name'])

    #partitions Abaqus coomands for readablility
    mymodel = mdb.models[indata['Model name']]
    p = mymodel.parts
    a = mymodel.rootAssembly
    m = mymodel.materials



    # Geometry of bridge deck
    mymodel.ConstrainedSketch(name='__profile__', sheetSize=2000.0)
    mymodel.sketches['__profile__'].rectangle(point1=((-indata['Span']/2), 0.0), 
        point2=((indata['Span']/2), indata['Width']))
    mymodel.Part(dimensionality=THREE_D, name='Bridge_deck', type=
        DEFORMABLE_BODY)
    
    p['Bridge_deck'].BaseShell(sketch= mymodel.sketches['__profile__'])
    del mymodel.sketches['__profile__']
    #del mdb.models['Model-1].sketches['__profile__']
    

    Concrete_data = Concrete_classes(indata['Concrete class'])
    Ecm = Concrete_data['Ecm']                         
    # Concrete properties of the bridge deck, Legs and foundation
    mymodel.Material(name='Concrete_b_d')
    m['Concrete_b_d'].Elastic(table=((Ecm, 0.25), ))
    m['Concrete_b_d'].Density(table=((indata['Density concrete']*1e-12,), ))
    m['Concrete_b_d'].Expansion(table=((indata['exp coef'], ), ), zero=0)

    mymodel.Material(name='Concrete_l')
    m['Concrete_l'].Elastic(table=((Ecm, 0.25), ))
    m['Concrete_l'].Density(table=((indata['Density concrete']*1e-12,), ))
    m['Concrete_l'].Expansion(table=((indata['exp coef'], ), ), zero=0)

    mymodel.Material(name='Concrete_f')
    m['Concrete_f'].Elastic(table=((Ecm, 0.25), ))
    m['Concrete_f'].Density(table=((indata['Density concrete']*1e-12,), ))
    m['Concrete_f'].Expansion(table=((indata['exp coef'], ), ), zero=0)

    mymodel.Material(name='Concrete_edge_beam')
    m['Concrete_edge_beam'].Elastic(table=((Ecm/1000, 0), ))
    m['Concrete_edge_beam'].Density(table=((indata['Density concrete']*1e-12,), ))


    #Create part, edge beams
    mymodel.ConstrainedSketch(name='__profile__', sheetSize=2000.0)
    mymodel.sketches['__profile__'].Line(point1=((-indata['Span']/2), 0.0), 
        point2=((indata['Span']/2), 0.0))
    
    mymodel.Part(dimensionality=THREE_D, name='Edge_beam', type=DEFORMABLE_BODY)
    
    p['Edge_beam'].BaseWire(sketch= mymodel.sketches['__profile__'])
    del mymodel.sketches['__profile__']
    
    mymodel.RectangularProfile(a=indata['Edge beam width'], b=indata['Edge beam height'], name=
        'Profile-1')
    
    mymodel.BeamSection(consistentMassMatrix=False, 
        integration=DURING_ANALYSIS, material='Concrete_edge_beam', name=
        'Edge_beam', poissonRatio=0.0, profile='Profile-1', temperatureVar=LINEAR)
    
    p['Edge_beam'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        edges=p['Edge_beam'].edges.findAt(((0.0, 0.0, 0.0), ), )), sectionName='Edge_beam', thicknessAssignment=
        FROM_SECTION)

    p['Edge_beam'].assignBeamSectionOrientation(method=N1_COSINES, n1=(0.0, 1.0, 0.0), 
        region=Region(edges=p['Edge_beam'].edges.findAt(((0, 0.0, 0.0), ), )))

    #Creates 2 instances corresponding to the edge beams
    a.Instance(dependent=ON, name='Edge_beam-1', part=p['Edge_beam'])
    
    a.Instance(dependent=ON, name='Edge_beam-2', part=p['Edge_beam'])
       
    a.translate(instanceList=('Edge_beam-2', ), vector=(0.0, indata['Width'], 0.0))
    
    #     circumEdges=a.instances['Edge_beam-1'].edges.findAt(((-4000.0, 0.0, 0.0), ), )))

    # Defining thickness of bridge deck
    if indata['Radius'] == 0:
        mymodel.HomogeneousShellSection(idealization=NO_IDEALIZATION, 
            integrationRule=SIMPSON, material='Concrete_b_d', name='Bridge_deck', 
            nodalThicknessField='', numIntPts=5, poissonDefinition=DEFAULT, 
            preIntegrate=OFF, temperature=GRADIENT, thickness=indata['Deck thickness'], thicknessField='', 
            thicknessModulus=None, thicknessType=UNIFORM, useDensity=OFF)

    else:
        mymodel.ExpressionField(description='', expression=
            '{} -sqrt(pow({},2)-pow(X,2))+{}'.format(indata['Deck thickness'],indata['Radius'],indata['Radius']), localCsys=None, name=
            'Bridge_deck_curvature')
        mymodel.HomogeneousShellSection(idealization=NO_IDEALIZATION, 
            integrationRule=SIMPSON, material='Concrete_b_d', name='Bridge_deck', 
            numIntPts=5, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=
            GRADIENT, thickness=0.0, thicknessField='Bridge_deck_curvature', 
            thicknessModulus=None, thicknessType=ANALYTICAL_FIELD, useDensity=OFF)

    #Applying the bridge deck section to the bridge deck
    p['Bridge_deck'].SectionAssignment(offset=0.0, offsetField=
            '', offsetType=MIDDLE_SURFACE, region=Region(
            faces=p['Bridge_deck'].faces.getSequenceFromMask(mask=(
            '[#1 ]', ), )), sectionName='Bridge_deck', thicknessAssignment=FROM_SECTION)

    # Creating the legs
    mymodel.ConstrainedSketch(name='__profile__', sheetSize=2000.0)
    mymodel.sketches['__profile__'].rectangle(point1=(0.0, 0.0), 
        point2=(indata['Width'], indata['Height legs']))
    mymodel.Part(dimensionality=THREE_D, name='Legs', type=DEFORMABLE_BODY)
    p['Legs'].BaseShell(sketch=mymodel.sketches['__profile__'])
    del mymodel.sketches['__profile__']

    mymodel.ExpressionField(description='', expression='{} + Z *({}-{})/{}'.format(indata['Leg thickness top'],indata['Leg thickness top'],indata['Leg thickness bottom'],indata['Height legs']), 
        localCsys=None, name='Leg_tapering')

    mymodel.HomogeneousShellSection(idealization=NO_IDEALIZATION, 
        integrationRule=SIMPSON, material='Concrete_l', name='Legs', numIntPts=5, 
        poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, 
        thickness=0.0, thicknessField='Leg_tapering', thicknessModulus=None, 
        thicknessType=ANALYTICAL_FIELD, useDensity=OFF)
    
    #Assigning the leg section to the legs
    p['Legs'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        faces=p['Legs'].faces.getSequenceFromMask(mask=('[#1 ]', ), )), sectionName='Legs', thicknessAssignment=FROM_SECTION)

    # Geometry of foundation
    if control_span == 12000:
        mymodel.ConstrainedSketch(name='__profile__', sheetSize=2000.0)
        mymodel.sketches['__profile__'].rectangle(point1=((-indata['Span']/2-indata['Leg thickness bottom']-indata['Foundation extrustion']), 0.0), 
            point2=((indata['Span']/2+indata['Leg thickness bottom']+indata['Foundation extrustion']), indata['Width']))
        mymodel.Part(dimensionality=THREE_D, name='Foundation', type=DEFORMABLE_BODY)
        p['Foundation'].BaseShell(sketch=mymodel.sketches['__profile__'])
        del mymodel.sketches['__profile__']
    else: 
        mymodel.ConstrainedSketch(name='__profile__', sheetSize=2000.0)
        mymodel.sketches['__profile__'].rectangle(point1=(0, 0.0), 
            point2=(indata['Foundation length'], indata['Width']))
        mymodel.Part(dimensionality=THREE_D, name='Foundation', type=DEFORMABLE_BODY)
        p['Foundation'].BaseShell(sketch=mymodel.sketches['__profile__'])
        del mymodel.sketches['__profile__']

    # Creating section for thickness of foundation
    mymodel.HomogeneousShellSection(idealization=NO_IDEALIZATION, 
        integrationRule=SIMPSON, material='Concrete_f', name='Foundation', 
        nodalThicknessField='', numIntPts=5, poissonDefinition=DEFAULT, 
        preIntegrate=OFF, temperature=GRADIENT, thickness=indata['Foundation thickness'], thicknessField='', 
        thicknessModulus=None, thicknessType=UNIFORM, useDensity=OFF)

    # Assigning the foundation section to the foundation parts
    p['Foundation'].SectionAssignment(offset=0.0, offsetField=
        '', offsetType=MIDDLE_SURFACE, region=Region(
        faces=p['Foundation'].faces.getSequenceFromMask(mask=(
        '[#1 ]', ), )), sectionName='Foundation', thicknessAssignment=FROM_SECTION)


    #Starting assembly
    #Creating an instance for the bridge deck
    a.Instance(dependent=ON, name='Bridge_deck-1', 
        part=p['Bridge_deck'])

    #Creating instance for 1st leg: Rotating leg 
    a.Instance(dependent=ON, name='Legs-1', part=
        p['Legs'])
    a.rotate(angle=90.0, axisDirection=(10.0, 0.0, 
        0.0), axisPoint=(0.0, 0.0, 0.0), instanceList=('Legs-1', ))
    a.rotate(angle=-90.0, axisDirection=(0.0, 0.0, 
        -10.0), axisPoint=(0.0, 0.0, indata['Height legs']), instanceList=('Legs-1', ))

    a.translate(instanceList=('Legs-1', ), vector=
        (-indata['Span']/2, 0.0, -indata['Height legs']))

    #Creating instance for 2nd leg: Rotating leg 
    a.Instance(dependent=ON, name='Legs-2', part=
        p['Legs'])
    a.rotate(angle=90.0, axisDirection=(10.0, 0.0, 
        0.0), axisPoint=(0.0, 0.0, 0.0), instanceList=('Legs-2', ))
    a.rotate(angle=90.0, axisDirection=(0.0, 0.0, 
        -10.0), axisPoint=(0.0, 0.0, indata['Height legs']), instanceList=('Legs-2', ))

    a.translate(instanceList=('Legs-2', ), vector=
        (indata['Span']/2, indata['Width'], -indata['Height legs']))


    #Positioning the foundation to match with the width of the walls
    if control_span==12000:
        #Creating the instance for the base plate when L = 12000 mm 
        a.Instance(dependent=ON, name='Foundation-1', 
            part=p['Foundation'])
        a.DatumPointByOffset(point=
            a.instances['Foundation-1'].vertices[1], 
            vector=((-indata['Leg thickness bottom']-indata['Foundation extrustion']), 0.0, 0.0))
        a.translate(instanceList=('Foundation-1', ), 
            vector=(0.0, 0.0, -indata['Height legs']))

        a.InstanceFromBooleanMerge(domain=GEOMETRY, 
            instances=(a.instances['Bridge_deck-1'], 
            a.instances['Legs-1'], 
            a.instances['Legs-2'], 
            a.instances['Foundation-1'],), 
            keepIntersections=ON, name='Bridge', originalInstances=SUPPRESS)
    
  
    else:
        #Creating instance num1 for the base plate when L = 16 000 mm
        a.Instance(dependent=ON, name='Foundation-1', 
            part=p['Foundation'])
        a.DatumPointByOffset(point=
            a.instances['Foundation-1'].vertices[0], 
            vector=(indata['Foundation extrustion'], 0.0, 0.0))
        a.translate(instanceList=('Foundation-1', ), 
            vector=((indata['Span']/2-indata['Foundation extrustion']), 0.0, -indata['Height legs']))
        
        #Creating instance num2 for the base plate when L = 16 000 mm
        a.Instance(dependent=ON, name='Foundation-2', 
            part=p['Foundation'])
        a.DatumPointByOffset(point=
            a.instances['Foundation-2'].vertices[1], 
            vector=(-indata['Foundation extrustion'], 0.0, 0.0))
        a.translate(instanceList=('Foundation-2', ), 
            vector=((-indata['Span']/2-(indata['Foundation length']-indata['Foundation extrustion'])), 0.0, -indata['Height legs']))   

        #Assembles the instances to one part
        a.InstanceFromBooleanMerge(domain=GEOMETRY, 
            instances=(a.instances['Bridge_deck-1'], 
            a.instances['Legs-1'], 
            a.instances['Legs-2'], 
            a.instances['Foundation-1'], 
            a.instances['Foundation-2'],), 
            keepIntersections=ON, name='Bridge', originalInstances=SUPPRESS)
        
    mdb.models[indata['Model name']].Tie(adjust=ON, main=Region(
        side1Edges=a.instances['Bridge-1'].edges.findAt(((0.0, 0.0, 0.0), ), )), name='Edge_beam_1', positionToleranceMethod=
        COMPUTED, secondary=Region(circumEdges=a.instances['Edge_beam-1'].edges.findAt(((0.0, 0.0, 0.0), ), )), thickness=ON, tieRotations=ON)
    
    mdb.models[indata['Model name']].Tie(adjust=ON, main=Region(
        side1Edges=a.instances['Bridge-1'].edges.findAt(((0.0, indata['Width'], 0.0), ), )), name='Edge_beam_2', positionToleranceMethod=
        COMPUTED, secondary=Region(circumEdges=a.instances['Edge_beam-2'].edges.findAt(((0.0, indata['Width'], 0.0), ), )), thickness=ON, tieRotations=ON)
    a.regenerate()

def Partition_loads(indata):
    #The loads applied on the bridge are, self-weigth, temperature loads, live loads and earth pressure 
    #The live loads are applied in the worst positions regarding moment or shear force, thus several
    #situation with the same load case may be apllied. 
    import numpy as np
    mymodel = mdb.models[indata['Model name']]
    p = mymodel.parts
    a = mymodel.rootAssembly

    #Creates a set for temperature loads
    a.Set(faces=a.instances['Bridge-1'].faces.findAt(((0,indata['Width']/2,0), )), name='Temp')

    #Ballast on bridge deck
    a.regenerate()
    a.Surface(name='Ballast_bridge_deck', side1Faces=
        a.instances['Bridge-1'].faces.findAt(((0,indata['Width']/2,0), ), ))

    #Earth pressure, resting earth pressure
    a.regenerate()
    a.Surface(name='Resting_earth_pressure', side2Faces=
        a.instances['Bridge-1'].faces.findAt(
        ((-indata['Span']/2,indata['Width']/2,-indata['Height legs']), )
        , ((indata['Span']/2,indata['Width']/2,-indata['Height legs']), ), ))

    #####################################################################
    #Earth pressure, thermal expansion, Break load and acceleration load
    # Each leg has to be paritioned since this earth prssure has its peak in the center of the height of the legs. 
    Coord_legs = []
    for n in [-indata['Span']/2, indata['Span']/2]:
        for b in [0,indata['Width']]: 
            Coord_legs.append((n,b,-indata['Height legs']/2))


    reshaped_coord_legs = [Coord_legs[i:i+2] for i in range(0, len(Coord_legs),  2)]
    if len(Coord_legs) %  2 !=  0:
        reshaped_coord_legs.append(Coord_legs[-1:])

    for partitions in reshaped_coord_legs:
        p['Bridge'].PartitionFaceByShortestPath(faces=
            p['Bridge'].faces.findAt(((partitions[0][0], indata['Width']/2, -indata['Height legs']/2), )), 
            point1=p['Bridge'].InterestingPoint(p['Bridge'].edges.findAt((partitions[0]), ), MIDDLE), 
            point2= p['Bridge'].InterestingPoint(p['Bridge'].edges.findAt((partitions[1]), ), MIDDLE))
    
    #Leg 1, upper partition. Creates surface
    a.regenerate()
    a.Surface(name='LEG_1_upper', side2Faces=
        a.instances['Bridge-1'].faces.findAt(
        ((-indata['Span']/2,indata['Width']/2,-indata['Height legs']/4), ), )) 
    
    
    #Leg 1, lower partition,creates surface
    a.regenerate()
    a.Surface(name='LEG_1_lower', side2Faces=a.instances['Bridge-1'].faces.findAt(
        ((-indata['Span']/2,indata['Width']/2,-3*indata['Height legs']/4), ), ))    
       
    #Leg 2, upper partition,creates surface
    a.regenerate()
    a.Surface(name='LEG_2_upper', side2Faces=a.instances['Bridge-1'].faces.findAt(
        ((indata['Span']/2,indata['Width']/2,-indata['Height legs']/4), ), ))

    #Leg 2, lower partition, creates surface
    a.regenerate()
    a.Surface(name='LEG_2_lower', side2Faces=a.instances['Bridge-1'].faces.findAt(
        ((indata['Span']/2,indata['Width']/2,-3*indata['Height legs']/4), ), ))   

    #Upper surfaces on legs, temp_expansion
    a.regenerate()
    a.Surface(name='Upper_earth_temp', side2Faces=a.instances['Bridge-1'].faces.findAt(
        ((-indata['Span']/2,indata['Width']/2,-indata['Height legs']/4), )
        , ((indata['Span']/2,indata['Width']/2,-indata['Height legs']/4), ), ))

    #Lower surfaces on legs, temp_expansion 
    a.regenerate()
    a.Surface(name='Lower_earth_temp', side2Faces=a.instances['Bridge-1'].faces.findAt(
        ((-indata['Span']/2,indata['Width']/2,-3*indata['Height legs']/4), )
        , ((indata['Span']/2,indata['Width']/2,-3*indata['Height legs']/4), ), ))    

    ###########################################################################
    #SW/2 is a worse case than SW/0 since it assumes heavy train traffic, the length of the load is longer and of greater magnitude, hence SW/0 is disregarded
    #Only one position of the load is apllied for SW/2 since the largest span of the "standard-bridges" is 24 meters, the distributed load of SW/2 (25 meters) will reach
    #the whole span segment.
    #---------------------#

    r_rails = indata['Rail spacing']
    if indata['no tracks'] == 2:
        Width_positions = [[indata['Width']/2-r_rails/2-3000,indata['Width']/2+r_rails/2-3000],[indata['Width']/2-r_rails/2+3000,indata['Width']/2+r_rails/2+3000]]
        track_number = [1,2] 
    else:
        Width_positions = [[indata['Width']/2-r_rails/2, indata['Width']/2+r_rails/2]]        #Global y-coordinates for rail
        track_number = [1]

    #Partitions the tracks on the bridge deck.
    Initial_partitions = []
    for track_id in range(len(track_number)):

        #Creates a list to store all x_positions of the point loads, which will be used later when
        #determening the positions of transversal paths, regarding the magnitude of the shear force.
        x_positions_boggiloads = []

        t_id = track_number[track_id]
        w_positions=Width_positions[track_id]
        Initial_partitions=[]
        reshaped_partitions=[]
        for widths in w_positions:
            for spans in [-indata['Span']/2,indata['Span']/2]:
                Initial_partitions.append((spans,widths,0))
        reshaped_partitions = [Initial_partitions[i:i+2] for i in range(0, len(Initial_partitions),  2)]
        if len(Initial_partitions) %  2 !=  0:
            reshaped_partitions.append(Initial_partitions[-1:])

        #Creates partition points for the tracks 
        for partitions in reshaped_partitions:
            for point in partitions:
                edge = p['Bridge'].edges.findAt(point)
                p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)

        #partitions the bridge deck in the positions of the rails
        for partitions in reshaped_partitions:
            p['Bridge'].PartitionFaceByShortestPath(faces=
                p['Bridge'].faces.findAt(((partitions[0][0]+(partitions[1][0]-partitions[0][0])/2, 
                partitions[0][1], 0.0), )), 
                point1=p['Bridge'].vertices.findAt((partitions[0]), ), 
                point2=p['Bridge'].vertices.findAt(partitions[1], ))
        
        #Creates surface for distributed load in load case SW/2
        a.regenerate()
        a.Surface(name='SW/2_'+str(t_id), side1Faces=a.instances['Bridge-1'].faces.findAt(
            ((0, w_positions[0]+(w_positions[1]-w_positions[0])/2, 0.0), )))

        ##################################################################################
        #LM/71_1, worst position for shear.
        #I I I I -------------# Load positions, '#' denotes the ends of the span, 'I' denotes the point loads, '-' denotes evenly distributed load     
            
        #defining positions of the loads, placing the first point load 100 mm from the edge.
        #local coordinates of the point loads, placed in the center of the bridge.
        point_pos_LM71_1= -indata['Span']/2+100
        x_pos = [point_pos_LM71_1]                 #First x-coordinate for load the point load
        num_point_loads = 3                             #number of additional point loads, x_pos is already counted
        Global_coord_point_LM71_1=[]                

        #Defining global x-coordinates for point loads
        for n in range(num_point_loads):
            new_point = x_pos[n] + 1600
            x_pos.append(new_point)

        #Defining global coordinates for each point 
        for n in x_pos:
            for y_pos in w_positions:
                new_point = (n, y_pos , 0)
                Global_coord_point_LM71_1.append(new_point)

        #Defining global coordinates for the uniformly distributed load, it will be applied as an area load. These coordinates are the coordinates in which a
        #partition will be performed
        Global_coord_dist_LM71_1 = []
        for y_pos in w_positions:
            Global_coord = (x_pos[-1]+800,y_pos,0)
            Global_coord_dist_LM71_1.append(Global_coord)
        reshaped_Global_coord_dist_LM71_1 = [Global_coord_dist_LM71_1[i:i+2] for i in range(0, len(Global_coord_dist_LM71_1),  2)]
        if len(Global_coord_dist_LM71_1) %  2 !=  0:
            reshaped_Global_coord_dist_LM71_1.append(Global_coord_dist_LM71_1[-1:])
        

        #Creates a reference point for nosing force
        a.ReferencePoint(point=(x_pos[0], w_positions[0], 17))



        ###########################################################
        #LM/71_2, worst position for moment in span.
        #----- I I I I -------# Load positions, '#' denotes the ends of the span, 'I' denotes the point loads, '-' denotes evenly distributed load      

        #First point load is placed L/2 - 1600 -1600 mm from the left support
        point_pos_LM71_2 = -2*1600
        x_pos = [point_pos_LM71_2]
        num_point_loads = 3
        Global_coord_point_LM71_2=[]

        for n in range(num_point_loads):
            new_point = x_pos[n] + 1600
            x_pos.append(new_point)
        

        for n in x_pos:
            for y_pos in w_positions:
                new_point = (n, y_pos , 0)
                Global_coord_point_LM71_2.append(new_point)

        Global_coord_dist_LM71_2 = []

        #Global start and end coordinates for the distributed load
        for x in [x_pos[0]-800,x_pos[-1]+800]:
            for y_pos in w_positions:
                Global_coord = (x,y_pos,0)
                Global_coord_dist_LM71_2.append(Global_coord)
        
        reshaped_Global_coord_dist_LM71_2 = [Global_coord_dist_LM71_2[i:i+2] for i in range(0, len(Global_coord_dist_LM71_2),  2)]
        if len(Global_coord_dist_LM71_2) %  2 !=  0:
            reshaped_Global_coord_dist_LM71_2.append(Global_coord_dist_LM71_2[-1:])

        a.ReferencePoint(point=(x_pos[2], w_positions[0], 17))


        #LM71_3
        #--- I I I I ---------# Load positions, '#' denotes the ends of the span, 'I' denotes the point loads, '-' denotes evenly distributed load      
        #First point load is placed so maximum load in the the support is obtained. The relation between the position and the geometry is approximated
        # According to the equations below. The relation isobtained through several parametric studies.
    
        d = indata['Span']*0.655-3100
        x =np.linspace(indata['Span']/2,indata['Span']/100-1)
        thicknesses = indata['Deck thickness'] - np.sqrt(indata['Radius']**2-(x)**2)+indata['Radius']
        td_ave = np.average(thicknesses)   
        point_pos = int(((((indata['Leg thickness top']**2+indata['Leg thickness bottom']**2)/(td_ave**2))-6.89)/6.89)*((d+2400-indata['Span']/2))+d)
       
        point_pos_LM71_3 = -indata['Span']/2+point_pos
        x_pos = [point_pos_LM71_3]
        num_point_loads = 3
        Global_coord_point_LM71_3=[]

        for n in range(num_point_loads):
            new_point = x_pos[n] + 1600
            x_pos.append(new_point)
            #Stores x_coordinates in main coordinates list 
        

        for n in x_pos:
            for y_pos in w_positions:
                new_point = (n, y_pos , 0)
                Global_coord_point_LM71_3.append(new_point)

        Global_coord_dist_LM71_3 = []

        #Global start and end coordinates for the distributed load
        for x in [x_pos[0]-800,x_pos[-1]+800]:
            for y_pos in w_positions:
                Global_coord = (x,y_pos,0)
                Global_coord_dist_LM71_3.append(Global_coord)
        
        reshaped_Global_coord_dist_LM71_3 = [Global_coord_dist_LM71_3[i:i+2] for i in range(0, len(Global_coord_dist_LM71_2),  2)]
        if len(Global_coord_dist_LM71_3) %  2 !=  0:
            reshaped_Global_coord_dist_LM71_3.append(Global_coord_dist_LM71_3[-1:])

        ######################################################################
        #adds partition points for point loads in load case LM71_1
        for point in Global_coord_point_LM71_1:
            try:
                edge = p['Bridge'].edges.findAt(point)
                p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
            except Exception as e:
                pass
        
        ref_point = a.referencePoints.keys()
        a.regenerate()
        coord = Global_coord_point_LM71_1[0]
        mymodel.RigidBody(name='Ref_point'+str(ref_point[1]), refPointRegion=
            Region(referencePoints=(a.referencePoints[ref_point[1]], )), 
            tieRegion=Region(vertices=a.instances['Bridge-1'].vertices.findAt(
            ((coord[0], coord[1], 0.0), ), )))

        #adds partition points for point loads in load case LM71_2
        for point in Global_coord_point_LM71_2:
            try:    
                edge = p['Bridge'].edges.findAt(point)
                p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
            except Exception as e:
                pass
        
        coord = Global_coord_point_LM71_2[5]
        a.regenerate()
        mymodel.RigidBody(name='Ref_point'+str(ref_point[0]), refPointRegion=
            Region(referencePoints=(a.referencePoints[ref_point[0]], )), 
            tieRegion=Region(vertices=a.instances['Bridge-1'].vertices.findAt(
            ((coord[0], coord[1], 0.0), ), )))

        #adds partition points for point loads in load case LM71_3
        for point in Global_coord_point_LM71_3:
            try:    
                edge = p['Bridge'].edges.findAt(point)
                p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
            except Exception as e:
                pass
        
        #adds partition points for distributed loads in load case LM71_1
        for point in Global_coord_dist_LM71_1:
            try:
                edge = p['Bridge'].edges.findAt(point)
                p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
            except Exception as e:
                pass

        #adds partition points for distributed loads in load case LM71_2
        for point in Global_coord_dist_LM71_2:
            try:
                edge = p['Bridge'].edges.findAt(point)
                p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
            except Exception as e:
                pass



        #adds partition points for distributed loads in load case LM71_2
        for point in Global_coord_dist_LM71_3:
            try:
                edge = p['Bridge'].edges.findAt(point)
                p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
            except Exception as e:
                pass
        



        #partition areas for the distributed loads in load case LM71_2 
        for partitions in reshaped_Global_coord_dist_LM71_2:
            try:
                p['Bridge'].PartitionFaceByShortestPath(
                    faces=p['Bridge'].faces.findAt(((partitions[0][0], 
                    partitions[0][1]+(partitions[1][1]-partitions[0][1])/2, 0.0), )), point1=
                    p['Bridge'].vertices.findAt((partitions[0]), ), point2=
                    p['Bridge'].vertices.findAt((partitions[1]), ))
            except Exception as e:
                pass
        
        #Creates surface for distributed load in LM71_2 
        a.regenerate()
        a.Surface(name='LM71_2_track_'+str(t_id), side1Faces=a.instances['Bridge-1'].faces.findAt(
            ((reshaped_Global_coord_dist_LM71_2[0][0][0]+(-indata['Span']/2-reshaped_Global_coord_dist_LM71_2[0][0][0])/2,reshaped_Global_coord_dist_LM71_2[0][0][1]+(reshaped_Global_coord_dist_LM71_2[0][1][1]-reshaped_Global_coord_dist_LM71_2[0][0][1])/2,0), )
            , ((reshaped_Global_coord_dist_LM71_2[1][0][0]+(indata['Span']/2-reshaped_Global_coord_dist_LM71_2[1][0][0])/2,reshaped_Global_coord_dist_LM71_2[1][0][1]+(reshaped_Global_coord_dist_LM71_2[1][1][1]-reshaped_Global_coord_dist_LM71_2[1][0][1])/2,0), ), ))
        
        #partition areas for the distributed loads in load case LM71_1 
        for partitions in reshaped_Global_coord_dist_LM71_1:
            try:
                p['Bridge'].PartitionFaceByShortestPath(
                    faces=p['Bridge'].faces.findAt(((partitions[0][0], 
                    partitions[0][1]+(partitions[1][1]-partitions[0][1])/2, 0.0), )), point1=
                    p['Bridge'].vertices.findAt((partitions[0]), ), point2=
                    p['Bridge'].vertices.findAt((partitions[1]), ))
            except Exception as e:
                pass
        



        #Creates surfaces for distributed load in LM71_1: dependant on the length of the bridge, it will be either 2 or 3 surfaces from the partitions (Because of the load case positions)
        if indata['Span']<=(indata['Span']+Global_coord_dist_LM71_1[0][0]-Global_coord_dist_LM71_2[0][0]):
            a.regenerate()
            a.Surface(name='LM71_1_track_'+str(t_id), side1Faces=
                a.instances['Bridge-1'].faces.findAt(
                ((Global_coord_dist_LM71_1[-1][0]+(Global_coord_dist_LM71_2[-1][0]-Global_coord_dist_LM71_1[-1][0])/2,Global_coord_dist_LM71_1[0][1]+(reshaped_Global_coord_dist_LM71_2[0][1][1]-Global_coord_dist_LM71_1[0][1])/2,0), )
                , ((reshaped_Global_coord_dist_LM71_2[1][0][0]+(indata['Span']/2-reshaped_Global_coord_dist_LM71_2[1][0][0])/2,reshaped_Global_coord_dist_LM71_2[1][0][1]+(reshaped_Global_coord_dist_LM71_2[1][1][1]-reshaped_Global_coord_dist_LM71_2[1][0][1])/2,0), ), ))
        else:
            a.regenerate()
            a.Surface(name='LM71_1_track_'+str(t_id), side1Faces=a.instances['Bridge-1'].faces.findAt(
                ((Global_coord_dist_LM71_1[-1][0]+(Global_coord_dist_LM71_2[0][0]-Global_coord_dist_LM71_1[-1][0])/2,Global_coord_dist_LM71_1[0][1]+(reshaped_Global_coord_dist_LM71_2[0][1][1]-Global_coord_dist_LM71_1[0][1])/2,0), )
                , ((reshaped_Global_coord_dist_LM71_2[0][0][0]+(reshaped_Global_coord_dist_LM71_2[-1][0][0]-reshaped_Global_coord_dist_LM71_2[0][0][0])/2,reshaped_Global_coord_dist_LM71_2[1][0][1]+(reshaped_Global_coord_dist_LM71_2[1][1][1]-reshaped_Global_coord_dist_LM71_2[1][0][1])/2,0), )
                , ((reshaped_Global_coord_dist_LM71_2[1][0][0]+(indata['Span']/2-reshaped_Global_coord_dist_LM71_2[1][0][0])/2,reshaped_Global_coord_dist_LM71_2[1][0][1]+(reshaped_Global_coord_dist_LM71_2[1][1][1]-reshaped_Global_coord_dist_LM71_2[1][0][1])/2,0), ), ))
        
        for partitions in reshaped_Global_coord_dist_LM71_3:
            try:
                p['Bridge'].PartitionFaceByShortestPath(
                    faces=p['Bridge'].faces.findAt(((partitions[0][0], partitions[0][1]+(partitions[1][1]-partitions[0][1])/2, 0.0), )), 
                    point1=p['Bridge'].vertices.findAt((partitions[0]), ), 
                    point2=p['Bridge'].vertices.findAt((partitions[1]), ))
            except Exception as e:
                pass
        
        #X-ccordinates for surfaces in the worst case for moment over the the support
        # if indata['Span']<=(5000+6400)*2:
        #     #3 surfaces corresponding to the distributed load
        #     X_coordinates = [(-indata['Span']/2+Global_coord_dist_LM71_3[0][0])/2,900,(indata['Span']/2+Global_coord_dist_LM71_2[-1][0])/2]
        # else:
        #     X_coordinates = [(-indata['Span']/2+Global_coord_dist_LM71_1[-1][0])/2,(Global_coord_dist_LM71_3[0][0]+Global_coord_dist_LM71_1[-1][0])/2,900,(indata['Span']/2+Global_coord_dist_LM71_2[-1][0])/2]
        #positions of partitions
        pos_1 = point_pos_LM71_1+5600
        pos_2 = point_pos_LM71_2-800
        pos_3 = point_pos_LM71_3-800

        if point_pos_LM71_3+indata['Span']/2<point_pos_LM71_2+indata['Span']/2:
            #3 surfaces corresponding to the distributed load
            X_right = [Global_coord_dist_LM71_3[-1][0]+0.1,indata['Span']/2-0.1]
        else:
            X_right = [indata['Span']/2-100]
        
        if pos_1<pos_2 and pos_2<pos_3:
            X_left = [pos_3-0.1,pos_2-0.1,-indata['Span']/2+0.1]
        elif pos_3<pos_2 and pos_1<pos_3:
            X_left = [pos_3-0.1,-indata['Span']/2+0.1]
        elif pos_3<pos_2 and pos_2<pos_1:
            X_left = [pos_3-0.1]
        elif pos_3<pos_1 and pos_1<pos_2:
            X_left = [pos_3-0.1]
        elif pos_2<pos_1 and pos_1<pos_3:
            X_left = [pos_3-0.1,pos_1-0.1,-indata['Span']/2+0.1]
        elif pos_2<pos_3 and pos_3<pos_1:
            X_left = [pos_3-0.1,-indata['Span']/2+0.1]
        elif pos_1 == pos_3 and pos_1<pos_2:
            X_left = [pos_3-0.1]
        elif pos_2 == pos_1 and pos_2<pos_3:
            X_left = [pos_3-0.1,pos_1-0.1]
        elif pos_1==pos_3 and pos_2<pos_3:
            X_left = [pos_3-0.1, pos_2-0.1]
        elif pos_2==pos_3 and pos_3<pos_1:
            X_left = [pos_3-0.1]
        elif pos_2==pos_3 and pos_3>pos_1:
            X_left = [pos_3-0.1,pos_1-0.1]
        elif pos_1==pos_2 and pos_3<pos_1:
            X_left = [pos_3-0.1]

        X_coordinates = X_right
        
        for pos in X_left:
            X_coordinates.append(pos)

       

        # if point_pos_LM71_3<point_pos_LM71_2 and point_pos_LM71_3-800>point_pos_LM71_1+5600:
        #     X_left = [point_pos_LM71_3-800-0.1,-indata['Span']/2+0.1]

        # elif point_pos_LM71_3>point_pos_LM71_2 and point_pos_LM71_1+5600<point_pos_LM71_2-800:
        #     X_left = [point_pos_LM71_3-0.1,point_pos_LM71_2-0.1,-indata['Span']/2+0.1] 

        # elif:  

        #     X_coordinates = [(-indata['Span']/2+Global_coord_dist_LM71_3[0][0])/2,900,(indata['Span']/2+Global_coord_dist_LM71_2[-1][0])/2]
        # else:
        #     X_coordinates = [(-indata['Span']/2+Global_coord_dist_LM71_1[-1][0])/2,(Global_coord_dist_LM71_3[0][0]+Global_coord_dist_LM71_1[-1][0])/2,900,(indata['Span']/2+Global_coord_dist_LM71_2[-1][0])/2]
        
        y = (w_positions[0]+w_positions[1])/2
        z = 0
        coordinates = []
        for x in X_coordinates:
            coordinates.append((x,y,z))
        surf_coord = [((x, y, z), ) for x, y, z in  coordinates]
        faces = [a.instances['Bridge-1'].faces.findAt(coord) for coord in surf_coord]
        a.Surface(name='LM71_3_track_'+str(t_id), side1Faces=faces)

        #Transforms the coordinates so is will be accepted in Brigade when creating sets for the point loads
        Global_coord_point_LM71_1_transformed = [((x, y, z), ) for x, y, z in Global_coord_point_LM71_1]
        Global_coord_point_LM71_2_transformed = [((x, y, z), ) for x, y, z in Global_coord_point_LM71_2]
        Global_coord_point_LM71_3_transformed = [((x, y, z), ) for x, y, z in Global_coord_point_LM71_3]

        inst = a.instances['Bridge-1']
        # Find the vertices at the given coordinates in LM71
        vert_LM71_1 = [inst.vertices.findAt(coord) for coord in Global_coord_point_LM71_1_transformed]
        vert_LM71_2 = [inst.vertices.findAt(coord) for coord in Global_coord_point_LM71_2_transformed]
        vert_LM71_3 = [inst.vertices.findAt(coord) for coord in Global_coord_point_LM71_3_transformed]


        #Creates partition points for point loads in LM71
        a.Set(name='Points_LM71_1_track_'+str(t_id), vertices=vert_LM71_1)
        a.Set(name='Points_LM71_2_track_'+str(t_id), vertices=vert_LM71_2)
        a.Set(name='Points_LM71_3_track_'+str(t_id), vertices=vert_LM71_3)
    
    ###############################################################################################################
    
    surface=a.surfaces
    sets = a.sets
    #Combinding surfaces of live loads, LEG_1 is added becasue the loop is weird. 
    #Parts of the first execution of the loop deletes some parts of the surface from track 2
    #Hence, all surfaces containing 'LEG_1' is combined, an thenthe combination is deleted.
    for s_name in ['LEG_1','LM71_1','LM71_2','LM71_3','SW/2']:
        #Combindiing surfaces from the tracks corrsponding to the same load case
        surfaces_LM71 = tuple(surface[name] for name in surface.keys() if s_name in name)
        
        names = []
        if s_name !='LEG_1':
            names = [n for n in surface.keys() if s_name in n]
        else:
            names.append('LEG_1')
        a.SurfaceByBoolean(name=s_name, surfaces=surfaces_LM71)

        for name in names:
            del mdb.models[indata['Model name']].rootAssembly.surfaces[name]

    #Combinding the boggi-loads from different load cases. In this for loop, the all iterations
    #works as intended
    for s_name in ['LM71_1','LM71_2','LM71_3']:
        #Combindiing Boggi loads from the tracks corrsponding to the same load case
        sets_LM71 = tuple(sets[name] for name in sets.keys() if s_name in name)
        names = [n for n in sets.keys() if s_name in n]
        
        a.SetByBoolean(name=s_name, sets=sets_LM71)

        for name in names:
            del sets[name]

    ################################
    #coordinates and partitions of the Foundation slab in case of 12m bridge. 
    #2 positions for the maximum distibuted load of 7.2 kPa. Width of the distributed load is 3m. Rest should be 2.5 kPa
    
    if indata['Manual control'] !='':
        control_span = indata['Manual control']*1000
    else:
        control_span = indata['Free span']

    if control_span == 12000:
            #Defines the foundation slab as surface:
        a.regenerate()
        a.Surface(name='Foundation', side1Faces=
            a.instances['Bridge-1'].faces.findAt(((0,indata['Width']/2,-indata['Height legs']), ), ))

        #Creates a set of the foundation slab.
        a.Set(faces=a.instances['Bridge-1'].faces.findAt(
                                                ((0, indata['Width']/2, -indata['Height legs']), ), 
                                                ((-indata['Span']/2-1, indata['Width']/2, -indata['Height legs']), ),
                                                ((indata['Span']/2+1, indata['Width']/2, -indata['Height legs']), ) ), 
                                                name='Foundation')

        Width_load = 3000                   #width of max distributed load
        X_positions = [-indata['Span']/2, -indata['Span']/2+Width_load,-Width_load/2,Width_load/2]    #Global x-coordinates for rail
        Initial_partitions_dist = []
        for x in X_positions:
            for y in [0,indata['Width']]:           #coresponds to the y-coordinates of the longitudinal edges of the bridge
                Initial_partitions_dist.append((x,y,-indata['Height legs']))
        dist_partitions_found = [Initial_partitions_dist[i:i+2] for i in range(0, len(Initial_partitions_dist),  2)]
        if len(Initial_partitions_dist) %  2 !=  0:
            dist_partitions_found.append(Initial_partitions_dist[-1:])
        

        #Creates partition points for the distributed load on the foundation
        for partitions in dist_partitions_found:
            for point in partitions:
                try:
                    edge = p['Bridge'].edges.findAt(point)
                    p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
                except Exception as e:
                    pass        
        
        #partitions the foundation deck in the positions of the distributed loads
        for partitions in dist_partitions_found[1:]:
            try:
                p['Bridge'].PartitionFaceByShortestPath(
                    faces=p['Bridge'].faces.findAt(((partitions[0][0], 
                    partitions[0][1]+(partitions[1][1]-partitions[0][1])/2, -indata['Height legs']), )), point1=
                    p['Bridge'].vertices.findAt((partitions[0]), ), 
                    point2=p['Bridge'].vertices.findAt((partitions[1]), ))
                
            except Exception as e:
                pass
            

        #Creates surfaces for the distributed load with larger magnitude
        a.regenerate()
        a.Surface(name='LM1_1', side1Faces=
            a.instances['Bridge-1'].faces.findAt(((-indata['Span']/2+Width_load/2,indata['Width']/2,-indata['Height legs']), ), ))
        
        a.regenerate()
        a.Surface(name='LM1_2', side1Faces=
            a.instances['Bridge-1'].faces.findAt(((0,indata['Width']/2,-indata['Height legs']), ), ))


        # Partition points, boggi loads on foundation in case of 12 m bridge
        xpos = [-indata['Span']/2+500,-indata['Span']/2+2500,-1000,1000,indata['Span']/2-2500,indata['Span']/2-500]         #Global x-positions for point loads
        inital_partitions_found = []
        for x in xpos:
            for y in [0,indata['Width']]:           #coresponds to the y-coordinates of the lonitudinal edges of the bridge
                inital_partitions_found.append((x,y,-indata['Height legs']))
            partitions_found = [inital_partitions_found[i:i+2] for i in range(0, len(inital_partitions_found),  2)]
        if len(inital_partitions_found ) %  2 !=  0:
            partitions_found.append(inital_partitions_found[-1:])
        
        Boggi_pos_found = []
        for x in xpos:
            for y in [250,250+1200, indata['Width']/2-600,indata['Width']/2+600,indata['Width']-(1200+250),indata['Width']-250]:           #coresponds to the y-coordinates of the lonitudinal edges of the bridge
                Boggi_pos_found.append((x,y,-indata['Height legs']))
        Boggi_pos_found_reshaped = [((x, y, z), ) for x, y, z in Boggi_pos_found]

        #Creates partition points on edges of the foundation, corresponding to the x-coordinate of the boggi-loads
        for partitions in partitions_found:
            for point in partitions:
                try:
                    edge = p['Bridge'].edges.findAt(point)
                    p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
                except Exception as e:
                    pass      

        #Partitions the lines for the boggie_loads
        for partitions in partitions_found:
            try:
                p['Bridge'].PartitionFaceByShortestPath(
                    faces=p['Bridge'].faces.findAt(((partitions[0][0], 
                    partitions[0][1]+(partitions[1][1]-partitions[0][1])/2, -indata['Height legs']), )), point1=
                    p['Bridge'].vertices.findAt((partitions[0]), ), point2=
                    p['Bridge'].vertices.findAt((partitions[1]), ))
                
            except Exception as e:
                pass

        #Create partitions points on priviously paritiond edges. Corresponding to the positions of the boggi loads
        for point in Boggi_pos_found:
            try:
                edge = p['Bridge'].edges.findAt(point)
                p['Bridge'].PartitionEdgeByPoint(edge=edge, point=point)
            except Exception as e:
                pass      

        #Stores all boggie points as vertecies
        Vert_boggie_foundation = [p['Bridge'].vertices.findAt(coord) for coord in Boggi_pos_found_reshaped]

        #Saves all boggi load positions in a set
        p['Bridge'].Set(name='Points_LM_1', vertices=Vert_boggie_foundation)       
    else:
        Boggi_pos_found = ''
        
        #Set of the foundation. Is used in the interaction with the ground 
        a.Set(faces=a.instances['Bridge-1'].faces.findAt(
                                                ((-indata['Span']/2-1, indata['Width']/2, -indata['Height legs']), ), 
                                                ((-indata['Span']/2+1, indata['Width']/2, -indata['Height legs']), ),
                                                ((indata['Span']/2-1, indata['Width']/2, -indata['Height legs']), ),
                                                ((indata['Span']/2+1, indata['Width']/2, -indata['Height legs']), ) ), 
                                                name='Foundation')

    return(x_positions_boggiloads,Width_positions,Boggi_pos_found)

def steps(indata):
    my_model_step = mdb.models[indata['Model name']].StaticLinearPerturbationStep
    my_model_step(name='SELF_WEIGHT', previous='Initial')
    my_model_step(name='BALLAST', previous='SELF_WEIGHT')
    my_model_step(name='TRACTION_TOWARDS_LEG_1', previous='BALLAST')
    my_model_step(name='TRACTION_TOWARDS_LEG_2', previous='TRACTION_TOWARDS_LEG_1')
    my_model_step(name='LM71_1', previous='TRACTION_TOWARDS_LEG_2')
    my_model_step(name='LM71_2', previous='LM71_1')
    my_model_step(name='SURCHARGE_LEG_1', previous='LM71_2')
    my_model_step(name='SURCHARGE_LEG_2', previous='SURCHARGE_LEG_1')
    my_model_step(name='LM71_3', previous='SURCHARGE_LEG_2')
    my_model_step(name='TEMP_LOAD_EXP',previous='LM71_3')
    my_model_step(name='TEMP_LOAD_CON',previous='TEMP_LOAD_EXP')
    my_model_step(name='RESTING_EARTH_PRESSURE',previous='TEMP_LOAD_CON')
    my_model_step(name='SHRINKAGE',previous='RESTING_EARTH_PRESSURE')
    my_model_step(name='NOSING_1',previous='RESTING_EARTH_PRESSURE')
    my_model_step(name='NOSING_2',previous='NOSING_1')
    

    if indata['Manual control'] !='':
        control_span = indata['Manual control']*1000
    else:
        control_span = indata['Free span']

    if control_span == 12000:
        my_model_step(name='LM_DIST_1', previous='NOSING_2')
        my_model_step(name='LM_DIST_2', previous='LM_DIST_1')
        my_model_step(name='LM_POINTS_1', previous='LM_DIST_2')
        my_model_step(name='LM_POINTS_2', previous='LM_POINTS_1')
        my_model_step(name='COATING_FOUND', previous='LM_POINTS_2')

    mdb.models[indata['Model name']].fieldOutputRequests['F-Output-1'].setValues(
        variables=('SF','U'))
    # mdb.models[indata['Model name']].fieldOutputRequests['F-Output-1'].setValues(
    # variables=('S', 'LE', 'U', 'RF', 'CF', 'SF'))

def loads_cases(indata):
    import numpy as np
    mymodel = mdb.models[indata['Model name']]
    a = mymodel.rootAssembly
    surface = a.surfaces
    pressure = mymodel.Pressure
    #Load coefficients 
    alpha = 1.33                    #Load coefficient
    
    #Dynamic factor accordign to SS-EN 1991-2 chapter 6.4.5.2
    n = 3
    k = 1.3
    Lm = (7+indata['Span']/1000+7)/n
    L_phi = k*Lm
    phi_2 = 1.44/(np.sqrt(L_phi)-0.2)+0.82
    load_factor = alpha*phi_2


    #Soil constants
    gamma = indata['Soil weight']*10**-6      #converts it from kN/m^3 to N/mm^3
    gammaM_ULS = 1.3                          #partial coefficient TK Geo13, 2.3.1
    gammaM_SLS = 1                            #partial coefficient TK Geo, chapter 3
    friction_angle_car = indata['Friction angle'] #characterist friction angle
    friction_angle_d = np.arctan(np.tan(np.radians(friction_angle_car))/gammaM_ULS)
    
    K0DA2 = 1 - np.sin(np.radians(friction_angle_car))
    K0DA3 = 1 - np.sin(friction_angle_d)

    indata.update({'K0 saftey class 2':K0DA2,'K0 saftey class 3':K0DA3})

    #geometry
    t_leg = (indata['Leg thickness top']+indata['Leg thickness bottom'])/2   #average leg thickness
    h = indata['Height legs']       #Leg height
    w = indata['Width']             # Leg width
    r_rails = indata['Rail spacing']
    #Loads 
    
    #####################################################
    #Resting earth pressure
    p_resting = round(gamma*K0DA2*indata['Height legs'],5) #Maximum earth pressure, at rest MPa or N/mm^2  

    ######################################################
    #Earth pressure due to temp inccrease, depends on the the horisontal deflection du the temp induced expansion 
    L = indata['Span']
    alpha_e = indata['exp coef']
    t0 = 10                         #casting temperature
    T_max = indata['max temp']      #Max air temp
    T_min = indata['min temp']      #Min air temp

    dTe_max = T_max+2               #corrected values according to SS-EN 1991-1-5, 6.1.3.1, TYPE 3
    dTe_min = T_min+8               #Corrected values according to SS-EN 1991-1-5, 6.1.3.1, TYPE 3

    dT_N_exp = dTe_max-t0
    dT_N_con = dTe_min-t0
     
    dTN_max = dTe_max-dTe_min       #Maximum temp-diff  SS EN 1991-1-5, 6.1.3.3

    c = 600                         #coefficient, unfavourable earth pressure due to temp loads 
    d_u_temp = round(dTN_max*alpha_e*L/2,5) #Horisontal displacement on each upper edge of the legs
    
    p_temp = round(c*gamma*d_u_temp/2,5)     #Rad Brobyggande TDOK 2016:0203, B.3.2.2.2 
    
    ########################################################
    #Shrinkage
    t_d = float(indata['Deck thickness'])
    r = float(indata['Radius'])
    l = float(indata['Span'])
    Concrete_properties = Concrete_classes(indata['Concrete class'])
    x =np.linspace(l/2,l/100-1)
    thicknesses = t_d - np.sqrt(r**2-(x)**2)+r  
    t_ave = np.average(thicknesses)

    #Cement type N 
    a_ds1 = 4 
    a_ds2 = 0.12

    fck = Concrete_properties['fck']
    fcm = Concrete_properties['fcm']
    fcm0 = 10 

    #From TRVINFRA 00227 chapter 7.1.6.1.4
    #From TRVINFRA 00227 chapter 7.1.6.1.4
    rH = 80.0
    rH0 = 100.0

    b_RH = 1.55*(1-(float(rH)/float(rH0))**3)   #Equation B.12 in SS-EN-1992-1-1
                                    
    eps_cd_0 = b_RH*0.85*((220+110*a_ds1)*np.exp(-a_ds2*fcm/fcm0))*10**-6    #Equation B.11 in SS-EN-1992-1-1
    Ac = t_ave*w
    u = w*2+t_ave*2

    h0 = 2*Ac/u                                      
    
    #interpolated kh from values from table 3.3 in SS-En 1992-1-1 
    if h0>=500:
        kh = 0.7
    elif h0<500 and h0>=300:
        kh = (0.75-0.7)/(300-500)*(h0-300)+0.75
    elif h0<300 and h0>=200:
        kh = (0.85-0.75)/(200-300)*(h0-200)+0.85
    elif h0<200 and h0>=100:
        kh = (1-0.85)/(100-200)*(h0-100)+1
    elif h0<100:
        kh = 1

    eps_cd = kh*eps_cd_0                            #Equation 3.9 in SS-EN 1992-1-1
    eps_ca = 2.5*(fck-10)*10**-6                    #Equation 3.12 in SS-EN 1992-1-1
    
    eps_cs =  eps_cd+eps_ca                 #Equation 3.8 in SS-EN 1992-1-1
    
    #Scaling the shrinkage as a temperature load
    dT_shrinkage = -eps_cs/alpha_e
    ########################################################
    #Creep
    t0 = 5
    if fcm <=35:
        phi_RH = 1 + (1-rH/100)/(0.1*h0**(0.3333))
        
    else:
        alpha_1 = (35/fcm)**0.7
        alpha_2 = (35/fcm)**0.2
        phi_RH = (1 + (1-rH/100)/(0.1*h0**(0.3333))*alpha_1)*alpha_2
    
    Beta_fcm = 16.8/np.sqrt(fcm)
    Beta_t0 = 1/(0.1+t0**0.2)

    phi0 = phi_RH*Beta_fcm*Beta_t0
    
    reduction_factor = 1/(1+phi0)
    scale_factor_deformation = 1+phi0
    indata.update({'Scale factor deformation':scale_factor_deformation})

    #########################################################
    # Earth pressure due to traction. Break nad acceleration load calulated according to SS-EN 1992, 6.5.3
    L = indata['Span']+indata['Leg thickness top']*2    #Influence length of traction force
    q_break = 22                    #Break load, kN/m, or N/mm
    q_acc = 33                      #Acceleration load, kN/m or N/mm

    t_leg = (indata['Leg thickness top']+indata['Leg thickness bottom'])/2   #average leg thickness
    h = float(indata['Height legs'])       #Leg height
    w = float(indata['Width'])             # Leg width
    r_rails = indata['Rail spacing']
        #Mximum traction force q*L will be used. 
    Q_break = q_break * L   #Total break force 
    Q_acc = q_acc * L       #Total acceleration force 

    if Q_break > 6000e3:            #Limit for break force
        Q_break = alpha*6000e3
    else:
        Q_break = alpha*Q_break
    
    if Q_acc > 1000e3:              #Limit for acceleration force
        Q_acc = alpha*1000e3
    else:
        Q_acc = alpha*Q_acc

    Q_tra = max([Q_break,Q_acc])    #Dimensioning traction force
    if indata['no tracks'] == 2:
        Q_tra = Q_tra*2
    
    I_leg = float(w)*float(t_leg)**3/12
    c = 300
    Concrete_data = Concrete_classes(indata['Concrete class'])
    E = Concrete_data['Ecm'] 

    d_u = 1                         #Assuming an inital horisontal displacement 
    R_tot = 6*E*I_leg*d_u/h**3      #Total reaction force lower edge of legs, displacement = 1mm
    dp_1 = c*gamma*d_u/2            #max earth pressure on half the height of the legs [MPa], displacement = 1mm
    dP_1 = dp_1*h/2*w               #Total earth force from earth pressure [N]
    d_u_p = Q_tra/(R_tot+dP_1)*d_u  #Scaling the displacement, finding equalibrium between forces
    p_traction = c*gamma*d_u_p/2    #Traction force 
    if indata['no tracks']==2:
        Q_tra = Q_tra/2
    q_traction = Q_tra/(indata['Span']*r_rails)
    
    ######################################################
    #Surcharge load, accordingto SS-EN 1991-2, 6.3.6.4
    Qvk= 250e3                      #shaft load, [N]
    L_train = 1600*4                #Lenght of a train carriage [mm]
    V_sur = Qvk*alpha*4/L_train
    if indata['no tracks'] ==1:
        q_surcharge = K0DA2*V_sur/w     #surcharge earth pressure
    elif indata['no tracks'] == 2:
        q_surcharge = 2*K0DA2*V_sur/w     #surcharge earth pressure, 2 trains, hence muliplied by 2
    
    c = 300
    d_u = 1                         #Assuming an inital horisontal displacement 
    R_tot = 11*E*I_leg*d_u/h**3     #Total reaction force lower edge of legs, displacement = 1mm
    
    dp_1_sur = c*gamma*d_u/2        # max earth pressure on half the height of the legs [MPa], displacement = 1mm
    dP_1_sur = dp_1_sur*h/2*w       #Total earth force from earth pressure [N]
    d_u_p = q_surcharge*h*w/(R_tot+dP_1_sur)*d_u  #Scaling the displacement, finding equalibrium between forces
    p_surcharge = c*gamma*d_u_p/2   #surcharge peak pressure second leg 

    #######################################################
    #Load case LM71, SS-EN 1991-2 
    Q = load_factor * 250e3/2             #Boggie load, shaftload/2 
    q_LM71 = load_factor * 80/r_rails     #distibuted laod as a surface pressure         

    ########################################################
    #Ballst laod 
    gamma_ballast = 20e-6           #Weight of ballast N/mm^3
    t_bal1 = 473                    #ballast thickness on the whole bridge deck
    t_bal2 = 853                    #ballast thickness beneath tracks
    q_bal_1 = t_bal1 * gamma_ballast #weight distribution over the whole width
    q_bal_2 = (t_bal2-t_bal1)*gamma_ballast #Extra ballast weight distribution beneath the tracks

    q_bal = [q_bal_1, q_bal_2]      #Distributed load, Ballast [N/mm^2]. [Distributed load over the whole width, distributed load beneath the tracks]

    ########################################################
    #Nosing force 
    Qk_nose = 100e3
    Q_nose = alpha*Qk_nose
    ########################################################
    # surface coating on foundation slab for 12m version
    t_sc = 500                      #Assuming a thickness of 500 mm
    gamma_sc = 23e-6
    q_sc = t_sc*gamma_sc

    ########################################################
    #Load case SW/2
    # q_SW_2 = alpha*150               #Distributed load, SW2 [N/mm]


    ########################################################
    #Foundation loads 
    q_LM_1 = [7.2*10**-3, 2.5*10**-3] #Distibuted loads on the foundation, [3m-segment, rest of foundation slab] [N/mm^2]
    Q_LM = [135*10**3,180*10**3]      #Boggi loads on foundation. [N/(point load)]

    ##########################################################
    #Self weight, Gravity loads for bridge parts + Ballast on top of bridge deck
    mymodel.Gravity(comp3=-9810, createStepName='SELF_WEIGHT', 
        distributionType=UNIFORM, field='', name='SELF_WEIGHT')

    pressure(createStepName='BALLAST', distributionType=UNIFORM, field='', magnitude=q_bal[0], name='Ballast_all', region=
        surface['Ballast_bridge_deck'])
    
    pressure(createStepName='BALLAST', distributionType=UNIFORM, field='', magnitude=q_bal[1], name='Ballast_track', region=
        surface['SW/2'])
    
    ############################################################
    #Resting earth pressure
    pressure(createStepName='RESTING_EARTH_PRESSURE',distributionType=HYDROSTATIC, field='', hReference=-indata['Height legs'], magnitude=p_resting, 
        name='RESTING_EARTH_PRESSURE', region=surface['Resting_earth_pressure'])
    
    ############################################################
    #Earth pressure due to temp increace
    #Expression for Hydrostatic pressure in negativ triangle on the lower part of the bridge legs.
    z0 = -indata['Height legs']/2
    z_max = -indata['Height legs']
    mymodel.ExpressionField(description='', expression='{} - (Z-{}) *{}/({}-{})'.format(p_temp,z0,p_temp,z_max,z0), localCsys=None, name='Earth_pressure_bot')
    
    pressure(createStepName='TEMP_LOAD_EXP', 
        distributionType=FIELD, field='Earth_pressure_bot', magnitude=p_temp, name='Earth_pressure_bot_temp', region=
        surface['Lower_earth_temp'])
    
    pressure(createStepName='TEMP_LOAD_EXP',distributionType=HYDROSTATIC, field='', hReference=-indata['Height legs']/2, magnitude=p_temp, 
        name='Upper_earth_temp', region=surface['Upper_earth_temp'])

    #############################################################
    #LM71_1, Point loads 
    mymodel.ConcentratedForce(cf3=-Q, createStepName=
        'LM71_1', distributionType=UNIFORM, field='', localCsys=None, name='Points_LM71_1'
        , region=a.sets['LM71_1'])
    
    #LM71_1, Distributed load
    pressure(createStepName='LM71_1', distributionType=UNIFORM, field='', magnitude=q_LM71, name='Dist_LM71_1', region=
        surface['LM71_1'])

    #############################################################
    #LM71_2, Point loads 
    mymodel.ConcentratedForce(cf3=-Q, createStepName=
        'LM71_2', distributionType=UNIFORM, field='', localCsys=None, name='Points_LM71_2'
        , region=a.sets['LM71_2'])
    
    #LM71_2, distributed loads 
    pressure(createStepName='LM71_2', distributionType=UNIFORM, field='', magnitude=q_LM71, name='Dist_LM71_2', region=
        surface['LM71_2'])
    #############################################################
    #LM71_3, Point loads 
    mymodel.ConcentratedForce(cf3=-Q, createStepName=
        'LM71_3', distributionType=UNIFORM, field='', localCsys=None, name='Points_LM71_3'
        , region=a.sets['LM71_3'])

    #LM71_3, distributed loads 
    pressure(createStepName='LM71_3', distributionType=UNIFORM, field='', magnitude=q_LM71, name='Dist_LM71_3', region=
        surface['LM71_3'])

    #############################################################
    #SW/2
    # pressure(createStepName='SW_2', distributionType=UNIFORM, field='', magnitude=q_SW_2, name='SW_2', region=
        # surface['SW/2'])

    #############################################################


    
    ##############################################################
    #Earth pressure surcharge load. 
    #Surcharge load, leg 
    legs = ['LEG_1','LEG_2']
    for n in range (2):
        mymodel.ExpressionField(description='', expression='{} - (Z-{}) *{}/({}-{})'.format(p_surcharge,z0,p_surcharge,z_max,z0), localCsys=None, name='Surcharge'+str(legs[n]))
        
        pressure(createStepName='SURCHARGE_'+str(legs[n-1]), 
            distributionType=FIELD, field='Surcharge'+str(legs[n]), magnitude=p_surcharge, name='Surcharge'+str(legs[n])+str('_lower'), region=
            surface[str(legs[n])+str('_lower')])
        
        pressure(createStepName='SURCHARGE_'+str(legs[n-1]),distributionType=HYDROSTATIC, field='', hReference=-indata['Height legs']/2, magnitude=p_surcharge, 
            name='Surcharge'+str(legs[n])+str('_upper'), region=surface[str(legs[n])+str('_upper')])
        
        pressure(createStepName='SURCHARGE_'+str(legs[n-1]),distributionType=UNIFORM, field='',  magnitude=q_surcharge, 
            name='Surcharge1'+str(legs[n-1]), region=surface[str(legs[n-1])+str('_upper')])
        
        pressure(createStepName='SURCHARGE_'+str(legs[n-1]),distributionType=UNIFORM, field='',  magnitude=q_surcharge, 
            name='Surcharge2'+str(legs[n-1]), region=surface[str(legs[n-1])+str('_lower')])
    
    ###############################################################
    #Appling traction loads a surface traction loads between the tracks
    # Traction direction, 1 and -1 in global x-direction of the bridge
    for dir in [1,-1]:
        if dir == -1:
            legs = 'LEG_1'
        else:
            legs = 'LEG_2'
        mymodel.SurfaceTraction(createStepName=
            'TRACTION_TOWARDS_'+str(legs), directionVector=((0,0,0),(dir,0,0)), distributionType=UNIFORM, field='', 
            localCsys=None, magnitude=q_traction, name='TRACTION_TOWARDS'+str(legs)+str('force'), region=
            a.surfaces['SW/2'], resultant=ON, 
            traction=GENERAL)
        
        mymodel.ExpressionField(description='', expression='{} - (Z-{}) *{}/({}-{})'.format(p_traction,z0,p_traction,z_max,z0), localCsys=None, name='Traction'+str(legs))
        
        pressure(createStepName='TRACTION_TOWARDS_'+str(legs), 
            distributionType=FIELD, field='Traction'+str(legs), magnitude=1, name='Traction'+str(legs)+str('_lower'), region=
            surface[str(legs)+str('_lower')])
        
        pressure(createStepName='TRACTION_TOWARDS_'+str(legs),distributionType=HYDROSTATIC, field='', hReference=-indata['Height legs']/2, magnitude=p_traction, 
            name='Traction'+str(legs)+str('_upper'), region=surface[str(legs)+str('_upper')])

    # Loads on Foundation slab  
    if indata['Manual control'] !='':
        control_span = indata['Manual control']*1000
    else:
        control_span = indata['Free span']

    if control_span == 12000:
        for n in range(2):
            pressure(createStepName='LM_DIST_'+str(n+1), distributionType=UNIFORM, field='', magnitude=(q_LM_1[0]-q_LM_1[1]), name='LM1_1_dist_'+str(n+1), region=
            surface['LM1_'+str(n+1)])

            pressure(createStepName='LM_DIST_'+str(n+1), distributionType=UNIFORM, field='', magnitude=q_LM_1[1], name='LM1_1_dist_whole_'+str(n+1), region=
            surface['Foundation'])
        id = 1
        for load in Q_LM:
            mymodel.ConcentratedForce(cf3=-load, createStepName=
                'LM_POINTS_'+str('{}'.format(id)), distributionType=UNIFORM, field='', localCsys=None, name='Points_LM'+str('{}'.format(id))
                , region=a.instances['Bridge-1'].sets['Points_LM_1'])
            id+=1
    
        pressure(createStepName='COATING_FOUND', distributionType=UNIFORM, field='', magnitude=q_sc, name='COATING_FOUND', region=
            surface['Foundation'])


    ##################################################################
    #Temperature loads
    mymodel.Temperature(createStepName='TEMP_LOAD_EXP', 
        crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=
        UNIFORM, magnitudes=(dT_N_exp), name='TEMP_LOAD_EXP', region=a.sets['Temp'])

    mymodel.Temperature(createStepName='TEMP_LOAD_CON', 
        crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=
        UNIFORM, magnitudes=(dT_N_con), name='TEMP_LOAD_CON', region=a.sets['Temp'])
    
    mymodel.Temperature(createStepName='SHRINKAGE', 
        crossSectionDistribution=CONSTANT_THROUGH_THICKNESS, distributionType=
        UNIFORM, magnitudes=(dT_shrinkage), name='SHRINKAGE', region=a.sets['Temp'])
    
    ####################################################################
    #Nosing force
    a.regenerate()
    nosing_keys = a.referencePoints.keys()
    if indata['no tracks'] == 2:
        ref1 = (a.referencePoints[nosing_keys[-1]], a.referencePoints[nosing_keys[-3]])
        ref2 = (a.referencePoints[nosing_keys[0]], a.referencePoints[nosing_keys[2]])
    else:
        ref1 = (a.referencePoints[nosing_keys[1]])
        ref2 = (a.referencePoints[nosing_keys[0]])
    mymodel.ConcentratedForce(cf2=Q_nose, createStepName=
        'NOSING_1', distributionType=UNIFORM, field='', localCsys=None, name=
        'Nosing_LM71_1', region=Region(referencePoints=(
        ref1, )))
    
    a.regenerate()
    nosing_keys = a.referencePoints.keys()
    mymodel.ConcentratedForce(cf2=Q_nose, createStepName=
        'NOSING_2', distributionType=UNIFORM, field='', localCsys=None, name=
        'Nosing_LM71_2', region=Region(referencePoints=(
        ref2, )))

def BC():
    import dataManagement    
    if 'on bedrock' in indata['Foundation type']:
        E_found = indata['Foundation E-modulus']            # E-modulus of packed fill material
        gamma_m = 1.3
        t_fill = 500                                        # thickness packed fill material
        kv = float(E_found)/t_fill*1.3                      # Spring thickness/m^2
    else:
        concrete_class = indata['Concrete class']
        w_foundation = indata['Width']                      # With of foundation slab 
        Epf = 50                                            # E-modulus of fill [MPa]
        tpf1 = 500                                          # thickness of fill [mm] 
        
        E_found = indata['Foundation E-modulus']            # E-modulus of soil 
        # The E-modulus of the clay is weighted down to twise the width of the foundation slab
        # IN accrdance to TRVINFRA-00227, chapter 15.1
        t_clay = 2*w_foundation-tpf1

        #Spring stiffness 
        E_hom = (Epf*tpf1 + E_found*t_clay)/(tpf1+t_clay)   # Homogenous E-modulus for fill layer and clay

        gamma_m = 1.3
        Concrete_data = Concrete_classes(concrete_class)
        E_ck = Concrete_data['Ecm']                         # Module of elasticity for foundation slab
  
        t_found = indata['Foundation thickness']            # thickenss of foundation
        v = 0.4                                             # poisson's ratio of soil

        I_found = w_foundation*t_found**3/12                

        kv =( 0.65*E_hom/(w_foundation*(1-v**2))*((E_hom*w_foundation**4)/(E_ck*I_found))**(1/12))/gamma_m  #Equation from handbok i plattgundlaggning, page 78

    mdb.customData.interaction.models[indata['Model name']].SpringToGround(name='Spring-To-Ground')
    dataManagement.modules.interaction.registerFormHandling.SpringToGround(modelName=indata['Model name'], definitionName='Spring-To-Ground', referenceCsysName='(Global)', 
                                                                               hostRegionName='Foundation', method='LINEAR_DEFINITION', 
                                                                               U1=True, U2=True, U3=True, UR1=False, UR2=False, UR3=False, 
                                                                               D11=10000, D22=300, D33=kv)

def BC1(indata):
    mymodel = mdb.models[indata['Model name']]

    if 'on bedrock' in indata['Foundation type']:
        E_found = indata['Foundation E-modulus']            # E-modulus of packed fill material
        gamma_m = 1.3
        t_fill = 500                                        # thickness packed fill material
        kv = float(E_found)/t_fill*1.3                      # Spring thickness/m^2
    else:
        concrete_class = indata['Concrete class']
        w_foundation = indata['Width']                      # With of foundation slab 
        Epf = 50                                            # E-modulus of fill [MPa]
        tpf1 = 500                                          # thickness of fill [mm] 
        
        E_found = indata['Foundation E-modulus']            # E-modulus of soil 
        # The E-modulus of the clay is weighted down to twise the width of the foundation slab
        # IN accrdance to TRVINFRA-00227, chapter 15.1
        t_clay = 2*w_foundation-tpf1

        #Spring stiffness 
        E_hom = (Epf*tpf1 + E_found*t_clay)/(tpf1+t_clay)   # Homogenous E-modulus for fill layer and clay

        gamma_m = 1.3
        Concrete_data = Concrete_classes(concrete_class)
        E_ck = Concrete_data['Ecm']                         # Module of elasticity for foundation slab
  
        t_found = indata['Foundation thickness']            # thickenss of foundation
        v = 0.4                                             # poisson's ratio of soil

        I_found = w_foundation*t_found**3/12                

        kv =( 0.65*E_hom/(w_foundation*(1-v**2))*((E_hom*w_foundation**4)/(E_ck*I_found))**(1/12))/gamma_m  #Equation from handbok i plattgundlaggning, page 78
        #creates sets of faces which the BC should be applied to.
    if indata['Manual control'] !='':
        control_span = indata['Manual control']*1000
    else:
        control_span = indata['Free span']
    
    i = mdb.models[indata['Model name']].rootAssembly.instances
    if control_span == 12000:
        #Elastic Foundation, 12 m bridge
        mymodel.ElasticFoundation(createStepName='Initial', name=
            'Foundation', stiffness=kv, surface=Region(
            side2Faces=i['Bridge-1'].faces.findAt(
            ((0.0,0.0,-indata['Height legs']), (0.0, 0.0, 1.0)),
            ((indata['Span']/2+indata['Foundation extrusion']/2,0.0,-indata['Height legs']), (0.0, 0.0, 1.0)),
            ((-indata['Span']/2-indata['Foundation extrusion']/2,0.0,-indata['Height legs']), (0.0, 0.0, 1.0)),  )))
    
        mymodel.DisplacementBC(amplitude=UNSET, createStepName=
            'Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name=
            'BC-1', region=Region(faces=i['Bridge-1'].faces.findAt(
            ((0.0,0.0,-indata['Height legs']), (0.0, 0.0, 1.0)),
            ((indata['Span']/2+indata['Foundation extrusion']/2,0.0,-indata['Height legs']), (0.0, 0.0, 1.0)),
            ((-indata['Span']/2-indata['Foundation extrusion']/2,0.0,-indata['Height legs']), (0.0, 0.0, 1.0)), )), 
            u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET)
            
    else:
        #Elastic foundation, 16 meter bridge
        mymodel.ElasticFoundation(createStepName='Initial', name=
            'Foundation', stiffness=kv, surface=Region(
            side2Faces=i['Bridge-1'].faces.findAt(
            (((-indata['Span']/2-indata['Foundation extrusion']/2), indata['Width']/2, -indata['Height legs']), (0.0, 0.0, 1.0)), 
            (((-indata['Span']/2+indata['Foundation extrusion']/2), indata['Width']/2, -indata['Height legs']), (0.0, 0.0, 1.0)), 
            (((indata['Span']/2-indata['Foundation extrusion']/2), indata['Width']/2, -indata['Height legs']), (0.0, 0.0, 1.0)), 
            (((indata['Span']/2+indata['Foundation extrusion']/2), indata['Width']/2, -indata['Height legs']), (0.0, 0.0, 1.0)), )))
        
        mymodel.DisplacementBC(amplitude=UNSET, createStepName=
            'Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name=
            'BC-1', region=Region(faces=i['Bridge-1'].faces.findAt(
            (((-indata['Span']/2-indata['Foundation extrusion']/2), indata['Width']/2, -indata['Height legs']), (0.0, 0.0, 1.0)), 
            (((-indata['Span']/2+indata['Foundation extrusion']/2), indata['Width']/2, -indata['Height legs']), (0.0, 0.0, 1.0)), 
            (((indata['Span']/2-indata['Foundation extrusion']/2), indata['Width']/2, -indata['Height legs']), (0.0, 0.0, 1.0)), 
            (((indata['Span']/2+indata['Foundation extrusion']/2), indata['Width']/2, -indata['Height legs']), (0.0, 0.0, 1.0)), )), 
            u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET)                   

def mesh(indata,mesh_size):           
    # #Enables to see thickness
    # mdb.models[indata['Model name']].FieldOutputRequest(createStepName='Step-1', name=
    #     'See_thickness_tap', variables=('STH', ))
    # mesh_size = 200
    #mesh size and meshig of the bridge
    for n in ['Bridge','Edge_beam']:
        mdb.models[indata['Model name']].parts['{}'.format(n)].seedPart(deviationFactor=0.1, 
            minSizeFactor=0.1, size=mesh_size)
        mdb.models[indata['Model name']].parts['{}'.format(n)].generateMesh()

    mdb.models[indata['Model name']].rootAssembly.regenerate()
    
def Load_combinations(indata):
    import __main__
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    import dataManagement
    data = dataManagement.modules.loadCombination.registerFormHandling.LoadGroup
    loadcombs = dataManagement.modules.loadCombination.registerFormHandling.LoadCombination
    import numpy as np
    #Different load groups depending on the varaint of the bridge
    if indata['Manual control'] !='':                               #If bridge foundation is manually set in the input
        control_span = indata['Manual control']*1000
    else:
        control_span = indata['Free span']

        
    file_path_ULS = "ULS.csv"

    if indata['no tracks'] == 2:
        file_path_SLS = "SLS_2.csv"
    else:
        file_path_SLS = "SLS_1.csv"

    ULS = np.genfromtxt(file_path_ULS, delimiter=';', skip_header=1)
    SLS = np.genfromtxt(file_path_SLS, delimiter=';', skip_header=1)
    # ['LM71_6.10A','LM71_6.10B','NOSING_6.10A','NOSING_6.10B','TEMP_6.10A','TEMP_6.10B','TRACTION_6.10A','TRACTION_6.10B','SURCHARGE_6.10A','SURCHARGE_6.10B']
    if control_span == 12000:
        load_combinations = {'LM71':['LM71_1','LM71_2','LM71_3'],'TRACTION':['TRACTION_TOWARDS_LEG_1','TRACTION_TOWARDS_LEG_2'],
                         'NOSING':['NOSING_1','NOSING_2'],'TEMP':['TEMP_LOAD_EXP','TEMP_LOAD_CON'],'SURCHARGE':['SURCHARGE_LEG_1','SURCHARGE_LEG_2'],
                         'LM1_DIST':['LM_DIST_1','LM_DIST_2']}

        Load_groups = ['LM71','TRACTION','NOSING','TEMP','SURCHARGE','LM1_DIST']
    else:
        load_combinations = {'LM71':['LM71_1','LM71_2','LM71_3'],'TRACTION':['TRACTION_TOWARDS_LEG_1','TRACTION_TOWARDS_LEG_2'],
                         'NOSING':['NOSING_1','NOSING_2'],'TEMP':['TEMP_LOAD_EXP','TEMP_LOAD_CON'],'SURCHARGE':['SURCHARGE_LEG_1','SURCHARGE_LEG_2']}

        Load_groups = ['LM71','TRACTION','NOSING','TEMP','SURCHARGE']
    

    for loads in Load_groups:
        mdb.customData.designCodes.models[indata['Model name']].LoadGroup(name=str(loads), loadGroupName=str(loads), type='LOADGROUP')
        Loads = [('{}'.format(step + str(1)), 'DESIGN_LOAD', '{}'.format(step), 'SUM_LAST_FRAME',  1,  0,  0,  0,  1,  1) for step in load_combinations[str(loads)]]

        data(modelName=indata['Model name'], loadId=str(loads), summationMethod='PICK_MOST_ADVERSE', 
            includeAllDesignLoads=True, numberOfDesignLoads=1, numberOfLoadCoefficients=1, 
            loads=(Loads), addZeroLoad=False, associatedComponents=('SF1','SF2','SF3','SF4','SF4','SF5','SM1','SM2','SM3'))
        
        mdb.customData.designCodes.models[indata['Model name']].loadGroups[str(loads)].setActive(active=True)

    
    mdb.customData.designCodes.models[indata['Model name']].LoadGroup(name='GR11_21', loadGroupName='GR11_21', type='LOADGROUP')
    mdb.customData.designCodes.models[indata['Model name']].LoadGroup(name='GR12_22', loadGroupName='GR12_22', type='LOADGROUP')
    mdb.customData.designCodes.models[indata['Model name']].LoadGroup(name='GR_LM71', loadGroupName='GR_LM71', type='LOADGROUP')

    if control_span ==12000:
        mdb.customData.designCodes.models[indata['Model name']].LoadGroup(name='GR1A_10_6A', loadGroupName='GR1A_10_6A', type='LOADGROUP')
        mdb.customData.designCodes.models[indata['Model name']].LoadGroup(name='GR1A_10_6B', loadGroupName='GR1A_10_6B', type='LOADGROUP')
        mdb.customData.designCodes.models[indata['Model name']].LoadGroup(name='GR1B', loadGroupName='GR1B', type='LOADGROUP')

        LM1_point_a = float(ULS[12][2])
        LM1_dist_a = float(ULS[13][2])

        data(modelName=indata['Model name'], loadId='GR1A_10_6A', summationMethod='CONDITIONAL', includeAllDesignLoads=True, numberOfDesignLoads=1,
            numberOfLoadCoefficients=1, loads=(('LM1_DIST1', 'LOADGROUP', 'LM1_DIST', '', LM1_dist_a, LM1_dist_a, LM1_dist_a, LM1_dist_a, 1, 1), 
                                               ('LM_POINTS_11', 'DESIGN_LOAD', 'LM_POINTS_1', 'SUM_LAST_FRAME', LM1_point_a, LM1_point_a, LM1_point_a, LM1_point_a, 1, 1)),
                                                addZeroLoad=True, associatedComponents=(('SF1','SF2','SF3','SF4','SF4','SF5','SM1','SM2','SM3')))
        
        mdb.customData.designCodes.models[indata['Model name']].loadGroups['GR1A_10_6A'].setActive(active=True)

        data(modelName=indata['Model name'], loadId='GR1A_10_6B', summationMethod='CONDITIONAL', includeAllDesignLoads=True, numberOfDesignLoads=1,
            numberOfLoadCoefficients=1, loads=(('LM1_DIST1', 'LOADGROUP', 'LM1_DIST', '', 1, 1, 1, 1, 1, 1), 
                                               ('LM_POINTS_11', 'DESIGN_LOAD', 'LM_POINTS_1', 'SUM_LAST_FRAME', 1, 1, 1, 1, 1, 1)),
                                                addZeroLoad=True, associatedComponents=(('SF1','SF2','SF3','SF4','SF4','SF5','SM1','SM2','SM3')))
        
        mdb.customData.designCodes.models[indata['Model name']].loadGroups['GR1A_10_6B'].setActive(active=True)

        data(modelName=indata['Model name'], loadId='GR1B', summationMethod='PICK_MOST_ADVERSE', includeAllDesignLoads=True, numberOfDesignLoads=1,
            numberOfLoadCoefficients=1, loads=(('GR1A_10_6B1', 'LOADGROUP', 'GR1A_10_6B', '', 1, 0, 0, 0, 1, 1), 
                                               ('LM_POINTS_21', 'DESIGN_LOAD', 'LM_POINTS_2', 'SUM_LAST_FRAME', 1, 0, 0, 0, 1, 1)),
                                                addZeroLoad=True, associatedComponents=(('SF1','SF2','SF3','SF4','SF4','SF5','SM1','SM2','SM3')))

        mdb.customData.designCodes.models[indata['Model name']].loadGroups['GR1B'].setActive(active=True)


    data(modelName=indata['Model name'], loadId='GR11_21', summationMethod='CONDITIONAL', includeAllDesignLoads=True, numberOfDesignLoads=1,
        numberOfLoadCoefficients=1, loads=(('LM711', 'LOADGROUP', 'LM71', '', 1, 1, 1, 1, 1, 1), ('NOSING1', 'LOADGROUP', 'NOSING', '', 1, 1, 1, 1, 1, 1), 
                                           ('SURCHARGE1', 'LOADGROUP', 'SURCHARGE', '', 0.5, 0.5, 0.5, 0.5, 1, 1)), addZeroLoad=True, associatedComponents=(('SF1','SF2','SF3','SF4','SF4','SF5','SM1','SM2','SM3')))
    
    mdb.customData.designCodes.models[indata['Model name']].loadGroups['GR11_21'].setActive(active=True)

    data(modelName=indata['Model name'], loadId='GR12_22', summationMethod='CONDITIONAL', includeAllDesignLoads=True, numberOfDesignLoads=1,
        numberOfLoadCoefficients=1, loads=(('LM711', 'LOADGROUP', 'LM71', '', 1, 1, 1, 1, 1, 1), ('NOSING1', 'LOADGROUP', 'NOSING', '', 0.5, 0.5, 0.5, 0.5, 1, 1), 
                                           ('SURCHARGE1', 'LOADGROUP', 'SURCHARGE', '', 1, 1, 1, 1, 1, 1)), addZeroLoad=True, associatedComponents=(('SF1','SF2','SF3','SF4','SF4','SF5','SM1','SM2','SM3')))
    
    mdb.customData.designCodes.models[indata['Model name']].loadGroups['GR12_22'].setActive(active=True)

    data(modelName=indata['Model name'], loadId='GR_LM71', summationMethod='PICK_MOST_ADVERSE', includeAllDesignLoads=True, numberOfDesignLoads=1,
        numberOfLoadCoefficients=1, loads=(('GR11_211', 'LOADGROUP', 'GR11_21', '', 1, 1, 1, 1, 1, 1), ('GR12_221', 'LOADGROUP', 'GR12_22', '', 1, 1, 1, 1, 1, 1)), 
        addZeroLoad=True, associatedComponents=(('SF1','SF2','SF3','SF4','SF4','SF5','SM1','SM2','SM3')))
    
    mdb.customData.designCodes.models[indata['Model name']].loadGroups['GR_LM71'].setActive(active=True)

    #ULS COEFFICIENTS

    Permanent_loads = ['SELF_WEIGHT','BALLAST','SHRINKAGE','RESTING_EARTH_PRESSURE']
    for combination in ['SIXTENA','SIXTENB']:
        Perm_loads = []
        mdb.customData.designCodes.models[indata['Model name']].LoadCombination(name=str(combination), loadCombinationName=str(combination),)
        if combination =='SIXTENA':
            i = 2
            j = 3
        elif combination == 'SIXTENB':
            i = 4
            j = 5
        for n in range(len(Permanent_loads)):
            #Earth pressure is multplied with a factor taking saftey factor 3 into account. The analysis is performed with K0 for characteristic values
            # Hence the unfavourable factor is multiplied with K0_3/K0_2 
            if ULS[0][0] == 3 and Permanent_loads[n]=='RESTING_EARTH_PRESSURE':
                factor = float(indata['K0 saftey class 3'])*1.1/(1.35*float(indata['K0 saftey class 2']))
                # factor = float(indata['K0 saftey class 3'])/(float(indata['K0 saftey class 2']))
            else:
                factor = 1
            step_ = Permanent_loads[n]
            pos = n+1
            unfav = float(np.around(float(ULS[pos][i])*factor, decimals=2))
            fave = float(ULS[pos][j])
            Perm_loads.append((str(step_)+'1', 'DESIGN_LOAD', str(step_), 'SUM_LAST_FRAME',unfav,fave,  1,  1))

        if ULS[0][0] == 3:
            factor = float(indata['K0 saftey class 3'])*1.4/(1.5*float(indata['K0 saftey class 2']))
            # factor = float(indata['K0 saftey class 3'])/(float(indata['K0 saftey class 2']))
        else:
            factor = 1

        gr11 = [float(ULS[6][i]),float(ULS[6][j])]
        temp = [float(ULS[15][i]),float(ULS[15][j])]
        sur = [np.round(float(ULS[16][i])*factor, decimals=2),np.round(float(ULS[16][j])*factor, decimals=2)]

        if control_span == 12000:
            LM_a = [1,1]                                        #Factors aleardy in Load group
            LM_b = [float(ULS[14][i]),float(ULS[14][j])]
            if combination == 'SIXTENB':
                Load_factors = {'GR_LM71':gr11,'TEMP':temp,'SURCHARGE':sur,'GR1B':LM_b}
            elif combination == 'SIXTENA':
                Load_factors = {'GR_LM71':gr11,'TEMP':temp,'SURCHARGE':sur,'GR1A_10_6A':LM_a}
        else:
            Load_factors = {'GR_LM71':gr11,'TEMP':temp,'SURCHARGE':sur}
        
        Variable_load = []
        for key in list(Load_factors.keys()):
            f = Load_factors[key]

            Variable_load.append((str(key)+'1', 'LOADGROUP', str(key), '',  float(f[0]),  float(f[1]),  float(f[1]),  float(f[1]),  1,  1))
            
        mdb.customData.designCodes.models[indata['Model name']].LoadCombination(name=str(combination), loadCombinationName=str(combination))

        loadcombs(modelName=indata['Model name'], loadId=str(combination), 
                  summationMethod='SUM_USER_DEFINED', includeAllDesignLoads=True, numberOfDesignLoads=1, numberOfLoadCoefficients=4, 
                  permanentLoads=(Perm_loads),variableLoads=(Variable_load), 
                addZeroLoad=True, associatedComponents=('SF1','SF2','SF3','SF4','SF4','SF5','SM1','SM2','SM3'))

        mdb.customData.designCodes.models[indata['Model name']].loadCombinations[str(combination)].setActive(active=True)
        


    #######################################################################################################################################
    # SLS 
    for combination in ['SLS_FREQUENT','SLS_QUASI']:
        Perm_loads = []
        
        if combination =='SLS_FREQUENT':
            i = 4
            j = 5
            SCALE_FACTOR = 1
        elif combination == 'SLS_QUASI':
            i = 6
            j = 7
            SCALE_FACTOR = indata['Scale factor deformation']
        for n in range(len(Permanent_loads)):
            #Earth pressure is multplied with a factor taking saftey factor 3 into account. The analysis is performed with K0 for characteristic values
            # Hence the unfavourable factor is multiplied with K0_3/K0_2 
            step_ = Permanent_loads[n]
            pos = n+1
            unfav = float(SLS[pos][i])
            fave = float(SLS[pos][j])
            Perm_loads.append((str(step_)+'11', 'DESIGN_LOAD', str(step_), 'SUM_LAST_FRAME',unfav,fave,  float(SCALE_FACTOR),  1))

        gr11 = [float(SLS[6][i]),float(SLS[6][j])]
        temp = [float(SLS[14][i]),float(SLS[14][j])]
        sur = [float(SLS[15][i]),float(SLS[15][j])]
        
        if control_span == 12000:
            if combination == 'SLS_FREQUENT':
                LM_a = [0.66,0] 
                Load_factors = {'GR_LM71':gr11,'TEMP':temp,'SURCHARGE':sur,'GR1A_10_6A':LM_a}
            else:
                Load_factors = {'TEMP':temp}
        else:
            if combination == 'SLS_FREQUENT':
                Load_factors = {'GR_LM71':gr11,'TEMP':temp,'SURCHARGE':sur}
            else:
                Load_factors = {'TEMP':temp}
        
        
        if combination == 'SLS_QUASI':
            Variable_load = []
            for key in list(Load_factors.keys()):
                f = Load_factors[key]
                Variable_load.append((str(key)+'1', 'LOADGROUP', str(key), '',  float(f[0]),  0,  0,  0,  1,  1))

                mdb.customData.designCodes.models[indata['Model name']].LoadCombination(name=str(combination), loadCombinationName=str(combination))

                loadcombs(modelName=indata['Model name'], loadId=str(combination), 
                        summationMethod='PICK_MOST_ADVERSE', includeAllDesignLoads=True, numberOfDesignLoads=1, numberOfLoadCoefficients=4, 
                        permanentLoads=(Perm_loads),variableLoads=((str(key)+'1', 'LOADGROUP', str(key), '',  float(f[0]),  0,  0,  0,  1,  1),('TEMP1'+str(5), 'LOADGROUP', 'TEMP', '',  float(temp[0]), 0 ,  0,  0,  1,  1)), 
                        addZeroLoad=True, associatedComponents=())
                mdb.customData.designCodes.models[indata['Model name']].loadCombinations[str(combination)].setActive(active=True)
        else:
            id = 1
            Variable_load = {}
            for key in list(Load_factors.keys()):
                f = Load_factors[key]

                mdb.customData.designCodes.models[indata['Model name']].LoadCombination(name=str(combination)+str(key), loadCombinationName=str(combination)+str(key))

                if 'TEMP' in key:
                    variable_load = ((str(key)+'1', 'LOADGROUP', str(key), '',  float(f[0]),  0,  0,  0,  1,  1),('TEMP1'+str(id), 'LOADGROUP', 'TEMP', '',  float(temp[1]), 0 ,  0,  0,  1,  1))
                else:
                    variable_load = ((str(key)+'1', 'LOADGROUP', str(key), '',  float(f[0]),  0,  0,  0,  1,  1),('TEMP1'+str(id), 'LOADGROUP', 'TEMP', '',  float(temp[1]), float(temp[1]) ,  0,  0,  1,  1))

                loadcombs(modelName=indata['Model name'], loadId=str(combination)+str(key), 
                        summationMethod='SUM_USER_DEFINED', includeAllDesignLoads=True, numberOfDesignLoads=1, numberOfLoadCoefficients=4, 
                        permanentLoads=(Perm_loads),variableLoads = variable_load, 
                        addZeroLoad=True, associatedComponents=()) 
                mdb.customData.designCodes.models[indata['Model name']].loadCombinations[str(combination)+str(key)].setActive(active=True)

                id+=1
    Load_comb = mdb.customData.designCodes.models[indata['Model name']].loadCombinations.keys()

    return Load_comb

def run_job(indata):
    jobname = indata['Model name']
    # mdb.Job(model=jobname, name=jobname)
    # mdb.jobs[jobname].setValues(description='', memory=90, memoryUnits=PERCENTAGE, 
    #     numCpus=1, numDomains=1)
    mdb.Job(name=jobname, model=indata['Model name'])
    job = mdb.jobs[jobname]
    job.setValues(description='', memoryUnits=PERCENTAGE, memory=95, numCpus=4, numDomains=4)
    job.setValues(queue='BrigadePlusQueue')
    job.submit(datacheckJob=False)
    # mdb.jobs['Job-1']._Message(JOB_COMPLETED, {'jobName': 'Job-1', 
    #     'time': 'Fri Mar 01 09:42:05 2024'})
    job.waitForCompletion()
    status = job.status
    return status
    # job.status 

def Results(indata,Load_comb,x_coords,y_coord,file_path):
    from operator import itemgetter
    import numpy as np
    import visualization
    #The prmemise is to devide the deck into 3 sections. On at each support and one in the center. The moment curves 
    #from all load combinations dictates where these sections starts and ends. 
    jobname = indata['Model name']
    try:
        o1 = session.openOdb(name=file_path+str(jobname)+'.odb')
        sess = session.viewports['Viewport: 1']
        sess.setValues(displayedObject=o1)
    except:
        pass
    
    if indata['Manual control'] !='':                               #If bridge foundation is manually set in the input
        control_span = indata['Manual control']*1000
    else:
        control_span = indata['Free span']
    #Extracts all the names of the load combinations
    load_combinations = Load_comb
    
    ####################################################################################################
    #Finding x-cordinate where moment is no longer positive or no longer negative
    #path in the center of the bridge and center of foundation:
    session.Path(name='Bridge deck', type=POINT_LIST, expression=((-indata['Span']/2,indata['Width']/2,0),(indata['Span']/2,indata['Width']/2,0)))
    session.Path(name='Foundation', type=POINT_LIST, expression=((-indata['Span']/2,indata['Width']/2,-indata['Height legs']),(indata['Span']/2,indata['Width']/2,-indata['Height legs'])))
    #Initial coordinates for when positive and negative moments change
    moment_x_bridge = {}
    if control_span == 12000:
        Moment_position_parts = ['Bridge deck','Foundation']
    else:
        Moment_position_parts = ['Bridge deck']
    for parts in Moment_position_parts:
        x_neg=indata['Span']
        x_pos=0
        for load_comb in [loads for loads in load_combinations if 'SLS' not in loads]:
            for f in [0,1]:
                #Changing the step which data is picked from 
                sess.odbDisplay.setFrame(step=load_comb, frame=f)

                #Changing the variable which data is picked from 
                sess.odbDisplay.setPrimaryVariable(variableLabel='SM', outputPosition=INTEGRATION_POINT, 
                    refinement=(COMPONENT, 'SM1'))

                session.XYDataFromPath(name='XY_data', path=session.paths[str(parts)], includeIntersections=False, 
                    projectOntoMesh=False, pathStyle=UNIFORM_SPACING, numIntervals=(int(indata['Span']/100+1)), 
                    projectionTolerance=0, shape=UNDEFORMED, labelType=TRUE_DISTANCE, 
                    removeDuplicateXYPairs=True, includeAllElements=False)

                x0 = session.xyDataObjects['XY_data'].data
                x0 = list(x0) 
                
                if int(x0[0][0]) == int(x0[1][0]):
                    array = [x for x in x0 if x[0] == x0[0][0]]
                    a = np.array([y for x,y in array])
                    a_len = len(a)
                    index_of_closest = np.abs(a - x0[a_len][1]).argmin()
                    to_add = (x0[0][0],a[index_of_closest])
                    del x0[:(a_len+1)]
                    x0.insert(0,to_add)
                
                #There might be several other points which lay in the end position of the path, 
                #this code saves the maxvalue in the end node
                if int(x0[-1][0]) == int(x0[-2][0]):
                    array = [x for x in x0 if x[0] == x0[-1][0]]
                    a = np.array([y for x,y in array])
                    a_len = len(a)
                    index_of_closest = np.abs(a - x0[-a_len-1][1]).argmin()
                    to_add = (x0[-1][0],a[index_of_closest])
                    del x0[-a_len:]
                    x0.append(to_add)

                mom = np.array([x[1] for x in x0 if x[0]<indata['Span']/2])
                if parts=='Foundation':
                    position=np.argmin(abs(mom))  #Foundation moment reaches 0 Nmm close to the center but decreases very rapidaly 
                else:
                    position = np.argmin(abs(mom+600e3))
                x_coord = x0[position][0]
                if x_coord < x_neg:
                    x_neg = x_coord
                elif x_coord>x_pos:
                    x_pos = x_coord

                moment_x_bridge.update({'{}'.format(parts):{'x neg':x_neg,'x pos':x_pos}})
    
    
    x_neg_b = moment_x_bridge['Bridge deck']['x neg']
    x_pos_b = moment_x_bridge['Bridge deck']['x neg']
    if x_neg_b <1500:
        x_neg_b = 1500
        x_pos_b = 1500
    moment_x_bridge.update({'Bridge deck':{'x neg':x_neg_b,'x pos':x_pos_b}})
    if control_span == 12000:
        x_pos_f = moment_x_bridge['Foundation']['x pos']
    
    #The Shear force should be taken undeneath a point load take the local effects into account
    #The closest Boggi axel from the case with largest shear force in the support is to be used to
    #to determening which point load corresponding the best to the x_pos and x_neg coordinates above. 

    # Shear_pos_center = np.array(x_coords[0])
    # diff = abs(Shear_pos_center-(x_neg-indata['Span']/2))
    # pos = np.argmin(diff)
    # x_shear_span = x_coords[0][pos]

    # #y-coordinate of rail 2 on track 1
    # y_t1_r2 = y_coord[0][1]


    path_coord = [{'Name':'Bridge deck support','coord':(('Center_b_deck_sup1',[-indata['Span']/2,indata['Width']/2,0],[x_pos_b-indata['Span']/2,indata['Width']/2,0]),
                                                         ('Center_b_deck_sup2',[indata['Span']/2,indata['Width']/2,0],[indata['Span']/2-x_pos_b,indata['Width']/2,0]),
                                                         ('Edge_b_deck_sup1',[-indata['Span']/2,1000,0],[x_pos_b-indata['Span']/2,1000,0]),
                                                         ('Edge_b_deck_sup2',[indata['Span']/2,1000,0],[indata['Span']/2-x_pos_b,1000,0]),
                                                         ('Transversal_Moment',[indata['Span']/2-500,0,0],[indata['Span']/2-500,indata['Width'],0]),
                                                         ('Transversal_Moment_2',[indata['Span']/2-x_pos_b/2,0,0],[indata['Span']/2-x_pos_b/2,indata['Width'],0]),
                                                         ('Transversal_Moment_3',[indata['Span']/2-x_pos_b,0,0],[indata['Span']/2-x_pos_b,indata['Width'],0]),
                                                         ('Transversal_Moment_4',[-indata['Span']/2+500,0,0],[-indata['Span']/2+500,indata['Width'],0]),
                                                         ('Transversal_Moment_5',[x_pos_b/2-indata['Span']/2,0,0],[x_pos_b/2-indata['Span']/2,indata['Width'],0]),)},

                {'Name':'Bridge deck span','coord':(('Center_b_deck_span',[x_neg_b-indata['Span']/2,indata['Width']/2,0],[indata['Span']/2-x_neg_b,indata['Width']/2,0]),
                                                    ('Edge_b_deck_span',[x_neg_b-indata['Span']/2,500,0],[indata['Span']/2-x_neg_b,500,0]),
                                                    ('Transversal_Moment_6',[0,0,0],[0,indata['Width'],0]),
                                                    ('Transversal_Moment_7',[(-indata['Span']/2+x_neg_b)/2,0,0],[(-indata['Span']/2+x_neg_b)/2,indata['Width'],0]),
                                                    ('Transversal_Moment_8',[(indata['Span']/2-x_neg_b)/2,0,0],[(indata['Span']/2-x_neg_b)/2,indata['Width'],0]),
                                                    ('Transversal_Moment_9',[indata['Span']/2-x_neg_b,0,0],[indata['Span']/2-x_neg_b,indata['Width'],0]))},

                {'Name':'Legs upper','coord':(('Central upper',[-indata['Span']/2,indata['Width']/2,0],[-indata['Span']/2,indata['Width']/2,-indata['Height legs']/2]),
                                              ('Central upper_2',[indata['Span']/2,indata['Width']/2,0],[indata['Span']/2,indata['Width']/2,-indata['Height legs']/2]),
                                              ('End_one_upper_leg',[-indata['Span']/2,1000,0],[-indata['Span']/2,1000,-indata['Height legs']/2]),
                                              ('End_two_upper_leg',[indata['Span']/2,1000,0],[indata['Span']/2,1000,-indata['Height legs']/2]),
                                              ('Transversal_Moment_10',[-indata['Span']/2,0,-100],[-indata['Span']/2,indata['Width'],-100]),
                                              ('Transversal_Moment_11',[indata['Span']/2,0,-100],[indata['Span']/2,indata['Width'],-100]),
                                              ('Transversal_Moment_12',[-indata['Span']/2,0,-indata['Height legs']/4],[-indata['Span']/2,indata['Width'],-indata['Height legs']/4]),
                                              ('Transversal_Moment_13',[indata['Span']/2,0,-indata['Height legs']/4],[indata['Span']/2,indata['Width'],-indata['Height legs']/4]))},

                {'Name':'Legs lower','coord':(('Central lower',[-indata['Span']/2,indata['Width']/2,-indata['Height legs']/2],[-indata['Span']/2,indata['Width']/2,-indata['Height legs']]),
                                              ('Central lower_2',[indata['Span']/2,indata['Width']/2,-indata['Height legs']/2],[indata['Span']/2,indata['Width']/2,-indata['Height legs']]),
                                              ('End_one_lower_leg',[-indata['Span']/2,1000,-indata['Height legs']/2],[-indata['Span']/2,1000,-indata['Height legs']]),
                                              ('End_two_lower_leg',[indata['Span']/2,1000,-indata['Height legs']/2],[indata['Span']/2,1000,-indata['Height legs']]),
                                              ('Transversal_Moment_14',[-indata['Span']/2,0,-indata['Height legs']],[-indata['Span']/2,indata['Width'],-indata['Height legs']]),
                                              ('Transversal_Moment_15',[indata['Span']/2,0,-indata['Height legs']],[indata['Span']/2,indata['Width'],-indata['Height legs']]),
                                              ('Transversal_Moment_16',[-indata['Span']/2,0,-indata['Height legs']*3/4],[-indata['Span']/2,indata['Width'],-indata['Height legs']*3/4]),
                                              ('Transversal_Moment_17',[indata['Span']/2,0,-indata['Height legs']*3/4],[indata['Span']/2,indata['Width'],-indata['Height legs']*3/4]))},]


    if control_span == 12000:
        x = [-indata['Span']/2-indata['Foundation extrustion'],x_pos_f]
        Foundation={'Name':'Foundation footing','coord':(
                                            ('Moment along found',[x[0],indata['Width']/2,-indata['Height legs']],[x[1],indata['Width']/2,-indata['Height legs']]),
                                            ('Moment along found edge',[x[0],500,-indata['Height legs']],[x[1],500,-indata['Height legs']]),
                                            ('Transversal_moment_17',[-indata['Span']/2-100,0,-indata['Height legs']],[-indata['Span']/2,indata['Width'],-indata['Height legs']]),
                                            ('Transversal_moment_17',[indata['Span']/2-100,0,-indata['Height legs']],[indata['Span']/2,indata['Width'],-indata['Height legs']]))}

        Rest_of_foundation = {'Name':'Foundation_12','coord':(
                                ('Moment along found',[-indata['Span']/2+x_pos_f,indata['Width']/2,-indata['Height legs']],[indata['Span']/2-x_pos_f,indata['Width']/2,-indata['Height legs']]),
                                ('Moment along found_edge',[-indata['Span']/2+x_pos_f,500,-indata['Height legs']],[indata['Span']/2-x_pos_f,500,-indata['Height legs']]))}
        path_coord.append(Foundation)
        path_coord.append(Rest_of_foundation)
    else:
        #Coordinates of footings
        x = [-indata['Span']/2-(indata['Foundation length']-indata['Foundation extrustion']),-indata['Span']/2+indata['Foundation extrustion']]
        Foundation = {'Name':'Foundation footing','coord':(
                                ('Moment along found',[x[0],indata['Width']/2,-indata['Height legs']],[x[1],indata['Width']/2,-indata['Height legs']]),
                                ('Moment along found edge',[x[0],500,-indata['Height legs']],[x[1],500,-indata['Height legs']]),
                                ('Transversal_Moment_17',[-indata['Span']/2-100,0,-indata['Height legs']],[-indata['Span']/2,indata['Width'],-indata['Height legs']]),
                                ('Transversal_Moment_17',[indata['Span']/2-100,0,-indata['Height legs']],[indata['Span']/2,indata['Width'],-indata['Height legs']]))}
        path_coord.append(Foundation)
    
    
    variables = [('SM',('SM1','SM2','SM3')),('SF',('SF1','SF4','SF5'))]

    SM1 ={}
    SM2 = {}
    SM3 = {}
    SF1 = {}
    SF4 = {}
    SF5 = {}
    SF5_SF4_comb={}
    
    Path = []
    
    for paths in path_coord:
        name = paths['Name']
        # shear_force={}
        for p in paths['coord']:
            path = session.Path(name=p[0], type=POINT_LIST, expression=(p[1],p[2]))
            # VEd = 0
            if 'Transversal_Moment' in p[0]:
                for comb in [loads for loads in load_combinations if 'SLS' not in loads]:
                    for f in [0,1]:
                        x_tot = []
                        var = 'SM'
                        vari = ['SM2','SM3']
                        for comp in vari:
                        
                            #Adresses which step to extract data from
                            sess.odbDisplay.setFrame(step=str(comb), frame=f)

                            #Changing the variable which data is picked from 
                            sess.odbDisplay.setPrimaryVariable(
                                variableLabel=var, outputPosition=INTEGRATION_POINT, refinement=(
                                COMPONENT, comp))
                            
                            #number of intervals to evaluated on the paths. Setting the evaluation point spacing to 100 mm. 

                            num_intervals = indata['Width']/100+1
        

                            #Extracts data from the paths 
                            session.XYDataFromPath(name='XY_data-'+str(path.name)+str(comb), path=path, includeIntersections=False, 
                                projectOntoMesh=False, pathStyle=UNIFORM_SPACING, numIntervals=num_intervals, 
                                projectionTolerance=0, shape=UNDEFORMED, labelType=TRUE_DISTANCE, 
                                removeDuplicateXYPairs=True, includeAllElements=False)

                            for keys in [key for key in session.xyDataObjects.keys() if 'temp' in key]:
                                del session.xyDataObjects[str(keys)]


                            #exctracts the data obtained from the path, and assigns it to a variable x
                            data_data = session.xyDataObjects['XY_data-'+str(path.name)+str(comb)].data
                            x0 = list(data_data)
                            #Legs and Bridge deck are connected. Outlier on the path extracts two values. One for the 
                            #top of the legs and on for the bridge deck. Hence, the following code is applied, where it is assumed the
                            #moments have different signs in these connection points. Meaning the moment in the top of the leg is negative and in the bridge deck it
                            #is positive. The code evaluates the sign of the variable in the next position on the path, and keeps the value in the end points which has
                            #the same sign. 
                            
                            if int(x0[0][0]) == int(x0[1][0]):
                                array = [x for x in x0 if x[0] == x0[0][0]]
                                a = np.array([y for x,y in array])
                                a_len = len(a)
                                index_of_closest = np.abs(a - x0[a_len][1]).argmin()
                                to_add = (x0[0][0],a[index_of_closest])
                                del x0[:(a_len+1)]
                                x0.insert(0,to_add)
                            
                            #There might be several other points which lay in the end position of the path, 
                            #this code saves the maxvalue in the end node
                            if int(x0[-1][0]) == int(x0[-2][0]):
                                array = [x for x in x0 if x[0] == x0[-1][0]]
                                a = np.array([y for x,y in array])
                                a_len = len(a)
                                index_of_closest = np.abs(a - x0[-a_len-1][1]).argmin()
                                to_add = (x0[-1][0],a[index_of_closest])
                                del x0[-a_len:]
                                x0.append(to_add)

                            x_tot.append(x0)    
                        SM2.update({str(path.name)+'-'+str(comb)+str(f):x_tot[0]})
                        SM3.update({str(path.name)+'-'+str(comb)+str(f):x_tot[1]})
            else:
                for comb in [loads for loads in load_combinations if 'SLS' not in loads]:    
                    for f in [0,1]:
                        x_tot = []
                        for var in variables:
                            for comp in var[1]:
                            
                                #Adresses which step to extract data from
                                sess.odbDisplay.setFrame(step=str(comb), frame=f)

                                #Changing the variable which data is picked from 
                                sess.odbDisplay.setPrimaryVariable(
                                    variableLabel=var[0], outputPosition=INTEGRATION_POINT, refinement=(
                                    COMPONENT, comp))
                                
                                #number of intervals to evaluated on the paths. Setting the evaluation point spacing to 100 mm. 
                                if name =='Bridge deck':
                                    num_intervals = int(indata['Span']/100+1)
                                elif name == 'Legs':
                                    num_intervals = int(indata['Height legs']/100+1)
                                else: 
                                    num_intervals = int(indata['Foundation length']/100+1)

                                #Extracts data from the paths 
                                session.XYDataFromPath(name='XY_data-'+str(path.name)+str(comb), path=path, includeIntersections=False, 
                                    projectOntoMesh=False, pathStyle=UNIFORM_SPACING, numIntervals=num_intervals, 
                                    projectionTolerance=0, shape=UNDEFORMED, labelType=TRUE_DISTANCE, 
                                    removeDuplicateXYPairs=True, includeAllElements=False)

                                for keys in [key for key in session.xyDataObjects.keys() if 'temp' in key]:
                                    del session.xyDataObjects[str(keys)]


                                #exctracts the data obtained from the path, and assigns it to a variable x
                                data_data = session.xyDataObjects['XY_data-'+str(path.name)+str(comb)].data
                                x0 = list(data_data)
                                #Legs and Bridge deck are connected. Outlier on the path extracts two values. One for the 
                                #top of the legs and on for the bridge deck. Hence, the following code is applied, where it is assumed the
                                #moments have different signs in these connection points. Meaning the moment in the top of the leg is negative and in the bridge deck it
                                #is positive. The code evaluates the sign of the variable in the next position on the path, and keeps the value in the end points which has
                                #the same sign. 
                                
                                if int(x0[0][0]) == int(x0[1][0]):
                                    array = [x for x in x0 if x[0] == x0[0][0]]
                                    a = np.array([y for x,y in array])
                                    a_len = len(a)
                                    index_of_closest = np.abs(a - x0[a_len][1]).argmin()
                                    to_add = (x0[0][0],a[index_of_closest])
                                    del x0[:(a_len+1)]
                                    x0.insert(0,to_add)
                                
                                #There might be several other points which lay in the end position of the path, 
                                #this code saves the maxvalue in the end node
                                if int(x0[-1][0]) == int(x0[-2][0]):
                                    array = [x for x in x0 if x[0] == x0[-1][0]]
                                    a = np.array([y for x,y in array])
                                    a_len = len(a)
                                    index_of_closest = np.abs(a - x0[-a_len-1][1]).argmin()
                                    to_add = (x0[-1][0],a[index_of_closest])
                                    del x0[-a_len:]
                                    x0.append(to_add)

                                x_tot.append(x0)

                        #Saves the data in the correct directory. 
                        SM1.update({str(path.name)+'-'+str(comb)+str(f):x_tot[0]})
                        SM2.update({str(path.name)+'-'+str(comb)+str(f):x_tot[1]})
                        SM3.update({str(path.name)+'-'+str(comb)+str(f):x_tot[2]})
                        SF1.update({str(path.name)+'-'+str(comb)+str(f):x_tot[3]})
                        SF4.update({str(path.name)+'-'+str(comb)+str(f):x_tot[4]})
                        SF5.update({str(path.name)+'-'+str(comb)+str(f):x_tot[5]})

    # Extracts the maximum and minimum sectional forces from the different load combinations and saves them
    # in a dictionary called 'Results' according to the bridge part. So, i.e in Results['Bridge deck'] all max
    # and min values are stored.  
    Results={}
    for paths in path_coord:                    #path groups corresonding to each part of the bridge, i.e (Bridge deck, Legs, Foundations
        name = paths['Name']                    #bridge part name
        #Creates sub dictionaries for all sectional forces
        maximumSM1 = {'Max':[0,''],'Min':[0,''],'Load combination max':'','Load combination min':''}                 
        maximumSM2 = {'Max':[0,''],'Min':[0,''],'Load combination max':'','Load combination min':''}
        maximumSM3 = {'Max':[0,''],'Min':[0,''],'Load combination max':'','Load combination min':''}
        maximumSF1 = {'Max':[0,''],'Min':[0,''],'Load combination max':'','Load combination min':''}
        maximumSF4 = {'Max':[0,''],'Min':[0,''],'Load combination max':'','Load combination min':''}
        maximumSF5 = {'Max':[0,''],'Min':[0,''],'Load combination max':'','Load combination min':''}

        for pth in paths['coord']:                       
            pth_name = pth[0]                   #path names of paths on the corresponding bridge part

            if 'Transversal_Moment' in pth_name:
                for f in [0,1]:
                    for comb in [loads for loads in load_combinations if 'SLS' not in loads]:
                        sm2_max = max(SM2[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sm2_min = min(SM2[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sm3_max = max(SM3[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sm3_min = min(SM3[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
            
                        #Storage for SM2
                        if sm2_max[1]>maximumSM2['Max'][0]:
                            maximumSM2.update({'Max':[sm2_max[1],sm2_max[0]],'Load combination max':str(comb)})

                        if sm2_min[1]<maximumSM2['Min'][0]:
                            maximumSM2.update({'Min':[sm2_min[1],sm2_min[0]],'Load combination min':str(comb)})
            
                        #Storage for SM3
                        if sm3_max[1]>maximumSM3['Max'][0]:
                            maximumSM3.update({'Max':[sm3_max[1],sm3_max[0]],'Load combination max':str(comb)})

                        if sm3_min[1]<maximumSM3['Min'][0]:
                            maximumSM3.update({'Min':[sm3_min[1],sm3_min[0]],'Load combination min':str(comb)})

            else:
                for f in [0,1]:
                    for comb in [loads for loads in load_combinations if 'SLS' not in loads]:
                        #Extracts maximum sectional forces from every load combination for each path
                        sm1_max = max(SM1[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sm1_min = min(SM1[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sm2_max = max(SM2[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sm2_min = min(SM2[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sm3_max = max(SM3[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sm3_min = min(SM3[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sf1_max = max(SF1[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sf1_min = min(SF1[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sf4_max = max(SF4[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sf4_min = min(SF4[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sf5_max = max(SF5[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))
                        sf5_min = min(SF5[(str(pth_name)+'-'+str(comb)+str(f))],key=itemgetter(1))

                        #Checks wheter the new combination yileds a sectional force of larger magnitude. If true, it replaces the previous
                        #max or min values.
                        if sm1_max[1]>maximumSM1['Max'][0]:
                            maximumSM1.update({'Max':[sm1_max[1],sm1_max[0]],'Load combination max':str(comb)})

                        if sm1_min[1]<maximumSM1['Min'][0]:
                            maximumSM1.update({'Min':[sm1_min[1],sm1_min[0]],'Load combination min':str(comb)})

                        #Storage for SM2
                        if sm2_max[1]>maximumSM2['Max'][0]:
                            maximumSM2.update({'Max':[sm2_max[1],sm2_max[0]],'Load combination max':str(comb)})

                        if sm2_min[1]<maximumSM2['Min'][0]:
                            maximumSM2.update({'Min':[sm2_min[1],sm2_min[0]],'Load combination min':str(comb)})
            
                        #Storage for SM3
                        if sm3_max[1]>maximumSM3['Max'][0]:
                            maximumSM3.update({'Max':[sm3_max[1],sm3_max[0]],'Load combination max':str(comb)})

                        if sm3_min[1]<maximumSM3['Min'][0]:
                            maximumSM3.update({'Min':[sm3_min[1],sm3_min[0]],'Load combination min':str(comb)})

                        #Storage for SF1
                        if sf1_max[1]>maximumSF1['Max'][0]:
                            maximumSF1.update({'Max':[sf1_max[1],sf1_max[0]],'Load combination max':str(comb)})

                        if sf1_min[1]<maximumSF1['Min'][0]:
                            maximumSF1.update({'Min':[sf1_min[1],sf1_min[0]],'Load combination min':str(comb)})

                        #Storage for SF4
                        if sf4_max[1]>maximumSF4['Max'][0]:
                            maximumSF4.update({'Max':[sf4_max[1],sf4_max[0]],'Load combination max':str(comb)})
                            
                        if sf4_min[1]<maximumSF4['Min'][0]:
                            maximumSF4.update({'Min':[sf4_min[1],sf4_min[0]],'Load combination min':str(comb)})

                        #Storage for SF5
                        if sf5_max[1]>maximumSF5['Max'][0]:
                            maximumSF5.update({'Max':[sf5_max[1],sf5_max[0]],'Load combination max':str(comb)})

                        if sf5_min[1]<maximumSF5['Min'][0]:
                            maximumSF5.update({'Min':[sf5_min[1],sf5_min[0]],'Load combination min':str(comb)})
        # if 'deck' in name or 'Foundation footing' in name or 'Foundation_12'in name:
        #     Results.update({str(name): {'SM1':maximumSM1,'SM2':maximumSM2,'SM3':maximumSM3,'SF1':maximumSF1,'SF4':maximumSF4,'SF5':maximumSF5,'VEd':SF5_SF4_comb[str(name)]}})
        # else:
        Results.update({str(name): {'SM1':maximumSM1,'SM2':maximumSM2,'SM3':maximumSM3,'SF1':maximumSF1,'SF4':maximumSF4,'SF5':maximumSF5}}) 

    return Results,path_coord,moment_x_bridge

def Rebar_combinations(indata,path_coord,moment_x_bridge):
    parts = [n['Name'] for n in path_coord]
    
    #x-coordinates where positive and negative moments changes from all load cases. 
    x_pos = moment_x_bridge['Bridge deck']['x pos']-indata['Span']/2
    x_neg = moment_x_bridge['Bridge deck']['x neg']-indata['Span']/2

    #Thicknesses in support section of the bridge deck
    t_sup_deck = indata['Deck thickness']-np.sqrt(indata['Radius']**2-(indata['Span']/2)**2)+indata['Radius']
    t_sup_deck_end = indata['Deck thickness']-np.sqrt(indata['Radius']**2-x_pos**2)+indata['Radius'] 

    #Thicknesses in the span scetion of the bridge deck
    t_span = indata['Deck thickness']
    t_span_end = indata['Deck thickness']-np.sqrt(indata['Radius']**2-x_neg**2)+indata['Radius']

    #Leg thicknesses in the top part
    t_leg_top = indata['Leg thickness top']

    #Leg thicknesses in the bottom part
    t_leg_bot = indata['Leg thickness bottom']
    t_leg_center = (t_leg_top+t_leg_bot)/2

    #Thickness of the foundation/foundations
    t_found = indata['Foundation thickness']

    # ['Bridge deck support', 'Bridge deck span', 'Legs upper', 'Legs lower', 'Foundation footing', 'Foundation']
    t = {'Bridge deck support':{'Thickness 1':t_sup_deck,'Thickness 2':t_sup_deck_end},'Bridge deck span':{'Thickness 1':t_span,'Thickness 2':t_span_end},
        'Legs upper':{'Thickness 1':t_leg_top,'Thickness 2':t_leg_center},'Legs lower':{'Thickness 1':t_leg_bot,'Thickness 2':t_leg_center},
        'Foundation footing':{'Thickness 1':t_found,'Thickness 2':t_found}}

    # t = {'Bridge deck support':t_sup_deck,'Bridge deck span':t_span,'Legs upper':t_leg_top,'Legs lower':t_leg_bot,'Foundation':t_found}
    concrete_cover = [35,55]                #Concrete cover in [mm]
    Rebar_size_s = [16,20,25]                 #Diameters of Longitudinal reinforcements [mm]
    Rebar_size_prim = [20,25]
    Rebar_layer = [1,2]                     #Number of reinforcement layers 
    spacing = np.linspace(75,400,14)       #Spacing between bars [mm]
    concrete_class = [indata['Concrete class']]             #Concrete class
    Stirrups_Size = 12                      #Diameter of stirrup reinforcements [mm]                      


    final_combinations = {}
    for p in parts:
        name = p
        id = 1
        if 'Foundation' in name:
            t_main = t['Foundation footing']['Thickness 1']
            t_secondary = t['Foundation footing']['Thickness 2']
        else:
            t_main = t['{}'.format(name)]['Thickness 1']
            t_secondary = t['{}'.format(name)]['Thickness 2']
        Combinations = []
        if t_secondary>=400:                                                                                      #Smallest height to fit 2 rebar layers 
            n_rebar_layers = Rebar_layer
        else:
            n_rebar_layers = [1]

        for n_rebar in n_rebar_layers:                                                                      #number of rebar horisontal layers
            if n_rebar == 1:
                for sp in spacing:                                                                          #Spacing between reinforcement
                    for si in Rebar_size_s:                                                                   #Size of reinforcement
                        for si_prim in Rebar_size_prim: 
                            for con_c in concrete_cover:                                                        #Concrete covers 
                                for c in concrete_class:                                                        #concrte classes     
                                    comb = {'Combination name':id,'Thickness main':t_main,'Thickness secondary':t_secondary,'no layers rebar':n_rebar,
                                                'Spacing layer 1':sp,'Spacing layer 2':'','Size layer 1':si,'Size layer 2':'',
                                                'Concrete class':c,'Concrete cover':con_c,'Stirrup size':Stirrups_Size,'Size layer prim':si_prim}
                                    Combinations.append(comb) 
                                    id+=1
            else:
                for si_1 in Rebar_size_s: 
                    for si_2 in [size for size in Rebar_size_s if size<=si_1]:
                        for sp_1 in spacing:
                            for si_prim in Rebar_size_prim: 
                                for sp_2 in [sp_1*space for space in [1,2,3,4,5] if space*sp_1<spacing[-1]*1.5]:               #Second layer should be above the first layer accrodng to SS-EN 1992-1-1 section 8,(8.2)
                                    for con_c in concrete_cover:
                                        for c in concrete_class:
                                            comb = {'Combination name':id,'Thickness main':t_main,'Thickness secondary':t_secondary,'no layers rebar':n_rebar,
                                                        'Spacing layer 1':sp_1,'Spacing layer 2':sp_2,'Size layer 1':si_1,'Size layer 2':si_2,
                                                        'Concrete class':c,'Concrete cover':con_c,'Stirrup size':Stirrups_Size,'Size layer prim':si_prim}
                                            Combinations.append(comb)  
                                            id+=1
        final_combinations.update({str(name):Combinations})
    
    return final_combinations,parts

def ULS(indata,results,moment_x_bridge,path_coord):
    import numpy as np
    import scipy as sci
    import scipy.optimize as opt 
    #Strain calculation
    def es_prim(x):                                         #Defining the compressive strain in the steel as a function of the compressive block
        return((x-dprimx)/x*ecu)

    def es_1(x):
        return((d1x-x)/x*ecu)

    def es_2(x):
        return((d2x-x)/x*ecu)

    #yeild functions
    #Yeilding in the top tension layer
    def equalibrium_yeild_secon_layer(x):
        return(sig_cm*x*b+es_prim(x)*Es*Asprimx-fyd*(As1x+As2x))

    #Yeilding in the bottom tnsion layer
    def equalibrium_yeild_first_layer(x):
        return(sig_cm*x*b+es_prim(x)*Es*Asprimx-es_2(x)*Es*As2x-fyd*(As1x))

    #Yeilding in the top reinfrocement
    def equalibrium_yeild_comp_layer(x):
        return(sig_cm*x*b+fyd*Asprimx-es_2(x)*Es*As2x-es_1(x)*Es*As1x)

    #Resulting moment capacities from each yeild function 
    def MRd_yeild_secon_layer():
        name = 'Second layer'
        x = opt.fsolve(equalibrium_yeild_secon_layer,t/2)
        es1 = es_1(x)
        es2 = es_2(x)
        esprim = es_prim(x)
        e = [es1,es2,esprim,esy]
        if es2 > esy and esprim<esy:
            deff = (d1x*As1x+d2x*As2x)/(As1x+As2x)
            MRd = sig_cm*b*x*(deff-Beta_R*x)+esprim*Es*(deff-dprimx)*Asprimx
            return MRd,x,deff

    def MRd_yeild_first_layer():
        name = 'First layer'
        x = opt.fsolve(equalibrium_yeild_first_layer,t/2)
        es1 = es_1(x)
        es2 = es_2(x)
        esprim = es_prim(x)
        e = [es1,es2,esprim,esy]
        if es1>esy and es2<esy and esprim<esy:
            deff = (d1x*As1x*fyd+d2x*As2x*es2*Es)/(As1x*fyd+As2x*es2*Es)
            MRd = sig_cm*b*x*(deff-Beta_R*x)+esprim*Es*(deff-dprimx)*Asprimx
            return MRd,x,deff
            
    def MRd_yeild_comp_layer():
        name = 'Compression layer'
        x = opt.fsolve(equalibrium_yeild_comp_layer,t/2)
        es1 = es_1(x)
        es2 = es_2(x)
        esprim = es_prim(x)
        e = [es1,es2,esprim,esy]
        if es1<esy and es2<esy and esprim>esy:
            deff = (d1x*As1x*es1*Es+d2x*As2x*es2*Es)/(As1x*es1*Es+As2x*es2*Es)
            MRd = sig_cm*b*x*(deff-Beta_R*x)+fyd*(deff-dprimx)*Asprimx
            return MRd,x,deff

    #Definition of cotangens
    def cot(deg):
        import numpy as np
        rad = np.radians(deg)
        return (1/np.tan(rad))

    #Different reinforcement combinations
    final_combinations,parts = Rebar_combinations(indata,path_coord,moment_x_bridge)
    comb_capacities = {}

    for n in range (len(final_combinations)):
        name = parts[n]
        combinations = []
        data = results[str(name)]
        # Designing moments according to Bjorn Engstrom (Design and analysis of slabs and flat slabs, 2014)
        # In Brigade the sign convetions for the moment is the other way around comapred to the book.
        # Hence, negative moment when tension in bottom, and positive moment when tension in top.

        abs_mxy =max(abs(data['SM3']['Max'][0]),abs(data['SM3']['Min'][0])) 
        mrx = data['SM1']['Min'][0]-abs_mxy
        if mrx>0:
            mrx = 0
        
        mry =  data['SM2']['Min'][0]-abs_mxy
        if mry>0:
            mry = 0

        mrx_prim = data['SM1']['Max'][0]+abs_mxy
        if mrx_prim < 0:
            mrx_prim = 0
        
        mry_prim = data['SM2']['Max'][0]+abs_mxy
        if mry_prim<0:
            mry_prim = 0

        #Compression reinforcement is estimated with As'> m'/(fyd*z)
        MEd_tension_x = max(abs(mrx),abs(mrx_prim))
        MEd_compression_x = min(abs(mrx),abs(mrx_prim))
        #Where is tensiion reinforcement, in the top or in the bottom
        Tension_x = 'Tension bottom' if abs(mrx) > abs(mrx_prim) else 'Tension top'


        MEd_tension_y = max(abs(mry),abs(mry_prim))
        MEd_compression_y = min(abs(mry),abs(mry_prim))
        #Where is tensiion reinforcement, in the top or in the bottom
        Tension_y = 'Tension bottom' if abs(mry) > abs(mry_prim) else 'Tension top'


        sf4 = max(abs(data['SF4']['Max'][0]),abs(data['SF4']['Min'][0]))
        sf5 = max(abs(data['SF5']['Max'][0]),abs(data['SF5']['Min'][0]))

        VEd = np.sqrt(sf4**2+sf5**2)*1000                                           #per meter width

        for combs in final_combinations[name]:
            id = combs['Combination name']
            t = combs['Thickness main']
            s1x = combs['Spacing layer 1']/1000
            if combs['Spacing layer 2'] =='':
                s2x = 100
            else:
                s2x = combs['Spacing layer 2']/1000
            
            o1x = combs['Size layer 1']

            if combs['Size layer 2']=='':
                o2x = 0
            else: 
                o2x = combs['Size layer 2']
            
            concrete_class = indata['Concrete class']
            concrete_cover = float(combs['Concrete cover'])
            concrete_properites = Concrete_classes(concrete_class)
            fck = float(concrete_properites['fck'])
            fyk = 500
            gamma_s = 1.15                                          #partial factor reinforcement (SS-EN 1992-1-1:2005 Table 2.1N)
            gamma_c =1.5                                            #partial factor concrete (SS-EN 1992-1-1:2005 Table 2.1N)
            Es = 200e+3

            ecu = 3.5e-3                                            #Ulitmate strain concrete (SS-EN 1992-1-1:2005,Table 3.1)
            fcd = fck/gamma_c
            fyd = fyk/gamma_s
            alpha_R = float(concrete_properites['alpha R'])
            Beta_R = float(concrete_properites['Beta R'])
            min_v_spac = 40                                         #Spacing between reinforcement 
            
            spacing = np.linspace(100,400,13)                       #Spacing between bars [mm]
            Es = 200e+3

            ##############################################################################
            # Firstley the amount of transversal reinforcement is calculated.
            # It is calulated as an area per meter instead of trying different layouts.
            # This is beacause the moment in the transversal direction is smaller than in the longitudinal. 
            # Thus there is more flexibility regarding the amount, spacing etc and can be modified in later stages.
            # Assumed one layer is enough. And to be conservative, the rebar size is assumed to be 25 mm, reducing zy  
            oy = 25
            t_ave = (float(combs['Thickness main'])+float(combs['Thickness secondary']))/2
            zy = 0.9* (t_ave - concrete_cover-oy/2)
            Asy = MEd_tension_y/(fyd*zy)*1000                       #mm^2/meter 
            Asy_prim = MEd_compression_y/(fyd*zy)*1000              #mm^2/meter
            
            #Diametr of rebars
            o_prim_x = float(combs['Size layer prim'])              # Area of 1 bar, compression zone
            As1x_i = o1x**2*np.pi/4                                 #Area of 1 bar, layer 1
            As2x_i = o2x**2*np.pi/4                                 #Area of 1 bar, layer 2
            As_prim_x_i = min(o1x,o2x)**2*np.pi/4   
            b = 1000        
            s_prim_x_min = 1.5*0.400                                    #Spacing [m]

            As1x = As1x_i/s1x
            As2x = As2x_i/s2x

            #Compression reinforcement is set to have the same diameter as the reinforcement in layer 1
            #And it has the maximum spacig, i.e 400 mm
            min_rebar = ''                                          #Minimum area of compressive rebars

            d1x = t-concrete_cover-o1x/2                            #Height reinforcement layer 1
            d2x = t-concrete_cover-o1x-min_v_spac-o2x/2             #Height reinforcement layer 2
            dprimx = concrete_cover+o_prim_x/2 
            Asx_eff = As1x_i/s1x+As2x_i/s2x                         #Effective area
            dx_eff  = (As1x_i/s1x*d1x+As2x_i/s2x*d2x)/(Asx_eff)     #Effective reinforcement height 
            
            Asprimx_min_s = As_prim_x_i/s_prim_x_min
            if Asprimx_min_s < (MEd_compression_x/(fyd*dx_eff*0.9)):
                Asprimx_min_s = MEd_compression_x/(fyd*dx_eff*0.9)
                s_prim_x_min = (As_prim_x_i/Asprimx_min_s)*1000

                spac_pos = np.argmin(abs(spacing-s_prim_x_min))
                s_prim_x = spacing[spac_pos]/1000
                Asprimx = As_prim_x_i/s_prim_x
            else:
                Asprimx = Asprimx_min_s
                s_prim_x = s_prim_x_min

            #Material indata. 
            c_dev = ''                                              #mattavvikelse p B120 baranade konstruktioner
            sig_cm = fcd*alpha_R
                                                    
            esy = fyd/Es                                            #Yeilding strain of steel

            functions = (MRd_yeild_secon_layer, MRd_yeild_first_layer, MRd_yeild_comp_layer)
            for func in functions:
                result = func()
                if result is not None:
                    MRd, x, deff = result                           # Unpack the returned values
                    break                                           # Stop iterating if MRd is returned
                else:
                    MRd = 0


            #Factors for platic rotations
            if fck <50:
                factor = 0.25
            else:
                factor = 0.15
            #MRd in Nmm/m, it gets divided by 1000 to translate it to Nmm/mm as the convention in brigade
            #Checks wheter the moment capacity is adequete
            MRd = MRd/1000
            # if MRd>MEd_tension_x and x<deff*factor:
            if MRd>MEd_tension_x:
                # print(MRd,MEd_tension_x, name)
                comb = combs
                comb.update({'MEdy [Nm/m]':MEd_tension_y,'MRdx [Nm/m]':MRd[0],'Asx effective tension':Asx_eff,'dx effective':deff,'Ax tot':As1x+As2x+Asprimx,'As1x':As1x,'As2x':As2x,'d1x':d1x,'d2x':d2x,'dprimx':dprimx,
                             'Asy':Asy,'Asy_prim':Asy_prim,'Asprimx':Asprimx,'Size layer y':oy,'MEdx':MEd_tension_x,'Tension X':Tension_x,'Tension y':Tension_y})
                b = 1000    #VEd in N/m                     #Section 6.2.2 in SS-EN 1992-1-1, Smallest width in the cross section which is in tension. 

                Asl = float(comb['Asx effective tension'])         #Section 6.2.2 in SS-EN 1992-1-1, Area of tension reinforcement reching a least (lbd+d)
                d = float(comb['dx effective'])                    #distance to tansion reinforcement [mm]
                z = d*0.9                                   #inner leverarm                    [mm]
                o_stirrups = float(combs['Stirrup size'])
                theta = 45                                  #inclination oc the shear crack
                fywd = 0.8*fyk                              #0.8*fywk in order to use the simplified expression for alphaw
                # NEd = 0                                   # Set to zero sice sig_cp can be excluded
                # Ac = combs['Thickness']*b                 #Concrete cross section area


                def VRd_no_stirrups_func():
                    k = 1 + np.sqrt(200/d)                  #factor in equation 6.2.a in SS-EN 1992-1-1
                    if k<=2:
                        k = 1 + np.sqrt(200/d)
                    else:
                        k = 2 

                    #It's allowd to exclude according to SS-EN 1992-1-1, section 6.2.2
                    #It's resonable, since induced normal forces due to temperature and breakig load not always are present
                    sig_cp = 0                              #It's allowd to exclude according to SS-EN 1992-1-1, section 6.2.2         

                    rho_1 = Asl/(b*d)                        #factor in equation 6.2.a in SS-EN 1992-1-1
                    if rho_1 <=0.02:
                        rho_1 = Asl/(b*d)
                    else: 
                        rho_1 = 0.02

                    C_Rd_c = 0.18/gamma_c                   #factor in equation 6.2.a
                    k1 = 0.15                               #factor in equation 6.2.a
                    v_min = 0.035*(k**(2/3))*fck**(1/2)     #from Equation 6.3N

                    VRd_c_1  =(C_Rd_c * k*(100*rho_1*fck)**(1/3)+k1*sig_cp)*b*d  #Equation 6.2.a
                    VRd_c_min = (v_min + k1*sig_cp)*b*d                         #Equation 6.2.b

                    VRd_no_stirrups = max(VRd_c_1,VRd_c_min)                    #Minimum shear capacity in the cross section         

                    return VRd_no_stirrups

                VRd_no_stirrups = VRd_no_stirrups_func()

                if VEd<VRd_no_stirrups:

                    combin = comb.copy()
                    combin.update({'Stirrups':'Stirrups not need','sx stirrups':'','s max':'','VRd':VRd_no_stirrups,'Asw':'','VEd':VEd})
                    combinations.append(combin)
                        
                else:
                    id2 = 1
                    for spac in np.flip(spacing):
                        # for num in [1,2,3]:                                             #Shear reinforcment attatched to every or every other or every third longitudinal reinforcement
                        #     As_w_i = (o_stirrups**2*np.pi)/4                            #Area of 1 stirrup reinforcement
                        #     spac_stirrups = s1x*num*1000                                #Transversal spacing of shear reinforcement

                        #     if spac_stirrups < 0.75*d or spac_stirrups<600:
                        #         num_stirrups = b/(s1x*num*1000)                         #Number of stirrups per meter

                        #         Asw = As_w_i*num_stirrups

                        # Shear force dimensioning
                        v = 0.6*(1-fck/250)                                     #Equation 6.6N
                        fywd = fyk*0.8

                        if fck<=60:                                             #Equation 6.10.aN
                            v1 = 0.6                                            
                        else:
                            v1 = 0.9-fck/200                                    #Equation 6.10.bN

                        sig_cp=0

                        if sig_cp>=0 and sig_cp<=0.25*fcd:
                            alpha_cw = 1+sig_cp/fcd 
                        elif sig_cp>0.25*fcd and sig_cp<=0.5*fcd:
                            alpha_cw = 1.25                                     #Equation 6.11.bN
                        else:
                            alpha_cw = 2.5*(1-sig_cp/fcd)                       #Equation 6.11.cN

                        Asw_max = 0.5*alpha_cw*v1*fcd*b*spac/fywd               #From equation 6.12 in SS-EN 1992-1-1

                        # VRd_s = Asw/spac *z *fywd*cot(theta)                    #Equation 6.8 in SS-EN 1992-1-1
                        
                        VRd_max = alpha_cw*b*z*v1*fcd/(cot(theta)+np.tan(np.radians(theta))) #Equation 6.9 in SS-EN 1992-1-1    #

                        
                        #Minimum shear reinforcement
                        s_l_max = 0.75 * d * (1+cot(90))                        #Equation 9.6N in SS-EN 1992-1-1
                        pw_min = (0.08*np.sqrt(fck))/fyk                        #Equation 9.5N in SS-EN 1992-1-1
                        Asw1 = VEd*spac/(z*fywd*cot(theta))
                        Asw2 = pw_min*(spac*b) 
                        Asw = max(Asw1,Asw2)
                        VRd_s = VEd
                        VRd = min(VRd_s,VRd_max)
                        VEd_to_fulfill = 0.5*b*d*v*fcd                          #Equation 6.5in SS-EN 1992-1-1

                        pw = Asw/(spac*b)
                                                                       #Equation 9.4N in SS-EN 1992-1-1                        
                        if VEd<=VRd and VEd<VEd_to_fulfill and pw>=pw_min and s_l_max>spac and Asw<Asw_max:
                          
                            combin = comb.copy()
                            combin.update({'Combination name':'{}-{}'.format(id,id2), 'Stirrups':'Stirrups needed','sx stirrups':spac,'s max':s_l_max,'VRd':VRd,'Asw':Asw,'VEd':VEd})
                            id2+=1
                            combinations.append(combin)
                            break

        comb_capacities.update({str(name):combinations})
    return comb_capacities,parts

def SLS(indata,Load_comb,file_path):
    import numpy as np

    # The SLS check is a simple check of the nodes in the bridge deck. In the analysis the
    # bridge deck is assumed to have zero cracks, which is favourable estimation. Meaning, some of the bridge combinations
    # which succesfully passes the SLS critera may have larger deflections. But its an adequete approach in this case,
    # Since the script is focused to be applicable in the prliminary phase in swedish road and railway plans. 
    
    # When analysing the deflections, the structural deflections are of interest. In the best case senarion, a seperate
    # Brigade analysis should be applied with a very stiff foundation. Since time is of the esence when running this multy critera analysis
    # The contribution from to the deflection from the foundation spring is subtractred from the bridge deck deflection. 

    jobname = indata['Model name']
    # try:
    o1 = session.openOdb(name=file_path+str(jobname)+'.odb')
    sess = session.viewports['Viewport: 1']
    sess.setValues(displayedObject=o1)
    # except:
    #     pass
    session.Path(name='Bridge deck edge', type=POINT_LIST, expression=((-indata['Span']/2,indata['Width']-500,0),(indata['Span']/2,indata['Width']-500,0)))
    session.Path(name='Bridge deck', type=POINT_LIST, expression=((-indata['Span']/2,indata['Width']/2,0),(indata['Span']/2,indata['Width']/2,0)))
    session.Path(name='Foundation edge sup1', type=POINT_LIST, expression=((-indata['Span']/2,indata['Width']-500,-indata['Height legs']),(-indata['Span']/2+500,indata['Width']-500,-indata['Height legs'])))
    session.Path(name='Foundation edge sup2', type=POINT_LIST, expression=((indata['Span']/2,indata['Width']-500,-indata['Height legs']),(indata['Span']/2-500,indata['Width']-500,-indata['Height legs'])))
    session.Path(name='Foundation cent sup1', type=POINT_LIST, expression=((-indata['Span']/2,indata['Width']/2,-indata['Height legs']),(-indata['Span']/2+500,indata['Width']/2,-indata['Height legs'])))
    session.Path(name='Foundation cent sup2', type=POINT_LIST, expression=((indata['Span']/2,indata['Width']/2,-indata['Height legs']),(indata['Span']/2-500,indata['Width']/2,-indata['Height legs'])))


    Paths = ['Bridge deck edge','Bridge deck']

    Paths_foundation_edge = ['Foundation edge sup1','Foundation edge sup2']
    Paths_foundation_center = ['Foundation cent sup1','Foundation cent sup2']

    def_max = 0
    def_max_quasi = 0
    for load_comb in [l for l in Load_comb if 'SLS' in l]:
        for pth in Paths: 
            if 'edge' in pth:
                Sup_paths = Paths_foundation_edge
            else:
                Sup_paths = Paths_foundation_center
            for f in [0,1]:
                #Changing the step which data is picked from 
                sess.odbDisplay.setFrame(step=load_comb, frame=f)

                #Changing the variable which data is picked from 
                sess.odbDisplay.setPrimaryVariable(variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, 'U3'))
                
                # Vertical deflection at footing, support 1 
                session.XYDataFromPath(name='XY_data_sup_1', path=session.paths[str(Sup_paths[0])], includeIntersections=False, 
                    projectOntoMesh=False, pathStyle=UNIFORM_SPACING, numIntervals=(20), 
                    projectionTolerance=0, shape=UNDEFORMED, labelType=TRUE_DISTANCE, 
                    removeDuplicateXYPairs=True, includeAllElements=False)

                # Vertical deflections at footing, support 2
                session.XYDataFromPath(name='XY_data_sup_2', path=session.paths[str(Sup_paths[1])], includeIntersections=False, 
                    projectOntoMesh=False, pathStyle=UNIFORM_SPACING, numIntervals=(20), 
                    projectionTolerance=0, shape=UNDEFORMED, labelType=TRUE_DISTANCE, 
                    removeDuplicateXYPairs=True, includeAllElements=False)



                x1 = session.xyDataObjects['XY_data_sup_1'].data
                x2 = session.xyDataObjects['XY_data_sup_2'].data 

                U3_sup_1 = list(x1)           #fictitious settlements at support 1
                U3_sup_2 = list(x2)           #fictitious settlements at support 2

                k = (float(U3_sup_1[0][1])-float(U3_sup_2[0][1]))/float((-indata['Span']))  # Linear increments per mm of the deflection of the footings

                #Creating data file with deflections of the bridge deck
                session.XYDataFromPath(name='XY_data', path=session.paths[str(pth)], includeIntersections=False, 
                    projectOntoMesh=False, pathStyle=UNIFORM_SPACING, numIntervals=(int(indata['Span']/100+1)), 
                    projectionTolerance=0, shape=UNDEFORMED, labelType=TRUE_DISTANCE, 
                    removeDuplicateXYPairs=True, includeAllElements=False)


                #Extracting deflection of the bridge deck
                x0 = session.xyDataObjects['XY_data'].data
                x0 = list(x0)

                #Final deflection of the bridge deck, deletes the contribution from "settlements" of supports
                UZ = np.array([(y-(U3_sup_1[0][1]+k*x)) for x,y in x0])
                
                if 'QUASI' in load_comb:
                    deflection_quasi = max(abs(UZ))
                    if deflection_quasi>def_max_quasi:
                        def_max_quasi = deflection_quasi
        
                else:
                    deflection = max(abs(UZ))
                    if deflection>def_max:
                        def_max = deflection
        
    deflection_limit = indata['Span']/800   #Limit accoring to TRAVINFRA 00227, chapter 8.2.4

    if deflection_limit>def_max:
        sls = {'Deflection check':'Deflection ceck OK','Deflection Frequent [mm]':def_max,'Deflection Quasi [mm]':def_max_quasi}
    else:
        sls = {'Deflection check':'Deflection ceck NOT OK','Deflection Frequent [mm]':def_max,'Deflection Quasi [mm]':def_max_quasi}
    
    

    return (sls)

def Evaluation(indata,parts,comb_capacities,moment_x_bridge):
   # def Evaluation(indata,parts,comb_capacities):
    import numpy as np
    import scipy as sci
    import scipy.optimize as opt
    import csv 
    import os
    ###############################################################################
    file_path_1 = 'Evaluation_criteria.csv'
    file_path_2 = 'Material_criteria.csv'
    file_path_3 = 'Formwork_cost.csv'
    # Define the data types for the columns
    dtype1 = [('Work/factor', 'U50'), ('deck', 'f8'), ('Wing', 'f8'), ('Leg', 'f8'), ('Found', 'f8'), ('unit', 'U5')]

    dtype2 = [('Concrete', 'U8'), ('SEK/m3', 'f8'), ('kg CO2e/m3 ', 'f8'), ('CO2e/kg', 'f8')]

    dtype3 = [('Work/factor', 'U13'), ('deck', 'f8'), ('Wing', 'f8'), ('Leg', 'f8'), ('Found', 'f8'), ('unit', 'U5')]
    # Load the CSV file into a structured numpy array
    time_parameters = np.genfromtxt(file_path_1, delimiter=';', dtype=dtype1, skip_header=1)
    material_parameters = np.genfromtxt(file_path_2, delimiter=';', dtype=dtype2, skip_header=1)
    Formwork_cost = np.genfromtxt(file_path_3, delimiter=';', dtype=dtype3, skip_header=1)
    ################################################################################
    #Concrete class
    concrete_class = indata['Concrete class'] 


    ################################################################################
    #Cost of material
    if concrete_class == 'C32/42':
        C_concrete = float(material_parameters[0][1])                                      # Cost, SEK/m3
    elif concrete_class == 'C35/C45':
        C_concrete = float(material_parameters[1][1])                                      # Cost, SEK/m3
    else:
        C_concrete = float(material_parameters[2][1])                                      # Cost, SEK/m3
    C_reinforcement = float(material_parameters[3][1])                                     # Cost, SEK/m3

    ################################################################################
    #CO2 equivalents of material
    if concrete_class == 'C32/42':
        E_concrete = float(material_parameters[0][2])                                      # CO2 equivalents, CO2/m3
    elif concrete_class == 'C35/C45':
        E_concrete = float(material_parameters[1][2])                                      # CO2 equivalents, CO2/m3
    else:
        E_concrete = float(material_parameters[2][2])                                      # CO2 equivalents, CO2/m3
    E_reinforcement = float(material_parameters[3][2])                                     # CO2 equivalents, CO2/m3

    ################################################################################
    Build_cost = 500                                                                # Cost [SEK] of 1 hour of work


    ################################################################################
    #Data from bridge deck
    if indata['Manual control'] !='':
        control_span = indata['Manual control']*1000
    else:
        control_span = indata['Free span']

    r = float(indata['Radius'])                                                            # Radius of underside of deck
    t_span = float(indata['Deck thickness'])                                               # Bridge deck thickness in span
    l_deck = float(indata['Free span'])                                                         # Lenght of deck
    t_sup = t_span-np.sqrt(r**2-(float(indata['Free span'])/2)**2)+r                            # Bridge deck thickness at support
    
    w = float(indata['Width'])

    #Calculating the area with segment theorem for circles
    theta = np.arcsin((l_deck/2)/r)*2                                               # Circle segment angle

    A_side_deck = t_sup*l_deck-0.5*r**2*(theta-np.sin(theta))                       # Radius side area of bridge deck [mm]
    
    A_under_side_deck = w*r*theta                                                   # Area of underside of bridge [mm^2]
    A_deck_form = (A_under_side_deck+A_side_deck*2)/10**6                           # Area of formwork for bridge deck [m^2]

    V_deck = A_side_deck*w/10**9                                                    # Volume of bridge deck [m^3]

    #Data from legs
    h = float(indata['Height legs'])                                                       # Height of bridge legs [mm]
    t_bot = float(indata['Leg thickness bottom'])                                          # Leg thickness in the bottom [mm]
    t_top = float(indata['Leg thickness top'])                                             # Leg thickness in the top [mm]

    A_leg = w*h                                                                     # Area/leg [mm^2]
    A_side_leg = t_bot *h + (t_top-t_bot)*h/2                                       # Area of leg, profile view [mm^2]

    A_leg_form = 2*(A_leg+2*A_side_leg+np.sqrt((t_top-t_bot)**2+h**2)*w)/10**6      # Area of formwork for legs[m^2]

    V_legs = 2*A_side_leg * w/10**9                                                 # Volume of legs [m^3]

    #Foundation lenght
    if control_span == 12000:
        foundation_lenght = indata['Foundation length']+indata['Foundation extrusion']*2    # Length of foundation 12m version
    else:
        foundation_lenght = indata['Foundation length']*2                           # Length of foundation 16m version

    t_found = float(indata['Foundation thickness'])                                        # Foundation thickness [mm]
    Foundation_length = float(indata['Foundation length'])
    A_foundation_form = (2*Foundation_length+2*w)*t_found/10**6                     # Area of formwork for foundation

    V_foundation = foundation_lenght*t_found*w/10**9                                # Volume of foundation [m^3]


    #################################################################################
    #Reinforcement lengths
                        
    l_span =  (indata['Span']/2-moment_x_bridge['Bridge deck']['x neg'])*2          # Total lenght of span segement, bridge deck
    l_support = moment_x_bridge['Bridge deck']['x pos']*2                           # Total lenght of support segment, bridge deck
    l_leg_upper = 2*(h/2)                                                           # Total lenght of upper leg segment, bridge leg
    l_leg_lower = 2*(h/2)                                                           # Total lenght of upper leg segment, bridge leg         
    Reinforcment_lengths = {'Bridge deck span':l_span,'Bridge deck support':l_support,'Legs upper':l_leg_upper,
                            'Legs lower':l_leg_lower}

    if control_span == 12000:
        l_foundation_center = indata['Foundation length']-2*moment_x_bridge['Foundation']['x pos']      # Total lenght of center segment of foundation for 12m bridge, bridge foundation
        l_foundation_footing = indata['Foundation extrusion']+moment_x_bridge['Foundation']['x pos']    # Total lenght of foundation footing segment (segment beneath legs)in 12m version, bridge foundation
        Reinforcment_lengths.update({'Foundation footing':l_foundation_footing,'Foundation_12':l_foundation_center})
    else:
        l_foundation_footing = indata['Foundation length']*2                        # Total lenght of foundation footing segment in 16m version, bridge foundation
        Reinforcment_lengths.update({'Foundation footing':l_foundation_footing})

    
    ##############################################################################
    #Functions to find x-positions of thicknesses in parts with variable thickness
    def Find_length_rebar_deck(x):
        return float(indata['Deck thickness'])-np.sqrt(r**2-x**2)+r-t_range

    def Find_length_rebar_leg(x):
        return t1+(t2-t1)/(h/2)*x-t_range  

    ############################################################################
    # Creates a directory for each bridge varation in indata
    directory = 'Bridge_data/'+indata['Model name']
    try:
        # Create the directory
        os.mkdir(directory)
    except:
        pass

    #############################################################################
    #Reinforcment areas, Buildability factors
    for p in parts:
        l = Reinforcment_lengths[p]
        w_meter = indata['Width']/1000                                          # All reinforcment areas are in mm^2/m, thus converting the width to meters. Used for reinforcement in x-direction
        l_meter = l/1000
        csv_name_location = str(directory)+'/'+str(indata['Model name'])+'_'+str(p)+'.csv'                                                         # All reinforcment areas are in mm^2/m, thus converting the lenght to meters. Used for reinforcement in y-direction                                                      
        try:
            with open(csv_name_location, 'w') as file:
                field_list = list(comb_capacities[p][0].keys())
                field = ['Part'] + field_list + ['Length of segment','Material cost of Reinforcement','Hours of reinforcement work','Cost of reinforcement labour','Emissions of reinforcement','Volume reinforcement']
                file.write(';'.join(field) + '\n')
        
                for comb in comb_capacities[p]:
                    Vx1 = comb['As1x']*w_meter*l
                    Vx2 = comb['As2x']*w_meter*l
                    Vx_prim = comb['Asprimx']*w_meter*l
                    Vy = (comb['Asy']+comb['Asy_prim'])*w*l_meter

                    if comb['Stirrups']== 'Stirrups not need':
                        V_stirrups = 0
                    else:
                        V_stirrups = (comb['Asw']*w_meter*l/comb['sx stirrups']) * abs(comb['Thickness main']-comb['Thickness secondary'])
                    possible_main_parts = ['deck','Wing','Leg','Found']
                    for n in possible_main_parts:
                        if n in p:
                            name = n
                    
                    #Positions of 'name' in array
                    pos = possible_main_parts.index(name)+1

                    V_Re = (Vx1+Vx2+Vx_prim+Vy+V_stirrups)/10**9                        # Total reinforcement volume [m^3]

                    #Buildability factors Reinforcement work
                    T_Reinforcement_work = float(time_parameters[2][pos])                      # h/m^3
                    T_variable_thickness = time_parameters[5][pos]                      # factor if reinforcement is placed in varable thickness
                    T_less_40 = float(time_parameters[6][pos])                                 # factor if thickenss is less than 400mm
                    T_bet_40_and_60 = float(time_parameters[7][pos])                           # factor if thickness i sbetween 400mm and 600mm
                    T_size_16 = float(time_parameters[8][pos])                                 # factor if Reinforcement size is 16mm
                    T_size_20 = float(time_parameters[9][pos])                                 # factor if reinforcement size is 20mm
                    T_size_25 = float(time_parameters[10][pos])                                # factor if reinforcement size is 25mm
                    T_shear_reinforcement = float(time_parameters[11][pos])                    # factor if shear reinforcement is present
                    
                    #Material parameter, extra reinforcement length due to anchorage
                    M_anchorage_factor = float(time_parameters[12][pos])                       # Extra reinforcement length due to anchorage                     

                    t1 = min(comb['Thickness main'],comb['Thickness secondary'])        # Minimum thickness in the part
                    t2 = max(comb['Thickness main'],comb['Thickness secondary'])        # Maximum thickness in the part

                    if t1 == t2:
                        if t1<=400:
                            T_R1 = T_less_40
                        elif t1>400 and t1<=600:
                            T_R1 = T_bet_40_and_60
                        else:
                            T_R1 = 1

                    elif t1 != t2:
                        #factor to be muliplied with the amount of reinforcement. Depends on
                        #the thickenss distrubution of the element. ie. if the thickness is less than 400 mm
                        # a larger factor is applied, if it's between 400 and 600 another factor is applied. If
                        # the thickness is larger than 600, the factor is 1. 
                        if t1 <=400:
                            if t2<=400:
                                T1 = T_less_40
                                T2 = 0
                                T3 = 0
                                T_R1 = T1
                            elif t2>400 and t2<=600:
                                if 'Bridge deck' in p:
                                    t_range = 400
                                    l_400 = opt.fsolve(Find_length_rebar_deck,1000)
                                    if 'span' in p:
                                        l1 = 2*l_400
                                        l2 = l-l1
                                    else:
                                        l1 = l-2*(indata['Span']/2-l_400)
                                        l2 = l - l1
                                if 'Leg' in p:
                                    t_range = 400
                                    l_400 = opt.fsolve(Find_length_rebar_leg,1)
                                    l1 = l-l_400*2
                                    l2 = l-l1
                                T1 = T_less_40*l1
                                T2 = T_bet_40_and_60*l2
                                T3 = 0
                                T_R1 = (T1+T2+T3)/(l1+l2)

                            elif t2>600:
                                if 'Bridge deck' in p:
                                    t_range = 400
                                    l_400 = opt.fsolve(Find_length_rebar_deck,1000)
                                    t_range = 600
                                    l_600 = opt.fsolve(Find_length_rebar_deck,1000)
                                    if 'span' in p:
                                        l1 = 2*l_400
                                        l2 = 2*(l_600-l_400)
                                        l3 = l-l1-l2
                                    else:
                                        l1 = l-2*(indata['Span']/2-l_400)
                                        l2 = l-2*(indata['Span']/2-l_600) - l1
                                        l3 = l - l1 - l2 
                                if 'Leg' in p:
                                    t_range = 400
                                    l_400 = opt.fsolve(Find_length_rebar_leg,1)
                                    t_range = 600
                                    l_600 = opt.fsolve(Find_length_rebar_leg,1)
                                    l1 = l-l_400*2
                                    l2 = 2*l_600-l1
                                    l3 = l-l1-l2
                                T1 = T_less_40*l1
                                T2 = T_bet_40_and_60*l2
                                T3 = 1*l3
                                T_R1 = (T1+T2+T3)/(l1+l2+l3)

                        elif t1>400 and t1<=600:
                            if t2>400 and t2<=600:
                                T1 = T_less_40
                                T2 = T_bet_40_and_60
                                T_R1 = T2
                            elif t2>600:
                                if 'Bridge deck' in p:
                                    t_range = 600
                                    l_600 = opt.fsolve(Find_length_rebar_deck,1000)
                                    if 'span' in p:
                                        l2 = 2*(l_600)
                                        l3 = l-l2
                                    else:
                                        l2 = l-2*(indata['Span']/2-l_600)
                                        l3 = l - l2 
                                if 'Leg' in p:
                                    t_range = 600
                                    l_600 = opt.fsolve(Find_length_rebar_leg,1)
                                    l2 = 2*l_600
                                    l3 = l-l2
                                T1 = 0
                                T2 = T_bet_40_and_60*l2
                                T3 = 1*l3
                                T_R1 = (T1+T2+T3)/(l2+l3)

                        elif t1>600:
                            T_R1 = 1    



                    
                    if comb['Stirrups']== 'Stirrups not need':
                        V_stirrups = 0
                    else:
                        V_stirrups = comb['Asw']*w_meter*l/comb['sx stirrups']

                    size_1 = comb['Size layer 1']
                    size_2 = comb['Size layer 2']
                    size_prim = comb['Size layer prim']
                    size_y = comb['Size layer y']

                    Reinforcement_size = {'Layer 1 x':{'size':size_1},'Layer 2 x':{'size':size_2},'Layer prim x':{'size':size_prim},'Layer y':{'size':size_y}}
                    Layers = ['Layer 1 x','Layer 2 x','Layer prim x','Layer y']
                    
                    for layers in Layers:
                        size = Reinforcement_size[layers]['size']
                        if size==16:
                            T_s = T_size_16
                        elif size == 20:
                            T_s = T_size_20
                        elif size == 25:
                            T_s = T_size_25


                        Reinforcement_size.update({'{}'.format(layers):{'size':size,'factor':T_s}})
                    T_R2 = (Vx1*Reinforcement_size[Layers[0]]['factor']+Vx2*Reinforcement_size[Layers[1]]['factor']+
                            Vx_prim*Reinforcement_size[Layers[2]]['factor']+Vy*Reinforcement_size[Layers[3]]['factor']+
                            V_stirrups*T_shear_reinforcement)/(V_Re*10**9)
                    
                    ########################################################################
                    #Calculation of cost, buildability and CO2-eqv-emissions for Reinfrocements

                    C_material_Re = V_Re * C_reinforcement * M_anchorage_factor
                    h_reinforcement = V_Re * M_anchorage_factor * T_Reinforcement_work * T_R1 * T_R2
                    C_build_Re = h_reinforcement * Build_cost
                    E_Re = V_Re * M_anchorage_factor * E_reinforcement
                    comb.update({'Length of segment':l,'Material cost of Reinforcement':C_material_Re,'Hours of reinforcement work':h_reinforcement,'Cost of reinforcement labour':C_build_Re,
                                'Emissions of reinforcement':E_Re,'Volume reinforcement':V_Re})

                    row = [str(p)] + [str(comb[key]) if not isinstance(comb[key], str) else comb[key] for key in field[1:]]
                    with open(csv_name_location, 'a') as file:                    
                    # Write the data row
                        file.write(';'.join(row) + '\n')
        except:
            pass
    ################################################################################
    #Factors including buildability of formwork  
    Formwork = float(time_parameters [0][1])                                      # hours/m2. Same for deck,leg and foundation
    Form_work_variable_thickness = float(time_parameters[4][1])                   # Factor to increase time i part has varaible thickness
    

    if t_bot != t_top:
        T_leg = Form_work_variable_thickness
        C_form_leg = float(Formwork_cost[1][3])
    else:
        T_leg = 1
        C_form_leg = float(Formwork_cost[0][3])

    if r == 0 or r == None:
        T_deck = 1
        C_form_deck = Formwork_cost[0][1]
    else:
        T_deck = Form_work_variable_thickness
        C_form_deck = Formwork_cost[1][1]


    C_form_found = float(Formwork_cost[0][4])

    A_Formwork = A_deck_form + A_leg_form + A_foundation_form
    h_formwork = Formwork * (A_deck_form * T_deck + A_leg_form * T_leg + A_foundation_form)
    C_build_form = h_formwork * Build_cost
    C_material_form = A_deck_form * C_form_deck + A_leg_form * C_form_leg + A_foundation_form * C_form_found

        
    ################################################################################
    #Cost, time and CO2-equ of concrete work

    V_concrete = V_deck + V_legs + V_foundation

    T_con_deck = float(time_parameters[1][1])
    T_con_leg = float(time_parameters[1][3])
    T_con_found = float(time_parameters[1][3])


    if concrete_class == 'C50/60':
        extra_work = float(time_parameters)[3][1]
    else:
        extra_work = 0
    h_concrete = (1+extra_work) * (T_con_deck * V_deck + T_con_leg * V_legs + T_con_found * V_foundation)
    C_material_Con = C_concrete * V_concrete
    C_build_Con = h_concrete * Build_cost
    E_Con = E_concrete * V_concrete

    indata.update({'Material cost of formwork':C_material_form,'Hours of formwork work':h_formwork,'Cost of formwork labour':C_build_form,
                'Material cost of concrete':C_material_Con,'Hours of concrete work':h_concrete,'Cost of concrete labour':C_build_Con,
                'Emissions of concrete':E_Con,'Volume concrete':V_concrete})
    
    csv_name_location2 = str(directory)+'/'+str(indata['Model name'])+'.csv'                                                         # All reinforcment areas are in mm^2/m, thus converting the lenght to meters. Used for reinforcement in y-direction                                                      
    field_list2 = list(indata.keys())
    row_indata = [str(indata[key]) for key in field_list2]
    with open(csv_name_location2, 'w') as file:
        file.write(';'.join(field_list2) + '\n')
        file.write(';'.join(row_indata) + '\n')
    
def remove(indata,file_path): 
    import os
    from abaqus import session
    import shutil
    # import subprocess

    for j in mdb.jobs.keys():
        del mdb.jobs[j]

    jobname = indata['Model name']
    try:
        odb = session.odbs['{}{}.{}'.format(file_path,jobname,'odb')]
        
        odb.close()
    except:
        pass
    delete=['.dat','.odb','.dat','.mdl','.msg','.odb-f','.prt','.sim','.SolverDriver.log','.sta','.stt','.odb_f','.inp','.bpj','.023','.LoadCombCalc.log','.progress','_backup.odb','.cmb']
    try:
        os.remove('{}.odb'.format(jobname))
    except:
        pass

    for n in delete:
        try:
            os.remove('{}{}'.format(jobname,n))
        except:
            pass
    
    for n_path in session.paths.keys():
        del session.paths[n_path]
    for n_path in session.xyDataObjects.keys():
        del session.xyDataObjects[n_path]

    del mdb.models[indata['Model name']]

    # try:
    #     # Define the command to kill the process
    #     command = 'taskkill /F /IM JobProcessor.exe /T'

    #     # Run the command using subprocess
    #     subprocess.call(command, shell=True)
    # except:
    #     pass

def run_script():
    import os
    indata1 = combination_multy()
    file_path = 'C:\BRIGADE Plus Work Directory\SBD railway/SBD_script/'       # Kolla ifall det ska vara C:/BRIGADE Plus Work Directory\SBD railway/
    for indata in indata1[6391:]:
        model_create(indata)
        x_coords,y_coord,Found_boggie = Partition_loads(indata)
        BC1(indata)
        steps(indata)
        loads_cases(indata)
        Load_comb = Load_combinations(indata)
        mesh_size = 200
        mesh(indata,mesh_size)
        try:
            status = run_job(indata)
        except:
            try:
                mesh_size = 190
                mesh(indata,mesh_size)
                status = run_job(indata)
            except:
                continue

        if str(status) =='COMPLETED':
            sls = SLS(indata,Load_comb,file_path)
            if sls['Deflection check'] == 'Deflection ceck OK':
                indata.update({'Deflection check':'Deflection OK','Deflection Frequent [mm]':sls['Deflection Frequent [mm]'],'Deflection Quasi':sls['Deflection Quasi [mm]']})
                results,path_coord,moment_x_bridge = Results(indata,Load_comb,x_coords,y_coord,file_path)
                comb_capacities,parts = ULS(indata,results,moment_x_bridge,path_coord)
                Evaluation(indata,parts,comb_capacities,moment_x_bridge)
                remove(indata,file_path)
            else:
                indata.update({'Deflection check':'Deflection NOT OK','Deflection Frequent [mm]':sls['Deflection Frequent [mm]'],'Deflection Quasi':sls['Deflection Quasi [mm]']})
                remove(indata,file_path)
                directory = 'Bridge_data/'+indata['Model name']
                try:
                    # Create the directory
                    os.mkdir(directory)
                except:
                    pass
                
                csv_name_location2 = str(directory)+'/'+str(indata['Model name'])+'.csv'                                                                               
                field_list2 = list(indata.keys())
                row_indata = [str(indata[key]) for key in field_list2]
                with open(csv_name_location2, 'w') as file:
                    file.write(';'.join(field_list2) + '\n')
                    file.write(';'.join(row_indata) + '\n')
        
run_script()


#Klockslag vid utskrift:
# now = datetime.now()
# print(now)
# indata1 = combination_multy()
# print(len(indata1))

# file_path = 'C:/Users/halucas/Desktop/Master_thesis/SBD_script/'

# indata=indata1[6175]

# model_create(indata)
# x_coords,y_coord,Found_boggie = Partition_loads(indata)
# BC1(indata)
# steps(indata)
# loads_cases(indata)
# Load_comb = Load_combinations(indata)
# mesh_size = 200
# mesh(indata,mesh_size)
# try:
#     status = run_job(indata)
# except:
#     pass
#     # try:
#     #     mesh_size = 190
#     #     mesh(indata,mesh_size)
#     #     status = run_job(indata)
#     # except:
#     #     pass
# #     # continue
# results,path_coord,moment_x_bridge = Results(indata,Load_comb,x_coords,y_coord,file_path)
# comb_capacities,parts = ULS(indata,results,moment_x_bridge,path_coord)
# sls = SLS(indata,Load_comb,file_path)
# if sls['Deflection check'] == 'Deflection ceck OK':
#     indata.update({'Deflection':'Deflection OK','Deflection [mm]':sls['Deflection [mm]']})
    
#     results,path_coord,moment_x_bridge = Results(indata,Load_comb,x_coords,y_coord,file_path)

#     comb_capacities,parts = ULS(indata,results,moment_x_bridge,path_coord)
#     Evaluation(indata,parts,comb_capacities,moment_x_bridge)
#     remove(indata,file_path)
# else:
#     directory = 'Bridge_data/'+indata['Model name']
#     csv_name_location2 = str(directory)+'/'+str(indata['Model name'])+'.csv'                                                         # All reinforcment areas are in mm^2/m, thus converting the lenght to meters. Used for reinforcement in y-direction                                                      
#     field_list2 = list(indata.keys())
#     row_indata = [str(indata[key]) for key in field_list2]
#     with open(csv_name_location2, 'w') as file:
#         file.write(';'.join(field_list2) + '\n')
#         file.write(';'.join(row_indata) + '\n')
#     remove(indata,file_path)
