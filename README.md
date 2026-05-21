# DANIEL ALEJANDRO RUIZ VIDAL - 220222028
# SARA XIMENA ZAMBRANO - 2220242019
# JUAN CAMILO LIBERATO - 2220251080

# Install the virtual environment
> python -m venv .venv

# Install the models
> ollama pull nomic-embed-text
> ollama pull gemma4:e2b

# Activate the venv
> .\.venv\Scripts\activate

# install requirements packages
> pip install -r .\requirements.txt

# install torch for CUDA
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Create a dataset/ folder in the project root
# Download the datasets and put them inside
# Link to drive with the datasets: https://drive.google.com/drive/folders/1VT1VLN_QL04DV0jb2aCUuBt86AdiqkPp?usp=sharing 

# Change the path in the LVIS data.yaml to "dataset/LVIS_Fruits_And_Vegetables"
# Change the val attribute to "images/val"

# Download the USDA dataset as JSON as well and put it inside the dataset/ folder

# Download the weights in the PESOS folder of the drive and put them inside the runs/detect/food_detector_v11m/weights folder

# Build the embedding database (If not already built)
> python scripts/build_usda_index.py

# Open a new terminal and execute the backend:
> uvicorn app.main:app --reload --port 8000

# Open a new terminal and execute the frontend:
> streamlit run ui/app.py

