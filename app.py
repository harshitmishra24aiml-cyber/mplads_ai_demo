from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd, numpy as np, io, os
from sklearn.ensemble import IsolationForest

app = FastAPI(title='MPLADS AI Risk Monitor')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data.csv')
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')

REQUIRED=['project_id','work_name','category','district','sanctioned_amount','expenditure','progress_percent','days_elapsed','planned_days','vendor_id','latitude','longitude']

def analyze(df):
    df=df.copy()
    for c in ['sanctioned_amount','expenditure','progress_percent','days_elapsed','planned_days','latitude','longitude']:
        df[c]=pd.to_numeric(df[c], errors='coerce').fillna(0)
    df['expenditure_ratio']=(df.expenditure/df.sanctioned_amount.replace(0,np.nan)).fillna(0)
    df['delay_ratio']=(df.days_elapsed/df.planned_days.replace(0,np.nan)).fillna(0)
    df['cost_deviation']=df.expenditure_ratio
    features=df[['expenditure_ratio','progress_percent','delay_ratio']].replace([np.inf,-np.inf],0).fillna(0)
    if len(df)>=5:
        model=IsolationForest(n_estimators=100, contamination=0.2, random_state=42)
        pred=model.fit_predict(features)
        df['ml_anomaly']=pred==-1
    else: df['ml_anomaly']=False
    scores=[]; reasons=[]
    for _,r in df.iterrows():
        score=0; rs=[]
        if r.expenditure_ratio>0.85:
            score+=25; rs.append('Expenditure is very high compared with sanctioned amount')
        if r.progress_percent<40 and r.expenditure_ratio>0.65:
            score+=30; rs.append('High expenditure with low physical progress')
        if r.delay_ratio>1.15:
            score+=25; rs.append('Project is beyond planned timeline')
        if r.progress_percent<30:
            score+=10; rs.append('Very low completion progress')
        if bool(r.ml_anomaly):
            score+=20; rs.append('Unusual pattern detected by Isolation Forest')
        score=min(score,100)
        level='High' if score>=60 else ('Medium' if score>=30 else 'Low')
        if not rs: rs=['No significant anomaly detected']
        scores.append((score,level)); reasons.append('; '.join(rs))
    df['risk_score']=[x[0] for x in scores]; df['risk_level']=[x[1] for x in scores]; df['reasons']=reasons
    return df

def records(df):
    out=[]
    for _,r in df.iterrows():
        d={k:(None if pd.isna(v) else v.item() if hasattr(v,'item') else v) for k,v in r.to_dict().items()}
        out.append(d)
    return out

@app.get('/', response_class=HTMLResponse)
def home():
    return open(INDEX_PATH, encoding='utf-8').read()

@app.get('/api/analyze')
def get_analysis():
    df=analyze(pd.read_csv(DATA_PATH))
    return {'projects':records(df),'summary':summary(df)}

@app.post('/api/upload')
async def upload(file: UploadFile=File(...)):
    raw = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        return JSONResponse(status_code=400, content={'error': f'Invalid CSV file: {exc}'})
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing: return {'error':f'Missing columns: {", ".join(missing)}'}
    df.to_csv(DATA_PATH,index=False)
    result=analyze(df)
    return {'projects':records(result),'summary':summary(result)}

def summary(df):
    return {'total':len(df),'high':int((df.risk_level=='High').sum()),'medium':int((df.risk_level=='Medium').sum()),'low':int((df.risk_level=='Low').sum()),'avg_risk':round(float(df.risk_score.mean()),1)}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', '8000')))
