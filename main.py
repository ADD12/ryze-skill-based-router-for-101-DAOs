import uvicorn
from src.rye_router.api import app

def main():
    print("Starting Rye AI Governance Engine...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()