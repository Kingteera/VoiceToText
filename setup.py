from cx_Freeze import setup, Executable

# Define build options
build_options = {
    "packages": ["tkinter", "PIL", "pydub","speech_recognition"],  # Add required packages here
    "excludes": [],  # Exclude unnecessary modules
    "include_msvcr": True,
    "include_files": ["src"]
    # "include_files": [""]  # Include extra files like data directories
}

executables = [
    Executable("voice2txt.py", base="Win32GUI", icon="src/icon/icon3.ico")  # GUI app with an icon
]

setup(
    name="Audio to Text Converter",
    version="1.0",
    description="Audio to Text Converter",
    options={"build_exe": build_options},
    executables=executables
)
