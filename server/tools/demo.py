import os
import logging
from pathlib import Path

import analyser

##############################################################################################################################

# Set logger
logPath = "./myLog.log"
os.remove(logPath) if os.path.exists(logPath) else None

logger = logging.getLogger('analyser')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

consoleHeader = logging.StreamHandler()
consoleHeader.setFormatter(formatter)
logger.addHandler(consoleHeader)

fileHandler = logging.FileHandler(logPath)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


path = r'D:\AIGraphCode\tpyscripts\DemoTmts\logs\demo_tmts_display_ASALE3741B000022_20241224_192419\log\screencap\case_20241224_192555.mp4'


# Start
for i in range(0, 1):
    logger.info("Start iteration: %s" % i)
    if Path(path).is_file():
        mediaPaths = [path]
    if Path(path).is_dir():
        mediaPaths = Path("./testVids").iterdir()
    for mediaPath in mediaPaths:
        logger.info("mediaPath: %s" % mediaPath)
        result, frameRate = analyser.mediaAnalyse(
            Path(mediaPath).as_posix(),
            chkTypes = ['bChkGlich', 'bChkFlick'],
            outputFolder = r'./output',
            modelDir = r'./models',
            camCrop = True,
            extractType = analyser.ExtractType.TENSOR
        )
        logger.info("result: %s" % result)
        logger.info("frameRate: %s" % frameRate)
    logger.info("Iteration %s over" % i)
logger.info("Done")

##############################################################################################################################