#  import the  require  pakages
from pypdf import PdfReader 
from PIL import Image
import pytesseract as tess
from  pytesseract import image_to_string
from pdf2image import convert_from_path
import os
from langchain.document_loaders import PyPDFLoader
from  dotenv import load_dotenv
from openai import OpenAI
import json

# load env
load_dotenv()

# api  key
api_key=os.getenv('OPENAI_API_KEY')

client=OpenAI()



os.environ['TESSDATA_PREFIX'] = r'C:/Program Files/Tesseract-OCR/tessdata'


# set teh  poeller path
poppler_path='C:\\Program Files\\poppler-24.02.0\\Library\\bin'
tess.pytesseract.tesseract_cmd='C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Path to the tessdata directory (this is where the 'eng.traineddata' file should be located)
tessdata_dir_config = r'--tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'




#  functipn for  read the  pdf from the 
def  read_pdf(pdf_file):
    data=[]

    with open(pdf_file,'rb') as file:
        print('file--->',file)
        reader=PdfReader(file)


        for page_num in range(len(reader.pages)):
                print(page_num)
                # page = pdf_reader.getPage(page_num)
                page = reader.pages[page_num]
                # print(page.extract_text(),'----->')
                data.append(page.extract_text())
        return data


#  extract  text  from  the  pdf image
def  extract_text_from_image(file_path):
    print("file path---->",file_path)
    chunk=[]
    #  find the  legth of the  i:
    pages=convert_from_path(file_path,first_page=1,last_page=30,poppler_path=poppler_path)
    for i,page in enumerate(pages):
        # print(image_to_string(page),'\n\n\n\n')
        chunk.append(image_to_string(page))
    return chunk

# read pdf from  langchain
# def  read_pdf_langchain(file_path):
#     pdf_loader=PyPDFLoader(file_path)
#     data=[]

#     #  lood the documents, which  splits into the pages
#     document=pdf_loader.load()

#     for i, doc in  enumerate(document):

#         # data.append(doc.page_content)
#          print(doc.page_content)
#          break 
#     # return data 
    

#  create respose from  open  ai
def open_ai_quiz_generate(extracted_texts=None):

    try:
        print("working to  generate the  quiz........")

        if not extracted_texts:
            return False
        
        # shuffel the extraacted text data 

        ## total number of questin
        # total_question=int(data['numberOfQuestions'])
        total_question=20
        
        #### pass the  prompt to the open ai  fro response
        response = client.chat.completions.create(temperature=0.3,
        model="gpt-4o-mini",
        response_format={ "type": "json_object" }, 
        messages=[{
                    "role": "system",
                    "content": f"""
                    You are a quiz generator designed to output JSON and in  the  genreaed  quiz  no  unicode include only original value use. Generate exactly {total_question} quiz questions based on the following criteria:

                    1. **Question Types**: Provide a mix of mcq, true_false, fill_ups, and short_answer questions. Group questions by type in the 'quiz_questions' dictionary.
                    2. **Format**:
                        - **mcq**: Include 4 options with one correct answer. Do not number the options.
                        - **true_false**: Provide a statement and indicate if it is true or false. Use string values "true" and "false".
                        - **fill_ups**: Provide a question with a blank to be filled.
                        - **short_answer**: Provide a question requiring a brief explanatory answer.
                    3. Each question must include 'question', 'options' (if applicable), 'answer', and 'explanation'.
                    4. Ensure all questions are relevant to the provided data.
                    5. Ensure the total number of questions is exactly {total_question}. If the number of generated questions does not meet this requirement, regenerate the questions until the count is accurate.
                    6. In  special  character  try to  pass the  original   instead of unicode like  this type "\\u*"
                    
                    Begin generating the questions based on the provided data: {extracted_texts}.
                    """
                }
                ]

        )
        
        #  Begin generating the questions now based on  the following data: {extracted_texts}

        res=response.choices[0].message.content
        
        response_dict=json.loads(res)
        print('\n\n\n\n--->>>>>>resposne---------->\n\n\n',response_dict)

        #   store resposne in json
        with open('res.json','w') as json_file:
            json.dump(response_dict,json_file,indent=4)

    # print('open ai response-->', res)
    except Exception as e:
        print(e)
    





if __name__ == "__main__":

    # call teh   function to read the  pdf
    text=read_pdf('pdf/math_2.pdf')

    # extract text from  ocr
    # text=extract_text_from_image('pdf/math_sample.pdf')


    # read_pdf_langchain('pdf/aqa-gcse-maths-higher-textbook.pdf')
    # print('------>\n\n\n',text,'----->')


    # call the  open ai  funtion to genrate the response
    open_ai_quiz_generate(extracted_texts=text)