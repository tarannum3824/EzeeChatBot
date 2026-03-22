from langchain_text_splitters import RecursiveCharacterTextSplitter

# Semantic separators ordered by priority:
# 1. Double newlines (paragraph boundaries)
# 2. Single newlines (line breaks)
# 3. Sentences (period/question/exclamation)
# 4. Commas, spaces (last resort)
SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", ", ", " "]


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=SEPARATORS,
        length_function=len,
    )
    return splitter.split_text(text)
