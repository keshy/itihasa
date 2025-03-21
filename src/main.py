import json

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import texttospeech

PROJECT_ID = 'prisma-cortex-playground'
MODEL_ID = "gemini-2.0-flash-001"
REGION = 'us-central1'

vertexai.init(project=PROJECT_ID, location=REGION)
gen_model = GenerativeModel(MODEL_ID)
tts_client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    speaking_rate=0.5
)


def process(text=None, lang=None):
    # https: // cloud.google.com / text - to - speech / docs / voices
    lang_code_map = {
        'English': 'en-US',
        'Hindi': 'hi-IN',
        'Tamil': 'ta-IN',
        'Gujarati': 'gu-IN',
        'Bengali': 'bn-IN',
        'Kannada': 'kn-IN',
        'Telugu': 'te-IN'
    }
    _to_english_line_by_line = f"""
        Your a lingual expert and adept at efficient and accurate translations. Given a piece of text or a verse specified in the <TEXT> field in a given language indicated by <INPUT_LANGUAGE>, translate the text line by line into the set of languages specified in the <LANGUAGE_CODE_MAP> dictionary which contains the language and its specific language code using the following guardrails: 
        - Ensure you use succinct easy to understand words for the target language in the translation. 
        - If you see numbers written in english to track paras or verses, please remove the numbers and perform the translation. 
        - If the context is too vast, try to use memory collected from previous sessions to apply to this context. 
        - If concept is difficult, add in a simple example to illustrate the point made in the text in the target language. 
        - The translation should be engaging for an offline/podcast hearing. 
        - Do not miss any line and strive for full coverage of translation. 
        The output format must follow the following pattern:
        - ensure its ONLY a valid JSON response. No other content should be there. 
        - JSON must include 2 fields - {{"answer": {{"<language_code>": "<translated_answer>"}}, "status": "pass or fail"}}. The answer field must be a dictionary of the language code as found in the values of <LANGUAGE_CODE_MAP>, and its corresponding translated text in that language. If translations to all languages specified in the <LANGUAGE_CODE_MAP> was completed, only then "status" field is to be marked as "pass" otherwise it should be marked as a "fail".
        - Do not allow translations for more than 10 languages at a time in one request.  
        - Do not return with any other response format other than the json in case of errors and add a status field as "fail". Optionally include an "error_msg" string field if status is fail indicating reason for failure. 
        
        <TEXT>
        {text}
        </TEXT>
        
        <INPUT_LANGUAGE>
        {lang}
        </INPUT_LANGUAGE>
        
        <LANGUAGE_CODE_MAP>
        {lang_code_map}
        </LANGUAGE_CODE_MAP
    """
    response = gen_model.generate_content(contents=_to_english_line_by_line)
    error = None
    try:
        tx = response.text.replace('```json', '')
        tx = tx.replace('```', '')
        response_dict = json.loads(tx)
        if response_dict.get('status') != 'pass':
            error = f'⚡Could not translate...'
            return [], error
        else:
            return response_dict.get('answer'), error
    except Exception as e:
        print(e)
        error = f'⚡Could not translate due to a run time exception: {e}'
        return [], error


