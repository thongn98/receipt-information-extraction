#Imports from python built-in modules
import json

#Imports from 3rd parties
import cv2
from transformers   import BertTokenizer
from torch.nn       import CrossEntropyLoss
from PIL            import Image

#Imports from this repository
from helpers        import actual_bbox_string, bbox_string, get_labels

LABEL_LIST_PATH = "data/labels.txt"
MAX_SEQ_LENGTH  = 512
MODEL_PATH      = "model/"

class InputExample(object):
    """
        This is taken from layoutlm repository with slight modification for prediction. 
        Represent a single training/test example for token classification. Each example corresponds to an receipt image

        Attributes:
            words           : list
                list of all the words in one example
            boxes           : list
                list of all the words' bounding boxes (relative with the image size)
            actual_bboxes   : list
                list of all the words' bounding boxes (absolute position)
            page_size       : list
                contains the [width, legnth] of the image
            file_name       : string
                the image file's name
            labels          : list
                list of all the classification labels for the words (each can be default to 0 when using to predict)
    """

    def __init__(self, words, boxes, actual_bboxes, page_size, labels, file_name):
        """
            Constructs a InputExample
        """
        self.words = words
        self.boxes = boxes
        self.actual_bboxes = actual_bboxes
        self.page_size = page_size
        self.file_name = file_name
        self.labels = labels


class InputFeatures(object):
    """
        This is taken from layoutlm repository with slight modification for prediction. 
        Represent a single set of features of data.

        Attributes:
            input_ids       : list
                tokenized and padded words sequence
            input_mask      : list
                mask sequence for the input words
            segment_ids     : list
                segment sequence 
            boxes           : list
                tokenized and padded relative bounding boxes sequence
            actual_bboxes   : list
                absolute bounding boxes sequence 
            page_size       : list 
                contains the [width, legnth] of the image
            file_name       : string 
                the image file's name
            labels_ids      : list 
                tokenized and padded label sequence
    """

    def __init__(
        self,
        input_ids,
        input_mask,
        segment_ids,
        boxes,
        actual_bboxes,
        page_size,
        label_ids,
        file_name
    ):
        """
            Constructs a InputFeatures
        """
        assert (
            0 <= all(boxes) <= 1000
        ), "Error with input bbox ({}): the coordinate value is not between 0 and 1000".format(
            boxes
        )
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.boxes = boxes
        self.actual_bboxes = actual_bboxes
        self.page_size = page_size
        self.label_ids = label_ids
        self.file_name = file_name

