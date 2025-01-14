import os
import sys
import psutil
import signal
import uvicorn
import argparse
import asyncio
import aiofiles
import zipfile
from fastapi import FastAPI, Request, Response, status, Depends, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List

from tools import analyser, recorder, stopAllEvent

##############################################################################################################################

# 启动参数解析，启动环境，应用端口由命令行传入
parser = argparse.ArgumentParser()
parser.add_argument("--host",     help = "主机",       type = str, default = "localhost")
parser.add_argument("--port",     help = "端口",       type = int, default = 80)
parser.add_argument("--modeldir", help = "models目录", type = str, default = "./models")
args = parser.parse_args()

host = args.host
port = args.port
modelDir = args.modeldir

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


# Get current root
currentRoot = Path(sys.argv[0]).root


# 上传文件存储目录
UPLOAD_DIR = Path(currentRoot).joinpath('uploads').as_posix()


# 输出文件存储目录
OUTPUT_DIR = Path(currentRoot).joinpath('outputs').as_posix()


# 定义写入大小
CHUNK_SIZE = 1024 * 1024


async def write_file(filePath, source: UploadFile):
    async with aiofiles.open(filePath, 'wb') as out_file:
        while content := await source.read(CHUNK_SIZE):
            await out_file.write(content)


async def read_file(filePath):
    async with aiofiles.open(filePath, 'rb') as file:
        while content := await file.read(CHUNK_SIZE):
            yield content


@app.post("/upload")
async def upload_file(files: List[UploadFile]):
    os.makedirs(UPLOAD_DIR, exist_ok = True)
    for file in files:
        filePath = Path(UPLOAD_DIR).joinpath(file.filename).as_posix()
        os.remove(filePath) if Path(filePath).exists() else None
        '''
        task = asyncio.create_task(write_file(filePath, file))
        asyncio.get_event_loop().run_until_complete(task)
        '''
        await write_file(filePath, file)
    return {"status": "Succeeded"}


@app.post('/execute_analyser')
async def execute_analyser(request: Request):
    data = await request.json()
    fileName = data.get('fileName')
    chkTypes = data.get('chkTypes')
    await asyncio.to_thread(analyser.mediaAnalyse,
        videoPath = Path(UPLOAD_DIR).joinpath(fileName).as_posix(),
        chkTypes = chkTypes,
        outputFolder = OUTPUT_DIR,
        modelDir = modelDir,
        stopEvent = stopAllEvent
    )
    '''
    zipPath = Path(OUTPUT_DIR).joinpath('result.zip').as_posix()
    os.remove(zipPath) if Path(zipPath).exists() else None
    with zipfile.ZipFile(zipPath, 'w', compression = zipfile.ZIP_DEFLATED) as zipFile:
        for type, paths in result.items():
            for path in paths:
                zipFile.write(path, arcname = f"[{type}]{Path(path).name}")
    return StreamingResponse(
        read_file(zipPath),
        headers = {"Content-Disposition": f"attachment; filename={Path(zipPath).name}"},
        media_type = "application/x-zip-compressed", 
    )
    '''
    return {'result': analyser.result}


@app.post('/stop')
async def stop():
    global stopAllEvent
    stopAllEvent.set()
    return {'message': "Stopping..."}


@app.post('/actuator/shutdown')
async def shutdown():
    global stopAllEvent
    stopAllEvent.set()
    uvicorn.Server(uvicorn.Config(app)).should_exit = True
    Process = psutil.Process(os.getpid())
    ProcessList =  Process.children(recursive = True) + [Process]
    for Process in ProcessList:
        try:
            os.kill(Process.pid, signal.SIGTERM)
        except:
            pass

##############################################################################################################################

if __name__ == '__main__':
    uvicorn.run(
        app = app,
        host = host,
        port = port
    )

##############################################################################################################################