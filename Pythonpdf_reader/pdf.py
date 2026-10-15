import fitz

doc = fitz.open("EY_Digital_PDF_Practice.pdf")
print(doc.page_count)
page1=doc[0]
print(page1.get_text())
print("next")
all_text_from_pdf=" "
for page in doc:
    all_text_from_pdf +=page.get_text()
    print(all_text_from_pdf)

    if "Maintenance" in all_text_from_pdf:
        print("Maintenance present")

        count=0
        if "V303" in all_text_from_pdf:
            count+=1
            print(count)

            page2=doc[1]
            print(page2.get_text())

            with open("digital_pdf_text.txt", "wb") as f:
                f.write(all_text_from_pdf)

                pdf.close()



