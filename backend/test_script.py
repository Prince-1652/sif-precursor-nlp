import asyncio
from app.engines.sif.engine import sif_engine
from app.engines.lsr.matcher import lsr_engine

async def run_test():
    text = "person fall down from crane"
    
    print("--- SIF ENGINE ---")
    sif_result = await sif_engine.analyze(text, "Incident")
    print("SIF Potential:", sif_result["sif_potential"])
    print("Risk Band:", sif_result["risk_band"])
    print("Score:", sif_result["score"])
    print("Evidence:")
    for ev in sif_result["evidence"]:
        print(f" - {ev['concept']}: {ev['text']} (type: {ev['type']}, weight: {ev['weight']})")
        
    print("\n--- LSR ENGINE ---")
    lsr_result = await lsr_engine.analyze(text)
    print("Matched Rules:")
    for rule in lsr_result:
        print(f" - {rule['rule_id']}: {rule['reason']}")

if __name__ == "__main__":
    asyncio.run(run_test())
