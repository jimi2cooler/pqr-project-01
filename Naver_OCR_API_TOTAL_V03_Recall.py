# 유료도로 OCR_API 호출

#1 'C:\AutoFine\10_Fine_Receipt_OCR\1_OCR_Scan_tif' 폴더내 스캔한 tif 파일을 모두 읽어서 'C:\AutoFine\10_Fine_Receipt_OCR\2_OCR_Scan_Convert_to_jpg' 폴더에 1장씩 쪼개서 jpg 파일형식으로 복사


from PIL import Image
from datetime import datetime
import os, glob
import requests
import uuid
import time
import base64
import json
import pandas as pd
import csv, re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import shutil
import urllib3

# ssl에러 메시지 제거
urllib3.disable_warnings()

# 콤보박스

window = tk.Tk()

def combo_click():
    global fine_venue
    fine_venue = venue.get()
    window.destroy()

venue = tk.StringVar()
window.title("부과기관")
window.geometry("200x100+800+300") # 가로길이 X 세로길이 + 가로좌표 + 세로좌표 

Combobox1 = ttk.Combobox(textvariable=venue, width=30)
Combobox1['value'] = ('지자체_광역', '지자체_시군구', '유료도로', '리콜통지서')
Combobox1.current(0)

Click_button = tk.Button(text="선택", command=combo_click)

Combobox1.pack()
Click_button.pack()

window.mainloop()


# 기관별로 API Key 변경

if fine_venue == "지자체_광역":
    api_url = ''
    secret_key = ''

elif fine_venue == "지자체_시군구":
    api_url = ''
    secret_key = ''

elif fine_venue == "유료도로":
    api_url = ''
    secret_key = ''

else :
    api_url = ''
    secret_key = ''


resourse_im_root = "C:/AutoFine/10_Fine_Receipt_OCR/1_OCR_Scan_tif/"
destination = "C:/AutoFine/10_Fine_Receipt_OCR/2_OCR_Scan_Convert_to_jpg/"

work_date = datetime.today().strftime("%Y%m%d%H%M%S")  

# Tif 이미지 한장씩 잘라서 jpg 파일로 전환

tif_images = glob.glob(resourse_im_root + "*.tif")

for a, image in enumerate(tif_images) :
    im = Image.open(image)
    im_n = im.n_frames

    today = datetime.today().strftime('%Y%m%d')

    for i in range(im_n):
        try:
            im.seek(i)
            im.save(destination + today +'_%s%s.jpg'%(a,i,))
        except EOFError:
            break


# 2 Naver API 호출하기

target_images_dir = destination
output_csv_dir = "C:/AutoFine/00_Programs/1_OCR_result/"
renamed_jpg_dir = "C:/AutoFine/10_Fine_Receipt_OCR/3_OCR_Scan_pdf/"
upload_renamed_jpg_dir = "C:/AutoFine/40_OCR_Image_Upload/"

target_image_files = os.listdir(target_images_dir)
target_images_ocr = glob.glob(target_images_dir + "*.jpg")  

ocr_result = {}
ocr_result_total = {}

