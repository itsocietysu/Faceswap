from xml.dom import minidom

class PRString:
    def __init__(self):
        self.line_space = 0
        self.color = (0, 0, 0)
        self.line_width = 0
        self.font = "Calibri"
        self.bold = False
        self.italic = False
        self.font_size = 26
        self.text = ""
        self.x = 0
        self.y = 0

class Strings:
    def get(self, id):
        return self.strings[id]

    def __init__(self, fname):
        self.fname = fname
        self.strings = {}

        xmldoc = minidom.parse(fname)
        itemlist = xmldoc.getElementsByTagName('string')

        for s in itemlist:
            new_string = PRString()
            if (s.attributes['lspace']):
                new_string.line_space = int(s.attributes['lspace'].value)

            if (s.attributes['color']):
                rgb = s.attributes['color'].value.split(',')
                new_string.color = (int(rgb[0]), int(rgb[1]), int(rgb[2]))

            if (s.attributes['width']):
                new_string.line_width = int(s.attributes['width'].value)

            if (s.attributes['font']):
                fontSettings = s.attributes['font'].value.split(',')
                new_string.font = fontSettings[0]

                if (len(fontSettings) > 1):
                    if (fontSettings[1] == 'bold'):
                        new_string.bold = True
                    if (fontSettings[1] == 'italic'):
                        new_string.italic = True

                if (len(fontSettings) > 2):
                    if (fontSettings[2] == 'bold'):
                        new_string.bold = True
                    if (fontSettings[2] == 'italic'):
                        new_string.italic = True

            if (s.attributes['size']):
                new_string.font_size = int(s.attributes['size'].value)

            if (s.attributes['pos']):
                xy = s.attributes['pos'].value.split(',')
                new_string.x = int(xy[0])
                new_string.y = int(xy[1])

            new_string.text = s.firstChild.nodeValue#.decode("utf-8")

            self.strings[s.attributes['id'].value] = new_string