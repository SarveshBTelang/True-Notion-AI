import warnings

def langchain_warnings():
    try:
        from langchain.schema import LangChainDeprecationWarning
        warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)
    except ImportError:
        # If LangChainDeprecationWarning not found, fallback to message filtering
        warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")
        warnings.filterwarnings("ignore", message=".*deprecated.*")

def all():
    warnings.filterwarnings("ignore")