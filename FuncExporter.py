# -*- coding:utf-8 -*-

from idaapi import plugin_t
from idaapi import PLUGIN_PROC
from idaapi import PLUGIN_OK
from PyQt5 import QtWidgets

import os
import ida_nalt
import idaapi
import idautils
import idc
import time
import re

def getSoName():
    fullpath = ida_nalt.get_input_file_path()
    filepath, filename = os.path.split(fullpath)
    return filename

def getSegAddr():
    textStart = []
    textEnd = []

    for seg in idautils.Segments():
        if (idc.get_segm_name(seg)).lower() == '.text' or (
        idc.get_segm_name(seg)).lower() == 'text'or (
        idc.get_segm_name(seg)).lower() == '__text':
            tempStart = idc.get_segm_start(seg)
            tempEnd = idc.get_segm_end(seg)

            textStart.append(tempStart)
            textEnd.append(tempEnd)

    return min(textStart), max(textEnd)

class myForm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(myForm, self).__init__(parent)

    def selectDir(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select a directory')
        return dir_path

class traceNatives(plugin_t):
    flags = PLUGIN_PROC
    comment = "FuncExporter"
    help = ""
    wanted_name = "FuncExporter"
    wanted_hotkey = ""

    def init(self):
        print("FuncExport plugin has been loaded.")
        print("Original author: https://github.com/jitcor/export_func_code")
        print("Clone source author: https://github.com/shuixi2013/export_func_code")
        return PLUGIN_OK
    
    def run(self, arg):
        ea, ed = getSegAddr()
        so_name  = getSoName()
        form = myForm()
        dir_path = form.selectDir()
        save_path = f"{dir_path}/{so_name.split('.')[0]}"

        if not os.path.isdir(save_path):
            save_path = f"{save_path}_export"

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        print(f"Exporting functions to: {save_path}")
        print(f"There are {len(list(idautils.Functions(ea, ed)))} functions in the code segment.")
        for func in idautils.Functions(ea, ed):
            percentage = ((func - ea) / (ed - ea)) * 100
            try:
                functionName = re.sub(r'[\W_]+', '_', str(idaapi.ida_funcs.get_func_name(func)))
                if len(list(idautils.FuncItems(func))) > 10:
                    arm_or_thumb = idc.get_sreg(func, "T")
                    if arm_or_thumb:
                        func += 1
                    code = str(idaapi.decompile(func))
                    save_func_filename = f"{save_path}/{functionName}.c"
                    with open(save_func_filename, "w+", encoding="utf-8") as f:
                        f.write(code)
                    
                    print(f"Successfully saved in file: {save_func_filename} {percentage:.2f}%")
            except Exception as e:
                print(e)

    def term(self):
        pass

def PLUGIN_ENTRY():
    return traceNatives()