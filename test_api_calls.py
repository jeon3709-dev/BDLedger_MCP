import asyncio
import os
from server import br_health_check, br_get_basis_ouln, br_get_title, br_get_recap_title

async def main():
    print("--- Running BDLedger MCP Server Live API Tests ---")
    if not os.path.exists(".env"):
        print("WARNING: .env file does not exist. Please create one with BLDRGST_API_KEY first.")
        
    print("\n[1] Running br_health_check...")
    res = await br_health_check()
    print("Health Check Result:", res)
    
    # Sample PNU: 1168010100108220002 (서울 강남구 역삼동 822-2)
    sample_pnu = "1168010100108220002"
    print(f"\n[2] Querying br_get_basis_ouln for PNU: {sample_pnu}...")
    res = await br_get_basis_ouln(pnu=sample_pnu)
    print("Basic Outline Status:", res.get("status"))
    if res.get("status") == "OK":
        print("Records count:", len(res.get("results", [])))
        print("First record preview:", res.get("results")[0])
    else:
        print("Message:", res.get("message"))
        
    print(f"\n[3] Querying br_get_title for PNU: {sample_pnu}...")
    res = await br_get_title(pnu=sample_pnu)
    print("Title Status:", res.get("status"))
    if res.get("status") == "OK":
        print("Records count:", len(res.get("results", [])))
        print("First record preview:", res.get("results")[0])
    else:
        print("Message:", res.get("message"))

if __name__ == "__main__":
    asyncio.run(main())
