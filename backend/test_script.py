import asyncio
from app.engines.sif.engine import sif_engine
from app.engines.lsr.engine import lsr_engine

async def run_test():
    texts = [
        "money is control panel",
        "worker was repairing control panel and got shocked",
        "person fall down from crane"
    ]
    
    for text in texts:
        print(f"\n====================\nTEST: {text}")
        print("--- SIF ENGINE ---")
        sif_result = await sif_engine.analyze(text, "Incident")
        print("SIF Potential:", sif_result["sif_potential"])
        print("Score:", sif_result["score"])
        
        print("\n--- LSR ENGINE ---")
        # LSR Engine API difference in test script? wait, matcher vs engine
        try:
            lsr_result = await lsr_engine.analyze(text)
        except Exception:
            # Fallback to local import if lsr_engine isn't exactly as above
            from app.engines.lsr.rule_loader import load_lsr_rules
            from app.engines.lsr.matcher import LSRMatcher
            matcher = LSRMatcher(load_lsr_rules())
            lsr_result = matcher.match(text)
            
        print("Matched Rules:")
        for rule in lsr_result:
            print(f" - {rule['rule_id']}: {rule['score']}")

if __name__ == "__main__":
    asyncio.run(run_test())