def convert_examples_to_features(
    examples,
    label_list,
    max_seq_length,
    tokenizer,
    cls_token_at_end=False,
    cls_token="[CLS]",
    cls_token_segment_id=1,
    sep_token="[SEP]",
    sep_token_extra=False,
    pad_on_left=False,
    pad_token=0,
    cls_token_box=[0, 0, 0, 0],
    sep_token_box=[1000, 1000, 1000, 1000],
    pad_token_box=[0, 0, 0, 0],
    pad_token_segment_id=0,
    pad_token_label_id=-1,
    sequence_a_segment_id=0,
    mask_padding_with_zero=True,
):
    """ 
        This function is from layoutlm repository with slight modification. Its purpose is to 
        convert an InputExample object into an InputFeatures object, including tokenize and pad 
        words and bounding boxes vector.

        Parameters:
            examples                : list 
                list of InputExample objects; each example corresponds to an image file
            label_list              : list
                list of all the possible labels
            max_seq_length          : int
                the maximum length of a sequence for the model
            cls_token_at_end        : bool
                whether to put a [CLS] token at the end or the beginning of the sequence. For layoutlm, this is set to False
            cls_token               : string
                what to used as the cls token
            cls_token_segment_id    : int
                what cls token in the segment sequence
            sep_token               : string
                what to used as the separation token between sentences
            sep_token_extra         : bool
                whether the model needs an extra sep_token between sentences. For layoutlm, this is set to False
            pad_on_left             : bool    
                whether to pad the beginning of the sequence. For layoutlm, this is set to False
            pad_token               : int
                what token to used in place of padding
            cls_token_box           : list
                what cls token to use in the box token sequence
            sep_token_box           : list
                what sep token to use in the box token sequence
            pad_token_box           : list
                what pad token to use in the box token sequence
            pad_token_segment_id    : int
                what pad token to use in the segment sequence
            pad_token_label_id      :  int
                what pad token to use in the label sequence
            sequence_a_segment_id   : int
                what to use as sequence token in segment sequence
            mask_padding_with_zero  : bool
                whether to mask the input words with 0
    """

    label_map = {label: i for i, label in enumerate(label_list)}

    features = []
    for (ex_index, example) in enumerate(examples):
        page_size = example.page_size
        file_name = example.file_name
        width, height = page_size
        tokens = []
        token_boxes = []
        actual_bboxes = []
        label_ids = []
        for word, label, box, actual_bbox in zip(
            example.words, example.labels, example.boxes, example.actual_bboxes
        ):
            word_tokens = tokenizer.tokenize(word)
            tokens.extend(word_tokens)
            token_boxes.extend([box] * len(word_tokens))
            actual_bboxes.extend([actual_bbox] * len(word_tokens))
            # Use the real label id for the first token of the word, and padding ids for the remaining tokens
            label_ids.extend(
                [label_map[label]] + [pad_token_label_id] * (len(word_tokens) - 1)
            )

        # Account for [CLS] and [SEP] with "- 2" and with "- 3" for RoBERTa.
        special_tokens_count = 3 if sep_token_extra else 2
        if len(tokens) > max_seq_length - special_tokens_count:
            tokens = tokens[: (max_seq_length - special_tokens_count)]
            token_boxes = token_boxes[: (max_seq_length - special_tokens_count)]
            actual_bboxes = actual_bboxes[: (max_seq_length - special_tokens_count)]
            label_ids = label_ids[: (max_seq_length - special_tokens_count)]

        # The convention in BERT is:
        # (a) For sequence pairs:
        #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
        #  type_ids:   0   0  0    0    0     0       0   0   1  1  1  1   1   1
        # (b) For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids:   0   0   0   0  0     0   0
        #
        # Where "type_ids" are used to indicate whether this is the first
        # sequence or the second sequence. The embedding vectors for `type=0` and
        # `type=1` were learned during pre-training and are added to the wordpiece
        # embedding vector (and position vector). This is not *strictly* necessary
        # since the [SEP] token unambiguously separates the sequences, but it makes
        # it easier for the model to learn the concept of sequences.
        #
        # For classification tasks, the first vector (corresponding to [CLS]) is
        # used as as the "sentence vector". Note that this only makes sense because
        # the entire model is fine-tuned.
        tokens += [sep_token]
        token_boxes += [sep_token_box]
        actual_bboxes += [[0, 0, width, height]]
        label_ids += [pad_token_label_id]
        if sep_token_extra:
            # roberta uses an extra separator b/w pairs of sentences
            tokens += [sep_token]
            token_boxes += [sep_token_box]
            actual_bboxes += [[0, 0, width, height]]
            label_ids += [pad_token_label_id]
        segment_ids = [sequence_a_segment_id] * len(tokens)

        if cls_token_at_end:
            tokens += [cls_token]
            token_boxes += [cls_token_box]
            actual_bboxes += [[0, 0, width, height]]
            label_ids += [pad_token_label_id]
            segment_ids += [cls_token_segment_id]
        else:
            tokens = [cls_token] + tokens
            token_boxes = [cls_token_box] + token_boxes
            actual_bboxes = [[0, 0, width, height]] + actual_bboxes
            label_ids = [pad_token_label_id] + label_ids
            segment_ids = [cls_token_segment_id] + segment_ids

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding_length = max_seq_length - len(input_ids)
        if pad_on_left:
            input_ids = ([pad_token] * padding_length) + input_ids
            input_mask = (
                [0 if mask_padding_with_zero else 1] * padding_length
            ) + input_mask
            segment_ids = ([pad_token_segment_id] * padding_length) + segment_ids
            label_ids = ([pad_token_label_id] * padding_length) + label_ids
            token_boxes = ([pad_token_box] * padding_length) + token_boxes
        else:
            input_ids += [pad_token] * padding_length
            input_mask += [0 if mask_padding_with_zero else 1] * padding_length
            segment_ids += [pad_token_segment_id] * padding_length
            label_ids += [pad_token_label_id] * padding_length
            token_boxes += [pad_token_box] * padding_length

        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length
        assert len(label_ids) == max_seq_length
        assert len(token_boxes) == max_seq_length

        features.append(
            InputFeatures(
                input_ids=input_ids,
                input_mask=input_mask,
                segment_ids=segment_ids,
                label_ids=label_ids,
                boxes=token_boxes,
                actual_bboxes=actual_bboxes,
                page_size=page_size,
                file_name=file_name
            )
        )
    return features

