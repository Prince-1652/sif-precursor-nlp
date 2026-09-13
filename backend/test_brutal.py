import asyncio
from app.engines.sif.engine import sif_engine
from app.engines.lsr.engine import lsr_engine
from app.engines.entities import entity_engine
from app.engines.decision import decision_engine
from app.engines.language_gate.detector import LanguageDetector
from app.engines.preprocessing.pipeline import run_preprocessing

async def run_tests():
    texts = [
        "money is crane",
        "the sky is blue and happy",
        "a random person was eating lunch",
        "",
        "!!!!!",
        "worker fell from crane and died",  # Actual SIF
        "cut my finger on paper",          # Low risk
        "crane" * 100,                     # Keyword stuffing
        "money is control panel",          # Another non-report
        "I love you but I hate the generator", # Emotion + keyword
        "thief broke the lock near the crane", # Failed barrier + LSR match
    ]
    
    print("Running Brutal Tests...\n")
    for text in texts:
        print(f"=====================================")
        print(f"INPUT: '{text}'")
        
        # 1. Preprocessing
        prep = run_preprocessing(text)
        print(f"PREPROC: Valid={prep.is_valid}, Errors={prep.validation_errors}, Text='{prep.normalized_text}'")
        if not prep.is_valid:
            print("--- SKIPPED FURTHER PROCESSING DUE TO INVALID TEXT ---")
            continue
            
        # 2. Language Gate
        detector = LanguageDetector()
        detection = detector.detect(prep.normalized_text)
        print(f"LANG GATE: language_code={detection.language_code}, confidence={detection.confidence}")
        
        # 3. Engines
        try:
            sif_res = await sif_engine.analyze(prep.normalized_text, "Incident")
            print(f"SIF ENGINE: potential={sif_res['sif_potential']}, score={sif_res['score']}")
        except Exception as e:
            sif_res = None
            print(f"SIF ENGINE: ERROR: {e}")
            
        try:
            lsr_res = await lsr_engine.analyze(prep.normalized_text)
            lsrs = [f"{r['rule_id']}({r['score']})" for r in lsr_res]
            print(f"LSR ENGINE: matched={len(lsr_res)}, details={lsrs}")
        except Exception as e:
            lsr_res = []
            print(f"LSR ENGINE: ERROR: {e}")
            
        try:
            entity_res = await entity_engine.extract(prep.normalized_text)
            ents = [f"{e['entity_type']}='{e['value']}'" for e in entity_res]
            print(f"ENTITY ENGINE: entities found = {len(entity_res)}, details={ents}")
        except Exception as e:
            entity_res = {}
            print(f"ENTITY ENGINE: ERROR: {e}")
            
        # 4. Decision
        if sif_res:
            try:
                review_state, contradictions, updated_sif = decision_engine.orchestrate(sif_res, lsr_res, entity_res)
                print(f"DECISION: state={review_state}, contradictions={contradictions}, updated_sif_potential={updated_sif['sif_potential']}")
            except Exception as e:
                print(f"DECISION: ERROR: {e}")
        
        print("\n")

    print("\n\n--- API ENDPOINT TESTS ---")
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    # 1. Deduplication loophole test
    payload = {
        "original_text": "worker was repairing control panel and got shocked",
        "report_type": "Incident",
        "source": "brutal_test"
    }
    headers = {"X-API-Key": "test-key-or-whatever"} # Note: security dependency might block
    
    # Let's override security dependency for test
    from app.core.security import verify_api_key
    app.dependency_overrides[verify_api_key] = lambda: True
    
    print("Testing Deduplication...")
    res1 = client.post("/api/v1/reports/manual", json=payload)
    if res1.status_code == 200:
        print("First manual POST success:", res1.json().get('id'))
    else:
        print("First manual POST failed:", res1.status_code, res1.text)
        
    res2 = client.post("/api/v1/reports/manual", json=payload)
    if res2.status_code == 200:
        print("Second manual POST success:", res2.json().get('id'))
        if res1.json().get('id') == res2.json().get('id'):
            print("Deduplication WORKED (same ID)")
        else:
            print("Deduplication FAILED (different IDs for same text!)")
    
    # 2. XSS / Injection test
    print("\nTesting Injection/XSS in text...")
    payload_xss = {
        "original_text": "<script>alert(1)</script> worker fell from crane",
        "report_type": "Incident",
        "source": "brutal_test"
    }
    res_xss = client.post("/api/v1/reports/analyze", json=payload_xss)
    print("XSS Analyze response status:", res_xss.status_code)
    if res_xss.status_code == 200:
        print("Normalized text after XSS:", res_xss.json().get('normalized_text'))
        
    # 3. Massive payload test
    print("\nTesting Massive Payload...")
    payload_massive = {
        "original_text": "crane " * 10000,
        "report_type": "Incident",
        "source": "brutal_test"
    }
    res_massive = client.post("/api/v1/reports/analyze", json=payload_massive)
    print("Massive payload status:", res_massive.status_code)

if __name__ == "__main__":
    asyncio.run(run_tests())
