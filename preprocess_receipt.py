import json
import os

import cv2

from PIL    import Image
from tqdm   import tqdm

from helpers import actual_bbox_string, bbox_string

image_data_path = "data/images/"
annotations_path = "data/annotations/"
extract_info_path = "data/extract/"

box_file = "train_box.txt"
image_file = "train_image.txt"
label_file = "train.txt"
mismatch_file = "ocr_mismatch.txt"

with open(
        label_file,
        "w",
        encoding="utf8",
    ) as fw, open(
        box_file,
        "w",
        encoding="utf8",
    ) as fbw, open(
        image_file,
        "w",
        encoding="utf8",
    ) as fiw, open(
        mismatch_file,
        "w",
        encoding="utf8"
    ) as fmw:
        for file in os.listdir(image_data_path):
            #Set up path variables to read/write
            image_path      = os.path.join(image_data_path, file)
            ocr_path        = image_path.replace("images", "annotations")
            ocr_path        = ocr_path.replace("jpg", "txt")
            extract_path    = image_path.replace("images", "extract")
            extract_path    = extract_path.replace("jpg", "json")

            #Get necessary image info 
            file_name       = os.path.basename(image_path)
            img             = cv2.imread(image_path) 
            image           = Image.fromarray(img, 'RGB')
            width, length   = image.size

            #Load dataset's extracted information json 
            with open(extract_path, "r", encoding="utf8") as f:
                data = json.load(f)
            
            #Process the dataset's ocr result file
            with open(ocr_path, "r", encoding="utf-8") as f:
                labels          = {"company" : "", "address": "", "total": "", "date": ""}
                company         = 0
                address         = 0
                total           = 0
                date            = 0
                curr_label      = None
                previous_label  = None
                curr_text       = ""
                
                #Extract text line and bounding box
                for line in f:
                    split_line                      = line.split(",")
                    x1, y1, x2, y2, x3, y3, x4, y4  = split_line[:8]
                    x1, y1, x2, y2, x3, y3, x4, y4  = int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), int(x4), int(y4)
                    split                           = "{},{},{},{},{},{},{},{},".format(x1,y1,x2,y2,x3,y3,x4,y4)
                    text                            = line.split(split)[1].lstrip().rstrip()

                    labeled                         = False
                    
                    #Label the text line. Assumption: Each extracted info field only spans across consecutive line. For example: the address printed on the receipt only spans
                    #across consecutive line
                    for key in data.keys():
                        if (text in data[key] or data[key] in text):
                            labeled     = True
                            labels[key] = labels[key] + " " + text
                            curr_label  = key

                            if(key  == "company"):
                                company += 1
                            elif(key == "date"):
                                date    += 1
                            elif(key == "total"):
                                total   += 1
                            else:
                                address += 1

                    if(labeled == False):
                        curr_label = "O"

                    if((curr_label == previous_label or previous_label == None) and (curr_label != "O")):
                        curr_text       = curr_text + " " + text
                        previous_label  = curr_label
                    elif(previous_label != None):
                        curr_text       = curr_text.rstrip().lstrip()
                        l               = previous_label.upper()
                        
                        if(len(curr_text.split()) == 1):
                            fw.write("{}\t{}\n".format(curr_text.split()[0], "S-"+ l))
                        else:
                            for i in range(len(curr_text.split())):
                                if (i == 0):
                                    fw.write("{}\t{}\n".format(curr_text.split()[i], "B-" + l))
                                elif (i == len(curr_text.split()) - 1):
                                    fw.write("{}\t{}\n".format(curr_text.split()[i], "E-" + l))
                                else:
                                    fw.write("{}\t{}\n".format(curr_text.split()[i], "I-" + l))

                        if(curr_label != "O"):
                            curr_text       = text
                            previous_label  = curr_label
                        else:
                            curr_text       = ""
                            previous_label  = None

                    phrase_width    = x2 - x1
                    width_per_char  = phrase_width/len(text)
                    words           = text.split()
                    current_length  = x1

                    #Write the process info into appropriate file
                    for w in words:
                        word_width          = width_per_char * len(w)
                        word_box            = [round(current_length), round(y1), round(current_length + word_width), round(y3)]
                        current_length      = current_length + word_width + width_per_char
                        box_string          = bbox_string(word_box, width, length)
                        actual_box_string   = actual_bbox_string(word_box, width, length)

                        fbw.write("{}\t{}\n".format(w, box_string))
                        fiw.write("{}\t{}\t{}\n".format(w, actual_box_string, file_name))

                        if(curr_label == "O"):
                            fw.write("{}\t{}\n".format(w, curr_label))

            fmw.write("Expected extract info{}\n".format(data))
            fmw.write("Processed extract info{}\n".format(labels))
            for key in data.keys():
                if(data[key] != labels[key].lstrip().rstrip()):
                    fmw.write("OCR mismatch in file {} specifically in key:{}; expected: {} but processed: {}\n".format(file_name, key, data[key], labels[key].lstrip().rstrip()))

            fw.write("\n")
            fbw.write("\n")
            fiw.write("\n")