import uvicorn
import argparse
import asyncio
from fastapi import FastAPI, Request, Response, status, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from tools.Exec import Exec, StopAllEvent, isalleventset

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
parser.add_argument("--modeldir", help = "models目录", type = str, default = './models')
args = parser.parse_args()

ModelDir = args.modeldir

##############################################################################################################################

# App definition
app = FastAPI()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.post('/execute')
async def execute(request: Request):
    data = await request.json()
    CaseCMD = data.get('CaseCMD')
    SaveDir_PC = data.get('SaveDir_PC')
    bChkH = data.get('chkHua')
    bChkBW = data.get('chkB_ok_W')
    bChkSplit_then_BW = data.get('chkSplit_then_BokW')
    bChkNobarSplit_then_BW = data.get('chkNobarSplit_then_BW')
    bChkBlackback = data.get('chkBlackback')
    output_folder = data.get('output_folder')
    result = await asyncio.to_thread(Exec,
        CaseCMD,
        SaveDir_PC,
        bChkH,
        bChkBW,
        bChkSplit_then_BW,
        bChkNobarSplit_then_BW,
        bChkBlackback,
        output_folder,
        ModelDir,
    )
    return {'message': result}


@app.post('/stop')
async def stop():
    global StopAllEvent
    StopAllEvent.set()
    return {'message': "Stopping..."}


@app.post('/actuator/shutdown')
async def shutdown():
    global StopAllEvent
    StopAllEvent.set()
    uvicorn.Server(uvicorn.Config(app)).should_exit = True
    return {'message': "Shutting down..."}

'''
@app.post('/terminate')
async def terminate():
    Process = psutil.Process(os.getpid())
    ProcessList =  Process.children(recursive = True) + [Process]
    for Process in ProcessList:
        try:
            os.kill(Process.pid, signal.SIGTERM)
        except:
            pass
    return {'message': "Terminating..."}
'''
##############################################################################################################################

if __name__ == '__main__':
    uvicorn.run(
        app = app,
        host = 'localhost',
        port = 8080
    )

##############################################################################################################################