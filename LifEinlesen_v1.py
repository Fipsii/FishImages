# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 22:49:53 2022

@author: acer
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 18:23:38 2022

@author: acer
"""
## Read.lif
import numpy as np
from PIL import Image
from readlif.reader import LifFile
import cv2 as cv2
import configparser 




def makeList (RawLifList):

    RawLifList = [i for i in RawLif.get_iter_image()] ### Create List with All ZStacks aka Lsit of 20 with every entity being 170 or so pictures
    z_list = [] ### New Lsit
    
    for x in range(len(RawLifList)): # For all picture Stacks
        
        temp  = [i for i in RawLifList[x].get_iter_z(t=0, c=0)] ## Für alle Einzelbilder in Zstacks
    
        for y in range(len(temp)):                              ## Für alle Bilder in Z-Stack
        
            temp[y] = np.array(temp[y])                         ## Mach aus den pillow einzelbildern objecten numpy arrays
     
        z_list.append(temp)                                     ## Und häng allow numpy objecte als eine list in die z_lsit
        
    return(z_list)

#################################################################


    
def makeImages (z_list):                                        ## Nimm 20 Lsite mit numpy Bilderliste

    AllImages = []

    for i in range(len(z_list)):                                ## für all Bilder (20)
    
        List = z_list[i]                                        ## Einzelbilder als eigene List
        
        for q in range(1,len(List)):                            ## für alle Bilder außer das Erste
        
            List[0] = np.where(List[0] < List[q], List[q], List[0]) ## Vergleiche immer das erste bild mit den andern höhere Werte werden in das erste Bild kopiert
    
        AllImages.append(List[0])                               ## Bild an Stelle 1 ist nun das MaxPixelValueBild

    return (AllImages)




#########################################################################
############################################

def PicturePreparation(Image_list):                             ## Bilder Pixelgenau schneiden und Helligkeit anpassen sowie Kontrast
   
    for x in range(0,len(Image_list)):                          ## Für alle Bilder
        
        Image_list[x] = np.array(Image_list[x])                 ## Eigentlich unnötig, Stelle sicher Bilder sind np.arrays, Rudiment der ersten Fassung
        Image_list[x] = cv2.getRectSubPix(Image_list[x], (512,512),(512.26/2,512/2)) ## Schneide Bild: 512/512 ist das endformat, 512.26/2, 512/2 der neue Mittelpunkt
                                                                                     ## Werte werden linear interpoliert: Pixel Ganz unten gehen verloren sowie ganz oben leicht dunkler
                                                                                     ## Dadurch fehlt im vergleich zu Fiji ein Pixel am Ende da der des letzen Bildes nicht ersetzt wird durch 
                                                                                     ## ein Bild drunter. Ist aber unwichtig da es immer schwarze Restzeile ist ohne Axon
        
        minval = np.percentile(Image_list[x], 50)               ## Kontrasterhöhung untere 50% auf null setzen, schwarzes Rauschen wert war beliebig 15% gehen auch
        Image_list[x] = np.clip(Image_list[x], minval, 255)
        Image_list[x] = ((Image_list[x] - Image_list[x].min())/(Image_list[x].max() - Image_list[x].min()))*255 ## Helligkeit normalisieren der Bilder
        
    return(Image_list)

def ProduceCutList (Image_list): ## Schneide Liste
    
    Cut_list = list(range(len(Image_list))) ## Liste mit Länge der Einzelbilder
    Cut_list[0] = Image_list[0]             ## Schneide Bild 1 nicht
    
    for x in range(1,len(Image_list)):      ## Ab Bild 2
        
        Cut_list[x] = Image_list[x][48:]    ## Cut die ersten 48 Entries (Overlap von 47.2 -> 48 wegen Rect subPix)
        
    return(Cut_list) 

############################################

def PictureRotate(CutImages):               ## Finde x-Verschiebung
    
   List_Rotated = []                        ## Lsite mit den Werten
   Rotated_Cut_list = CutImages             ## Liste mit Bidlern
   
   for x in range(len(Rotated_Cut_list)-1): ## Für alle bilder aus Bild 1
       
       Error_list = []                      ## Liste mit Fehler werten für jede Rotation
       LastRow =  Rotated_Cut_list[x][-1]   ## Schnittstelle der Bilder in Bild 1
       FirstRow =  Rotated_Cut_list[x+1][0] ## Schnittstelle in Bild 2
       
       for y in range(-256,256):            ## Für 256 nach links und rechts (ganzes Bild) unnötig kostet aber kaum Zeit
           
           Roll = np.roll(FirstRow, y, axis=0) ## Rotate array in x axis
           IntermediateRow = LastRow - Roll    ## Subtract ist from the other row
           AbsoluteValues = np.absolute(IntermediateRow) ## get absolute values
           SumOfValues = np.sum(AbsoluteValues) ##
           Error_list.append(SumOfValues)

       IndexList = list(range(-256,256))
    
       LowestErrorPixel = IndexList[Error_list.index(min(Error_list))]
       
       List_Rotated.append(LowestErrorPixel)    
       
   for z in range(len(List_Rotated)-1):
           
       List_Rotated[z+1] += List_Rotated[z]
       
   return (List_Rotated,  Rotated_Cut_list)


def RotateUncutList (Image_list, List_Rotated):
    
    for x in range(1, len(Image_list)):
       
        Image_list[x] = np.roll(Image_list[x], List_Rotated[x-1], axis = 1)
        
    return(Image_list)

def Blend (UncutListRotated):
    
    for x in range(len(UncutListRotated)-1):
        
        UpperImage = UncutListRotated[x][-48:]
        LowerImage = UncutListRotated[x+1][:48]
        Combination = np.zeros((48,512))
        
        for y in range(len(LowerImage)):
            
            if y == 0:
            
                alpha = 0
                Combination[y] = (LowerImage[y]*alpha) + (UpperImage[y]*(1-alpha))
            
            else:
             
                alpha = y/48
                Combination[y] = (LowerImage[y]*alpha) + (UpperImage[y]*(1-alpha))   
    
        UncutListRotated[x][-48:] = Combination
        UncutListRotated[x+1] = UncutListRotated[x+1][48:]
          
    return(UncutListRotated)
   
def Stitch(Image_list): 
    
    
    while len(Image_list) > 1:
        Image1 = Image_list[0]
        Image2 = Image_list[1]
        
        Zusammenschnitt = np.concatenate((Image1, Image2), axis = 0)
        
        Image_list.pop(0)
        Image_list[0] = Zusammenschnitt
      
    
    WholeArray = Zusammenschnitt
    #print(type(WholeArray))
    return(WholeArray)

def ImageSave (WholeArray, savelocation, x):
    
        save = savelocation + Name + str(x) +'.tif'
        #print(type(WholeArray), WholeArray, 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        #WholeArray = np.array(WholeArray.astype('uint8'))
        ImageFromArray = Image.fromarray(WholeArray)
        ImageFromArray.save(save)
        ImageFromArray.show()
    
        return(ImageFromArray)


def MakeGreenBMP (ImageFromArray, savelocation, x):
    
    BMP = ImageFromArray.convert('RGBA')
    save = savelocation + Name + str(x) +'.bmp'
    BMP_array = np.array(BMP)
    #print(save)
    lut = np.zeros((256,1,4))
    zeros = [0]*256
    alphaValue = [255]*256
    lut[:,0,0] = zeros
    lut[:,0,1] = list(range(256))
    lut[:,0,2] = zeros
    lut[:,0,3] = alphaValue
    
    
    GreenBMP = cv2.LUT(BMP_array, lut)
    cv2.imwrite(save,GreenBMP)
    
    return(GreenBMP)


def SplitImages(ImageSplit, Lifliste):
    
    Temp = ImageSplit.copy()
    OrderedLifList = []
    z = 0
    y = 0
    for number in range(len(Temp)):
    
        ImageSplit[number] = int(ImageSplit[number])

    for x in ImageSplit:
        z += x
        OrderedLifList.append(Lifliste[y:z])
        y += x
        
    return (OrderedLifList)    


############################################################ it fucking works! 15.04.22
config = configparser.ConfigParser()
config.sections()
Configfile = config.read('example.ini')
config.sections()

path = config['Changeable']['path']
savelocation = config['Changeable']['savelocation']
Format = config['Changeable']['Format']
Name = config['Changeable']['Name']
ImageSplit = list(config['Changeable']['ImagesPerFish'])


RawLif = LifFile(path)
Lifliste = makeList(RawLif)
Lifliste = makeImages(Lifliste) 
Split = SplitImages(ImageSplit, Lifliste)
#Image.fromarray(Lifliste[0]).show()
print(np.shape(Split))

for x in range(len(Split)):
    
    ImageSequence = Split[x]
    print(len(ImageSequence))
    ImageSequencePrep = PicturePreparation(ImageSequence)
    
    if len(ImageSequence) > 1:
        print(x)
        Cut = ProduceCutList(ImageSequencePrep)
        RotationValues, Rotated_Cut_Images = PictureRotate(Cut)
        RotatedUncutList = RotateUncutList(ImageSequencePrep, RotationValues)
        BlendedCut = Blend(RotatedUncutList)
        StitchedImage = Stitch(BlendedCut)
        Saved = ImageSave(StitchedImage, savelocation, x)
        BMPSave = MakeGreenBMP(Saved, savelocation, x)

    else:
        
        StitchedImage = ImageSequencePrep
        Saved = ImageSave(StitchedImage, savelocation, x)
        BMPSave = MakeGreenBMP(Saved, savelocation, x)

        
### Bei durchgang 2 Wholearray leere Liste