from pypdf import PdfReader
reader = PdfReader("EY_Digital_PDF_Practice.pdf")
print("Pages:", len(reader.pages))

total_txt=""
for page in reader.pages:
    total_txt+=page.extract_text()
    print(total_txt)


page=reader.pages[0]
page1=page.extract_text()

page=reader.pages[1]
page2=page.extract_text()

print(f"{page1}\n{page2}")

if "Northstar Maintanence"in total_txt:
    print("northstar Maintanence present")
    count=0
for sentence in total_txt.split("\n"):
    for word in sentence.split(" "):
        if "vendor" in sentence :
            count=count+1
            print(count)
            with open ("pypdf_output.txt",'a') as f:
                f.write(total_txt)


