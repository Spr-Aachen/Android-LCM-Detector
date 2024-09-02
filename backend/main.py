import os
import io
import sys
import json
import uvicorn
import argparse
from typing import List, Union, Optional
from fastapi import FastAPI, Request, Response, status, Depends, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

from tools.Exec import *

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
    result = Exec(
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

##############################################################################################################################

if __name__ == '__main__':
    uvicorn.run(
        app = app,
        host = 'localhost',
        port = 8080
    )

##############################################################################################################################