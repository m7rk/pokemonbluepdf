import sys
import textwrap

from pdfrw import PdfWriter
from pdfrw.objects.pdfname import PdfName
from pdfrw.objects.pdfstring import PdfString
from pdfrw.objects.pdfdict import PdfDict
from pdfrw.objects.pdfarray import PdfArray

def create_script(js):
  action = PdfDict()
  action.S = PdfName.JavaScript
  action.JS = js
  return action
  
def create_page(width, height):
  page = PdfDict()
  page.Type = PdfName.Page
  page.MediaBox = PdfArray([0, 0, width, height])

  page.Resources = PdfDict()
  page.Resources.Font = PdfDict()
  page.Resources.Font.F1 = PdfDict()
  page.Resources.Font.F1.Type = PdfName.Font
  page.Resources.Font.F1.Subtype = PdfName.Type1
  page.Resources.Font.F1.BaseFont = PdfName.Courier
  
  return page

def create_field(name, x, y, width, height, value="", f_type=PdfName.Tx):
  annotation = PdfDict()
  annotation.Type = PdfName.Annot
  annotation.Subtype = PdfName.Widget
  annotation.FT = f_type
  annotation.Ff = 2
  annotation.Rect = PdfArray([x, y, x + width, y + height])
  annotation.T = PdfString.encode(name)
  annotation.V = PdfString.encode(value)

  annotation.BS = PdfDict()
  annotation.BS.W = 0

  appearance = PdfDict()
  appearance.Type = PdfName.XObject
  appearance.SubType = PdfName.Form
  appearance.FormType = 1
  appearance.BBox = PdfArray([0, 0, width, height])
  appearance.Matrix = PdfArray([1.0, 0.0, 0.0, 1.0, 0.0, 0.0])

  return annotation

def create_text(x, y, size, txt):
  return f"""
  BT
  /F1 {size} Tf
  {x} {y} Td ({txt}) Tj
  ET
  """

def create_button(name, x, y, width, height, value):
  button = create_field(name, x, y, width, height, f_type=PdfName.Btn)
  button.AA = PdfDict()
  button.Ff = 65536
  button.MK = PdfDict()
  button.MK.BG = PdfArray([0.90])
  button.MK.CA = value
  return button

def create_key_buttons(keys_info):
  buttons = []
  for info in keys_info:
    name = info["name"] + "_button"
    key = info["key"]
    button = create_button(name, info["x"], info["y"], info["width"], info["height"], info["name"])
    button.AA = PdfDict()
    button.AA.D = create_script(f"key_down('{key}')")
    button.AA.U = create_script(f"key_up('{key}')")
    buttons.append(button)
  return buttons

if __name__ == "__main__":
  with open("gameboy.js") as f:
    js = f.read()

  
  width = 180
  height = 144
  scale = 2

  writer = PdfWriter()
  page = create_page(width * scale-8, height * scale + 220)
  page.AA = PdfDict()
  page.AA.O = create_script("try {"+js+"} catch (e) {app.alert(e.stack || e)}")

  fields = []
  for i in range(0, height):
    field = create_field(f"field_{i}", 0, i*scale + 220, width*scale-8, scale, "")
    fields.append(field)

    fields += create_key_buttons([
      {"name": "<", "key": "1", "x": 10, "y": 100, "width": 30, "height": 30},
      {"name": ">", "key": "0", "x": 70, "y": 100, "width": 30, "height": 30},
      {"name": "^", "key": "2", "x": 40, "y": 130, "width": 30, "height": 30},
      {"name": "v", "key": "3", "x": 40, "y": 70, "width": 30, "height": 30},
      {"name": "a", "key": "4", "x": 250, "y": 100, "width": 30, "height": 30},
      {"name": "b", "key": "5", "x": 290, "y": 100, "width": 30, "height": 30},
      {"name": "select", "key": "6", "x": 130, "y": 100, "width": 40, "height": 30},
      {"name": "start", "key": "7", "x": 180, "y": 100, "width": 40, "height": 30},
    ])

  """
    input_field = create_field(f"key_input", 450, 64, 150, 64, "Type here for keyboard controls.")
    input_field.AA = PdfDict()
    input_field.AA.K = create_script("key_pressed(event.change)")
    fields.append(input_field)



    page.Contents = PdfDict()
    page.Contents.stream = "\n".join([
      create_text(320, 190, 24, "DoomPDF"),
      create_text(450, 162, 12, "Controls:"),
      create_text(450, 148, 8, "WASD, q = esc, z = enter, e = use, space = fire"),
      create_text(450, 136, 8, "shift+WASD = sprint, m = map, 1-7 = weapons"),
      create_text(320, 34, 8, "Upload custom WAD files at: https://doompdf.pages.dev/"),
      create_text(320, 22, 8, "Source code: https://github.com/ading2210/doompdf"),
      create_text(320, 10, 8, "Note: This PDF only works in Chromium-based browsers.")
    ])
    """

  page.Annots = PdfArray(fields)
  writer.addpage(page)
  writer.write("out2.pdf")