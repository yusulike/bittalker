try:
    import supertonic
    import inspect
    from supertonic.core import Supertonic
    
    # Try to find constants
    print("Searching for Repo ID in supertonic...")
    for name, val in inspect.getmembers(supertonic.core):
        if "supertone" in str(val) or "hf" in str(val) or "REPO" in name:
            print(f"{name}: {val}")
            
    # Check init signature defaults if any
    sig = inspect.signature(Supertonic.__init__)
    print(f"Init sig: {sig}")

except Exception as e:
    print(e)
