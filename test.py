import pymupdf
import fitz
from time import sleep

document_filepath = knowledge_dir_files[1]
print(f"{document_filepath = }")

if ".pdf" in document_filepath:
    document_loader = PyMuPDFLoader(document_filepath)
    pages = document_loader.load()

pages


from IPython.display import Markdown

if not hasattr(fitz.Page, "find_tables"):
    raise RuntimeError("This PyMuPDF version does not support the table feature")

for document_filepath in knowledge_dir_files:
    doc = fitz.open(document_filepath)
    # page = doc[14]

    for idx, page in enumerate(doc):
        tabs = page.find_tables()  # detect the tables
        md_text = None
        for i, tab in enumerate(tabs):  # iterate over all tables
            print(f"file: {document_filepath} \npage: {idx} \ntable:{i}")
            md_text = tab.to_markdown()
            Markdown(md_text)
            sleep(1)

            # cur_df = tab.to_pandas()
            # display(cur_df)
            # for cell in tab.header.cells:
            #     page.draw_rect(cell,color=fitz.pdfcolor["red"],width=0.3)
            # page.draw_rect(tab.bbox,color=fitz.pdfcolor["green"])
            # print(f"Table {i} column names: \n{tab.header.names}, \nexternal: {tab.header.external}")

        # show_image(page, f"Table & Header BBoxes")

tab.to_pandas()