def preprocess(image_file):
    """
        Preprocess the words and bounding boxes inputs into InputFeatures to be put into the model

        Parameter:
            image_file: list
                Contains necessary information, more specifically the words, their bounding boxes, receipt image dimension, and the file names
        
        Return:
            list
                list of InputFeatures object containing the processed data to be input to the model
    """
    actual_bboxes       = []
    words               = []
    boxes               = []
    page_size           = []
    labels              = []
    examples            = []
    file_name           = ""
    pad_token_label_id  = CrossEntropyLoss().ignore_index

    for i in image_file:
        if(i == ""):
            if words:
                examples.append(
                    InputExample(
                        words           = words,
                        boxes           = boxes,
                        actual_bboxes   = actual_bboxes,
                        page_size       = page_size,
                        labels          = labels,
                        file_name       = file_name
                    )
                )
                
                words           = []
                boxes           = []
                actual_bboxes   = []
                file_name       = None
                page_size       = []
                labels          = []
        else:
            i_split         = i.split("\t")
            file_name       = i_split[3].strip()
            actual_bbox     = [int(b) for b in i_split[1].split()]
            page_size       = [int(i) for i in i_split[2].split()]
            width, length   = page_size
            box             = [int(1000 * (actual_bbox[0] / width)), 
                            int(1000 * (actual_bbox[1] / length)), 
                            int(1000 * (actual_bbox[2] / width)), 
                            int(1000 * (actual_bbox[3] / length))]

            actual_bboxes.append(actual_bbox)
            boxes.append(box)
            words.append(i_split[0])
            labels.append("O")

    if words:
        examples.append(
            InputExample(
                words=words,
                labels=labels,
                boxes=boxes,
                actual_bboxes=actual_bboxes,
                file_name=file_name,
                page_size=page_size,
            )
        )

    label_list  = get_labels(LABEL_LIST_PATH)
    tokenizer   = BertTokenizer.from_pretrained(
        MODEL_PATH,
        do_lower_case   = True,
        cache_dir       = None,
    )
    features    = convert_examples_to_features(
                examples,
                label_list,
                MAX_SEQ_LENGTH,
                tokenizer,
                cls_token_at_end        = False,
                # xlnet has a cls token at the end
                cls_token               = tokenizer.cls_token,
                cls_token_segment_id    = 0,
                sep_token               = tokenizer.sep_token,
                sep_token_extra         = False,
                pad_on_left             = False,
                pad_token               = tokenizer.convert_tokens_to_ids([tokenizer.pad_token])[0],
                pad_token_segment_id    = 0,
                pad_token_label_id      = pad_token_label_id,
                )
    
    return features




