###################################################################################################
######## File Conversions

# def img2b64(img_path):
#     """Convert image to base64 string"""
#     with open(img_path, "rb") as image_file:
#         b64_string = base64.b64encode(image_file.read())
#     return b64_string


# def b642img(b64_string, img_path):
#     """Convert base64 string to image"""
#     with open(img_path, "wb") as fh:
#         fh.write(base64.decodebytes(b64_string))
#     return print(f"The variable '{get_varname(b64_string)}' has been written to {img_path}")


# def html2md(html_path: str):
#     """Function to convert html webpage (saved manually) to a markdown format"""
#     html_string = file_open(html_path)
#     md_string = markdownify(html_string)

#     basename_html = os.path.basename(html_path)
#     basename_md = basename_html.replace(".html", ".md")
#     out_path = html_path.replace(basename_html, basename_md)
#     write_file(md_string, out_path)
#     print(f"File saved to: {out_path}")

#     return md_string


# def url2md(url: str, output_basename: str):
#     """At some point I'll want to make it so that my url2md function can iterate over a list of pages"""
#     response = urllib.request.urlopen(url)
#     html_string = response.read().decode("UTF-8")

#     md_string = markdownify(html_string)

#     file_save(md_string, f"{output_basename}.md")