for b, ti in enumerate(target_images_ocr) :
    image_file = ti

    with open(image_file,'rb') as f:
        file_data = f.read()

    request_json = {
        'images': [
            {
                'format': 'jpg',
                'name': target_image_files[b],
                'data': base64.b64encode(file_data).decode()
    #            'url': image_url
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = json.dumps(request_json,).encode('UTF-8')
    headers = {
    'X-OCR-SECRET': secret_key,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", api_url, headers=headers, data = payload, verify = False)
    rescode = response.status_code

    result = response.json()
    
    # response 결과에 따라 
    if (rescode == 200) :

        try :

            fields_num = len(result['images'][0]['fields'])
            
            uid = result['images'][0]['uid']
            title = result['images'][0]['title']['name']
            idx = b + 1

            i = 0
            ocr_result['title'] = title
            ocr_result['uid'] = uid
            
            if fine_venue != '리콜통지서' :

                for i in range(fields_num) :
                    field = result['images'][0]['fields'][i]['name']
                    infer_text = result['images'][0]['fields'][i]['inferText']
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                    ocr_result[field] = infer_text.replace('\n', ' ')

                # 특정 필드값 문자열 처리
                try :
                    ocr_result['차량번호'] = ocr_result['차량번호'].replace(' ', '')
                    ocr_result['위반일시'] = "{0:0<12}".format("".join(re.findall("\d+", ocr_result['위반일시'])))
                    ocr_result['납부금액'] = "".join(re.findall("\d+", ocr_result['납부금액']))
                    ocr_result['납부기한'] = "{0:0<8}".format("".join(re.findall("\d+", ocr_result['납부기한'])))

                except KeyError:
                    pass


                ocr_result_total[uid] = ocr_result
                ocr_result_total[uid]['no'] = idx
                ocr_result = {} 
                
                try :
                    renamed_nm = title + "_" + ocr_result_total[uid]['발급기관'] + "_" + ocr_result_total[uid]['차량번호'] + "_" + ocr_result_total[uid]['위반일시'] 
                    renamed_nm = re.sub(pattern=r'[^\w\s]', repl='', string=renamed_nm) + ".jpg"
                    img_renamed_nm = ocr_result_total[uid]['차량번호'] + "_" + ocr_result_total[uid]['위반일시'] + ".jpg" # 일괄업로드 용 이미지파일명
                    img_renamed_nm = re.sub(pattern=r'[^\w\s]', repl='', string=img_renamed_nm) + ".jpg"
                except KeyError:
                    renamed_nm = title + "_" + ocr_result_total[uid]['차량번호'] + "_" + ocr_result_total[uid]['위반일시']
                    renamed_nm = re.sub(pattern=r'[^\w\s]', repl='', string=renamed_nm)+ ".jpg"
                    img_renamed_nm = ocr_result_total[uid]['차량번호'] + "_" + ocr_result_total[uid]['위반일시']  # 일괄업로드 용 이미지파일명
                    img_renamed_nm = re.sub(pattern=r'[^\w\s]', repl='', string=img_renamed_nm) + ".jpg"
                
                ocr_result_total[uid]['file_name'] = renamed_nm

                upload_img_path_after = upload_renamed_jpg_dir + img_renamed_nm.replace('jpg', "jpg")

                shutil.copy(ti, renamed_jpg_dir + renamed_nm)
                
                if os.path.exists(upload_img_path_after) :
                    pass

                else :
                    shutil.copy(ti, upload_img_path_after)
                
                print(renamed_nm + " is done!")

                # 일괄업로드용 이미지 파일 생성 (기존 파일 복사해서 다른 폴더로 이동)
                # resource_img_path = renamed_jpg_dir + renamed_nm
                # upload_img_path = upload_renamed_jpg_dir + renamed_nm
                # upload_img_path_after = upload_renamed_jpg_dir + img_renamed_nm

                # try : 
                #     shutil.copy(ti, upload_img_path_after)
                
                # except :
                #     pass

                time.sleep(response.elapsed.total_seconds())

            # venue가 '리콜통지서인 경우'

            else : 

                for i in range(fields_num) :
                    field = result['images'][0]['fields'][i]['name']
                    infer_text = result['images'][0]['fields'][i]['inferText']
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                    ocr_result[field] = infer_text.replace('\n', ' ')

                # 특정 필드값 문자열 처리
                try :
                    ocr_result['차대번호'] = ocr_result['차대번호'].replace(' ', '')
                    
                except KeyError:
                    pass

        except :
            continue

    else :
        print(response.text)
        
        next
    
    # 임시 jpg 폴더 내 파일 제거

    # if os.path.exists(renamed_jpg_dir) :
    #     for file in os.scandir(file.path) :
    #         os.remove(file.path)

    # else :
    #     pass
        




# 3. Nested Dict 형태의 결과값을 특정필드를 정의한 후 자료를 읽어서 CSV 파일에 저장하기. 저장 parameter에서 'wb'이면 str 에러 발생, 이 경우 'w'로 하면 문제없음

if fine_venue != '리콜통지서' :

    csv_fields = ['no','file_name', 'title','발급기관', '차량번호', '위반장소', '위반일시', '위반내용', '납부기한', '납부금액', '고객조회번호', '전자납부번호']

    with open(output_csv_dir + "naver_ocr_result_" + work_date + ".csv", "w", newline='') as csv_f:
        w = csv.DictWriter(csv_f, fieldnames = csv_fields)
        w.writeheader()
        for k in ocr_result_total :
            w.writerow({field : ocr_result_total[k].get(field) or "" for field in csv_fields})

    print("Successfully Done! Good Job!")

else :

    with open(output_csv_dir + "naver_ocr_result_" + work_date + ".csv", "w", newline='') as csv_f:
        w = csv.DictWriter(csv_f, fieldnames = ['no','file_name', 'title','차대번호', '딜러사'])
        w.writeheader()
        for k in ocr_result_total :
            w.writerow({field : ocr_result_total[k].get(field) or "" for field in csv_fields})

    print("Successfully Done! Good Job!")

    
