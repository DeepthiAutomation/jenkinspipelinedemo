import html, io, os, re, subprocess, tempfile, warnings
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance
warnings.filterwarnings('ignore')

FFMPEG_EXE = r"C:\Users\Skandan Anumala\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"
FFPROBE_EXE = FFMPEG_EXE.replace('ffmpeg.exe', 'ffprobe.exe')
if not os.path.exists(FFMPEG_EXE):
    FFMPEG_EXE, FFPROBE_EXE = 'ffmpeg', 'ffprobe'

st.set_page_config(page_title='AgriVoice Offline', page_icon='GramSetu_AI.png', layout='centered', initial_sidebar_state='expanded')

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#f7f4ed;--card:#fff;--ink:#17211b;--muted:#6f766f;--green:#174c36;--green2:#21684a;--soft:#e7f2eb;--line:#ddd6c8;--amber:#c7782f}
.stApp{background:radial-gradient(circle at top left,rgba(33,104,74,.10),transparent 28%),linear-gradient(180deg,#fbf8f1 0%,var(--bg) 100%);color:var(--ink);font-family:Inter,sans-serif}.block-container{max-width:1080px;padding:2rem 1.4rem 4rem}#MainMenu,footer,header{visibility:hidden}.title-box{background:linear-gradient(135deg,#fff 0%,#f3efe4 100%);border:1px solid var(--line);border-radius:22px;padding:34px;margin-bottom:20px;box-shadow:0 18px 50px rgba(23,76,54,.10)}.title-box h1{margin:0;color:var(--green);font-size:44px;line-height:1.05;font-weight:800;letter-spacing:-1.3px}.title-box p{margin:14px 0 0;color:var(--muted);font-size:16px;line-height:1.65}.notice{background:#fff8ec;border:1px solid #efd7b5;border-left:5px solid var(--amber);border-radius:14px;padding:15px 18px;color:#80511f;font-size:14px;line-height:1.6;margin-bottom:22px}.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0 30px}.steps div{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:15px;box-shadow:0 8px 24px rgba(23,76,54,.06)}.steps b{display:inline-flex;width:28px;height:28px;align-items:center;justify-content:center;border-radius:10px;background:var(--green);color:#fff;font-size:13px;margin-right:9px}.steps span{font-size:13.5px;color:var(--ink);font-weight:600}h1,h2,h3{color:var(--green)!important;font-family:Inter,sans-serif!important;letter-spacing:-.5px}h3{font-size:22px!important;font-weight:800!important}.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.72);border:1px solid var(--line);padding:6px;border-radius:16px;gap:6px;box-shadow:0 8px 24px rgba(23,76,54,.05)}.stTabs [data-baseweb="tab"]{border-radius:12px;padding:10px 18px;font-weight:700;color:var(--muted)}.stTabs [aria-selected="true"]{background:var(--green)!important;color:white!important}textarea,.stTextArea textarea{background:white!important;color:var(--ink)!important;border:1.5px solid var(--line)!important;border-radius:16px!important;font-size:15.5px!important;line-height:1.7!important;padding:15px!important}textarea:focus,.stTextArea textarea:focus{border-color:var(--green2)!important;box-shadow:0 0 0 4px rgba(33,104,74,.13)!important}div[data-baseweb="select"]>div{background:white!important;border-radius:14px!important;border:1.5px solid var(--line)!important;min-height:46px!important}.stSelectbox label,.stTextArea label,.stFileUploader label{color:var(--green)!important;font-weight:800!important;font-size:14px!important}.stButton>button{border-radius:14px;padding:.75rem 1.25rem;font-weight:800;border:1px solid var(--line);background:white;color:var(--ink);box-shadow:0 5px 16px rgba(23,76,54,.06)}.stButton>button:hover{border-color:var(--green2);color:var(--green);transform:translateY(-1px)}.stButton>button[kind="primary"]{background:var(--green)!important;color:white!important;border:none!important;box-shadow:0 14px 28px rgba(23,76,54,.24)!important}.output-box,.feature-card{background:white;border:1px solid var(--line);border-left:6px solid var(--green2);border-radius:18px;padding:22px 24px;box-shadow:0 12px 30px rgba(23,76,54,.07);color:var(--ink)}.output-box{font-size:17px;line-height:1.9}[data-testid="stFileUploaderDropzone"]{background:rgba(255,255,255,.85)!important;border:2px dashed #c8c0ae!important;border-radius:18px!important}.stProgress>div>div{background:linear-gradient(90deg,var(--green),#57b984)!important}div[data-testid="stAlert"]{border-radius:16px;border:1px solid var(--line)}.stDownloadButton>button{background:var(--soft)!important;color:var(--green)!important;border:1px solid #c9e3d1!important;border-radius:14px!important;font-weight:800!important}[data-testid="stSidebar"]{background:#efe9dc;border-right:1px solid var(--line)}[data-testid="stSidebar"] button{width:100%}audio,video{width:100%;border-radius:18px;margin-top:10px;box-shadow:0 10px 30px rgba(0,0,0,.10)}hr{border-color:var(--line)!important}@media(max-width:700px){.title-box h1{font-size:32px}.steps{grid-template-columns:1fr 1fr}}
</style>
''', unsafe_allow_html=True)

st.markdown('''<div class="title-box"><h1>AgriVoice Offline</h1><p>Offline AI translation for field trainers, farmers, PDFs, images, videos, and live voice conversations.</p></div>''', unsafe_allow_html=True)
st.markdown('''<div class="notice"><b>CPU-first demo:</b> Runs on Intel i5 11th Gen / 8 GB RAM. First run downloads models once; after that, the app works from local cache.</div>''', unsafe_allow_html=True)
st.markdown('''<div class="steps"><div><b>1</b><span>Speak or upload</span></div><div><b>2</b><span>Extract text/speech</span></div><div><b>3</b><span>Translate offline</span></div><div><b>4</b><span>Listen or download</span></div></div>''', unsafe_allow_html=True)

LANGUAGES={'English':'en','Hindi':'hi','Marathi':'mr'}
NLLB_CODES={'en':'eng_Latn','hi':'hin_Deva','mr':'mar_Deva'}
WHISPER_CODES={'en':'en','hi':'hi','mr':'mr'}
MMS_TTS_MODELS={'en':'facebook/mms-tts-eng','hi':'facebook/mms-tts-hin','mr':'facebook/mms-tts-mar'}
for k in ['input_text','text_translation','image_extracted_text','image_translation','pdf_extracted_text','pdf_translation','video_transcript','video_translation','video_srt','live_transcript','live_translation']:
    st.session_state.setdefault(k,'')
for k in ['video_audio_bytes','dubbed_video_bytes','original_video_bytes','live_audio_bytes']:
    st.session_state.setdefault(k,b'')
st.session_state.setdefault('ffmpeg_ok',None)

def show_output_box(text):
    st.markdown(f"<div class='output-box'>{html.escape(str(text)).replace(chr(10),'<br>')}</div>", unsafe_allow_html=True)
def show_feature(text): st.markdown(f"<div class='feature-card'>{text}</div>", unsafe_allow_html=True)
def clean_text_for_tts(text): return re.sub(r'\s+',' ',str(text).strip()).replace('।','.')

@st.cache_resource(show_spinner=False)
def load_translation_model():
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    name='facebook/nllb-200-distilled-600M'
    return AutoTokenizer.from_pretrained(name), AutoModelForSeq2SeqLM.from_pretrained(name)
def translate_chunk(text,src,tgt):
    if src==tgt: return text
    tok,model=load_translation_model(); tok.src_lang=NLLB_CODES[src]; target=NLLB_CODES[tgt]
    inputs=tok(text,return_tensors='pt',padding=True,truncation=True,max_length=512)
    bos=tok.lang_code_to_id[target] if hasattr(tok,'lang_code_to_id') else tok.convert_tokens_to_ids(target)
    out=model.generate(**inputs,forced_bos_token_id=bos,max_length=512)
    return tok.batch_decode(out,skip_special_tokens=True)[0]
def translate_text(text,src,tgt):
    text=str(text).strip()
    if not text or src==tgt: return text
    if len(text)<=700: return translate_chunk(text,src,tgt)
    chunks=[]; cur=''
    for line in text.splitlines():
        line=line.strip()
        if not line: continue
        if len(cur)+len(line)+1>700:
            if cur: chunks.append(cur)
            cur=line
        else: cur=cur+'\n'+line if cur else line
    if cur: chunks.append(cur)
    return '\n'.join(translate_chunk(c,src,tgt) for c in chunks)

@st.cache_resource(show_spinner=False)
def load_tts_model(lang):
    from transformers import AutoTokenizer, VitsModel
    name=MMS_TTS_MODELS[lang]
    return VitsModel.from_pretrained(name), AutoTokenizer.from_pretrained(name)
def create_audio(text,lang,max_chars=900):
    import scipy.io.wavfile, torch
    text=clean_text_for_tts(text)
    if not text: return None
    if len(text)>max_chars: text=text[:max_chars]
    model,tok=load_tts_model(lang); inputs=tok(text,return_tensors='pt')
    if 'input_ids' in inputs and inputs['input_ids'].shape[-1]<2:
        text+='.'; inputs=tok(text,return_tensors='pt')
    with torch.no_grad(): wav=model(**inputs).waveform.squeeze().numpy()
    buf=io.BytesIO(); scipy.io.wavfile.write(buf,model.config.sampling_rate,wav); buf.seek(0); return buf.read()

@st.cache_resource(show_spinner=False)
def load_whisper_model():
    from faster_whisper import WhisperModel
    return WhisperModel('tiny',device='cpu',compute_type='int8')
def transcribe_audio_file(path,src,tgt=None):
    model=load_whisper_model(); task='translate' if tgt=='en' and src!='en' else 'transcribe'
    segs,info=model.transcribe(path,language=WHISPER_CODES.get(src),task=task,beam_size=5,vad_filter=False,condition_on_previous_text=False)
    return ' '.join(s.text.strip() for s in segs if s.text.strip())
def transcribe_video(path,src):
    model=load_whisper_model(); segs,info=model.transcribe(path,language=WHISPER_CODES.get(src),task='transcribe',beam_size=5,vad_filter=True,condition_on_previous_text=False)
    parts=[]; blocks=[]
    for i,s in enumerate(segs,1):
        t=s.text.strip()
        if t: parts.append(t); blocks.append({'index':i,'start':float(s.start),'end':float(s.end),'text':t})
    return '\n'.join(parts),blocks

@st.cache_resource(show_spinner=False)
def load_ocr_reader(lang):
    import easyocr
    return easyocr.Reader(['en'] if lang=='en' else ['hi','en'],gpu=False)
def preprocess_for_ocr(img):
    img=img.convert('RGB'); w,h=img.size
    if max(w,h)<1800:
        scale=1800/max(w,h); img=img.resize((int(w*scale),int(h*scale)),Image.LANCZOS)
    return ImageEnhance.Sharpness(ImageEnhance.Contrast(img).enhance(1.8)).enhance(1.7)
def ocr_image(img,lang):
    res=load_ocr_reader(lang).readtext(np.array(preprocess_for_ocr(img)),detail=0,paragraph=False)
    return '\n'.join(str(x).strip() for x in res if str(x).strip())
def extract_pdf_text_and_images(pdf_bytes,lang,progress,status):
    import fitz
    doc=fitz.open(stream=pdf_bytes,filetype='pdf'); out=[]
    for i,page in enumerate(doc):
        status.text(f'Reading page {i+1} of {len(doc)}...'); progress.progress((i+1)/len(doc)); parts=[]
        txt=page.get_text('text').strip()
        if txt: parts.append(txt)
        pix=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
        img=Image.frombytes('RGB',[pix.width,pix.height],pix.samples); ot=ocr_image(img,lang).strip()
        if ot: parts.append(ot)
        if parts: out.append('\n\n'.join(parts))
    doc.close(); return '\n\n'.join(out)

def srt_time(sec):
    sec=max(0,float(sec)); whole=int(sec); ms=int(round((sec-whole)*1000));
    if ms>=1000: whole+=1; ms-=1000
    return f'{whole//3600:02}:{(whole%3600)//60:02}:{whole%60:02},{ms:03}'
def get_video_duration(path):
    r=subprocess.run([FFPROBE_EXE,'-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',path],capture_output=True,text=True)
    if r.returncode!=0: raise RuntimeError(r.stderr)
    return float(r.stdout.strip())
def make_translated_srt(blocks,src,tgt):
    s=''
    for i,b in enumerate(blocks,1):
        s+=f"{i}\n{srt_time(b['start'])} --> {srt_time(b['end'])}\n{translate_text(b['text'],src,tgt).strip()}\n\n"
    return s
def create_segment_dubbed_audio(blocks,src,tgt,progress_bar=None,status_text=None):
    import scipy.io.wavfile, scipy.signal
    if not blocks: return None
    sr=16000; final=np.zeros(int(sr*(int(blocks[-1]['end']*1000)+2000)/1000),dtype=np.float32)
    for i,b in enumerate(blocks,1):
        if status_text: status_text.text(f'Generating synced voice segment {i} of {len(blocks)}...')
        if progress_bar: progress_bar.progress(i/len(blocks))
        start=int(b['start']*1000); end=int(b['end']*1000); slot=max(500,end-start)
        txt=clean_text_for_tts(translate_text(b['text'],src,tgt))
        if not txt: continue
        try: ab=create_audio(txt,tgt,max_chars=220)
        except Exception: continue
        if not ab: continue
        s,d=scipy.io.wavfile.read(io.BytesIO(ab));
        if d.ndim>1: d=d.mean(axis=1)
        d=d.astype(np.float32);
        if np.max(np.abs(d))>0: d=d/np.max(np.abs(d))*.8
        if s!=sr: d=scipy.signal.resample_poly(d,sr,s)
        maxs=int(sr*slot/1000); d=d[:maxs]
        stt=int(sr*start/1000); enn=min(stt+len(d),len(final))
        if stt<len(final): final[stt:enn]+=d[:enn-stt]
    m=np.max(np.abs(final))
    if m>1: final=final/m*.95
    buf=io.BytesIO(); scipy.io.wavfile.write(buf,sr,final); buf.seek(0); return buf.read()
def build_dubbed_video(video_path,wav_bytes,srt_text=None):
    tmp=tempfile.mkdtemp(); wav=os.path.join(tmp,'audio.wav'); out=os.path.join(tmp,'out.mp4')
    open(wav,'wb').write(wav_bytes)
    vf='scale=trunc(iw/2)*2:trunc(ih/2)*2'
    if srt_text:
        sp=os.path.join(tmp,'subs.srt'); open(sp,'w',encoding='utf-8').write(srt_text); esc=sp.replace('\\','/').replace(':','\\:'); vf=f"subtitles='{esc}',"+vf
    cmd=[FFMPEG_EXE,'-y','-i',video_path,'-i',wav,'-map','0:v:0','-map','1:a:0','-vf',vf,'-c:v','libx264','-pix_fmt','yuv420p','-preset','fast','-crf','23','-c:a','aac','-b:a','128k','-movflags','+faststart','-shortest',out]
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0: raise RuntimeError(r.stderr)
    return open(out,'rb').read()
def download_youtube_video(url):
    import yt_dlp
    td=tempfile.mkdtemp(); tmpl=os.path.join(td,'yt.%(ext)s')
    with yt_dlp.YoutubeDL({'format':'mp4/best','outtmpl':tmpl,'quiet':True,'noplaylist':True,'merge_output_format':'mp4'}) as ydl:
        info=ydl.extract_info(url,download=True); f=ydl.prepare_filename(info)
        return f if f.endswith('.mp4') else os.path.splitext(f)[0]+'.mp4'

with st.sidebar:
    st.markdown('### Offline Models')
    if st.button('Preload Translation'):
        with st.spinner('Loading...'): load_translation_model()
        st.success('Ready')
    if st.button('Preload Speech'):
        with st.spinner('Loading...'): load_whisper_model()
        st.success('Ready')
    if st.button('Preload TTS'):
        with st.spinner('Loading...'):
            load_tts_model('en'); load_tts_model('hi'); load_tts_model('mr')
        st.success('Ready')
    if st.button('Preload OCR'):
        with st.spinner('Loading...'):
            load_ocr_reader('en'); load_ocr_reader('hi')
        st.success('Ready')
    st.divider(); st.markdown('### Downloads')
    if st.session_state.live_audio_bytes: st.download_button('Live Voice Audio',st.session_state.live_audio_bytes,'live_translation.wav','audio/wav')
    if st.session_state.dubbed_video_bytes: st.download_button('Dubbed Video',st.session_state.dubbed_video_bytes,'dubbed_video.mp4','video/mp4')

tab1,tab2,tab3,tab4,tab5=st.tabs(['Text','Image OCR','PDF OCR','Video Dubbing','Live Translation'])

with tab1:
    st.subheader('Translate Text'); text=st.text_area('Text:',height=180,key='input_text')
    c1,c2=st.columns(2); src_lang=c1.selectbox('From:',list(LANGUAGES),0,key='txt_src'); tgt_lang=c2.selectbox('To:',list(LANGUAGES),1,key='txt_tgt')
    if st.button('Translate Text',type='primary'):
        if text.strip():
            with st.spinner('Translating...'): st.session_state.text_translation=translate_text(text,LANGUAGES[src_lang],LANGUAGES[tgt_lang])
        else: st.warning('Enter text first.')
    if st.session_state.text_translation:
        show_output_box(st.session_state.text_translation); st.download_button('Download Text',st.session_state.text_translation,'text_translation.txt','text/plain')

with tab2:
    st.subheader('Image OCR Translation'); imgfile=st.file_uploader('Choose image:',type=['png','jpg','jpeg','webp','bmp','tif','tiff'],key='img')
    c1,c2=st.columns(2); sl=c1.selectbox('Image language:',list(LANGUAGES),0,key='img_src'); tl=c2.selectbox('Translate to:',list(LANGUAGES),1,key='img_tgt')
    if imgfile:
        im=Image.open(imgfile).convert('RGB'); st.image(im,use_container_width=True)
        if st.button('Extract Text from Image',type='primary'):
            with st.spinner('Reading image...'): st.session_state.image_extracted_text=ocr_image(im,LANGUAGES[sl]); st.session_state.image_translation=''
    if st.session_state.image_extracted_text:
        corr=st.text_area('Review text:',value=st.session_state.image_extracted_text,height=160,key='img_corr')
        if st.button('Translate Image Text',type='primary'):
            with st.spinner('Translating...'): st.session_state.image_translation=translate_text(corr,LANGUAGES[sl],LANGUAGES[tl])
    if st.session_state.image_translation: show_output_box(st.session_state.image_translation)

with tab3:
    st.subheader('PDF OCR Translation'); pdf=st.file_uploader('Choose PDF:',type=['pdf'],key='pdf')
    c1,c2=st.columns(2); sl=c1.selectbox('PDF language:',list(LANGUAGES),0,key='pdf_src'); tl=c2.selectbox('Translate to:',list(LANGUAGES),1,key='pdf_tgt')
    if pdf and st.button('Extract Text from PDF',type='primary'):
        p=st.progress(0); s=st.empty()
        try:
            st.session_state.pdf_extracted_text=extract_pdf_text_and_images(pdf.getvalue(),LANGUAGES[sl],p,s); st.session_state.pdf_translation=''; st.success('PDF extracted.')
        except Exception as e: st.error('PDF failed.'); st.caption(str(e))
        finally: p.empty(); s.empty()
    if st.session_state.pdf_extracted_text:
        corr=st.text_area('Review text:',value=st.session_state.pdf_extracted_text,height=240,key='pdf_corr')
        if st.button('Translate PDF Text',type='primary'):
            with st.spinner('Translating...'): st.session_state.pdf_translation=translate_text(corr,LANGUAGES[sl],LANGUAGES[tl])
    if st.session_state.pdf_translation: show_output_box(st.session_state.pdf_translation)

with tab4:
    st.subheader('Video Speech Translation & Dubbing'); show_feature('<b>Synced video dubbing:</b> translates each speech segment and places audio at original timestamps.')
    yt=st.text_input('Optional YouTube link:'); vid=st.file_uploader('Or choose video:',type=['mp4','mov','avi','mkv','webm'],key='vid')
    c1,c2=st.columns(2); sl=c1.selectbox('Spoken language:',list(LANGUAGES),0,key='vid_src'); tl=c2.selectbox('Dub voice to:',list(LANGUAGES),1,key='vid_tgt')
    burn=st.checkbox('Burn translated subtitles into video',False)
    if yt.strip(): st.video(yt.strip())
    if vid: st.video(vid)
    if (yt.strip() or vid) and st.button('Dub Video with Translated Voice',type='primary'):
        path=None
        try:
            if yt.strip():
                with st.spinner('Downloading...'): path=download_youtube_video(yt.strip())
            else:
                suffix=os.path.splitext(vid.name)[1] or '.mp4'; tmp=tempfile.NamedTemporaryFile(delete=False,suffix=suffix); tmp.write(vid.getvalue()); tmp.close(); path=tmp.name
            with open(path,'rb') as f: st.session_state.original_video_bytes=f.read()
            dur=get_video_duration(path); st.caption(f'Video length: {dur/60:.1f} minutes')
            if dur>20*60: st.error('Use a video up to 20 minutes.'); st.stop()
            with st.spinner('Transcribing...'): transcript,blocks=transcribe_video(path,LANGUAGES[sl])
            if not transcript.strip(): st.warning('No speech detected.')
            else:
                st.session_state.video_transcript=transcript
                with st.spinner('Making subtitles...'):
                    st.session_state.video_translation=translate_text(transcript,LANGUAGES[sl],LANGUAGES[tl]); st.session_state.video_srt=make_translated_srt(blocks,LANGUAGES[sl],LANGUAGES[tl])
                pr=st.progress(0); status=st.empty(); wav=create_segment_dubbed_audio(blocks,LANGUAGES[sl],LANGUAGES[tl],pr,status); status.empty()
                if wav:
                    st.session_state.video_audio_bytes=wav
                    with st.spinner('Building MP4...'): st.session_state.dubbed_video_bytes=build_dubbed_video(path,wav,st.session_state.video_srt if burn else None)
                    st.success('Dubbed video ready.')
        except Exception as e: st.error('Video processing failed.'); st.caption(str(e))
        finally:
            if path and os.path.exists(path): os.remove(path)
    if st.session_state.video_transcript: st.text_area('Original Transcript:',value=st.session_state.video_transcript,height=140,key='vtrans')
    if st.session_state.video_translation: show_output_box(st.session_state.video_translation)
    if st.session_state.video_srt: st.download_button('Download Subtitles',st.session_state.video_srt,'translated_subtitles.srt','text/plain')
    if st.session_state.dubbed_video_bytes:
        st.video(st.session_state.dubbed_video_bytes); st.download_button('Download Dubbed Video',st.session_state.dubbed_video_bytes,'dubbed_video.mp4','video/mp4')

with tab5:
    st.subheader('Live Voice Translation'); show_feature('<b>Live mode:</b> Record a short voice clip. Hindi/Marathi → English uses Whisper translate mode, avoiding bad romanized Hindi.')
    c1,c2=st.columns(2); sl=c1.selectbox('Speak in:',list(LANGUAGES),1,key='live_src'); tl=c2.selectbox('Translate voice to:',list(LANGUAGES),0,key='live_tgt')
    src=LANGUAGES[sl]; tgt=LANGUAGES[tl]
    st.info('Record 5–20 seconds. Speak clearly.')
    aud=st.audio_input('Record your voice:',sample_rate=16000,key='live_audio_input')
    if aud:
        st.audio(aud,format='audio/wav')
        if st.button('Translate Recorded Voice',type='primary',key='live_btn'):
            path=None
            try:
                tmp=tempfile.NamedTemporaryFile(delete=False,suffix='.wav'); tmp.write(aud.getbuffer()); tmp.close(); path=tmp.name
                with st.spinner('Step 1/3: Listening...'): transcript=transcribe_audio_file(path,src,tgt)
                if not transcript.strip(): st.warning('No speech detected.')
                else:
                    st.session_state.live_transcript=transcript
                    with st.spinner('Step 2/3: Translating...'):
                        if tgt=='en' and src!='en': translation=transcript
                        elif src==tgt: translation=transcript
                        else: translation=translate_text(transcript,src,tgt)
                        st.session_state.live_translation=translation
                    with st.spinner('Step 3/3: Generating voice...'):
                        st.session_state.live_audio_bytes=create_audio(st.session_state.live_translation,tgt,max_chars=700) or b''
                    st.success('Live translation ready.')
            except Exception as e: st.error('Live translation failed.'); st.caption(str(e))
            finally:
                if path and os.path.exists(path): os.remove(path)
    if st.session_state.live_transcript:
        st.subheader('Detected / Translated Speech'); st.text_area('Transcript:',value=st.session_state.live_transcript,height=100,key='live_transcript_box')
    if st.session_state.live_translation:
        st.subheader(f'Final Output → {tl}'); show_output_box(st.session_state.live_translation)
    if st.session_state.live_audio_bytes:
        st.subheader('Translated Voice'); st.audio(st.session_state.live_audio_bytes,format='audio/wav'); st.download_button('Download Live Translation Audio',st.session_state.live_audio_bytes,'live_translated_voice.wav','audio/wav')

st.divider(); st.caption('AgriVoice Offline · OCR · PDF Translation · Synced Video Dubbing · Live Voice Translation')
