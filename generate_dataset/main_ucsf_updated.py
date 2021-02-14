import nltk
import re
import os
import json
import pickle
import difflib
from difflib import SequenceMatcher
from chardet.universaldetector import UniversalDetector
from coordinate_map import CoordinateMap
import xml.etree.ElementTree as ET
import sys
import argparse
import array





find = False
Low = 0;
High = 9;
max_length = 127;
delta = 32

#array('i');
ascii = array.array('i',(0 for i in range(0,max_length)))
#BinaryTree tree;
const_offset = 32;
#var_offset = 0;
#left_node = 32;
#right_node = 96;
#root_node = 64;
#var_offset = ((root_node * left_node) % right_node)
var_offset = 32;

#global_pos = 1;
pos_offset = 3;


char_array = ["!","","#","$","%","&","'","yy","zz","*","+","bb","ww",".","xx"]
ch_array = ["A","B","C","D","E","F","G","H","I","J"]
int_array= ["0","1","2","3","4","5","6","7","8","9"]


def applyReflection(word, index):

        ascii_value = 0;
        str_reflected ='';
 #       var_offset = (root_node * left_node) % right_node
        length =  len(word);

        for pos in range(0, length):
            ascii_value = ord(word[pos]);
            lap_off = (index + pos) % pos_offset;
           # lap_off = 0
           # print (ascii_value)
            str_reflected = replaceCharAt(str_reflected, ascii_value, lap_off);
        #word = 'YES'
        return str_reflected + append_index(index)+"|";
    

def append_index(index):
    
    output_string="";
    int_string = str(index)
    
    # Iterate over the string 
    for element in int_string: 
  #      print(ch_array[int(element)])
        output_string = output_string + ch_array[int(element)]  

    return output_string

  
def replaceCharAt(str_reflected, org_value, lap_off):

        reflected_value = (max_length - org_value) + 1;
        
        if ((reflected_value + var_offset + const_offset) > max_length):
                if (((reflected_value + var_offset + const_offset) % max_length) < 32):
                    reflected_value = ((reflected_value + var_offset + const_offset) % max_length)+ delta + lap_off;
                    if reflected_value >= 33 and reflected_value <= 47:
                        str_reflected = str_reflected + '+'+ char_array[reflected_value-delta-1] +'+|';
                    else:
                        str_reflected = str_reflected + '+'+ chr(reflected_value) +'+|';
                else:
                    reflected_value = ((reflected_value + var_offset + const_offset) % max_length) + lap_off;
                    str_reflected = str_reflected + chr(reflected_value) +'|';
        else:
            reflected_value = reflected_value + var_offset + const_offset + lap_off;
            str_reflected = str_reflected + chr(reflected_value) +'|';
        return str_reflected;




def isolate_phi(xml_folder):
    #isolate all phi and data with coordinates
    #turn them into a json representation
    phi = {} #fn --> {"text":"...", "phi":[{"type":"DATE"...}]}
    for root_dir, dirs, files in os.walk(xml_folder):
        for f in files:
            with open(root_dir+f, 'r', encoding='latin1') as file:
                tree = ET.parse(file)
                root = tree.getroot()

                text = ""
                phi_list = []

                for child in root:
                    if child.tag == "TEXT":
                        text = child.text
                        # if f == '167937985.txt.xml':
                        #     print(text)
                        #print (child.tag, child.attrib, child.text)
                    if child.tag == "TAGS":
                        for t in child:
                            phi_list.append(t.attrib)
                            #print(t.tag, t.attrib, t.text)
                phi[f] = {"text":text, "phi":phi_list}
    return phi

def main():
    # get input/output/filename

    ap = argparse.ArgumentParser()
    ap.add_argument("-x", "--xml", default="../data/i2b2_xml/",
                    help="Path to the directory or the file that contains the note xml files, the default is ../data/i2b2_xml/",
                    type=str)
    ap.add_argument("-o", "--output", default="../data/phi_notes_i2b2.json",
                    help="Path to the file that contains a summary of the phi in the xml files, the default is ../data/phi_notes_i2b2.json",
                    type=str)
    ap.add_argument("-n", "--notes", default="../data/i2b2_notes/",
                    help="Path to the directory or the file that contains the PHI note, the default is ../data/i2b2_notes/",
                    type=str)
    ap.add_argument("-a", "--anno", default="../data/i2b2_anno/",
                    help="Path to the directory or the file that contains the PHI annotation, the default is ../data/i2b2_anno/",
                    type=str)
    ap.add_argument("-s", "--phi", default="../data/i2b2_phi/",
                    help="Path to the directory to save the PHI summary in, the default is ../data/i2b2_phi/",
                    type=str)
    ap.add_argument("-c", "--context", default="../data/i2b2_phi_context",
                    help="Path to the directory to save the PHI context summary in, the default is ../data/i2b2_phi_context",
                    type=str)
    ap.add_argument("-p", "--pos", default="../data/i2b2_phi_pos",
                    help="Path to the directory to save the PHI pos summary in, the default is ../data/i2b2_phi_pos",
                    type=str)

    args = ap.parse_args()

    xml_folder = args.xml
    outpath = args.output
    
    # Run main function
    phi = isolate_phi(xml_folder)
    
   # print (phi)
   # exit
   # print (phi)

    #save our data
    json.dump(phi, open(outpath, "w"), indent=4)

    NOTES_FOLDER = args.notes
    ANNO_FOLDER = args.anno

    with open('abc.txt', 'w', newline='')  as myfile:

        #save our phi notes 
        for fn in phi:
            
          #  print(  phi[fn]["phi"])
    
            #get text and remove any initial *'s from the raw notes
            txt = phi[fn]["text"].replace("*", " ")
          #  txt = phi[fn]["text"].replace(phi[fn]["text"], " **"+applyReflection(phi[fn]["text"], phi[fn]["start"])+"** ",1)
    
          #  phi_reduced = phi_reduced.replace(x, " **"+applyReflection(x, index)+"** ",1)
    
            #save our notes file
            with open(NOTES_FOLDER+fn.split(".")[0]+".txt", "w",encoding='utf-8') as note_file:
                note_file.write(txt)
      
                #create a coordinate mapping of all phi
                c = CoordinateMap()
                for p in phi[fn]["phi"]:
                    try:
                        start = int(p['start'])
                        end = int(p['end'])
                    except KeyError:
                        start = int(p['spans'].split('~')[0])
                        end = int(p['spans'].split('~')[1])
                    c.add_extend(fn, start, end)
        
        
                contents = []
                last_marker = 0
                
                for start,stop in c.filecoords(fn):
                    contents.append(txt[last_marker:start])
                    myfile.write(txt[start:stop])
                    myfile.write("\n")
                    print (txt[start:stop])
                        
                        #add a * for each letter preserving shape
                    phi_hidden = re.sub(r"[a-zA-Z0-9]", "*", txt[start:stop])
                   # phi_hidden = " **"+applyReflection(txt[start:stop], start)+"** "
                      #  phi_reduced = phi_reduced.replace(x, " **"+applyReflection(x, index)+"** ",1)
            
                    contents.append(phi_hidden)
                    last_marker = stop
            
                    #wrap it up by adding on the remaining values if we haven't hit eof
                    if last_marker < len(txt):
                        contents.append(txt[last_marker:len(txt)])
            
                    with open(ANNO_FOLDER+fn.split(".")[0]+".txt", "w", encoding='utf-8') as anno_file:
                        anno_file.write("".join(contents))
        myfile.close()

           # print (contents)
    
if __name__ == "__main__":
    main()
