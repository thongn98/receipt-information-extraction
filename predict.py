#Imports from 3rd parties
import cv2
import torch 
import numpy as np

from transformers       import BertTokenizer
from layoutlm           import LayoutlmForTokenClassification
from torch.nn           import CrossEntropyLoss
from PIL                import Image

#Imports from this repository
from preprocess         import preprocess
from helpers            import get_labels, set_seed

MODEL_PATH = "model/"
LABEL_LIST_PATH = "data/labels.txt"
set_seed(42)
label_list = get_labels(LABEL_LIST_PATH)
pad_token_label_id = CrossEntropyLoss().ignore_index

def predict(image_file):
    """
        Predict token-level classification given the words and bounding boxes

        Parameter:
            image_file: list
                Contains necessary information, more specifically the words, their bounding boxes, receipt image dimension, and the file names
        
        Return:
            dict
                Contains the extracted information(company, address, date, total) with the corresponding image file name
    """
    features    = preprocess(image_file)
    model       = LayoutlmForTokenClassification.from_pretrained(MODEL_PATH)
    device      = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model.to(device)

    input_ids_tensor        = torch.tensor([f.input_ids for f in features], dtype=torch.long)
    attention_mask_tensor   = torch.tensor([f.input_mask for f in features], dtype=torch.long)
    boxes_tensor            = torch.tensor([f.boxes for f in features], dtype=torch.long)
    token_type_ids_tensor   = torch.tensor([f.segment_ids for f in features], dtype=torch.long)
    all_label_ids           = torch.tensor([f.label_ids for f in features], dtype=torch.long)

    with torch.no_grad():
        inputs = {
                    "input_ids": input_ids_tensor.to(device),
                    "attention_mask": attention_mask_tensor.to(device),
                    "labels": all_label_ids.to(device),
                    "bbox": boxes_tensor.to(device),
                    "token_type_ids" : token_type_ids_tensor.to(device)
                }
        outputs = model(**inputs)
        preds   = outputs[1].detach().cpu().numpy()
        
    preds           = np.argmax(preds, axis=2)
    out_label_ids   = inputs["labels"].detach().cpu().numpy()
    preds_list      = [[] for _ in range(out_label_ids.shape[0])]
    label_map       = {i: label for i, label in enumerate(label_list)}

    for i in range(out_label_ids.shape[0]):
        for j in range(out_label_ids.shape[1]):
            if out_label_ids[i, j] != pad_token_label_id:
                preds_list[i].append(label_map[preds[i][j]])

    to_be_append    = []
    results         = []
    result          = []
    prediction_id   = 0

    for i in image_file:
        if(i == ""):
            prediction_id   += 1

            results.append(result)

            result          = []
        else:
            word        = i.split("\t")[0]
            pred        = preds_list[prediction_id].pop(0)
            file_name   = i.split("\t")[-1]

            result.append((word,pred, file_name))

    if result:
        results.append(result)

    for r in results:
        company     = ""
        address     = ""
        date        = ""
        total       = ""
        file_name   = ""

        for w, l, fn in r:
            file_name = fn
            if("COMPANY" in l):
                company = company + " " + w
            elif("ADDRESS" in l):
                address = address + " " + w
            elif("DATE" in l):
                date    = date + " " + w 
            elif("TOTAL" in l):
                total   = total + " " + w
            else:      
                pass

        tba = {"image"      : file_name.strip(),
                "company"   : company.strip(), 
                "address"   : address.strip(), 
                "date"      : date.strip(), 
                "total"     : total.strip()}

        to_be_append.append(tba)

    return to_be_append