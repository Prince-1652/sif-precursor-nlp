import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app.engines.sif.engine import sif_engine
from app.engines.language_gate.detector import LanguageDetector
from app.engines.language_gate.gate import decide_routing

async def main():
    text = "Worker slipped on wet surface during work at height. Fall protection was missing."
    res = await sif_engine.analyze(text, "INCIDENT")
    print("SIF Result 1:", res)
    
    text2 = "Maintenance team bypassed safety interlocks on the conveyor belt to speed up repairs."
    res2 = await sif_engine.analyze(text2, "INCIDENT")
    print("SIF Result 2:", res2)

    detector = LanguageDetector()
    texts = [
        "Worker slipped on wet surface during work at height. Fall protection was missing.",
        "Worker got a minor papercut. All loto was verified prior.",
        "Maintenance team bypassed safety interlocks on the conveyor belt to speed up repairs."
    ]
    for t in texts:
        det = detector.detect(t)
        dec = decide_routing(det, len(t))
        print(f"Lang: {det.language_code}, Conf: {det.confidence:.4f}, Mixed: {det.is_mixed}, Decision: {dec}")

if __name__ == '__main__':
    asyncio.run(main())
