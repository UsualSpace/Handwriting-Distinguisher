from pdf2image import convert_from_path
import os

Input PDF file
pdf_path = [
    'sentences_alyajouri.pdf',
    'sentences_le.pdf',
    'sentences_brodowicz.pdf',
    'sentences_scalzone.pdf'
]
writer_name = [
	'alyajouri',
    'le',
    'brodowicz',
    'scalzone'
]

for index in range(len(pdf_path)):
	# Output folder
	output_folder = f'{writer_name[index]}_jpeg'
	os.makedirs(output_folder, exist_ok=True)

	# Convert PDF pages to JPEG
	pages = convert_from_path(pdf_path[index], dpi=72)
	for i, page in enumerate(pages):
		output_path = os.path.join(output_folder, f'{writer_name[index]}_{i+1}.jpeg') 
		page.save(output_path, 'JPEG')

print("Conversion complete.")
