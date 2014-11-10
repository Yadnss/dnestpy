"""Module for parsing the uistring xml files"""
import xml.etree.ElementTree as ET

class UIString(dict):
    """Dict-like container of message-id's and corresponding messages"""

    def __init__(self, path):
        super(UIString, self).__init__()
        tree = ET.parse(path)
        for child in tree.iter('message'):
            self[int(child.get('mid'))] = child.text
