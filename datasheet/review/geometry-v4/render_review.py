#!/usr/bin/env python3
"""Render the finished v0.4 PDF and retain visual-review hashes."""
from pathlib import Path
import hashlib,json
import fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
PDF=ROOT/'rs485_controller_datasheet_v0.4_review.pdf'
OUT=ROOT/'review/v0.4-pages';OUT.mkdir(exist_ok=True)
d=fitz.open(PDF);thumbs=[];manifest=[]
for i,page in enumerate(d,1):
    target=OUT/f'page-{i:02}.png';page.get_pixmap(matrix=fitz.Matrix(1.55,1.55)).save(target)
    image=Image.open(target).convert('RGB');image.thumbnail((280,395));thumb=Image.new('RGB',(300,425),'#e7ece8');thumb.paste(image,((300-image.width)//2,5));ImageDraw.Draw(thumb).text((12,408),f'Page {i}',fill='#173a33');thumbs.append(thumb)
    manifest.append({'page':i,'file':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
sheet=Image.new('RGB',(900,425*((len(thumbs)+2)//3)),'white')
for i,image in enumerate(thumbs):sheet.paste(image,((i%3)*300,(i//3)*425))
sheet.save(OUT/'contact-sheet.png')
(OUT/'render-manifest.json').write_text(json.dumps({'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'pages':manifest},indent=2)+'\n')
print(f'Rendered {len(d)} pages from final PDF.')
