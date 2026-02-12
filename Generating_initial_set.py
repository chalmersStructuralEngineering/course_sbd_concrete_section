import numpy as np
import pandas as pd
import os
import copy
import scipy.optimize as opt 
from multiprocessing import Lock
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor
from multiprocessing.pool import Pool
import sys
import time
import shutil

def Rebar_combinations():

    import numpy as np
    concrete_cover = [35]                  #Concrete cover in [mm]
    Rebar_size_s = [16,20,25]                 #Diameters of Longitudinal reinforcements [mm]
    Rebar_size_prim = [16,20,25]
    Rebar_layer = [1,2]                     #Number of reinforcement layers 
    spacing = np.linspace(100,300,5)       #Spacing between bars [mm]

    concrete_class = ['C35/C45']           #Concrete class

    Stirrups_Size = 12                      #Diameter of stirrup reinforcements [mm]                      
    n_rebar_layers = [2]

    final_combinations = []
    # for p in parts:
    #     name = p
    #     id = 1
    #     if 'Foundation' in name:
    #         t_main = t['Foundation footing']['Thickness 1']
    #         t_secondary = t['Foundation footing']['Thickness 2']
    #     else:
    #         t_main = t['{}'.format(name)]['Thickness 1']
    #         t_secondary = t['{}'.format(name)]['Thickness 2']
    #     Combinations = []
    #     if t_secondary>=400:                                                                                      #Smallest height to fit 2 rebar layers 
    #         n_rebar_layers = Rebar_layer
    #     else:
    #         n_rebar_layers = [1]

    for n_rebar in n_rebar_layers:                                                                      #number of rebar horisontal layers
        if n_rebar == 1:
            for sp in spacing:                                                                          #Spacing between reinforcement
                for si in Rebar_size_s:                                                                   #Size of reinforcement
                    for si_prim in [sii for sii in Rebar_size_prim if sii ==si]: 
                        for con_c in concrete_cover:                                                        #Concrete covers 
                            for c in concrete_class:                                                        #concrte classes     
                                comb = {'Combination name':id,'no layers rebar':n_rebar,
                                            'Spacing layer 1':sp,'Spacing layer 2':'','Size layer 1':si,'Size layer 2':'',
                                            'Concrete class':c,'Concrete cover':con_c,'Stirrup size':Stirrups_Size,'Size layer prim':si_prim}
                                final_combinations.append(comb) 
                                
        else:
            for si_1 in Rebar_size_s: 
                for si_2 in [si_1]:
                    for sp_1 in spacing:
                        for si_prim in [size for size in Rebar_size_prim if size ==si_1]: 
                            for sp_2 in [sp_1*space for space in [1,2,3] if space*sp_1<spacing[-1]*2]:               #Second layer should be above the first layer accrodng to SS-EN 1992-1-1 section 8,(8.2)
                                for con_c in concrete_cover:
                                    for c in concrete_class:
                                        comb = {'Combination name':id,'no layers rebar':n_rebar,
                                                    'Spacing layer 1':sp_1,'Spacing layer 2':sp_2,'Size layer 1':si_1,'Size layer 2':si_2,
                                                    'Concrete class':c,'Concrete cover':con_c,'Stirrup size':Stirrups_Size,'Size layer prim':si_prim}
                                        final_combinations.append(comb)
    return final_combinations

def cot(deg):
    rad = np.radians(deg)
    return (1/np.tan(rad))