if __name__ == '__main__':
    txl, error = process(text="""
         0 नारायणं नमस्कृत्य नरं चैव नरॊत्तमम
      देवीं सरस्वतीं चैव ततॊ जयम उदीरयेत
  1 लॊमहर्षणपुत्र उग्रश्रवाः सूतः पौराणिकॊ नैमिषारण्ये शौनकस्य कुलपतेर दवादशवार्षिके सत्रे
  2 समासीनान अभ्यगच्छद बरह्मर्षीन संशितव्रतान
      विनयावनतॊ भूत्वा कदा चित सूतनन्दनः
  3 तम आश्रमम अनुप्राप्तं नैमिषारण्यवासिनः
      चित्राः शरॊतुं कथास तत्र परिवव्रुस तपस्विनः
  4 अभिवाद्य मुनींस तांस तु सर्वान एव कृताञ्जलिः
      अपृच्छत स तपॊवृद्धिं सद्भिश चैवाभिनन्दितः
  5 अथ तेषूपविष्टेषु सर्वेष्व एव तपस्विषु
      निर्दिष्टम आसनं भेजे विनयाल लॊमहर्षणिः
  6 सुखासीनं ततस तं तु विश्रान्तम उपलक्ष्य च
      अथापृच्छद ऋषिस तत्र कश चित परस्तावयन कथाः
  7 कृत आगम्यते सौते कव चायं विहृतस तवया
      कालः कमलपत्राक्ष शंसैतत पृच्छतॊ मम
  8 [सूत]
      जनमेजयस्य राजर्षेः सर्पसत्रे महात्मनः
      समीपे पार्थिवेन्द्रस्य सम्यक पारिक्षितस्य च
  9 कृष्णद्वैपायन परॊक्ताः सुपुण्या विविधाः कथाः
      कथिताश चापि विधिवद या वैशम्पायनेन वै
  10 शरुत्वाहं ता विचित्रार्था महाभारत संश्रिताः
     बहूनि संपरिक्रम्य तीर्थान्य आयतनानि च
 11 समन्तपञ्चकं नाम पुण्यं दविजनिषेवितम
     गतवान अस्मि तं देशं युद्धं यत्राभवत पुरा
     पाण्डवानां कुरूणां च सर्वेषां च महीक्षिताम
 12 दिदृक्षुर आगतस तस्मात समीपं भवताम इह
     आयुष्मन्तः सर्व एव बरह्मभूता हि मे मताः
 13 अस्मिन यज्ञे महाभागाः सूर्यपावक वर्चसः
     कृताभिषेकाः शुचयः कृतजप्या हुताग्नयः
     भवन्त आसते सवस्था बरवीमि किम अहं दविजाः
 14 पुराणसंश्रिताः पुण्याः कथा वा धर्मसंश्रिताः
     इतिवृत्तं नरेन्द्राणाम ऋषीणां च महात्मनाम
 15 [रसयह]
     दवैपायनेन यत परॊक्तं पुराणं परमर्षिणा
     सुरैर बरह्मर्षिभिश चैव शरुत्वा यद अभिपूजितम
 16 तस्याख्यान वरिष्ठस्य विचित्रपदपर्वणः
     सूक्ष्मार्थ नयाययुक्तस्य वेदार्थैर भूषितस्य च
 17 भारतस्येतिहासस्य पुण्यां गरन्थार्थ संयुताम
     संस्कारॊपगतां बराह्मीं नानाशास्त्रॊपबृंहिताम
 18 जनमेजयस्य यां राज्ञॊ वैशम्पायन उक्तवान
     यथावत स ऋषिस तुष्ट्या सत्रे दवैपायनाज्ञया
 19 वेदैश चतुर्भिः समितां वयासस्याद्भुत कर्मणः
     संहितां शरॊतुम इच्छामॊ धर्म्यां पापभयापहाम
 20 [सूत]
     आद्यं पुरुषम ईशानं पुरुहूतं पुरु षटुतम
     ऋतम एकाक्षरं बरह्म वयक्ताव्यक्तं सनातनम
 21 असच च सच चैव च यद विश्वं सद असतः परम
     परावराणां सरष्टारं पुराणं परम अव्ययम
 22 मङ्गल्यं मङ्गलं विष्णुं वरेण्यम अनघं शुचिम
     नमस्कृत्य हृषीकेशं चराचरगुरुं हरिम
 23 महर्षेः पूजितस्येह सर्वलॊके महात्मनः
     परवक्ष्यामि मतं कृत्स्नं वयासस्यामित तेजसः
 24 आचख्युः कवयः के चित संप्रत्याचक्षते परे
     आख्यास्यन्ति तथैवान्ये इतिहासम इमं भुवि
 25 इदं तु तरिषु लॊकेषु महज जञानं परतिष्ठितम
     विस्तरैश च समासैश च धार्यते यद दविजातिभिः
 26 अलंकृतं शुभैः शब्दैः समयैर दिव्यमानुषैः
     छन्दॊ वृत्तैश च विविधैर अन्वितं विदुषां परियम
 27 निष्प्रभे ऽसमिन निरालॊके सर्वतस तमसावृते
     बृहद अण्डम अभूद एकं परजानां बीजम अक्षयम
 28 युगस्यादौ निमित्तं तन महद दिव्यं परचक्षते
     यस्मिंस तच छरूयते सत्यं जयॊतिर बरह्म सनातनम
 29 अद्भुतं चाप्य अचिन्त्यं च सर्वत्र समतां गतम
     अव्यक्तं कारणं सूक्ष्मं यत तत सदसद आत्मकम
 30 यस्मात पितामहॊ जज्ञे परभुर एकः परजापतिः
     बरह्मा सुरगुरुः सथाणुर मनुः कः परमेष्ठ्य अथ
    """, lang="SANSKRIT")
    if txl and type(txl) == dict:
        for code, translation in txl.items():
            name = code + '-Standard-A'
            voice = texttospeech.VoiceSelectionParams(language_code=code, name=name)
            request = texttospeech.SynthesizeLongAudioRequest(
                parent="projects/prisma-cortex-playground/locations/us-central1",
                input={'text': translation},
                audio_config=audio_config,
                voice=voice,
                output_gcs_uri=f'gs://hyperion-graph-bench/mahabharat/tx-{code}'
            )
            response = tts_client.synthesize_long_audio(request=request)
            print(f'Audio content written to file "sample_{code}.LINEAR16"')