def create_parts_init(i,j):
    path = "C:\BRIGADE Plus Work Directory\SBD railway\SBD_script/Bridge_data_copy/"+"Slab_bridge-"+str(i)+"/Slab_bridge-"+str(i)
    path_2 = "C:\BRIGADE Plus Work Directory\SBD railway\SBD_script/Bridge_data/Initial_set/"
    final_combinations = Rebar_combinations()
    try:
        csv_Found_12 = pd.read_csv(path+"_Foundation_12.csv",delimiter=';')
        csv_Found_12.flags.writeable = False
    except:
        pass

    csv_bridge = pd.read_csv(path+".csv",delimiter=';')
    csv_bridge.writeable = False

    try:
        csv_span_deck = pd.read_csv(path+"_Bridge deck span.csv",delimiter=';')
        csv_span_deck.writeable = False
        csv_sup_deck =pd.read_csv(path+"_Bridge deck support.csv",delimiter=';')
        csv_sup_deck.flags.writeable = False
        csv_Leg_up = pd.read_csv(path+"_Legs upper.csv",delimiter=';')
        csv_Leg_up.flags.writeable = False
        csv_Leg_low = pd.read_csv(path+"_Legs lower.csv",delimiter=';')
        csv_Leg_low.flags.writeable = False
        csv_Found_foot = pd.read_csv(path+"_Foundation footing.csv",delimiter=';')
        csv_Found_foot.flags.writeable = False
    except:
       pass

    try:
        t1 = float(csv_span_deck['Thickness main'][1])
        t2 = float(csv_sup_deck['Thickness main'][1])
        t3 = float(csv_Leg_up['Thickness main'][1])
        t4 = float(csv_Leg_low['Thickness main'][1])
        t5 = float(csv_Found_foot['Thickness main'][1])
    except:
        print('wrong')
        if csv_bridge['Free span'][0]==16000:
            csv_span_deck2 = pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Bridge deck span.csv",delimiter=';')
            csv_span_deck2.writeable = False
            csv_sup_deck2 =pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Bridge deck support.csv",delimiter=';')
            csv_sup_deck2.flags.writeable = False
            csv_Leg_up2 = pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Legs upper.csv",delimiter=';')
            csv_Leg_up2.flags.writeable = False
            csv_Leg_low2 = pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Legs lower.csv",delimiter=';')
            csv_Leg_low2.flags.writeable = False
            csv_Found_foot2 = pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Foundation footing.csv",delimiter=';')
            csv_Found_foot2.flags.writeable = False
            
            r = float(csv_bridge['Radius'][0])
            l_deck = float(csv_bridge['Span'][0])
            l_sup = float(csv_sup_deck2['Length of segment'][0])
            lspan = l_deck-l_sup
            l_leg = float(csv_bridge['Height legs'][0])
            l_foun = float(csv_bridge['Foundation length'][0])*2

            t_sp_1 = float(csv_bridge['Deck thickness'][0])
            t_sp_2 = t_sp_1-np.sqrt(r**2-(lspan/2)**2)+r
            t_su_1 = t_sp_1-np.sqrt(r**2-(l_deck/2)**2)+r
            t_l_1 = float(csv_bridge['Leg thickness top'][0])
            t_l_2 =  float(csv_bridge['Leg thickness bottom'][0])
            t_l_3 = (t_l_1+t_l_2)/l_leg
            t_found = float(csv_bridge['Foundation thickness'][0])
            
            Asy_sp = float(csv_span_deck2['Asy'][0])
            Asypr_sp = float(csv_span_deck2['Asy_prim'][0])
            Asy_su = float(csv_sup_deck2['Asy'][0])
            Asypr_su = float(csv_sup_deck2['Asy_prim'][0])
            Asy_lu = float(csv_Leg_up2['Asy'][0])
            Asypr_lu = float(csv_Leg_up2['Asy_prim'][0])
            Asy_lo = float(csv_Leg_low2['Asy'][0])
            Asypr_lo = float(csv_Leg_low2['Asy_prim'][0])
            Asy_f = float(csv_Found_foot2['Asy'][0])
            Asypr_f = float(csv_Found_foot2['Asy_prim'][0])

            VEd_sp = float(csv_span_deck2['VEd'][0])
            VEd_su = float(csv_sup_deck2['VEd'][0])
            VEd_lu = float(csv_Leg_up2['VEd'][0])
            VEd_lo = float(csv_Leg_low2['VEd'][0])
            VEd_f = float(csv_Found_foot2['VEd'][0])

            Ap_sp = float(min(csv_span_deck2['Asprimx']))
            Ap_su = float(min(csv_sup_deck2['Asprimx']))
            Ap_lu = float(min(csv_Leg_up2['Asprimx']))
            Ap_lo = float(min(csv_Leg_low2['Asprimx']))
            Ap_f = float(min(csv_Found_foot2['Asprimx']))



            csv_span_deck = {'Length of segment':[0,lspan],'Thickness main':[0,t_sp_1],'Thickness secondary':[0,t_sp_2],'Asy':[0,Asy_sp],'Asy_prim':[0,Asypr_sp],'VEd':[0,VEd_sp],'Size layer y':[0,25],'Asprimx':[0,Ap_sp]}
            csv_sup_deck = {'Length of segment':[0,l_sup],'Thickness main':[0,t_su_1],'Thickness secondary':[0,t_sp_2],'Asy':[0,Asy_su],'Asy_prim':[0,Asypr_su],'VEd':[0,VEd_su],'Size layer y':[0,25],'Asprimx':[0,Ap_su]}
            csv_Leg_up = {'Length of segment':[0,l_leg],'Thickness main':[0,t_l_1],'Thickness secondary':[0,t_l_3],'Asy':[0,Asy_lu],'Asy_prim':[0,Asypr_lu],'VEd':[0,VEd_lu],'Size layer y':[0,25],'Asprimx':[0,Ap_lu]}
            csv_Leg_low = {'Length of segment':[0,l_leg],'Thickness main':[0,t_l_2],'Thickness secondary':[0,t_l_3],'Asy':[0,Asy_lo],'Asy_prim':[0,Asypr_lo],'VEd':[0,VEd_lo],'Size layer y':[0,25],'Asprimx':[0,Ap_lo]}
            csv_Found_foot = {'Length of segment':[0,l_foun],'Thickness main':[0,t_found],'Thickness secondary':[0,t_found],'Asy':[0,Asy_f],'Asy_prim':[0,Asypr_f],'VEd':[0,VEd_f],'Size layer y':[0,25],'Asprimx':[0,Ap_f]}
        
        elif csv_bridge['Free span'][0]==12000:
            csv_span_deck2 = pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Bridge deck span.csv",delimiter=';')
            csv_span_deck2.writeable = False
            csv_sup_deck2 =pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Bridge deck support.csv",delimiter=';')
            csv_sup_deck2.flags.writeable = False
            csv_Leg_up2 = pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Legs upper.csv",delimiter=';')
            csv_Leg_up2.flags.writeable = False
            csv_Leg_low2 = pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Legs lower.csv",delimiter=';')
            csv_Leg_low2.flags.writeable = False
            csv_Found_foot2 = pd.read_csv(path_2 + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Foundation footing.csv",delimiter=';')
            csv_Found_foot2.flags.writeable = False
            csv_Found_122 = pd.read_csv(path + "Slab_bridge-" + str(j) + "/Slab_bridge-" + str(j) + "_Foundation_12.csv",delimiter=';')
            csv_Found_122.flags.writeable = False


            r = float(csv_bridge['Radius'][0])
            l_deck = float(csv_bridge['Span'][0])
            l_sup = float(csv_sup_deck2['Length of segment'][0])
            lspan = l_deck-l_sup
            l_leg = float(csv_bridge['Height legs'][0])
            l_foun = float(csv_Found_foot2['Length of segment'][0])
            l_12 = (float(csv_bridge['Foundation extrusion'][0])*2+l_deck)-l_foun

            t_sp_1 = float(csv_bridge['Deck thickness'][0])
            t_sp_2 = t_sp_1-np.sqrt(r**2-(lspan/2)**2)+r
            t_su_1 = t_sp_1-np.sqrt(r**2-(l_deck/2)**2)+r
            t_l_1 = float(csv_bridge['Leg thickness top'][0])
            t_l_2 =  float(csv_bridge['Leg thickness bottom'][0])
            t_l_3 = (t_l_1+t_l_2)/l_leg
            t_found = float(csv_bridge['Foundation thickness'][0])
            
            Asy_sp = float(csv_span_deck2['Asy'][0])
            Asypr_sp = float(csv_span_deck2['Asy_prim'][0])
            Asy_su = float(csv_sup_deck2['Asy'][0])
            Asypr_su = float(csv_sup_deck2['Asy_prim'][0])
            Asy_lu = float(csv_Leg_up2['Asy'][0])
            Asypr_lu = float(csv_Leg_up2['Asy_prim'][0])
            Asy_lo = float(csv_Leg_low2['Asy'][0])
            Asypr_lo = float(csv_Leg_low2['Asy_prim'][0])
            Asy_f = float(csv_Found_foot2['Asy'][0])
            Asypr_f = float(csv_Found_foot2['Asy_prim'][0])
            Asy_12 = float(csv_Found_122['Asy'][0])
            Asypr_12 = float(csv_Found_122['Asy_prim'][0])

            VEd_sp = float(csv_span_deck2['VEd'][0])
            VEd_su = float(csv_sup_deck2['VEd'][0])
            VEd_lu = float(csv_Leg_up2['VEd'][0])
            VEd_lo = float(csv_Leg_low2['VEd'][0])
            VEd_f = float(csv_Found_foot2['VEd'][0])
            VEd_12 = float(csv_Found_122['VEd'][0])

            Ap_sp = float(min(csv_span_deck2['Asprimx']))
            Ap_su = float(min(csv_sup_deck2['Asprimx']))
            Ap_lu = float(min(csv_Leg_up2['Asprimx']))
            Ap_lo = float(min(csv_Leg_low2['Asprimx']))
            Ap_f = float(min(csv_Found_foot2['Asprimx']))
            Ap_12= float(min(csv_Found_122['Asprimx']))

            csv_span_deck = {'Length of segment':[0,lspan],'Thickness main':[0,t_sp_1],'Thickness secondary':[0,t_sp_2],'Asy':[0,Asy_sp],'Asy_prim':[0,Asypr_sp],'VEd':[0,VEd_sp],'Size layer y':[0,25],'Asprimx':[0,Ap_sp]}
            csv_sup_deck = {'Length of segment':[0,l_sup],'Thickness main':[0,t_su_1],'Thickness secondary':[0,t_sp_2],'Asy':[0,Asy_su],'Asy_prim':[0,Asypr_su],'VEd':[0,VEd_su],'Size layer y':[0,25],'Asprimx':[0,Ap_su]}
            csv_Leg_up = {'Length of segment':[0,l_leg],'Thickness main':[0,t_l_1],'Thickness secondary':[0,t_l_3],'Asy':[0,Asy_lu],'Asy_prim':[0,Asypr_lu],'VEd':[0,VEd_lu],'Size layer y':[0,25],'Asprimx':[0,Ap_lu]}
            csv_Leg_low = {'Length of segment':[0,l_leg],'Thickness main':[0,t_l_2],'Thickness secondary':[0,t_l_3],'Asy':[0,Asy_lo],'Asy_prim':[0,Asypr_lo],'VEd':[0,VEd_lo],'Size layer y':[0,25],'Asprimx':[0,Ap_lo]}
            csv_Found_foot = {'Length of segment':[0,l_foun],'Thickness main':[0,t_found],'Thickness secondary':[0,t_found],'Asy':[0,Asy_f],'Asy_prim':[0,Asypr_f],'VEd':[0,VEd_f],'Size layer y':[0,25],'Asprimx':[0,Ap_f]}            
            csv_Found_12 = {'Length of segment':[0,l_12],'Thickness main':[0,t_found],'Thickness secondary':[0,t_found],'Asy':[0,Asy_12],'Asy_prim':[0,Asypr_12],'VEd':[0,VEd_12],'Size layer y':[0,25],'Asprimx':[0,Ap_12]}



    spacing = np.linspace(100,400,13)  

    if float(csv_bridge['Free span'][0]) == 12000:
        parts={'csv_span_deck':csv_span_deck,'csv_sup_deck':csv_sup_deck,'csv_Leg_up':csv_Leg_up,'csv_Leg_low':csv_Leg_low,'csv_Found_foot':csv_Found_foot,'csv_Found_12':csv_Found_12}
        parts = [csv_span_deck,csv_sup_deck,csv_Leg_up,csv_Leg_low,csv_Found_foot,csv_Found_12]
        parts_str = (["csv_span_deck","csv_sup_deck","csv_Leg_up","csv_Leg_low","csv_Found_foot","csv_Found_12"],
                     ['Bridge deck span','Bridge deck support','Legs upper','Legs lower', 'Foundation footing','Foundation_12'])
        
    else:
        parts = [csv_span_deck,csv_sup_deck,csv_Leg_up,csv_Leg_low,csv_Found_foot]
        parts_str = (["csv_span_deck","csv_sup_deck","csv_Leg_up","csv_Leg_low","csv_Found_foot"],
                     ['Bridge deck span','Bridge deck support','Legs upper','Legs lower', 'Foundation footing'])
    combinations = {}
    
    w = float(csv_bridge['Width'][0])
    concrete_class = csv_bridge['Concrete class'][0]
    for j in range(len(parts)):
        p = parts[j]
        name = parts_str[0][j]
        comb = final_combinations.copy()
        t = float(p['Thickness main'][1])
        t2 = float(p['Thickness secondary'][1])
        Asy = float(p['Asy'][1])
        Asy_prim = float(p['Asy_prim'][1])
        min_v_spac = 40
        As_prim_ref = float(min(p['Asprimx'][1:]))
        l = float(p['Length of segment'][1])
        VEd = float(p['VEd'][1])
        oy = float(p['Size layer y'][1])
        combs=[]
        for c in comb:
            o1 = c['Size layer 1']
            o_prim = c['Size layer prim']
            s1 = c['Spacing layer 1']
            if c['no layers rebar'] ==2:
                s2 = c['Spacing layer 2']
                o2 = c['Size layer 2']
            else:
                s2 = 100
                o2 = 0

            As_1 = (o1**2/4*np.pi)/(s1/1000)
            As_2 = (o2**2/4*np.pi)/(s2/1000)
            concrete_cover = c['Concrete cover']
            d1 = t-concrete_cover-o1/2                            #Height reinforcement layer 1
            d2 = t-concrete_cover-o1-min_v_spac-o2/2        

            d =(As_1*d1+As_2*d2)/(As_1+As_2)
            
            As_prim_trial = ((o_prim**2/4)*np.pi)/(2*0.3)
            if As_prim_trial>As_prim_ref:
                As_prim = As_prim_trial
            else:
                As_prim_ref_2 = As_prim_trial*(2*0.3)/(spacing/1000)
                pos = np.argmin(abs(As_prim_ref_2-As_prim_ref)) 
                As_prim = As_prim_ref_2[pos]
            
            z = d*0.9
            theta = 45 
            fck = 35
            fyk = 500
            fcd = fck/1.5
            b = 1000
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

            for spac in np.flip(spacing):
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
                    c.update({'Stirrups':'Stirrups needed','sx stirrups':spac,'Asw':Asw,'Thickness main':t,'Thickness secondary':t2,
                              'As1x':As_1,'As2x':As_2,'Asy':Asy,'Asy_prim':Asy_prim,'Length of segment':l,'Asprimx':As_prim,'Width':w,
                              'Concrete class':concrete_class,'Size layer y':oy,'VEd':VEd})
                    combin = c.copy()
                    combs.append(combin)
                    break
        combinations.update({name:combs})
        
    return combinations,parts_str






    # MIN 12, Max 12 = [9,1072]
    # MAX 16, MIN 16 = [1785,7012]

def Evaluation():
    
    def Find_length_rebar_deck(x):
        return float(indata['Deck thickness'][0])-np.sqrt(r**2-x**2)+r-t_range

    def Find_length_rebar_leg(x):
        return t1+(t2-t1)/(h/2)*x-t_range  
    j=0
    for i in range(1,7021):
        print(i)
        path = "C:\BRIGADE Plus Work Directory\SBD railway\SBD_script/Bridge_data/Initial_set/"
        try:
            indata = pd.read_csv(path + "Slab_bridge-"+str(i)+"/Slab_bridge-"+str(i)+"_new.csv",delimiter=';')
            indata.flags.writeable = False
        except:
            continue
        
        combinations,parts = create_parts_init(i,j)
        file_path_1 = 'Evaluation_criteria.csv'
        file_path_2 = 'Material_criteria.csv'

        # Define the data types for the columns
        dtype1 = [('Work/factor', 'U50'), ('deck', 'f8'), ('Wing', 'f8'), ('Leg', 'f8'), ('Found', 'f8'), ('unit', 'U5')]

        dtype2 = [('Concrete', 'U8'), ('SEK/m3', 'f8'), ('kg CO2e/m3 ', 'f8'), ('CO2e/kg', 'f8')]

        # Load the CSV file into a structured numpy array
        time_parameters = np.genfromtxt(file_path_1, delimiter=';', dtype=dtype1, skip_header=1)
        material_parameters = np.genfromtxt(file_path_2, delimiter=';', dtype=dtype2, skip_header=1)

        ############################################################################

        #Concrete class
        # concrete_class = combinations[parts[0]][0]

        ################################################################################
        #Cost of material
        # if concrete_class == 'C32/42':
        #     C_concrete = float(material_parameters[0][1])                                      # Cost, SEK/m3
        # elif concrete_class == 'C35/C45':
        #     C_concrete = float(material_parameters[1][1])                                      # Cost, SEK/m3
        # else:
        #     C_concrete = float(material_parameters[2][1])                                      # Cost, SEK/m3
        C_reinforcement = float(material_parameters[3][1])                                     # Cost, SEK/m3

        ################################################################################
        #CO2 equivalents of material
        # if concrete_class == 'C32/42':
        #     E_concrete = float(material_parameters[0][2])                                      # CO2 equivalents, CO2/m3
        # elif concrete_class == 'C35/C45':
        #     E_concrete = float(material_parameters[1][2])                                      # CO2 equivalents, CO2/m3
        # else:
        #     E_concrete = float(material_parameters[2][2])                                      # CO2 equivalents, CO2/m3
        E_reinforcement = float(material_parameters[3][2])                                     # CO2 equivalents, CO2/m3

        ################################################################################
        Build_cost = 500                                                                # Cost [SEK] of 1 hour of work

        ################################################################################

        # Creates a directory for each bridge varation in indata
        directory = 'C:\BRIGADE Plus Work Directory\SBD railway\SBD_script\Bridge_data/Initial_set/Slab_bridge-'+str(i)
        # try:
        #     # Create the directory
        #     os.mkdir(directory)
        # except:
        #     pass
        
        r = float(indata['Radius'][0])
        h = float(indata['Height legs'][0])
        for k in range(len(parts[0])):
            p = parts[0][k]
            p_name = parts[1][k]
            l = combinations[p][0]['Length of segment']
            w_meter = combinations[p][0]['Width']/1000                                          # All reinforcment areas are in mm^2/m, thus converting the width to meters. Used for reinforcement in x-direction
            w = combinations[p][0]['Width']
            l_meter = l/1000

            csv_name_location = str(directory)+'/'+'Slab_bridge-'+str(i)+'_'+p_name+'.csv'                                                         # All reinforcment areas are in mm^2/m, thus converting the lenght to meters. Used for reinforcement in y-direction                                                      
            # try:
            with open(csv_name_location, 'w') as file:
                field_list = list(combinations[p][0].keys())
                field = field_list + ['Material cost of Reinforcement','Hours of reinforcement work','Cost of reinforcement labour','Emissions of reinforcement','Volume reinforcement']
                file.write(';'.join(field) + '\n')
            
            for comb in combinations[p]:
                
                Vx1 = comb['As1x']*w_meter*l
                Vx2 = comb['As2x']*w_meter*l
                Vx_prim = comb['Asprimx']*w_meter*l
                Vy = (comb['Asy']+comb['Asy_prim'])*w*l_meter

                if comb['Stirrups']== 'Stirrups not need':
                    V_stirrups = 0
                else:
                    V_stirrups = (comb['Asw']*w_meter*l/comb['sx stirrups']) * abs(comb['Thickness main']-comb['Thickness secondary'])/2
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
                            if 'deck' in p:
                                t_range = 400
                                l_400 = opt.fsolve(Find_length_rebar_deck,1000)
                                if 'span' in p:
                                    l1 = 2*l_400
                                    l2 = l-l1
                                else:
                                    l1 = l-2*(indata['Span'][0]/2-l_400)
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
                            if 'deck' in p:
                                t_range = 400
                                l_400 = opt.fsolve(Find_length_rebar_deck,1000)
                                t_range = 600
                                l_600 = opt.fsolve(Find_length_rebar_deck,1000)
                                if 'span' in p:
                                    l1 = 2*l_400
                                    l2 = 2*(l_600-l_400)
                                    l3 = l-l1-l2
                                else:
                                    l1 = l-2*(indata['Span'][0]/2-l_400)
                                    l2 = l-2*(indata['Span'][0]/2-l_600) - l1
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
                            if 'deck' in p:
                                t_range = 600
                                l_600 = opt.fsolve(Find_length_rebar_deck,1000)
                                if 'span' in p:
                                    l2 = 2*(l_600)
                                    l3 = l-l2
                                else:
                                    l2 = l-2*(indata['Span'][0]/2-l_600)
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
                comb.update({'Material cost of Reinforcement':C_material_Re,'Hours of reinforcement work':h_reinforcement,'Cost of reinforcement labour':C_build_Re,
                            'Emissions of reinforcement':E_Re,'Volume reinforcement':V_Re})

                row = [str(p)] + [str(comb[key]) if not isinstance(comb[key], str) else comb[key] for key in field[1:]]
                with open(csv_name_location, 'a') as file:                    
                        # Write the data row
                            file.write(';'.join(row) + '\n')
            # except:
            #     pass

        j = i

def concrete_volume():

    for i in range(1089,1088):
        print(i)
        path = "C:\BRIGADE Plus Work Directory\SBD railway\Bridge_data/"

        try:
            indata = pd.read_csv(path + "Slab_bridge-" + str(i) + "/Slab_bridge-" + str(i) + ".csv",delimiter=';')
        except:
            continue
        
        try:
            Emissions = float(indata['Emissions of concrete'][0])
        except:
            Emissions = 0
        
        if Emissions !=0:
            # Example usage
            destination_folder = "C:\BRIGADE Plus Work Directory\SBD railway\SBD_script/Bridge_data/Initial_set/Slab_bridge-"+str(i)+"/Slab_bridge-"+str(i)+"_new.csv"
            indata.to_csv(destination_folder, index=False, sep=';')
            # copy_and_rename(source_file, destination_folder, new_file_name)
            continue

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
        concrete_class = indata['Concrete class'][0]


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
        if indata['Manual control'][0] !='':
            control_span = indata['Manual control'][0]*1000
        else:
            control_span = indata['Free span'][0]

        r = float(indata['Radius'][0])                                                            # Radius of underside of deck
        t_span = float(indata['Deck thickness'][0])                                               # Bridge deck thickness in span
        l_deck = float(indata['Free span'][0])                                                         # Lenght of deck
        t_sup = t_span-np.sqrt(r**2-(float(indata['Free span'][0])/2)**2)+r                            # Bridge deck thickness at support
        
        w = float(indata['Width'][0])

        #Calculating the area with segment theorem for circles
        theta = np.arcsin((l_deck/2)/r)*2                                               # Circle segment angle

        A_side_deck = t_sup*l_deck-0.5*r**2*(theta-np.sin(theta))                       # Radius side area of bridge deck [mm]
        
        A_under_side_deck = w*r*theta                                                   # Area of underside of bridge [mm^2]
        A_deck_form = (A_under_side_deck+A_side_deck*2)/10**6                           # Area of formwork for bridge deck [m^2]

        V_deck = A_side_deck*w/10**9                                                    # Volume of bridge deck [m^3]

        #Data from legs
        h = float(indata['Height legs'][0])                                                       # Height of bridge legs [mm]
        t_bot = float(indata['Leg thickness bottom'][0])                                          # Leg thickness in the bottom [mm]
        t_top = float(indata['Leg thickness top'][0])                                             # Leg thickness in the top [mm]

        A_leg = w*h                                                                     # Area/leg [mm^2]
        A_side_leg = t_bot *h + (t_top-t_bot)*h/2                                       # Area of leg, profile view [mm^2]

        A_leg_form = 2*(A_leg+2*A_side_leg+np.sqrt((t_top-t_bot)**2+h**2)*w)/10**6      # Area of formwork for legs[m^2]

        V_legs = 2*A_side_leg * w/10**9                                                 # Volume of legs [m^3]

    #Foundation lenght
        if control_span == 12000:
            foundation_lenght = indata['Foundation length'][0]+indata['Foundation extrusion'][0]*2    # Length of foundation 12m version
        else:
            foundation_lenght = indata['Foundation length'][0]*2                           # Length of foundation 16m version

        t_found = float(indata['Foundation thickness'][0])                                        # Foundation thickness [mm]
        A_foundation_form = (2*foundation_lenght+2*w)*t_found/10**6                     # Area of formwork for foundation

        V_foundation = foundation_lenght*t_found*w/10**9                                # Volume of foundation [m^3]

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

        # path_3 = "C:/Users/halucas/Desktop/Master_thesis/SBD_script/Bridge_data/Initial_set/Slab_bridge-"+str(i)+"/Slab_bridge-"+str(i)+"_Bridge deck span.csv"
        # try:
        #     pd.read_csv(path_3,delimiter=';')
        # except:
        #     continue

        path_2 = "C:\BRIGADE Plus Work Directory\SBD railway\SBD_script/Bridge_data/Initial_set/Slab_bridge-"+str(i)+"/Slab_bridge-"+str(i)+"_new.csv"
        indata['Volume concrete'] = [V_concrete]  # Example: Adding a new column with some values
        indata['Hours of concrete work'] = [h_concrete]  # Example: Adding a new column with some values
        indata['Cost of concrete labour'] = [C_build_Con]  # Example: Adding a new column with some values
        indata['Material cost of concrete'] = [C_material_Con]  # Example: Adding a new column with some values
        indata['Emissions of concrete'] = [E_Con]  # Example: Adding a new column with some values    
        indata['Hours of formwork work'] = [h_formwork]  # Example: Adding a new column with some values
        indata['Cost of formwork labour'] = [C_build_form]  # Example: Adding a new column with some values
        indata['Material cost of formwork'] = [C_material_form]  # Example: Adding a new column with some values
        
        indata.to_csv(path_2, index=False, sep=';')

def count_comb_one_part():
   final_combinations = Rebar_combinations()
   print(len(final_combinations))

def create_folders():
    for i in range(1,7021):
        path = "C:\BRIGADE Plus Work Directory\SBD railway\SBD_script/Bridge_data/"
        try:
            indata = pd.read_csv(path + "Slab_bridge-" + str(i) + "/Slab_bridge-" + str(i) + ".csv",delimiter=';')
        except:
            continue
        
        path2 = "C:\BRIGADE Plus Work Directory\SBD railway\SBD_script/Bridge_data/Initial_set/Slab_bridge-"+str(i)
        os.mkdir(path2)

# def main():
#     # i = 1
#     # combinations,parts = create_parts_init(i)
#     # print(combinations[parts[0]][0])
#     # for ii in parts:
#     #     for comb in combinations[ii]:
#     #         print(comb['As2x'])
#     with Pool(cpu_count()) as p:
        
#         items = [(i) for i in range(1081,7021)]
#     # for i in range(len_deck_span):
#     #     Bridge_iterations(i,ii,Bridge, Deck_span, Deck_support, Leg_upper, Leg_lower, footing, found12,len_deck_span ,len_deck_sup, len_leg_upper, len_leg_lower, len_footing, len_found12, C_concrete, E_concrete,csv_name)
#         p.starmap(Evaluation, items)

def trying():
    Evaluation()
# count_comb_one_part()
# trying()
# create_folders()
# concrete_volume()
Evaluation()
